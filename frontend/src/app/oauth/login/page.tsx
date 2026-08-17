"use client";

import React, { useEffect, useRef, useState } from 'react';
import './login.css';

export default function OAuthLoginPage() {
    const [step, setStep] = useState(1);
    const [email, setEmail] = useState('');
    const [code, setCode] = useState(['', '', '', '', '', '']);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    // True while we check if the user already has a valid session
    const [checkingSession, setCheckingSession] = useState(true);

    const inputRefs = useRef<(HTMLInputElement | null)[]>([]);

    // Grab the `?next` URL once — this is the backend OAuth authorize URL that
    // Claude is waiting for. In the OAuth flow this is always present.
    const getNextUrl = () => {
        if (typeof window === 'undefined') return null;
        return new URLSearchParams(window.location.search).get('next');
    };

    // On mount: if the user already has a valid session, skip the form entirely
    // and redirect straight back to Claude via the `?next` URL.
    useEffect(() => {
        const checkExistingSession = async () => {
            try {
                const res = await fetch('/api/auth/me');
                if (res.ok) {
                    const data = await res.json();
                    const nextUrl = getNextUrl();
                    if (nextUrl) {
                        // Already logged in — complete the OAuth handshake immediately
                        const urlObj = new URL(nextUrl);
                        if (data.access_token) urlObj.searchParams.set('token', data.access_token);
                        if (data.refresh_token) urlObj.searchParams.set('refresh_token', data.refresh_token);
                        window.location.href = urlObj.toString();
                        return;
                    }
                }
            } catch {
                // No session or network error — show the login form
            }
            setCheckingSession(false);
        };
        checkExistingSession();
    }, []);

    const handleCodeChange = (index: number, value: string) => {
        if (value.length > 1) value = value.slice(-1);
        const newCode = [...code];
        newCode[index] = value;
        setCode(newCode);
        if (value !== '' && index < 5) inputRefs.current[index + 1]?.focus();

        if (newCode.every(d => d !== '')) {
            setTimeout(() => document.getElementById('verify-btn')?.click(), 50);
        }
    };

    const handleKeyDown = (index: number, e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === 'Backspace' && code[index] === '' && index > 0) {
            inputRefs.current[index - 1]?.focus();
        } else if (e.key === 'ArrowLeft' && index > 0) {
            inputRefs.current[index - 1]?.focus();
        } else if (e.key === 'ArrowRight' && index < 5) {
            inputRefs.current[index + 1]?.focus();
        }
    };

    const handlePaste = (e: React.ClipboardEvent<HTMLInputElement>) => {
        e.preventDefault();
        const pastedData = e.clipboardData.getData('text/plain').trim();
        if (/^\d{6}$/.test(pastedData)) {
            const newCode = pastedData.split('');
            setCode(newCode);
            inputRefs.current[5]?.focus();
            setTimeout(() => document.getElementById('verify-btn')?.click(), 50);
        }
    };

    const handleRequestOtp = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!email || !email.includes('@')) {
            setError("Please enter a valid email address.");
            return;
        }

        setIsLoading(true);
        setError('');
        setSuccess('');

        const formData = new URLSearchParams();
        formData.append('email', email);

        try {
            const res = await fetch('/api/login/otp', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: formData.toString()
            });
            const data = await res.json();

            if (data.status === 'success') {
                setSuccess("OTP sent! Please check your inbox.");
                setTimeout(() => {
                    setStep(2);
                    setTimeout(() => inputRefs.current[0]?.focus(), 50);
                }, 1000);
            } else {
                setError(data.message || "Failed to send OTP");
            }
        } catch {
            setError("Network error. Make sure the backend is running.");
        } finally {
            setIsLoading(false);
        }
    };

    const handleVerifyOtp = async (e: React.FormEvent) => {
        e.preventDefault();
        const token = code.join('');

        if (token.length !== 6) {
            setError('Please enter the full 6-digit code.');
            return;
        }

        setIsLoading(true);
        setError('');

        const formData = new URLSearchParams();
        formData.append('email', email);
        formData.append('token', token);

        try {
            const res = await fetch('/api/login/verify', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: formData.toString()
            });
            const data = await res.json();

            if (data.status === 'success') {
                // In the OAuth flow there is always a `?next` pointing to the
                // backend /authorize URL. Always go there — never fall back to
                // the dashboard, because Claude is waiting for the auth code.
                const nextUrl = getNextUrl();
                if (nextUrl) {
                    const urlObj = new URL(nextUrl);
                    if (data.access_token) urlObj.searchParams.set('token', data.access_token);
                    if (data.refresh_token) urlObj.searchParams.set('refresh_token', data.refresh_token);
                    window.location.href = urlObj.toString();
                } else {
                    // Fallback: no `?next` means the user landed here directly;
                    // send them to their dashboard.
                    window.location.href = data.redirect || '/userdashboard';
                }
            } else if (data.status === 'conflict') {
                setStep(3);
            } else {
                setError(data.message || "Invalid code.");
            }
        } catch {
            setError("Network error. Make sure the backend is running.");
        } finally {
            setIsLoading(false);
        }
    };

    const handleForceLogout = async (e: React.MouseEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError('');

        try {
            const res = await fetch('/api/login/confirm-session', {
                method: 'POST'
            });
            const data = await res.json();

            if (data.status === 'success') {
                const nextUrl = getNextUrl();
                if (nextUrl) {
                    const urlObj = new URL(nextUrl);
                    if (data.access_token) urlObj.searchParams.set('token', data.access_token);
                    if (data.refresh_token) urlObj.searchParams.set('refresh_token', data.refresh_token);
                    window.location.href = urlObj.toString();
                } else {
                    window.location.href = data.redirect || '/userdashboard';
                }
            } else {
                setError(data.message || "Failed to override session.");
            }
        } catch {
            setError("Network error.");
        } finally {
            setIsLoading(false);
        }
    };

    const handleBack = (e: React.MouseEvent) => {
        e.preventDefault();
        setStep(1);
        setError('');
        setSuccess('');
        setCode(['', '', '', '', '', '']);
    };

    // Render nothing while checking for an existing session to avoid
    // flashing the login form before the redirect fires.
    if (checkingSession) return null;

    return (
        <div className="login-theme">
            <div className="bg-grid"></div>
            <div className="bg-glow"></div>

            <div className="login-wrapper">
                <div className="login-card">
                    <div className="login-header">
                        <div className="brand-text" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '15px' }}>
                            <img src="/logo.png" alt="OdooX Logo" style={{ height: '48px', width: 'auto' }} />
                        </div>
                        <h2>Connect to Claude</h2>
                        <p className="login-desc">Sign in with ODOOX to authorize Claude.</p>
                    </div>

                    {error && <div className="alert alert-error">{error}</div>}
                    {success && <div className="alert alert-success">{success}</div>}

                    {/* Step 1: Request OTP */}
                    <div className={`step-container ${step === 1 ? 'step-visible' : 'step-hidden'}`}>
                        <form onSubmit={handleRequestOtp}>
                            <div className="form-group">
                                <label className="form-label" htmlFor="email">Email Address</label>
                                <input
                                    type="email"
                                    id="email"
                                    className="form-input"
                                    required
                                    placeholder="name@company.com"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                />
                            </div>

                            <button type="submit" className="btn btn-primary btn-block" disabled={isLoading}>
                                {isLoading ? (
                                    <>
                                        <svg className="spinner" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg>
                                        Sending...
                                    </>
                                ) : "Send OTP"}
                            </button>
                        </form>
                    </div>

                    {/* Step 2: Verify OTP */}
                    <div className={`step-container ${step === 2 ? 'step-visible' : 'step-hidden'}`}>
                        <form onSubmit={handleVerifyOtp}>
                            <div className="form-group text-center">
                                <label className="form-label" style={{ textTransform: 'none', color: 'var(--text-secondary)' }}>
                                    Enter the 6-digit code sent to your email
                                </label>
                                <div className="otp-input-group" onPaste={handlePaste}>
                                    {code.map((digit, idx) => (
                                        <input
                                            key={idx}
                                            ref={(el) => { inputRefs.current[idx] = el; }}
                                            type="text"
                                            maxLength={1}
                                            className="form-input otp-input"
                                            value={digit}
                                            onChange={(e) => handleCodeChange(idx, e.target.value)}
                                            onKeyDown={(e) => handleKeyDown(idx, e)}
                                            required
                                        />
                                    ))}
                                </div>
                            </div>

                            <button id="verify-btn" type="submit" className="btn btn-primary btn-block mt-3" disabled={isLoading}>
                                {isLoading ? (
                                    <>
                                        <svg className="spinner" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg>
                                        Verifying...
                                    </>
                                ) : "Verify & Login"}
                            </button>

                            <div className="text-center mt-3" style={{ display: 'flex', justifyContent: 'center', gap: '1.5rem', alignItems: 'center' }}>
                                <a href="#" onClick={handleBack} className="back-link">
                                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                        <path d="M19 12H5M12 19l-7-7 7-7"/>
                                    </svg>
                                    Back to email
                                </a>
                                <a href="#" onClick={handleRequestOtp} className="back-link" style={{ color: 'var(--brand-primary)' }}>
                                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ marginRight: '4px' }}>
                                        <path d="M21 2v6h-6M3 12a9 9 0 0 1 15-6.7L21 8M3 22v-6h6M21 12a9 9 0 0 1-15 6.7L3 16"/>
                                    </svg>
                                    Resend OTP
                                </a>
                            </div>
                        </form>
                    </div>

                    {/* Step 3: Force Logout (active session on another device) */}
                    <div className={`step-container ${step === 3 ? 'step-visible' : 'step-hidden'}`}>
                        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
                            <h4 style={{ color: 'var(--text-primary)', marginBottom: '0.5rem' }}>Active Session Detected</h4>
                            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                                You are currently logged in on another device. For security reasons, you can only have one active session at a time.
                            </p>
                        </div>
                        <button
                            className="btn btn-danger btn-block"
                            onClick={handleForceLogout}
                            disabled={isLoading}
                        >
                            {isLoading ? (
                                <>
                                    <svg className="spinner" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg>
                                    Processing...
                                </>
                            ) : "Force Logout Other Device"}
                        </button>
                        <button
                            className="btn btn-outline btn-block mt-3"
                            onClick={handleBack}
                            disabled={isLoading}
                        >
                            Cancel
                        </button>
                    </div>

                    <div className="footer-text">
                        Secure authentication powered by Supabase
                    </div>
                </div>
            </div>
        </div>
    );
}
