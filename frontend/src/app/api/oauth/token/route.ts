import { NextResponse } from 'next/server';

export async function POST(request: Request) {
    try {
        const contentType = request.headers.get('content-type') || '';
        let body;
        
        if (contentType.includes('application/x-www-form-urlencoded')) {
            const formData = await request.formData();
            body = new URLSearchParams();
            formData.forEach((value, key) => {
                body.append(key, value.toString());
            });
        } else if (contentType.includes('application/json')) {
            const json = await request.json();
            body = new URLSearchParams();
            for (const key in json) {
                body.append(key, json[key]);
            }
        } else {
            return NextResponse.json({ error: "invalid_request", error_description: "Unsupported content type" }, { status: 400 });
        }

        const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        
        const res = await fetch(`${backendUrl}/token`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: body.toString()
        });

        const data = await res.json();
        return NextResponse.json(data, { status: res.status });

    } catch (e: any) {
        console.error("OAuth token proxy failed", e);
        return NextResponse.json({ error: "server_error", error_description: "Internal Server Error" }, { status: 500 });
    }
}
