import fernet from 'fernet';

export function getActiveFernet() {
    const keyStr = process.env.ENCRYPTION_KEY || '';
    if (!keyStr) return null;
    
    // Fernet expects a 44-character base64url string. 
    // If the ENCRYPTION_KEY is valid, it can be passed directly to the Secret constructor.
    try {
        const secret = new fernet.Secret(keyStr);
        return secret;
    } catch (e) {
        console.error("Invalid fernet secret", e);
        return null;
    }
}

import crypto from 'crypto';

export function encrypt(secretText: string): string {
    if (!secretText) return secretText;
    const kek = getActiveFernet();
    if (!kek) return secretText;
    
    // Generate a random 32-byte key, base64 encoded
    const rawKey = crypto.randomBytes(32);
    const dekStr = rawKey.toString('base64')
        .replace(/\+/g, '-')
        .replace(/\//g, '_')
        .replace(/=+$/, '') + '='; // Fernet requires exactly 44 chars (32 bytes base64 encoded)

    const dekSecret = new fernet.Secret(dekStr);
    
    // Encrypt the plaintext with DEK
    const dekToken = new fernet.Token({
        secret: dekSecret,
        time: Date.parse(new Date().toUTCString())
    });
    const ciphertext = dekToken.encode(secretText);
    
    // Encrypt the DEK with KEK
    const kekToken = new fernet.Token({
        secret: kek,
        time: Date.parse(new Date().toUTCString())
    });
    const encryptedDek = kekToken.encode(dekStr);
    
    return `ENVELOPE_V1:${encryptedDek}:${ciphertext}`;
}

export function decrypt(tokenStr: string): string {
    if (!tokenStr) return tokenStr;
    
    const kek = getActiveFernet();
    if (!kek) return tokenStr;

    if (tokenStr.startsWith('ENVELOPE_V1:')) {
        try {
            const parts = tokenStr.split(':');
            const encryptedDek = parts[1];
            const ciphertext = parts[2];
            
            // Decrypt DEK
            const kekToken = new fernet.Token({
                secret: kek,
                token: encryptedDek,
                ttl: 0
            });
            const dekStr = kekToken.decode();
            
            // Decrypt ciphertext with DEK
            const dekSecret = new fernet.Secret(dekStr);
            const dekToken = new fernet.Token({
                secret: dekSecret,
                token: ciphertext,
                ttl: 0
            });
            return dekToken.decode();
        } catch (e) {
            console.error("Envelope Decryption failed", e);
            return tokenStr;
        }
    }

    // Fallback if not a fernet token (for backward compatibility matching the Python backend)
    if (!tokenStr.startsWith('gAAAAAB')) return tokenStr;
    
    const token = new fernet.Token({
        secret: kek,
        token: tokenStr,
        ttl: 0 // Python backend has no strict ttl by default for this, or uses 0 to bypass ttl verification in fernet.js
    });
    try {
        return token.decode();
    } catch (e) {
        console.error("Decryption failed", e);
        return tokenStr; // Fallback if decryption fails
    }
}
