"use client";

import React from 'react';
import { useRouter } from 'next/navigation';

export default function SignOutButton({ className }: { className?: string }) {
    const router = useRouter();

    const handleLogout = async (e: React.MouseEvent) => {
        e.preventDefault();
        try {
            await fetch('/api/logout', { method: 'POST' });
        } catch (err) {
            console.error("Logout error", err);
        } finally {
            router.push('/login');
            router.refresh();
        }
    };

    return (
        <button 
            onClick={handleLogout} 
            className={className} 
            style={{ background: 'transparent', border: 'none', cursor: 'pointer', fontFamily: 'inherit', padding: 0 }}
        >
            Sign Out
        </button>
    );
}
