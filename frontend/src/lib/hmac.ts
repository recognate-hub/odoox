export async function signWithHmac(text: string): Promise<string> {
    const keyStr = process.env.ENCRYPTION_KEY || 'default_secret_key_needs_to_be_32_bytes_at_least';
    const encoder = new TextEncoder();
    const keyData = encoder.encode(keyStr);
    
    const cryptoKey = await crypto.subtle.importKey(
        'raw',
        keyData,
        { name: 'HMAC', hash: 'SHA-256' },
        false,
        ['sign']
    );
    
    const signature = await crypto.subtle.sign(
        'HMAC',
        cryptoKey,
        encoder.encode(text)
    );
    
    // Convert ArrayBuffer to hex string
    return Array.from(new Uint8Array(signature))
        .map(b => b.toString(16).padStart(2, '0'))
        .join('');
}

export async function verifyHmac(text: string, signatureHex: string): Promise<boolean> {
    const expected = await signWithHmac(text);
    return expected === signatureHex;
}
