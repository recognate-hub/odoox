import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || '';
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || '';

export async function POST(request: NextRequest) {
    try {
        const body = await request.json();
        const { link_token, odoo_url, odoo_db, odoo_username, odoo_password } = body;

        if (!link_token || !odoo_url || !odoo_db || !odoo_username || !odoo_password) {
            return NextResponse.json({ status: "error", message: "Missing required fields" }, { status: 400 });
        }

        // The link_token is actually the user's Supabase access_token in our simplified workflow.
        // We use it to authenticate the Supabase client directly!
        const userClient = createClient(supabaseUrl, supabaseKey, {
            global: { headers: { Authorization: `Bearer ${link_token}` } }
        });

        const { data: userResponse, error } = await userClient.auth.getUser();
        if (error || !userResponse?.user) {
            return NextResponse.json({ status: "error", message: "Invalid or expired Integration Key" }, { status: 401 });
        }

        const userId = userResponse.user.id;

        const { data: workspaces } = await userClient
            .from('user_workspaces')
            .select('id')
            .eq('user_id', userId);

        const workspaceCount = workspaces ? workspaces.length : 0;

        if (workspaceCount >= 1) {
            return NextResponse.json({ 
                status: "error", 
                message: "You have reached the maximum limit of 1 connected database." 
            }, { status: 403 });
        }

        // Insert new workspace securely (RLS is satisfied by the user's access token)
        const { data: insertedData, error: insertError } = await userClient
            .from('user_workspaces')
            .insert({
                user_id: userId,
                odoo_url,
                odoo_db,
                odoo_username,
                odoo_password,
                is_active: true
            })
            .select()
            .single();

        if (insertError) {
            console.error("Workspace Insert Error", insertError);
            return NextResponse.json({ status: "error", message: "Failed to save workspace in database" }, { status: 500 });
        }

        return NextResponse.json({ 
            status: "success", 
            message: "Successfully connected", 
            workspace_id: insertedData.id 
        });

    } catch (e: any) {
        console.error("Register Error:", e);
        return NextResponse.json({ status: "error", message: e.message || "Unknown error" }, { status: 500 });
    }
}
