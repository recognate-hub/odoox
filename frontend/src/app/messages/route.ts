import { NextRequest } from 'next/server';

export const dynamic = 'force-dynamic';

export async function POST(request: NextRequest) {
    let backendUrlRaw = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';
    backendUrlRaw = backendUrlRaw.replace('localhost', '127.0.0.1');
    const backendUrl = backendUrlRaw.replace(/\/+$/, "");
    const messagesUrl = new URL('/messages', backendUrl);
    
    request.nextUrl.searchParams.forEach((value, key) => {
        messagesUrl.searchParams.append(key, value);
    });

    const headers = new Headers();
    request.headers.forEach((value, key) => {
        if (key.toLowerCase() !== 'host') {
            headers.set(key, value);
        }
    });

    try {
        const response = await fetch(messagesUrl.toString(), {
            method: 'POST',
            headers,
            body: request.body, // stream the body
            // @ts-ignore
            duplex: 'half' // required by Node for streaming bodies in fetch
        });

        return new Response(response.body, {
            status: response.status,
            headers: response.headers,
        });
    } catch (error) {
        console.error("Messages Proxy Error:", error);
        return new Response("Messages Proxy Error", { status: 500 });
    }
}
