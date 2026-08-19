"use client";

import React, { useEffect, useState } from 'react';

type User = {
    id: string;
    email: string;
    created_at: string;
    last_sign_in_at: string;
    plan: string;
};

export default function AdminUsersPage() {
    const [users, setUsers] = useState<User[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        const fetchUsers = async () => {
            try {
                const res = await fetch('/api/admin/users');
                if (!res.ok) {
                    throw new Error('Failed to fetch users');
                }
                const data = await res.json();
                if (data.status === 'success') {
                    setUsers(data.users);
                } else {
                    throw new Error(data.detail || 'Failed to fetch users');
                }
            } catch (err: any) {
                console.error(err);
                setError(err.message || 'Network error');
            } finally {
                setIsLoading(false);
            }
        };

        fetchUsers();
    }, []);

    return (
        <div style={{ padding: '3rem' }}>
            <h1 style={{ color: 'var(--text-primary)', marginBottom: '0.5rem', fontSize: '2rem' }}>Registered Users</h1>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '3rem' }}>View all sign-in user details.</p>

            {error && (
                <div className="alert alert-error" style={{ marginBottom: '2rem' }}>
                    {error}
                </div>
            )}

            {isLoading ? (
                <div style={{ display: 'flex', gap: '1rem', alignItems: 'center', color: 'var(--brand-primary)' }}>
                    <svg className="spinner" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg>
                    Loading users...
                </div>
            ) : (
                <div style={{ background: 'rgba(10, 10, 10, 0.5)', border: '1px solid rgba(255, 255, 255, 0.05)', borderRadius: '12px', overflow: 'hidden' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                        <thead style={{ background: 'rgba(0, 0, 0, 0.3)' }}>
                            <tr>
                                <th style={{ padding: '1rem 1.5rem', borderBottom: '1px solid rgba(255, 255, 255, 0.05)', color: 'var(--text-muted)', fontWeight: 500, fontSize: '0.875rem' }}>ID</th>
                                <th style={{ padding: '1rem 1.5rem', borderBottom: '1px solid rgba(255, 255, 255, 0.05)', color: 'var(--text-muted)', fontWeight: 500, fontSize: '0.875rem' }}>Email</th>
                                <th style={{ padding: '1rem 1.5rem', borderBottom: '1px solid rgba(255, 255, 255, 0.05)', color: 'var(--text-muted)', fontWeight: 500, fontSize: '0.875rem' }}>Status</th>
                                <th style={{ padding: '1rem 1.5rem', borderBottom: '1px solid rgba(255, 255, 255, 0.05)', color: 'var(--text-muted)', fontWeight: 500, fontSize: '0.875rem' }}>Joined</th>
                                <th style={{ padding: '1rem 1.5rem', borderBottom: '1px solid rgba(255, 255, 255, 0.05)', color: 'var(--text-muted)', fontWeight: 500, fontSize: '0.875rem' }}>Last Sign-In</th>
                            </tr>
                        </thead>
                        <tbody>
                            {users.map(user => (
                                <tr key={user.id} style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.02)' }}>
                                    <td style={{ padding: '1rem 1.5rem', color: 'var(--text-secondary)', fontSize: '0.875rem', fontFamily: 'monospace' }}>{user.id.split('-')[0]}...</td>
                                    <td style={{ padding: '1rem 1.5rem', color: 'var(--text-primary)' }}>{user.email}</td>
                                    <td style={{ padding: '1rem 1.5rem' }}>
                                        {user.plan === 'free' ? (
                                            <span style={{ padding: '0.25rem 0.5rem', borderRadius: '4px', background: 'rgba(255, 255, 255, 0.05)', color: 'var(--text-secondary)', fontSize: '0.75rem', textTransform: 'uppercase', fontWeight: 600 }}>Unpaid</span>
                                        ) : (
                                            <span style={{ padding: '0.25rem 0.5rem', borderRadius: '4px', background: 'rgba(163, 230, 53, 0.1)', color: 'var(--brand-primary)', fontSize: '0.75rem', textTransform: 'uppercase', fontWeight: 600 }}>Paid - {user.plan}</span>
                                        )}
                                    </td>
                                    <td style={{ padding: '1rem 1.5rem', color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
                                        {new Date(user.created_at).toLocaleDateString()}
                                    </td>
                                    <td style={{ padding: '1rem 1.5rem', color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
                                        {user.last_sign_in_at ? new Date(user.last_sign_in_at).toLocaleString() : 'Never'}
                                    </td>
                                </tr>
                            ))}
                            {users.length === 0 && (
                                <tr>
                                    <td colSpan={5} style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
                                        No users found.
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
}
