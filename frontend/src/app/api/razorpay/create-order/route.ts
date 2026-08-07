import { NextRequest, NextResponse } from 'next/server';
import Razorpay from 'razorpay';

const razorpay = new Razorpay({
    key_id: process.env.RAZORPAY_KEY_ID!,
    key_secret: process.env.RAZORPAY_KEY_SECRET!,
});

export async function POST(request: NextRequest) {
    try {
        const body = await request.json();
        
        const currency = body.currency || 'INR';
        const planName = body.plan || 'OdooX Pro - Single User';

        let userId = 'unknown';
        const token = request.cookies.get('access_token')?.value;
        const { getSupabaseWithToken, supabase } = await import('@/lib/supabase');
        
        if (token) {
            const supabaseAuth = getSupabaseWithToken(token);
            const { data } = await supabaseAuth.auth.getUser();
            if (data?.user) userId = data.user.id;
        }

        // Fetch dynamic pricing from Supabase app_config
        const isTeamPlan = planName.toLowerCase().includes('team');
        const configKey = isTeamPlan ? 'team_plan_price' : 'single_plan_price';
        let amount = 0;

        const { data, error } = await supabase.from('app_config').select('value').eq('key', configKey).single();
        
        if (error || !data) {
            console.error('Could not fetch dynamic price from Supabase:', error);
            return NextResponse.json({ success: false, message: 'Pricing system error. Please try again.' }, { status: 500 });
        }
        
        amount = parseFloat(data.value) * 100; // Convert Rupees to Paise

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
