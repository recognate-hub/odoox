import { NextResponse } from 'next/server';
import { getSupabaseWithToken, supabase } from '@/lib/supabase';
import { cookies } from 'next/headers';

export async function GET() {
    try {
        const cookieStore = await cookies();
        const token = cookieStore.get('access_token')?.value;
        const refresh_token = cookieStore.get('refresh_token')?.value;

        // No credentials at all — definitely not authenticated
        if (!token && !refresh_token) {
            return NextResponse.json({ status: "error", detail: "Not authenticated" }, { status: 401 });
        }

        let userData: any = null;
        let activeToken = token;
        let activeRefresh = refresh_token;
        let tokensRefreshed = false;

        // 1. Try the existing access_token first
        if (token) {
            try {
                const client = getSupabaseWithToken(token);
                const { data, error } = await client.auth.getUser();
                if (!error && data.user) {
                    userData = data;
                }
            } catch {
                // Token may be expired — fall through to refresh
            }
        }

        // 2. If access_token failed or was missing, try refreshing with refresh_token
        if (!userData && refresh_token) {
            try {
                const { data: refreshData, error: refreshError } = await supabase.auth.refreshSession({
                    refresh_token
                });
                if (!refreshError && refreshData.session) {
                    activeToken = refreshData.session.access_token;
                    activeRefresh = refreshData.session.refresh_token || refresh_token;
                    tokensRefreshed = true;

                    // Verify the refreshed token works
                    const client = getSupabaseWithToken(activeToken);
                    const { data } = await client.auth.getUser();
                    userData = data;
                }
            } catch {
                // Refresh also failed — session is truly expired
            }
        }

        // 3. If neither worked, the session is expired
        if (!userData?.user) {
            return NextResponse.json({ status: "error", detail: "Session expired or invalid" }, { status: 401 });
        }

        const response = NextResponse.json({
            status: "success",
            user: {
                id: userData.user.id,
                email: userData.user.email,
            },
            access_token: activeToken,
            refresh_token: activeRefresh || null
        });

        // Update cookies if tokens were refreshed so subsequent requests use the new tokens
        if (tokensRefreshed) {
            const cookieDefaults = {
                httpOnly: true,
                sameSite: 'lax' as const,
                secure: process.env.NODE_ENV === 'production',
                path: '/',
            };
            if (activeToken) {
                response.cookies.set({ name: 'access_token', value: activeToken, ...cookieDefaults, maxAge: 3600 });
            }
            if (activeRefresh) {
                response.cookies.set({ name: 'refresh_token', value: activeRefresh, ...cookieDefaults, maxAge: 7 * 24 * 60 * 60 });
            }
        }

        return response;
    } catch (e: any) {
        console.error("Auth check failed", e);
        return NextResponse.json({ status: "error", detail: "Session expired or invalid" }, { status: 401 });
    }
}
