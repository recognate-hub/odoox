import { NextResponse } from 'next/server';

export async function POST(req: Request) {
    try {
        const { url } = await req.json();
        if (!url) {
            return NextResponse.json({ error: 'URL is required' }, { status: 400 });
        }

        let cleanUrl = url.trim().replace(/\/+$/, '');
        if (!/^https?:\/\//i.test(cleanUrl)) {
            cleanUrl = 'http://' + cleanUrl;
        }

        const xmlBody = `<?xml version="1.0"?>
<methodCall>
  <methodName>list</methodName>
  <params>
  </params>
</methodCall>`;

        const response = await fetch(`${cleanUrl}/xmlrpc/2/db`, {
            method: 'POST',
            headers: {
                'Content-Type': 'text/xml',
            },
            body: xmlBody,
        });

        if (!response.ok) {
            return NextResponse.json({ error: 'Failed to connect to Odoo server' }, { status: response.status });
        }

        const responseText = await response.text();
        
        if (responseText.includes('<fault>')) {
            return NextResponse.json({ error: 'Odoo returned a fault (list_db might be disabled)' }, { status: 400 });
        }

        // Simple regex to extract strings in the array
        const dbNames: string[] = [];
        const regex = /<string>(.*?)<\/string>/g;
        let match;
        while ((match = regex.exec(responseText)) !== null) {
            // list method returns an array of strings
            dbNames.push(match[1]);
        }

        return NextResponse.json({ databases: dbNames });

    } catch (error: any) {
        return NextResponse.json({ error: error.message || 'Failed to fetch databases' }, { status: 500 });
    }
}
