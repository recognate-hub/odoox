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

        // --- Payment check ---
        const { createClient } = await import('@supabase/supabase-js');
        const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || '';
        const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

        if (!supabaseServiceKey) {
            console.error("SUPABASE_SERVICE_ROLE_KEY is missing.");
            return NextResponse.json({ status: "error", message: "Server misconfiguration" }, { status: 500 });
        }

        const adminClient = createClient(supabaseUrl, supabaseServiceKey);
        const { data: paymentData } = await adminClient
            .from('payments')
            .select('id')
            .eq('user_id', userId)
            .limit(1);

        const hasPaid = !!(paymentData && paymentData.length > 0);
        const redirectUrl = hasPaid ? "/userdashboard" : "/payment";

        // Build a SINGLE response object so all Set-Cookie headers are guaranteed
        // to be sent together. The old code created a second NextResponse and then
        // tried to copy cookies from the first — but Next.js queues Set-Cookie
        // headers internally and .getAll() does NOT capture them all, causing the
        // access_token and refresh_token cookies to be silently dropped. Without
        // those cookies, the OAuth /authorize endpoint sees no token and redirects
        // the user back to the login page immediately after a successful OTP.
        const cookieDefaults = {
            httpOnly: true,
            sameSite: 'lax' as const,
            secure: process.env.NODE_ENV === 'production',
            path: '/',
        };

        const finalResponse = NextResponse.json({ status: "success", redirect: redirectUrl });

        // Auth cookies (session-length — expire when browser closes)
        finalResponse.cookies.set({ name: 'access_token', value: data.session.access_token, ...cookieDefaults });

        if (data.session.refresh_token) {
            finalResponse.cookies.set({ name: 'refresh_token', value: data.session.refresh_token, ...cookieDefaults });
        }

        // Device session cookie (persistent, 7 days)
        const { randomUUID } = await import('crypto');
        finalResponse.cookies.set({
            name: 'device_session_id',
            value: randomUUID(),
            ...cookieDefaults,
            maxAge: 7 * 24 * 60 * 60,
        });

        // Payment cookies (persistent, 7 days)
        if (hasPaid) {
            const { signWithHmac } = await import('@/lib/hmac');
            const signature = await signWithHmac(userId);

            finalResponse.cookies.set({ name: 'paid_user_id',       value: userId,     ...cookieDefaults, maxAge: 7 * 24 * 60 * 60 });
            finalResponse.cookies.set({ name: 'payment_signature',   value: signature,  ...cookieDefaults, maxAge: 7 * 24 * 60 * 60 });
            finalResponse.cookies.set({ name: 'is_paid',             value: 'true',     ...cookieDefaults, maxAge: 7 * 24 * 60 * 60 });
        }

        return finalResponse;
    } catch (e: any) {
        console.error("OTP Verify Error", e);
        return NextResponse.json({ status: "error", message: e.message || "Unknown error" });
    }
}
