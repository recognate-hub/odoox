import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://hoifuflsrcckndwsrspf.supabase.co';
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || 'sb_publishable_ptTVVc600X4zqcZ1fPJyhg_XiksNeXX';
const supabase = createClient(supabaseUrl, supabaseKey);

async function testInsert() {
    // try inserting with just a random UUID to see if it complains about missing fields
    const { data, error } = await supabase.from('user_workspaces').insert([{ user_id: 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11' }]);
    console.log("Error:", error);
    console.log("Data:", data);
}
testInsert();
