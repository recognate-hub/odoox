"use client";

import React, { useState, useEffect } from 'react';
import '../../login/login.css';

export default function AdminPricingPage() {
    const [singlePrice, setSinglePrice] = useState<string>('');
    const [isLoading, setIsLoading] = useState(true);
    const [isSaving, setIsSaving] = useState(false);
    const [statusMessage, setStatusMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);

    useEffect(() => {
        const fetchPricing = async () => {
            try {
                const res = await fetch('/api/admin/pricing');
                
                if (!res.ok) {
                    throw new Error('Failed to fetch pricing');
                }

                const data = await res.json();
                setSinglePrice(data.singlePrice.toString());

            } catch (error) {
                console.error('Failed to initialize admin panel:', error);
                setStatusMessage({ type: 'error', text: 'Database Error: Check your connection or tables.' });
            } finally {
                setIsLoading(false);
            }
        };

        fetchPricing();
    }, []);

    const handleSave = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsSaving(true);
        setStatusMessage(null);
        try {
            const res = await fetch('/api/admin/pricing', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ singlePrice })
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
        <div style={{ padding: '3rem' }}>
            <h1 style={{ color: 'var(--text-primary)', marginBottom: '0.5rem', fontSize: '2rem' }}>Pricing Configuration</h1>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '3rem' }}>Manage your application pricing (in INR).</p>

            {statusMessage && (
                <div className={`alert ${statusMessage.type === 'error' ? 'alert-error' : 'alert-success'}`} style={{ marginBottom: '2rem', maxWidth: '600px' }}>
                    {statusMessage.text}
                </div>
            )}

            {isLoading ? (
                <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', color: 'var(--brand-primary)' }}>
                    <svg className="spinner" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg>
                    Loading pricing...
                </div>
            ) : (
                <div style={{ background: 'rgba(10, 10, 10, 0.5)', border: '1px solid rgba(255, 255, 255, 0.05)', borderRadius: '12px', padding: '2rem', maxWidth: '600px' }}>
                    <form onSubmit={handleSave}>
                        <div className="form-group">
                            <label className="form-label">Single User Plan Price (₹)</label>
                            <input 
                                type="number" 
                                className="form-input" 
                                value={singlePrice} 
                                onChange={(e) => setSinglePrice(e.target.value)}
                                required 
                            />
                        </div>
                        <button 
                            type="submit" 
                            className="btn btn-primary" 
                            style={{ width: '100%', marginTop: '2rem' }}
                            disabled={isSaving}
                        >
                            {isSaving ? (
                                <>
                                    <svg className="spinner" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg>
                                    Saving...
                                </>
                            ) : "Save Changes"}
                        </button>
                    </form>
                </div>
            )}
        </div>
    );
}
