import { NextRequest } from 'next/server';

export const dynamic = 'force-dynamic';

export async function GET(request: NextRequest) {
    const backendUrlRaw = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const backendUrl = backendUrlRaw.replace(/\/+$/, "");
    const sseUrl = new URL('/sse', backendUrl);
    
    // Forward all query parameters (like token, workspace_id)
    request.nextUrl.searchParams.forEach((value, key) => {
        sseUrl.searchParams.append(key, value);
    });

    const headers = new Headers();
    request.headers.forEach((value, key) => {
        if (key.toLowerCase() !== 'host' && key.toLowerCase() !== 'connection') {
            headers.set(key, value);
        }
    });

    try {
        const response = await fetch(sseUrl.toString(), {
            method: 'GET',
            headers,
        });

        const responseHeaders = new Headers(response.headers);
        responseHeaders.set('Cache-Control', 'no-cache, no-transform');
        responseHeaders.set('Connection', 'keep-alive');

        return new Response(response.body, {
            status: response.status,
            headers: responseHeaders,
        });
    } catch (error) {
        console.error("SSE Proxy Error:", error);
        return new Response("SSE Proxy Error", { status: 500 });
    }
}
