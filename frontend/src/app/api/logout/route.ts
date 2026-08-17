import { NextRequest, NextResponse } from 'next/server';
import { cookies } from 'next/headers';
import { getSupabaseWithToken } from '@/lib/supabase';

export async function POST(request: NextRequest) {
    const cookieStore = await cookies();
    const token = cookieStore.get('access_token')?.value;

    if (token) {
        const userClient = getSupabaseWithToken(token);
        const { data: userResponse } = await userClient.auth.getUser();
        if (userResponse?.user) {
            await userClient
                .from('active_sessions')
                .delete()
                .eq('user_id', userResponse.user.id);
        }
    }

    const response = NextResponse.json({ status: "success", message: "Logged out" });
    response.cookies.delete('access_token');
    response.cookies.delete('refresh_token');
    response.cookies.delete('device_session_id');
    response.cookies.delete('paid_user_id');
    response.cookies.delete('payment_signature');
    response.cookies.delete('is_paid');
    
    return response;
}
