import { NextResponse } from 'next/server';
import { cookies } from 'next/headers';

export async function POST(request: Request) {
    try {
        const cookieStore = await cookies();
        const token = cookieStore.get('access_token')?.value;

        if (!token) {
            return NextResponse.json({ status: "error", detail: "Not authenticated" }, { status: 401 });
        }

        const body = await request.json();
        const apiKey = body.api_key;
        
        if (!apiKey) {
            return NextResponse.json({ status: "error", detail: "api_key is required" }, { status: 400 });
        }

        const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        
        // Backend expects form data for this route
        const formData = new URLSearchParams();
        formData.append('api_key', apiKey);
        
        const res = await fetch(`${backendUrl}/api/workspace/api-key/revoke`, {
            method: 'POST',
            headers: {
                'Cookie': `access_token=${token}`,
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: formData.toString()
        });

        const data = await res.json();
        
        if (!res.ok) {
            return NextResponse.json(data, { status: res.status });
        }

        return NextResponse.json(data);

    } catch (e: any) {
        console.error("API key revocation failed", e);
        return NextResponse.json({ status: "error", detail: "Internal Server Error" }, { status: 500 });
    }
}
