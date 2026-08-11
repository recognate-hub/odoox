"use client";

import React, { useEffect, useState } from 'react';
import Link from 'next/link';

export default function AdminDashboardPage() {
    const [stats, setStats] = useState({
        totalUsers: 0,
        recentSignins: 0,
        singlePrice: 0
    });
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const fetchDashboardData = async () => {
            try {
                const [usersRes, pricingRes] = await Promise.all([
                    fetch('/api/admin/users'),
                    fetch('/api/admin/pricing')
                ]);

                if (usersRes.ok && pricingRes.ok) {
                    const usersData = await usersRes.json();
                    const pricingData = await pricingRes.json();

                    if (usersData.status === 'success' && pricingData.status === 'success') {
                        const users = usersData.users || [];
                        
                        // Calculate recent sign-ins (last 7 days)
                        const oneWeekAgo = new Date();
                        oneWeekAgo.setDate(oneWeekAgo.getDate() - 7);
                        
                        const recent = users.filter((u: any) => {
                            if (!u.last_sign_in_at) return false;
                            return new Date(u.last_sign_in_at) >= oneWeekAgo;
                        }).length;

                        setStats({
                            totalUsers: users.length,
                            recentSignins: recent,
                            singlePrice: pricingData.singlePrice
                        });
                    }
                }
            } catch (err) {
                console.error("Failed to load dashboard data", err);
            } finally {
                setIsLoading(false);
            }
        };

        fetchDashboardData();
    }, []);

    return (
        <div style={{ padding: '3rem' }}>
            <h1 style={{ color: 'var(--text-primary)', marginBottom: '0.5rem', fontSize: '2rem' }}>Admin Overview</h1>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '3rem' }}>High-level metrics for the OdooX application.</p>

            {isLoading ? (
                <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', color: 'var(--brand-primary)' }}>
                    <svg className="spinner" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg>
                    Loading metrics...
                </div>
            ) : (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1.5rem' }}>
                    {/* Stat Card 1 */}
                    <div style={{ background: 'rgba(10, 10, 10, 0.5)', border: '1px solid rgba(255, 255, 255, 0.05)', borderRadius: '12px', padding: '1.5rem' }}>
                        <div style={{ color: 'var(--text-muted)', fontSize: '0.875rem', marginBottom: '0.5rem' }}>Total Registered Users</div>
                        <div style={{ fontSize: '2.5rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                            {stats.totalUsers}
                        </div>
                        <div style={{ marginTop: '1rem' }}>
                            <Link href="/admin/users" style={{ color: 'var(--brand-primary)', textDecoration: 'none', fontSize: '0.875rem' }}>View Details →</Link>
                        </div>
                    </div>

                    {/* Stat Card 2 */}
                    <div style={{ background: 'rgba(10, 10, 10, 0.5)', border: '1px solid rgba(255, 255, 255, 0.05)', borderRadius: '12px', padding: '1.5rem' }}>
                        <div style={{ color: 'var(--text-muted)', fontSize: '0.875rem', marginBottom: '0.5rem' }}>Recent Sign-Ins (7d)</div>
                        <div style={{ fontSize: '2.5rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                            {stats.recentSignins}
                        </div>
                    </div>

                    {/* Stat Card 3 */}
                    <div style={{ background: 'rgba(10, 10, 10, 0.5)', border: '1px solid rgba(255, 255, 255, 0.05)', borderRadius: '12px', padding: '1.5rem' }}>
                        <div style={{ color: 'var(--text-muted)', fontSize: '0.875rem', marginBottom: '0.5rem' }}>Current Single Plan Price</div>
                        <div style={{ fontSize: '2.5rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                            ₹{stats.singlePrice}
                        </div>
                        <div style={{ marginTop: '1rem' }}>
                            <Link href="/admin/pricing" style={{ color: 'var(--brand-primary)', textDecoration: 'none', fontSize: '0.875rem' }}>Configure →</Link>
                        </div>
                    </div>


                </div>
            )}
        </div>
    );
}
