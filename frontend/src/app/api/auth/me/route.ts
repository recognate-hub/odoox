import { NextResponse } from 'next/server';
import { getSupabaseWithToken } from '@/lib/supabase';
import { cookies } from 'next/headers';

export async function GET() {
    try {
        const cookieStore = await cookies();
        const token = cookieStore.get('access_token')?.value;
        const refresh_token = cookieStore.get('refresh_token')?.value;

        if (!token) {
            return NextResponse.json({ status: "error", detail: "Not authenticated" }, { status: 401 });
        }

        const supabase = getSupabaseWithToken(token);
        const { data, error } = await supabase.auth.getUser();

        if (error || !data.user) {
            throw new Error("Invalid token");
        }

        return NextResponse.json({
            status: "success",
            user: {
                id: data.user.id,
                email: data.user.email,
            },
            access_token: token,
            refresh_token: refresh_token || null
        });
    } catch (e: any) {
        console.error("Auth check failed", e);
        return NextResponse.json({ status: "error", detail: "Session expired or invalid" }, { status: 401 });
    }
}
