import { NextResponse } from 'next/server';
import { getSupabaseWithToken } from '@/lib/supabase';
import { cookies } from 'next/headers';

export async function GET(request: Request) {
    try {
        const cookieStore = await cookies();
        const token = cookieStore.get('access_token')?.value;

        if (!token) {
            return NextResponse.json({ status: "error", detail: "Not authenticated" }, { status: 401 });
        }

        const supabase = getSupabaseWithToken(token);
        const { data: userResponse, error: userError } = await supabase.auth.getUser();

        if (userError || !userResponse.user) {
            throw new Error("Invalid token");
        }

        const userId = userResponse.user.id;

        const { data: workspaceData, error: workspaceError } = await supabase
            .from('user_workspaces')
            .select('*')
            .eq('user_id', userId);

        if (workspaceError) {
            throw workspaceError;
        }

        const url = new URL(request.url);
        const baseUrl = `${url.protocol}//${url.host}/`;

        const workspaces = workspaceData ? workspaceData.map(w => ({
            id: w.id,
            odoo_url: w.odoo_url || "",
            odoo_db: w.odoo_db || "",
            odoo_username: w.odoo_username || "",
            has_password: !!w.odoo_password,
            connection_url: `${baseUrl}sse?token=${token}&workspace_id=${w.id}`
        })) : [];

        const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || '';
        const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || ''; 
        const adminSupabase = (await import('@supabase/supabase-js')).createClient(supabaseUrl, supabaseServiceKey);

        const { data: payments, error: payError } = await adminSupabase
            .from('payments')
            .select('plan')
            .eq('user_id', userId)
            .limit(1);

        const planType = payments && payments.length > 0 ? payments[0].plan : 'single';
        const limit = planType === 'team' ? 10 : 1;

        return NextResponse.json({
            status: "success",
            workspaces: workspaces,
            plan_type: planType,
            limit: limit,
            token: token,
        });

    } catch (e: any) {
        console.error("Workspace fetch failed", e);
        return NextResponse.json({ status: "error", detail: "Session expired or invalid" }, { status: 401 });
    }
}
