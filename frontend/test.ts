import { createClient } from '@supabase/supabase-js';

const supabaseUrl = 'https://hoifuflsrcckndwsrspf.supabase.co';
const supabaseKey = 'sb_publishable_ptTVVc600X4zqcZ1fPJyhg_XiksNeXX';
const supabase = createClient(supabaseUrl, supabaseKey);

async function testRLS() {
    // 1. Sign up a fake user
    const email = `testuser_${Date.now()}@example.com`;
    const password = 'TestPassword123!';
    
    const { data: authData } = await supabase.auth.signUp({
        email,
        password
    });
    
    const userId = authData.user?.id;
    const token = authData.session?.access_token;
    
    // 2. Create authenticated client
    const userClient = createClient(supabaseUrl, supabaseKey, {
        global: { headers: { Authorization: `Bearer ${token}` } }
    });
    
    // 3. Attempt to insert
    await userClient.from('payments').insert([{
        user_id: userId,
        razorpay_order_id: `order_${Date.now()}`,
        razorpay_payment_id: `pay_${Date.now()}`
    }]);
    
    // 4. Select
    const { data: selectData, error: selectError } = await userClient.from('payments').select('*').eq('user_id', userId).limit(1);
    
    console.log("Select Data:", selectData);
    console.log("Select Error:", selectError);
}

testRLS();
