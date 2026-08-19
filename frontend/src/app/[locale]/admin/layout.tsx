"use client";

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter, usePathname } from 'next/navigation';
import '../../oauth/login/login.css';

export default function AdminLayout({ children }: { children: React.ReactNode }) {
    const router = useRouter();
    const pathname = usePathname();
    const [isLoading, setIsLoading] = useState(true);
    const [isUnauthorized, setIsUnauthorized] = useState(false);

    useEffect(() => {
        const checkAdmin = async () => {
            try {
                // We'll reuse the pricing endpoint just to check admin auth status for the layout.
                // It returns 401 if unauth, 403 if not admin.
                const res = await fetch('/api/admin/pricing');
                
                if (res.status === 401) {
                    router.push('/login');
                    return;
                }
                
                if (res.status === 403) {
                    setIsUnauthorized(true);
                    setIsLoading(false);
                    return;
                }
                
                setIsLoading(false);
            } catch (error) {
                console.error('Failed to verify admin status:', error);
            }
        };

        checkAdmin();
    }, [router]);

    if (isLoading) {
        return (
            <div className="login-theme" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
                <div className="bg-grid"></div>
                <div className="bg-glow"></div>
                <svg className="spinner" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg>
            </div>
        );
    }

    if (isUnauthorized) {
        return (
            <div className="login-theme" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
                <div className="bg-grid"></div>
                <div className="bg-glow"></div>
                <div className="login-card" style={{ maxWidth: '480px', textAlign: 'center' }}>
                    <h2 style={{ color: 'var(--brand-primary)' }}>Unauthorized</h2>
                    <p style={{ marginTop: '1rem', color: 'var(--text-secondary)' }}>You do not have administrator privileges to view this area.</p>
                    <button className="btn btn-primary" style={{ marginTop: '2rem' }} onClick={() => router.push('/')}>Return Home</button>
                </div>
            </div>
        );
    }

    return (
        <div className="login-theme" style={{ display: 'flex', height: '100vh', overflow: 'hidden' }}>
            <div className="bg-grid"></div>
            <div className="bg-glow"></div>
            
            {/* Sidebar */}
            <aside style={{ width: '260px', background: 'rgba(10, 10, 10, 0.7)', backdropFilter: 'blur(10px)', borderRight: '1px solid rgba(255, 255, 255, 0.05)', display: 'flex', flexDirection: 'column', zIndex: 10 }}>
                <div style={{ padding: '2rem' }}>
                    <div className="brand-text" style={{ fontSize: '1.5rem', marginBottom: '2rem' }}>
                        <span style={{ color: 'var(--brand-primary)' }}>ODOOX</span> ADMIN
                    </div>
                    
                    <nav style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                        <Link 
                            href="/admin" 
                            style={{ 
                                padding: '0.75rem 1rem', 
                                borderRadius: '8px', 
                                color: pathname === '/admin' ? 'var(--brand-primary)' : 'var(--text-secondary)',
                                background: pathname === '/admin' ? 'rgba(163, 230, 53, 0.1)' : 'transparent',
                                textDecoration: 'none',
                                fontWeight: pathname === '/admin' ? 600 : 400,
                                display: 'flex', alignItems: 'center', gap: '0.5rem'
                            }}
                        >
                            Dashboard
                        </Link>
                        <Link 
                            href="/admin/users" 
                            style={{ 
                                padding: '0.75rem 1rem', 
                                borderRadius: '8px', 
                                color: pathname === '/admin/users' ? 'var(--brand-primary)' : 'var(--text-secondary)',
                                background: pathname === '/admin/users' ? 'rgba(163, 230, 53, 0.1)' : 'transparent',
                                textDecoration: 'none',
                                fontWeight: pathname === '/admin/users' ? 600 : 400,
                                display: 'flex', alignItems: 'center', gap: '0.5rem'
                            }}
                        >
                            Users
                        </Link>
                        <Link 
                            href="/admin/pricing" 
                            style={{ 
                                padding: '0.75rem 1rem', 
                                borderRadius: '8px', 
                                color: pathname === '/admin/pricing' ? 'var(--brand-primary)' : 'var(--text-secondary)',
                                background: pathname === '/admin/pricing' ? 'rgba(163, 230, 53, 0.1)' : 'transparent',
                                textDecoration: 'none',
                                fontWeight: pathname === '/admin/pricing' ? 600 : 400,
                                display: 'flex', alignItems: 'center', gap: '0.5rem'
                            }}
                        >
                            Pricing
                        </Link>
                        <Link 
                            href="/admin/health" 
                            style={{ 
                                padding: '0.75rem 1rem', 
                                borderRadius: '8px', 
                                color: pathname === '/admin/health' ? 'var(--brand-primary)' : 'var(--text-secondary)',
                                background: pathname === '/admin/health' ? 'rgba(163, 230, 53, 0.1)' : 'transparent',
                                textDecoration: 'none',
                                fontWeight: pathname === '/admin/health' ? 600 : 400,
                                display: 'flex', alignItems: 'center', gap: '0.5rem'
                            }}
                        >
                            System Health
                        </Link>
                    </nav>
                </div>
                
                <div style={{ marginTop: 'auto', padding: '2rem' }}>
                    <Link href="/" style={{ color: 'var(--text-muted)', textDecoration: 'none', fontSize: '0.875rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        ← Back to Site
                    </Link>
                </div>
            </aside>

            {/* Main Content Area */}
            <main style={{ flex: 1, overflowY: 'auto', position: 'relative', zIndex: 10 }}>
                {children}
            </main>
        </div>
    );
}
