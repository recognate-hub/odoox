import { NextRequest } from 'next/server';

export const dynamic = 'force-dynamic';
export const runtime = 'edge';

export async function GET(request: NextRequest) {
    let backendUrlRaw = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';
    // Node 18+ fetch prefers IPv6 ::1 for localhost, which fails if FastAPI binds to 0.0.0.0 (IPv4)
    backendUrlRaw = backendUrlRaw.replace('localhost', '127.0.0.1');
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
        responseHeaders.set('Access-Control-Allow-Origin', '*');
        responseHeaders.set('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
        responseHeaders.set('Access-Control-Allow-Headers', 'Content-Type, Authorization');

        return new Response(response.body, {
            status: response.status,
            headers: responseHeaders,
        });
    } catch (error) {
        console.error("SSE Proxy Error:", error);
        return new Response("SSE Proxy Error", { status: 500 });
    }
}

export async function OPTIONS(request: NextRequest) {
    return new Response(null, {
        status: 204,
        headers: {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        },
    });
}
