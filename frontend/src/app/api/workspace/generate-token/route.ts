import { NextRequest, NextResponse } from 'next/server';
import { getSupabaseWithToken } from '@/lib/supabase';
import crypto from 'crypto';

export async function POST(request: NextRequest) {
    try {
        const token = request.cookies.get('access_token')?.value;
        if (!token) {
            return NextResponse.json({ status: "error", message: "Not authenticated" }, { status: 401 });
        }

        const userClient = getSupabaseWithToken(token);
        const { data: userResponse, error } = await userClient.auth.getUser();
        
        if (error || !userResponse?.user) {
            return NextResponse.json({ status: "error", message: "Invalid session" }, { status: 401 });
        }

        const userId = userResponse.user.id;
        // Generate a 6-character random alphanumeric token
        const linkToken = 'odx_' + crypto.randomBytes(4).toString('hex').slice(0, 6);

        const { error: insertError } = await userClient
            .from('connection_tokens')
            .upsert({ user_id: userId, token: linkToken });

        if (insertError) {
            console.error("Token Insert Error:", insertError);
            return NextResponse.json({ status: "error", message: "Failed to generate token. Did you run the SQL migration?" }, { status: 500 });
        }

        return NextResponse.json({ status: "success", link_token: linkToken });

    } catch (e: any) {
        return NextResponse.json({ status: "error", message: e.message || "Unknown error" }, { status: 500 });
    }
}
