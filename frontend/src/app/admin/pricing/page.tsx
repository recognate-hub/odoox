"use client";

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import '../../login/login.css';

export default function AdminPricingPage() {
    const router = useRouter();
    const [singlePrice, setSinglePrice] = useState<string>('');
    const [teamPrice, setTeamPrice] = useState<string>('');
    const [isLoading, setIsLoading] = useState(true);
    const [isSaving, setIsSaving] = useState(false);
    const [statusMessage, setStatusMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);
    const [isUnauthorized, setIsUnauthorized] = useState(false);

    useEffect(() => {
        const checkAdminAndFetch = async () => {
            try {
                const res = await fetch('/api/admin/pricing');
                
                if (res.status === 401) {
                    router.push('/login');
                    return;
                }
                
                if (res.status === 403) {
                    setIsUnauthorized(true);
                    setStatusMessage({ type: 'error', text: 'Unauthorized: You do not have administrator privileges.' });
                    setIsLoading(false);
                    return;
                }
                
                if (!res.ok) {
                    throw new Error('Failed to fetch pricing');
                }

                const data = await res.json();
                setSinglePrice(data.singlePrice.toString());
                setTeamPrice(data.teamPrice.toString());

            } catch (error) {
                console.error('Failed to initialize admin panel:', error);
                setStatusMessage({ type: 'error', text: 'Database Error: Check your connection or tables.' });
            } finally {
                setIsLoading(false);
            }
        };

        checkAdminAndFetch();
    }, [router]);

    const handleSave = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsSaving(true);
        setStatusMessage(null);
        try {
            const res = await fetch('/api/admin/pricing', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ singlePrice, teamPrice })
            });
            
            const data = await res.json();
            
            if (data.status === 'success') {
                setStatusMessage({ type: 'success', text: 'Prices updated successfully!' });
            } else {
                throw new Error(data.detail || 'Update failed');
            }
        } catch (error: any) {
            console.error('Failed to update prices:', error);
            setStatusMessage({ type: 'error', text: error.message || 'Update failed.' });
        } finally {
            setIsSaving(false);
        }
    };

    return (
        <div className="login-theme">
            <div className="bg-grid"></div>
            <div className="bg-glow"></div>
            
            <div className="login-wrapper">
                <div className="login-card" style={{ maxWidth: '480px' }}>
                    <div className="login-header">
                        <div className="brand-text">
                            <span style={{ color: 'var(--brand-primary)' }}>ODOOX</span> ADMIN
                        </div>
                        <p className="login-desc">Manage your application pricing</p>
                    </div>

                    {statusMessage && (
                        <div className={`alert ${statusMessage.type === 'error' ? 'alert-error' : 'alert-success'}`}>
                            {statusMessage.text}
                        </div>
                    )}

                    {isLoading ? (
                        <div style={{ display: 'flex', justifyContent: 'center', padding: '2rem 0' }}>
                            <svg className="spinner" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg>
                        </div>
                    ) : isUnauthorized ? (
                        <div className="text-center mt-3">
                            <button onClick={() => router.push('/userdashboard')} className="btn btn-primary btn-block">
                                Return to Dashboard
                            </button>
                        </div>
                    ) : (
                        <form onSubmit={handleSave}>
                            <div className="form-group">
                                <label className="form-label" htmlFor="singlePrice">Single User Plan (₹)</label>
                                <input 
                                    type="number" 
                                    id="singlePrice" 
                                    className="form-input" 
                                    required 
                                    value={singlePrice}
                                    onChange={(e) => setSinglePrice(e.target.value)}
                                    min="1"
                                />
                            </div>
                            
                            <div className="form-group" style={{ marginTop: '1.5rem' }}>
                                <label className="form-label" htmlFor="teamPrice">Team / Agency Plan (₹)</label>
                                <input 
                                    type="number" 
                                    id="teamPrice" 
                                    className="form-input" 
                                    required 
                                    value={teamPrice}
                                    onChange={(e) => setTeamPrice(e.target.value)}
                                    min="1"
                                />
                            </div>

                            <button type="submit" className="btn btn-primary btn-block mt-3" disabled={isSaving}>
                                {isSaving ? (
                                    <>
                                        <svg className="spinner" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg>
                                        Saving...
                                    </>
                                ) : "Save Pricing"}
                            </button>
                        </form>
                    )}
                </div>
            </div>
        </div>
    );
}
