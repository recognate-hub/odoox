import createMiddleware from 'next-intl/middleware';
import { routing } from './i18n/routing';
import { NextResponse, NextRequest } from 'next/server';
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || '';
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || '';

const intlMiddleware = createMiddleware(routing);

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
    
    // Remove locale prefix for auth logic check
    const localeRegex = new RegExp(`^/(${routing.locales.join('|')})`);
    const pathWithoutLocale = pathname.replace(localeRegex, '') || '/';

    // Protected Route: Dashboard
    if (pathWithoutLocale.startsWith('/userdashboard')) {
        if (!token) {
            return NextResponse.redirect(new URL('/login', request.url));
        }

        const isPaid = await checkPaymentStatus(request);
        if (!isPaid) {
            return NextResponse.redirect(new URL('/payment', request.url));
        }
    }

    // Protected Route: Payment
    if (pathWithoutLocale.startsWith('/payment')) {
        if (!token) {
            return NextResponse.redirect(new URL('/login', request.url));
        }

        const isPaid = await checkPaymentStatus(request);
        if (isPaid) {
            return NextResponse.redirect(new URL('/userdashboard', request.url));
        }
    }

    // Public Routes (Login only)
    if (pathWithoutLocale === '/login') {
        if (token) {
            const isPaid = await checkPaymentStatus(request);
            if (isPaid) {
                return NextResponse.redirect(new URL('/userdashboard', request.url));
            } else {
                return NextResponse.redirect(new URL('/payment', request.url));
            }
        }
    }

    return intlMiddleware(request);
}

export const config = {
  matcher: [
    '/',
    '/(de|en|es|fr)/:path*',
    '/((?!api|_next|_vercel|oauth|sse|messages|.*\\..*).*)'
  ]
};
