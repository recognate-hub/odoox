import { NextResponse, NextRequest } from 'next/server';
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || '';
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || '';

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

export default async function middleware(request: NextRequest) {
    const token = request.cookies.get('access_token')?.value;
    const { pathname } = request.nextUrl;

    // Protected Route: Dashboard
    if (pathname.startsWith('/userdashboard')) {
        if (!token) {
            return NextResponse.redirect(new URL('/login', request.url));
        }

        const isPaid = await checkPaymentStatus(request);
        if (!isPaid) {
            return NextResponse.redirect(new URL('/payment', request.url));
        }
    }

    // Protected Route: Payment
    if (pathname.startsWith('/payment')) {
        if (!token) {
            return NextResponse.redirect(new URL('/login', request.url));
        }

        const isPaid = await checkPaymentStatus(request);
        if (isPaid) {
            return NextResponse.redirect(new URL('/userdashboard', request.url));
        }
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
  matcher: [
    '/((?!api|_next|_vercel|oauth|sse|messages|.*\\..*).*)'
  ]
};
