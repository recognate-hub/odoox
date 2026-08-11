import { NextRequest, NextResponse } from 'next/server';
import { supabase } from '@/lib/supabase';

export async function POST(request: NextRequest) {
    try {
        const formData = await request.formData();
        const email = formData.get('email') as string;
        const token = formData.get('token') as string;

        if (!email || !token) {
            return NextResponse.json({ status: "error", message: "Email and token are required" }, { status: 400 });
        }

        const { data, error } = await supabase.auth.verifyOtp({
            email,
            token,
            type: 'email'
        });

        if (error || !data.session) {
            console.error("OTP Verify Error", error);
            return NextResponse.json({ status: "error", message: error?.message || "Invalid or expired OTP." });
        }

        const userId = data.session.user.id;

        const response = NextResponse.json({ 
            status: "success",
            message: "Login successful"
        });

        // Always set access_token cookie
        response.cookies.set({
            name: 'access_token',
            value: data.session.access_token,
            httpOnly: true,
            sameSite: 'lax',
            secure: process.env.NODE_ENV === 'production',
            path: '/'
        });

        // Set refresh_token cookie (needed by OAuth authorize endpoint)
        if (data.session.refresh_token) {
            response.cookies.set({
                name: 'refresh_token',
                value: data.session.refresh_token,
                httpOnly: true,
                sameSite: 'lax',
                secure: process.env.NODE_ENV === 'production',
                path: '/'
            });
        }

        // If no conflict, proceed with session creation
        const { randomUUID } = await import('crypto');
        const deviceSessionId = randomUUID();

        response.cookies.set({
            name: 'device_session_id',
            value: deviceSessionId,
            httpOnly: true,
            sameSite: 'lax',
            secure: process.env.NODE_ENV === 'production',
            path: '/',
            maxAge: 7 * 24 * 60 * 60
        });

        let hasPaid = false;
        
        const { createClient } = await import('@supabase/supabase-js');
        const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || '';
        const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY; 

        if (!supabaseServiceKey) {
            console.error("SUPABASE_SERVICE_ROLE_KEY is missing. Admin client cannot be initialized safely.");
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

        const redirectUrl = hasPaid ? "/userdashboard" : "/payment";
        const finalResponse = NextResponse.json({ status: "success", redirect: redirectUrl });

        // Copy cookies from original response
        const cookies = response.cookies.getAll();
        for (const cookie of cookies) {
            finalResponse.cookies.set(cookie);
        }

        // Set is_paid cookie if they have paid
        if (hasPaid) {
            const { signWithHmac } = await import('@/lib/hmac');
            const signature = await signWithHmac(userId);

            finalResponse.cookies.set({
                name: 'paid_user_id',
                value: userId,
                httpOnly: true,
                sameSite: 'lax',
                secure: process.env.NODE_ENV === 'production',
                path: '/',
                maxAge: 7 * 24 * 60 * 60
            });

            finalResponse.cookies.set({
                name: 'payment_signature',
                value: signature,
                httpOnly: true,
                sameSite: 'lax',
                secure: process.env.NODE_ENV === 'production',
                path: '/',
                maxAge: 7 * 24 * 60 * 60
            });

            finalResponse.cookies.set({
                name: 'is_paid',
                value: 'true',
                httpOnly: true,
                sameSite: 'lax',
                secure: process.env.NODE_ENV === 'production',
                path: '/',
                maxAge: 7 * 24 * 60 * 60
            });
        }
        return finalResponse;
    } catch (e: any) {
        console.error("OTP Verify Error", e);
        return NextResponse.json({ status: "error", message: e.message || "Unknown error" });
    }
}
