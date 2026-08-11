import { NextResponse } from 'next/server';
import { getSupabaseWithToken } from '@/lib/supabase';
import { cookies } from 'next/headers';
import { createClient } from '@supabase/supabase-js';

export async function GET() {
    try {
        const cookieStore = await cookies();
        const token = cookieStore.get('access_token')?.value;

        if (!token) {
            return NextResponse.json({ status: "error", detail: "Not authenticated" }, { status: 401 });
        }

        const supabase = getSupabaseWithToken(token);
        
        // 1. Get User Profile
        const { data: { user }, error: userError } = await supabase.auth.getUser();
        if (userError || !user?.email) {
            return NextResponse.json({ status: "error", detail: "Invalid token or user" }, { status: 401 });
        }

        // 2. Check Admin Status
        const { data: adminData, error: adminError } = await supabase
            .from('admin_users')
            .select('*')
            .eq('email', user.email)
            .single();

        if (adminError || !adminData) {
            return NextResponse.json({ status: "unauthorized", detail: "You do not have administrator privileges." }, { status: 403 });
        }

        // 3. Fetch All Users using Service Role Key
        const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || '';
        const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY;
        
        if (!supabaseServiceKey) {
            console.error("Missing SUPABASE_SERVICE_ROLE_KEY");
            return NextResponse.json({ status: "error", detail: "Server misconfiguration. Cannot fetch users." }, { status: 500 });
        }

        const adminClient = createClient(supabaseUrl, supabaseServiceKey);
        
        const { data: authData, error: authError } = await adminClient.auth.admin.listUsers();
        
        if (authError) {
            throw authError;
        }

        const { data: paymentsData, error: paymentsError } = await adminClient
            .from('payments')
            .select('user_id');

        if (paymentsError) {
            console.error("Failed to fetch payments for admin", paymentsError);
        }

        // Create a lookup map for faster checking
        const planMap: Record<string, string> = {};
        if (paymentsData) {
            paymentsData.forEach((p: any) => {
                planMap[p.user_id] = 'single'; // Since plan column doesn't exist, we assume single
            });
        }

        // Return a simplified list of users
        const usersList = authData.users.map(u => ({
            id: u.id,
            email: u.email,
            created_at: u.created_at,
            last_sign_in_at: u.last_sign_in_at,
            plan: planMap[u.id] || 'free'
        }));

        return NextResponse.json({
            status: "success",
            users: usersList
        });

    } catch (e: any) {
        console.error("Admin users fetch failed", e);
        return NextResponse.json({ status: "error", detail: "Internal Server Error" }, { status: 500 });
    }
}
