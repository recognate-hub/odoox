import { NextResponse } from 'next/server';
import { cookies } from 'next/headers';

export async function GET(request: Request) {
    try {
        const url = new URL(request.url);
        
        const cookieStore = await cookies();
        const token = cookieStore.get('access_token')?.value;
        const refresh_token = cookieStore.get('refresh_token')?.value;

        const rawBackendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const backendUrl = rawBackendUrl.endsWith('/') ? rawBackendUrl.slice(0, -1) : rawBackendUrl;
        
        // Append all search params from the frontend request to the backend request
        const backendRequestUrl = new URL(`${backendUrl}/oauth/authorize`);
        url.searchParams.forEach((value, key) => {
            backendRequestUrl.searchParams.append(key, value);
        });

        // Construct cookie header
        let cookieHeader = '';
        if (token) cookieHeader += `access_token=${token}; `;
        if (refresh_token) cookieHeader += `refresh_token=${refresh_token}`;

        const res = await fetch(backendRequestUrl.toString(), {
            method: 'GET',
            headers: {
                'Cookie': cookieHeader
            },
            redirect: 'manual' // We need to intercept the 303 redirect
        });

        // If backend responds with a redirect (303)
        if (res.status === 303 || res.status === 302 || res.status === 307 || res.status === 308) {
            const location = res.headers.get('location');
            if (location) {
                // Return the same redirect to the client browser
                return NextResponse.redirect(new URL(location, request.url), res.status);
            }
        }

        // Otherwise return whatever it returned
        const data = await res.text();
        return new NextResponse(data, {
            status: res.status,
            headers: {
                'Content-Type': res.headers.get('content-type') || 'text/plain'
            }
        });

    } catch (e: any) {
        console.error("OAuth authorize proxy failed", e);
        return NextResponse.json({ status: "error", detail: "Internal Server Error" }, { status: 500 });
    }
}
