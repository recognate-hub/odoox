import { NextResponse } from 'next/server';
import { getSupabaseWithToken } from '@/lib/supabase';
import { cookies } from 'next/headers';

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

        // 3. Fetch Prices
        const { data: configData, error: configError } = await supabase
            .from('app_config')
            .select('*')
            .in('key', ['single_plan_price']);

        if (configError) throw configError;

        let singlePrice = 0;

        if (configData) {
            const single = configData.find(d => d.key === 'single_plan_price');
            if (single) singlePrice = parseFloat(single.value);
        }

        return NextResponse.json({
            status: "success",
            singlePrice
        });

    } catch (e: any) {
        console.error("Admin check failed", e);
        return NextResponse.json({ status: "error", detail: "Internal Server Error" }, { status: 500 });
    }
}

export async function POST(request: Request) {
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

        // 3. Update Prices
        const body = await request.json();
        const { singlePrice } = body;

        if (!singlePrice) {
            return NextResponse.json({ status: "error", detail: "Missing price" }, { status: 400 });
        }

        const { error: err1 } = await supabase
            .from('app_config')
            .update({ value: parseFloat(singlePrice) })
            .eq('key', 'single_plan_price');
            
        if (err1) throw err1;

        return NextResponse.json({ status: "success" });

    } catch (e: any) {
        console.error("Admin update failed", e);
        return NextResponse.json({ status: "error", detail: "Internal Server Error" }, { status: 500 });
    }
}
