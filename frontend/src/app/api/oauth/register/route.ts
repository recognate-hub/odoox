import { NextResponse } from 'next/server';

export async function POST(request: Request) {
    try {
        const json = await request.json();
        const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        
        const res = await fetch(`${backendUrl}/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(json)
        });

        const data = await res.json();
        return NextResponse.json(data, { status: res.status });

    } catch (e: any) {
        console.error("OAuth register proxy failed", e);
        return NextResponse.json({ error: "server_error", error_description: "Internal Server Error" }, { status: 500 });
    }
}
