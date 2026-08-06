import { createClient } from '@supabase/supabase-js';

const supabase = createClient('https://hoifuflsrcckndwsrspf.supabase.co', 'sb_publishable_ptTVVc600X4zqcZ1fPJyhg_XiksNeXX');

async function main() {
    const { data, error } = await supabase.from('user_workspaces').select('*').limit(1);
    console.log("Error:", error);
    console.log("Data:", data);
}

main();
