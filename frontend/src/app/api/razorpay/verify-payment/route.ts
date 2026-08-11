import { NextRequest, NextResponse } from 'next/server';
import crypto from 'crypto';

export async function POST(request: NextRequest) {
    try {
        const body = await request.json();
        const { razorpay_order_id, razorpay_payment_id, razorpay_signature } = body;

        if (!razorpay_order_id || !razorpay_payment_id || !razorpay_signature) {
            return NextResponse.json(
                { success: false, message: 'Missing payment verification parameters' },
                { status: 400 }
            );
        }

        // Verify signature using HMAC SHA256
        const sign = razorpay_order_id + '|' + razorpay_payment_id;
        const expectedSignature = crypto
            .createHmac('sha256', process.env.RAZORPAY_KEY_SECRET!)
            .update(sign)
            .digest('hex');

        if (expectedSignature === razorpay_signature) {
            // Payment is verified
            // Fetch order to get the plan
            const Razorpay = require('razorpay');
            const rzp = new Razorpay({
                key_id: process.env.RAZORPAY_KEY_ID!,
                key_secret: process.env.RAZORPAY_KEY_SECRET!,
            });
            const order = await rzp.orders.fetch(razorpay_order_id);
            const plan = order.notes?.plan || 'OdooX Pro - Single User';

            let userId = order.notes?.user_id;

            if (!userId || userId === 'unknown') {
                const token = request.cookies.get('access_token')?.value;
                if (token) {
                    const { getSupabaseWithToken } = await import('@/lib/supabase');
                    const userSupabase = getSupabaseWithToken(token);
                    const { data: userResponse } = await userSupabase.auth.getUser();
                    if (userResponse?.user) {
                        userId = userResponse.user.id;
                    }
                }
            }

            if (userId && userId !== 'unknown') {
                const { createClient } = await import('@supabase/supabase-js');
                const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || '';
                const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || ''; 
                const adminClient = createClient(supabaseUrl, supabaseServiceKey);
                
                // Check if payment already exists
                const { data: existing } = await adminClient
                    .from('payments')
                    .select('id')
                    .eq('razorpay_order_id', razorpay_order_id)
                    .limit(1);

                if (!existing || existing.length === 0) {
                    const { error: insertError } = await adminClient.from('payments').insert([{
                        user_id: userId,
                        razorpay_order_id,
                        razorpay_payment_id
                    }]);
                    
                    if (insertError) {
                        console.error("Database Insert Error in Verify Payment:", insertError);
                    }
                }
            }

            const response = NextResponse.json({
                success: true,
                message: 'Payment verified successfully',
                payment_id: razorpay_payment_id,
                order_id: razorpay_order_id,
                plan: 'single'
            });

            const { signWithHmac } = await import('@/lib/hmac');
            const signature = await signWithHmac(userId);

            response.cookies.set({
                name: 'paid_user_id',
                value: userId,
                httpOnly: true,
                sameSite: 'lax',
                secure: process.env.NODE_ENV === 'production',
                path: '/',
                maxAge: 5 * 365 * 24 * 60 * 60
            });

            response.cookies.set({
                name: 'payment_signature',
                value: signature,
                httpOnly: true,
                sameSite: 'lax',
                secure: process.env.NODE_ENV === 'production',
                path: '/',
                maxAge: 5 * 365 * 24 * 60 * 60
            });

            response.cookies.set({
                name: 'is_paid',
                value: 'true',
                httpOnly: true,
                sameSite: 'lax',
                secure: process.env.NODE_ENV === 'production',
                path: '/',
                maxAge: 5 * 365 * 24 * 60 * 60 // 5 years
            });

            return response;
        } else {
            return NextResponse.json(
                { success: false, message: 'Payment verification failed — signature mismatch' },
                { status: 400 }
            );
        }
    } catch (error: any) {
        console.error('Payment verification error:', error);
        return NextResponse.json(
            { success: false, message: error.message || 'Verification failed' },
            { status: 500 }
        );
    }
}
