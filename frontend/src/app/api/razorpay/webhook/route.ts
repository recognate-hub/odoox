import { NextRequest, NextResponse } from 'next/server';
import crypto from 'crypto';
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || '';
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY || ''; 

export async function POST(request: NextRequest) {
    try {
        const body = await request.text();
        const signature = request.headers.get('x-razorpay-signature');

        if (!signature) {
            return NextResponse.json({ error: 'Missing signature' }, { status: 400 });
        }

        const expectedSignature = crypto
            .createHmac('sha256', process.env.RAZORPAY_WEBHOOK_SECRET || process.env.RAZORPAY_KEY_SECRET!)
            .update(body)
            .digest('hex');

        if (expectedSignature !== signature) {
            return NextResponse.json({ error: 'Invalid signature' }, { status: 400 });
        }

        const event = JSON.parse(body);

        if (event.event === 'order.paid' || event.event === 'payment.captured') {
            const entity = event.payload.payment?.entity || event.payload.order?.entity;
            const razorpay_order_id = entity.order_id || entity.id;
            const plan = entity.notes?.plan || 'OdooX Pro - Single User';
            const isTeam = plan.includes('Team');
            const userId = entity.notes?.user_id;

            if (userId && userId !== 'unknown') {
                const supabase = createClient(supabaseUrl, supabaseServiceKey);
                
                // Check if payment already exists
                const { data: existing } = await supabase
                    .from('payments')
                    .select('id')
                    .eq('razorpay_order_id', razorpay_order_id)
                    .limit(1);

                if (!existing || existing.length === 0) {
                    await supabase.from('payments').insert([{
                        user_id: userId,
                        razorpay_order_id
                    }]);
                }
            }
        }

        return NextResponse.json({ status: 'ok' });
    } catch (error) {
        console.error('Webhook error:', error);
        return NextResponse.json({ error: 'Webhook handler failed' }, { status: 500 });
    }
}
