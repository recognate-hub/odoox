import { NextRequest, NextResponse } from 'next/server';
import crypto from 'crypto';
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || '';
// Uses the Service Role Key since webhooks are unauthenticated server-to-server calls
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || ''; 

export async function POST(request: NextRequest) {
    try {
        const bodyText = await request.text();
        const signature = request.headers.get('x-razorpay-signature');
        const webhookSecret = process.env.RAZORPAY_WEBHOOK_SECRET || process.env.RAZORPAY_KEY_SECRET;

        if (!signature || !webhookSecret) {
            return NextResponse.json({ success: false, message: 'Missing signature or secret' }, { status: 400 });
        }

        // Verify webhook signature
        const expectedSignature = crypto
            .createHmac('sha256', webhookSecret)
            .update(bodyText)
            .digest('hex');

        if (expectedSignature !== signature) {
            console.error("Webhook signature mismatch");
            return NextResponse.json({ success: false, message: 'Invalid signature' }, { status: 400 });
        }

        const payload = JSON.parse(bodyText);
        const eventType = payload.event;

        const supabase = createClient(supabaseUrl, supabaseServiceKey);

        if (eventType === 'payment.failed') {
            const paymentId = payload.payload.payment.entity.id;
            const orderId = payload.payload.payment.entity.order_id;
            console.log(`Payment failed: ${paymentId} for order ${orderId}`);
            
            // In a real system, you might delete the payment record or mark it failed
            // await supabase.from('payments').update({ status: 'failed' }).eq('razorpay_payment_id', paymentId);
        } else if (eventType === 'payment.authorized' || eventType === 'payment.captured') {
            // Already handled synchronously by the frontend, but good for safety net
            console.log(`Payment captured via webhook: ${payload.payload.payment.entity.id}`);
        } else if (eventType === 'subscription.cancelled') {
            // Future-proofing for subscriptions
            console.log(`Subscription cancelled via webhook`);
        }

        return NextResponse.json({ success: true, message: 'Webhook processed' });
    } catch (error: any) {
        console.error('Webhook processing error:', error);
        return NextResponse.json({ success: false, message: error.message }, { status: 500 });
    }
}
