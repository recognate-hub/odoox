import { NextResponse } from 'next/server';
import { getSupabaseWithToken } from '@/lib/supabase';
import { cookies } from 'next/headers';
import { encrypt } from '@/lib/encryption';

export async function POST(request: Request) {
    try {
        const cookieStore = await cookies();
        const token = cookieStore.get('access_token')?.value;

        if (!token) {
            return NextResponse.json({ status: "error", detail: "Not authenticated" }, { status: 401 });
        }

        const formData = await request.formData();
        const odoo_url = formData.get('odoo_url') as string;
        const odoo_db = formData.get('odoo_db') as string;
        const odoo_username = formData.get('odoo_username') as string;
        const odoo_password = formData.get('odoo_password') as string;

        const supabase = getSupabaseWithToken(token);
        const { data: userResponse, error: userError } = await supabase.auth.getUser();

        if (userError || !userResponse.user) {
            return NextResponse.json({ status: "error", detail: "Unauthorized" }, { status: 401 });
        }

        const userId = userResponse.user.id;

        const workspace_id = formData.get('workspace_id') as string;

        // Fetch current workspaces
        const { data: existingData } = await supabase
            .from('user_workspaces')
            .select('*')
            .eq('user_id', userId);

        const currentCount = existingData ? existingData.length : 0;
        let existing = null;

        // Enforce Plan Limits for NEW workspaces
        if (!workspace_id) {
            const { data: paymentData } = await supabase
                .from('payments')
                .select('plan')
                .eq('user_id', userId)
                .limit(1);

            const isTeamPlan = paymentData && paymentData.length > 0 && paymentData[0].plan === 'team';
            if (!isTeamPlan && currentCount >= 1) {
                return NextResponse.json({ 
                    status: "error", 
                    message: "Single Plan allows only 1 workspace. Please upgrade to Team to add more." 
                }, { status: 403 });
            }
        }

        if (workspace_id && existingData) {
            existing = existingData.find(w => w.id === parseInt(workspace_id, 10) || w.id === workspace_id);
            if (!existing) {
                return NextResponse.json({ status: "error", detail: "Workspace not found" }, { status: 404 });
            }
        }

        let finalPassword = odoo_password;
        if (odoo_password === "********" && existing) {
            finalPassword = existing.odoo_password;
        } else {
            finalPassword = odoo_password ? encrypt(odoo_password) : odoo_password;
        }

        const payload = {
            user_id: userId,
            odoo_url,
            odoo_db,
            odoo_username,
            odoo_password: finalPassword
        };

        if (existing) {
            // Update specific workspace
            const { error: updateError } = await supabase
                .from('user_workspaces')
                .update(payload)
                .eq('id', existing.id)
                .eq('user_id', userId); // Extra safety
            
            if (updateError) throw updateError;
        } else {
            // Inserting new workspace
            const planType = cookieStore.get('plan_type')?.value || 'single';
            const limit = planType === 'team' ? 10 : 1;
            
            if (currentCount >= limit) {
                return NextResponse.json({ 
                    status: "error", 
                    message: `Plan limit reached. Your ${planType} plan allows up to ${limit} connected database(s).` 
                }, { status: 403 });
            }

            const { error: insertError } = await supabase
                .from('user_workspaces')
                .insert([payload]);
            
            if (insertError) throw insertError;
        }

        return NextResponse.json({ status: "success", message: "Configuration saved successfully." });

    } catch (e: any) {
        console.error("DB Save Error", e);
        return NextResponse.json({ status: "error", message: e.message || "Unknown error" });
    }
}
