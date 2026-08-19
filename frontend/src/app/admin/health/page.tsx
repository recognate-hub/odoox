"use client";

import React, { useEffect, useState } from 'react';

type HealthStatus = {
    status: string;
    odoo_connected: boolean;
    config_valid: boolean;
    error?: string;
};

export default function AdminHealthPage() {
    const [health, setHealth] = useState<HealthStatus | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const fetchHealth = async () => {
            try {
                const res = await fetch('/api/health');
                const data = await res.json();
                setHealth(data);
            } catch (err) {
                console.error("Health check failed", err);
                setHealth({
                    status: 'error',
                    odoo_connected: false,
                    config_valid: false,
                    error: 'Failed to contact health endpoint.'
                });
            } finally {
                setIsLoading(false);
            }
        };

        fetchHealth();
        // Refresh every 30s
        const interval = setInterval(fetchHealth, 30000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div style={{ padding: '3rem' }}>
            <h1 style={{ color: 'var(--text-primary)', marginBottom: '0.5rem', fontSize: '2rem' }}>System Health</h1>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '3rem' }}>Monitor backend connectivity and configuration.</p>

            {isLoading && !health ? (
                <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', color: 'var(--brand-primary)' }}>
                    <svg className="spinner" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg>
                    Checking system health...
                </div>
            ) : health ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', maxWidth: '800px' }}>
                    
                    {/* Overall Status */}
                    <div style={{ 
                        background: 'rgba(10, 10, 10, 0.5)', 
                        border: `1px solid ${health.status === 'ok' ? 'rgba(163, 230, 53, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`, 
                        borderRadius: '12px', 
                        padding: '1.5rem',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between'
                    }}>
                        <div>
                            <div style={{ color: 'var(--text-muted)', fontSize: '0.875rem', marginBottom: '0.5rem' }}>Overall System Status</div>
                            <div style={{ fontSize: '1.5rem', fontWeight: 600, color: health.status === 'ok' ? 'var(--brand-primary)' : 'var(--accent-red)' }}>
                                {health.status.toUpperCase()}
                            </div>
                        </div>
                        <div style={{ 
                            width: '16px', height: '16px', borderRadius: '50%', 
                            background: health.status === 'ok' ? 'var(--brand-primary)' : 'var(--accent-red)',
                            boxShadow: `0 0 12px ${health.status === 'ok' ? 'var(--brand-primary)' : 'var(--accent-red)'}` 
                        }}></div>
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
                        {/* Config Validation */}
                        <div style={{ background: 'rgba(10, 10, 10, 0.5)', border: '1px solid rgba(255, 255, 255, 0.05)', borderRadius: '12px', padding: '1.5rem' }}>
                            <div style={{ color: 'var(--text-muted)', fontSize: '0.875rem', marginBottom: '1rem' }}>Configuration valid?</div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: health.config_valid ? 'var(--brand-primary)' : 'var(--text-secondary)' }}>
                                {health.config_valid ? (
                                    <><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg> Valid</>
                                ) : (
                                    <><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg> Invalid</>
                                )}
                            </div>
                        </div>

                        {/* Odoo Connection */}
                        <div style={{ background: 'rgba(10, 10, 10, 0.5)', border: '1px solid rgba(255, 255, 255, 0.05)', borderRadius: '12px', padding: '1.5rem' }}>
                            <div style={{ color: 'var(--text-muted)', fontSize: '0.875rem', marginBottom: '1rem' }}>Odoo XMLRPC Connectivity</div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: health.odoo_connected ? 'var(--brand-primary)' : 'var(--text-secondary)' }}>
                                {health.odoo_connected ? (
                                    <><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg> Connected</>
                                ) : (
                                    <><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg> Disconnected</>
                                )}
                            </div>
                        </div>
                    </div>

                    {health.error && (
                        <div className="alert alert-error">
                            {health.error}
                        </div>
                    )}
                </div>
            ) : null}
        </div>
    );
}
