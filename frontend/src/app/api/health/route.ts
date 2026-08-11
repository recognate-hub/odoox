import { NextResponse } from 'next/server';

export async function GET() {
    try {
        const rawBackendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const backendUrl = rawBackendUrl.endsWith('/') ? rawBackendUrl.slice(0, -1) : rawBackendUrl;
        const res = await fetch(`${backendUrl}/health`, {
            method: 'GET',
            // Increase timeout or ignore cache
            cache: 'no-store'
        });

        const data = await res.json();
        return NextResponse.json(data, { status: res.status });
    } catch (e: any) {
        console.error("Health check failed", e);
        return NextResponse.json({ 
            status: "degraded", 
            odoo_connected: false, 
            config_valid: false,
            error: e.message 
        }, { status: 500 });
    }
}
