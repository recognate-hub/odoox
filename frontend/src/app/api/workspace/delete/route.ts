import { NextResponse } from 'next/server';
import { getSupabaseWithToken } from '@/lib/supabase';
import { cookies } from 'next/headers';

export async function POST(request: Request) {
    try {
        const cookieStore = await cookies();
        const token = cookieStore.get('access_token')?.value;

        if (!token) {
            return NextResponse.json({ status: "error", detail: "Not authenticated" }, { status: 401 });
        }

        const body = await request.json();
        const workspace_id = body.workspace_id;

        if (!workspace_id) {
            return NextResponse.json({ status: "error", detail: "Workspace ID is required" }, { status: 400 });
        }

        const supabase = getSupabaseWithToken(token);
        const { data: userResponse, error: userError } = await supabase.auth.getUser();

        if (userError || !userResponse.user) {
            return NextResponse.json({ status: "error", detail: "Unauthorized" }, { status: 401 });
        }

        const userId = userResponse.user.id;

        const { error: deleteError } = await supabase
            .from('user_workspaces')
            .delete()
            .eq('id', workspace_id)
            .eq('user_id', userId); // Extra safety

        if (deleteError) {
            throw deleteError;
        }

        return NextResponse.json({ status: "success", message: "Workspace deleted successfully." });

    } catch (e: any) {
        console.error("DB Delete Error", e);
        return NextResponse.json({ status: "error", message: e.message || "Unknown error" }, { status: 500 });
    }
}
