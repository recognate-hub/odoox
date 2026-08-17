import { NextRequest, NextResponse } from 'next/server';
import { getSupabaseWithToken } from '@/lib/supabase';
import crypto from 'crypto';

export async function POST(request: NextRequest) {
    try {
        const token = request.cookies.get('access_token')?.value;
        if (!token) {
            return NextResponse.json({ status: "error", message: "Not authenticated" }, { status: 401 });
        }

        const userClient = getSupabaseWithToken(token);
        const { data: userResponse, error } = await userClient.auth.getUser();
        
        if (error || !userResponse?.user) {
            return NextResponse.json({ status: "error", message: "Invalid session" }, { status: 401 });
        }

        const userId = userResponse.user.id;
        const deviceSessionId = crypto.randomUUID();

        const { error: upsertError } = await userClient
            .from('active_sessions')
            .upsert({ user_id: userId, device_session_id: deviceSessionId });
            
        if (upsertError) {
            console.error("Session Upsert Error:", upsertError);
            return NextResponse.json({ status: "error", message: "Could not register device session. Has the SQL migration been run?" }, { status: 500 });
        }

        let hasPaid = false;
        const { createClient } = await import('@supabase/supabase-js');
        const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || '';
        const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY;
        if (!supabaseServiceKey) {
            console.error("SUPABASE_SERVICE_ROLE_KEY is missing in confirm-session.");
            return NextResponse.json({ status: "error", message: "Server misconfiguration" }, { status: 500 });
        }
        const adminClient = createClient(supabaseUrl, supabaseServiceKey);

        const { data: paymentData } = await adminClient
            .from('payments')
            .select('id')
            .eq('user_id', userId)
            .limit(1);

        if (paymentData && paymentData.length > 0) {
            hasPaid = true;
        }

        const refreshToken = request.cookies.get('refresh_token')?.value;
        const redirectUrl = hasPaid ? "/userdashboard" : "/payment";
        const response = NextResponse.json({ 
            status: "success", 
            redirect: redirectUrl,
            access_token: token,
            refresh_token: refreshToken || null
        });

        response.cookies.set({
            name: 'device_session_id',
            value: deviceSessionId,
            httpOnly: true,
            sameSite: 'lax',
            secure: process.env.NODE_ENV === 'production',
            path: '/',
            maxAge: 7 * 24 * 60 * 60
        });

        if (hasPaid) {
            const { signWithHmac } = await import('@/lib/hmac');
            const signature = await signWithHmac(userId);

            response.cookies.set({
                name: 'paid_user_id',
                value: userId,
                httpOnly: true,
                sameSite: 'lax',
                secure: process.env.NODE_ENV === 'production',
                path: '/',
                maxAge: 7 * 24 * 60 * 60
            });

            response.cookies.set({
                name: 'payment_signature',
                value: signature,
                httpOnly: true,
                sameSite: 'lax',
                secure: process.env.NODE_ENV === 'production',
                path: '/',
                maxAge: 7 * 24 * 60 * 60
            });

            response.cookies.set({
                name: 'is_paid',
                value: 'true',
                httpOnly: true,
                sameSite: 'lax',
                secure: process.env.NODE_ENV === 'production',
                path: '/',
                maxAge: 7 * 24 * 60 * 60
            });
        }
        
        return response;
    } catch (e: any) {
        return NextResponse.json({ status: "error", message: e.message || "Unknown error" }, { status: 500 });
    }
}
