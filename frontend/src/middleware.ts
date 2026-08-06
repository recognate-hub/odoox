import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || '';
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || '';

const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY || supabaseKey;

async function checkDeviceSession(request: NextRequest, token: string): Promise<boolean> {
    const cookieSessionId = request.cookies.get('device_session_id')?.value;
    if (!cookieSessionId) return false;

    try {
        const userSupabase = createClient(supabaseUrl, supabaseKey, {
            global: { headers: { Authorization: `Bearer ${token}` } }
        });
        const { data: userResponse } = await userSupabase.auth.getUser();
        if (!userResponse?.user) return false;

        const { data: activeSession } = await userSupabase
            .from('active_sessions')
            .select('device_session_id')
            .eq('user_id', userResponse.user.id)
            .limit(1);

        if (activeSession && activeSession.length > 0) {
            return activeSession[0].device_session_id === cookieSessionId;
        }
        return false;
    } catch {
        return false;
    }
}

async function checkPaymentStatus(request: NextRequest): Promise<boolean> {
    try {
        const paidUserId = request.cookies.get('paid_user_id')?.value;
        const paymentSignature = request.cookies.get('payment_signature')?.value;

        if (!paidUserId || !paymentSignature) {
            return false;
        }

        const { verifyHmac } = await import('@/lib/hmac');
        const isValid = await verifyHmac(paidUserId, paymentSignature);

        if (!isValid) return false;

        // Optionally, check if the token user ID matches the paid user ID
        const token = request.cookies.get('access_token')?.value;
        if (token) {
            const userSupabase = createClient(supabaseUrl, supabaseKey, {
                global: { headers: { Authorization: `Bearer ${token}` } }
            });
            const { data: userResponse } = await userSupabase.auth.getUser();
            if (userResponse?.user && userResponse.user.id !== paidUserId) {
                return false;
            }
        }
        
        return true;
    } catch {
        return false;
    }
}

export async function middleware(request: NextRequest) {
    const token = request.cookies.get('access_token')?.value;
    const { pathname } = request.nextUrl;

    // Protected Route: Dashboard
    if (pathname.startsWith('/userdashboard')) {
        if (!token) {
            return NextResponse.redirect(new URL('/login', request.url));
        }
        
        const isSessionValid = await checkDeviceSession(request, token);
        if (!isSessionValid) {
            return NextResponse.redirect(new URL('/login?session_expired=true', request.url));
        }

        const isPaid = await checkPaymentStatus(request);
        if (!isPaid) {
            return NextResponse.redirect(new URL('/payment', request.url));
        }
        return NextResponse.next();
    }

    // Protected Route: Payment
    if (pathname.startsWith('/payment')) {
        if (!token) {
            return NextResponse.redirect(new URL('/login', request.url));
        }

        const isSessionValid = await checkDeviceSession(request, token);
        if (!isSessionValid) {
            return NextResponse.redirect(new URL('/login?session_expired=true', request.url));
        }

        const isPaid = await checkPaymentStatus(request);
        if (isPaid) {
            return NextResponse.redirect(new URL('/userdashboard', request.url));
        }
        return NextResponse.next();
    }

    // Public Routes (Login only)
    if (pathname === '/login') {
        if (token) {
            const isPaid = await checkPaymentStatus(request);
            if (isPaid) {
                return NextResponse.redirect(new URL('/userdashboard', request.url));
            } else {
                return NextResponse.redirect(new URL('/payment', request.url));
            }
        }
    }

    return NextResponse.next();
}

export const config = {
    matcher: ['/', '/login', '/userdashboard/:path*', '/payment/:path*'],
};
