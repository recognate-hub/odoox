import { NextResponse } from 'next/server';
import { cookies } from 'next/headers';

export async function GET(request: Request) {
    try {
        const cookieStore = await cookies();
        const token = cookieStore.get('access_token')?.value;

        if (!token) {
            return NextResponse.json({ status: "error", detail: "Not authenticated" }, { status: 401 });
        }

        const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        
        const res = await fetch(`${backendUrl}/api/workspace/api-key`, {
            method: 'GET',
            headers: {
                'Cookie': `access_token=${token}`
            }
        });

        const data = await res.json();
        
        if (!res.ok) {
            return NextResponse.json(data, { status: res.status });
        }

        return NextResponse.json(data);

    } catch (e: any) {
        console.error("API key generation failed", e);
        return NextResponse.json({ status: "error", detail: "Internal Server Error" }, { status: 500 });
    }
}
