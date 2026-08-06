import { NextRequest, NextResponse } from 'next/server';
import Razorpay from 'razorpay';

const razorpay = new Razorpay({
    key_id: process.env.RAZORPAY_KEY_ID!,
    key_secret: process.env.RAZORPAY_KEY_SECRET!,
});

export async function POST(request: NextRequest) {
    try {
        const body = await request.json();
        
        const amount = body.amount || 499900; // ₹4,999 in paise
        const currency = body.currency || 'INR';

        const planName = body.plan || 'OdooX Pro - Single User';

        let userId = 'unknown';
        const token = request.cookies.get('access_token')?.value;
        if (token) {
            const { getSupabaseWithToken } = await import('@/lib/supabase');
            const supabase = getSupabaseWithToken(token);
            const { data } = await supabase.auth.getUser();
            if (data?.user) userId = data.user.id;
        }

        const options = {
            amount: amount,
            currency: currency,
            receipt: `odoox_${Date.now()}`,
            notes: {
                plan: planName,
                base_price: (amount / 100).toString(),
                user_id: userId,
            },
        };

        const order = await razorpay.orders.create(options);

        return NextResponse.json({
            success: true,
            order_id: order.id,
            amount: order.amount,
            currency: order.currency,
        });
    } catch (error: any) {
        console.error('Razorpay order creation failed:', error);
        return NextResponse.json(
            { success: false, message: error.message || 'Failed to create order' },
            { status: 500 }
        );
    }
}
