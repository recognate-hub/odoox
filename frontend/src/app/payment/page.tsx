"use client";

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import './payment.css';

declare global {
    interface Window {
        Razorpay: any;
    }
}

export default function PaymentPage() {
    const router = useRouter();
    const [isLoading, setIsLoading] = useState(false);
    const [paymentStatus, setPaymentStatus] = useState<'idle' | 'processing' | 'success' | 'error'>('idle');
    const [errorMessage, setErrorMessage] = useState('');
    const [selectedPlanPrice, setSelectedPlanPrice] = useState<number | null>(null);

    // Load Razorpay checkout script
    useEffect(() => {
        const script = document.createElement('script');
        script.src = 'https://checkout.razorpay.com/v1/checkout.js';
        script.async = true;
        document.body.appendChild(script);
        return () => {
            document.body.removeChild(script);
        };
    }, []);

    const handlePayment = async (price: number, planName: string) => {
        setIsLoading(true);
        setErrorMessage('');
        setPaymentStatus('processing');
        setSelectedPlanPrice(price);

        try {
            // Step 1: Create order on the server
            const orderRes = await fetch('/api/razorpay/create-order', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    amount: price * 100, // Convert to paise
                    currency: 'INR',
                    plan: planName,
                }),
            });

            const orderData = await orderRes.json();

            if (!orderData.success) {
                throw new Error(orderData.message || 'Failed to create order');
            }

            // Step 2: Open Razorpay checkout modal
            const options = {
                key: process.env.NEXT_PUBLIC_RAZORPAY_KEY_ID,
                amount: orderData.amount,
                currency: orderData.currency,
                name: 'OdooX',
                description: planName,
                order_id: orderData.order_id,
                handler: async function (response: any) {
                    // Step 3: Verify payment on the server
                    try {
                        const verifyRes = await fetch('/api/razorpay/verify-payment', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                razorpay_order_id: response.razorpay_order_id,
                                razorpay_payment_id: response.razorpay_payment_id,
                                razorpay_signature: response.razorpay_signature,
                            }),
                        });

                        const verifyData = await verifyRes.json();

                        if (verifyData.success) {
                            setPaymentStatus('success');
                            // Redirect to dashboard after a brief success state
                            setTimeout(() => {
                                router.push('/userdashboard');
                            }, 2000);
                        } else {
                            setPaymentStatus('error');
                            setErrorMessage(verifyData.message || 'Payment verification failed');
                        }
                    } catch (err) {
                        setPaymentStatus('error');
                        setErrorMessage('Could not verify payment. Please contact support.');
                    }
                },
                prefill: {
                    name: '',
                    email: '',
                    contact: '',
                },
                notes: {
                    plan: planName,
                },
                theme: {
                    color: '#a3e635',
                    backdrop_color: 'rgba(0, 0, 0, 0.8)',
                },
                modal: {
                    ondismiss: function () {
                        setIsLoading(false);
                        setPaymentStatus('idle');
                        setSelectedPlanPrice(null);
                    },
                },
            };

            const rzp = new window.Razorpay(options);
            rzp.on('payment.failed', function (response: any) {
                setPaymentStatus('error');
                setErrorMessage(response.error.description || 'Payment failed. Please try again.');
                setIsLoading(false);
                setSelectedPlanPrice(null);
            });
            rzp.open();
        } catch (err: any) {
            setPaymentStatus('error');
            setErrorMessage(err.message || 'Something went wrong. Please try again.');
            setIsLoading(false);
            setSelectedPlanPrice(null);
        }
    };

    return (
        <div className="payment-theme">
            <div className="bg-grid"></div>
            <div className="ambient-glow"></div>

            <header className="header">
                <div className="header-content">
                    <Link href="/" className="brand">
                        <img src="/logo.png" alt="OdooX Logo" style={{ height: '36px', width: 'auto' }} />
                    </Link>
                </div>
            </header>

            <main className="payment-wrapper">
                <div className="payment-header">
                    <h1 className="title">
                        Choose your <br/>
                        <span className="title-gradient">Access Plan.</span>
                    </h1>
                    <p className="subtitle">
                        Get 5 years of unrestricted access to the OdooX AI Gateway. No recurring bills, no surprises.
                    </p>
                </div>

                {/* Status Messages */}
                {paymentStatus === 'success' && (
                    <div className="status-message success" style={{ marginBottom: '2rem', maxWidth: '800px', marginLeft: 'auto', marginRight: 'auto' }}>
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
                        Payment successful! Redirecting to dashboard...
                    </div>
                )}
                {paymentStatus === 'error' && (
                    <div className="status-message error" style={{ marginBottom: '2rem', maxWidth: '800px', marginLeft: 'auto', marginRight: 'auto' }}>
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>
                        {errorMessage}
                    </div>
                )}

                <div className="plans-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '2rem', maxWidth: '900px', margin: '0 auto 3rem auto' }}>
                    
                    {/* Single User Plan */}
                    <div className="pricing-card delay-1">
                        <div className="plan-header-section">
                            <div className="tier-name">Single User</div>
                            <p className="tier-desc">Perfect for solo developers and freelancers integrating AI with Odoo.</p>
                        </div>

                        <div className="price-block">
                            <div className="price-container">
                                <span className="currency">₹</span>
                                <span className="price">1</span>
                            </div>
                            <div className="billing-note">One-time payment · Valid for 5 years</div>
                        </div>

                        <button 
                            className="btn btn-primary btn-outline" 
                            onClick={() => handlePayment(1, 'OdooX Pro - Single User')}
                            disabled={isLoading || paymentStatus === 'success'}
                        >
                            {isLoading && selectedPlanPrice === 1 ? (
                                <>
                                    <span className="spinner"></span>
                                    Processing...
                                </>
                            ) : (
                                `Select Single User`
                            )}
                        </button>

                        <div className="features-divider">
                            <span>Included</span>
                        </div>

                        <ul className="features-list">
                            <li className="feature-item">
                                <CheckIcon /> Unlimited MCP Queries
                            </li>
                            <li className="feature-item">
                                <CheckIcon /> Connect 1 Odoo Database
                            </li>
                            <li className="feature-item">
                                <CheckIcon /> Standard Security
                            </li>
                            <li className="feature-item">
                                <CheckIcon /> Community Support
                            </li>
                        </ul>
                    </div>

                    {/* Team Plan */}
                    <div className="pricing-card featured delay-2">
                        <div className="pro-badge">Recommended</div>
                        
                        <div className="plan-header-section">
                            <div className="tier-name">Team / Agency</div>
                            <p className="tier-desc">Complete access to the AI-powered Odoo MCP Gateway for your entire team.</p>
                        </div>

                        <div className="price-block">
                            <div className="price-container">
                                <span className="currency">₹</span>
                                <span className="price">1</span>
                            </div>
                            <div className="billing-note">One-time payment · Valid for 5 years</div>
                        </div>

                        <button 
                            className="btn btn-primary" 
                            onClick={() => handlePayment(1, 'OdooX Pro - Team')}
                            disabled={isLoading || paymentStatus === 'success'}
                        >
                            {isLoading && selectedPlanPrice === 1 ? (
                                <>
                                    <span className="spinner"></span>
                                    Processing...
                                </>
                            ) : (
                                `Select Team Plan`
                            )}
                        </button>

                        <div className="features-divider">
                            <span>Everything in Single, plus</span>
                        </div>

                        <ul className="features-list">
                            <li className="feature-item">
                                <CheckIcon /> Connect up to 10 Odoo Databases
                            </li>
                            <li className="feature-item">
                                <CheckIcon /> Sub-50ms Global Edge Routing
                            </li>
                            <li className="feature-item">
                                <CheckIcon /> End-to-End AES-256 Encryption
                            </li>
                            <li className="feature-item">
                                <CheckIcon /> Priority Email & Chat Support
                            </li>
                        </ul>
                    </div>
                </div>

                <div className="trust-footer">
                    <div className="trust-item">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
                        Secure Payment via Razorpay
                    </div>
                    <div className="trust-item">
                        Instant Activation
                    </div>
                    <div className="trust-item">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                        Instant Activation
                    </div>
                </div>
            </main>
        </div>
    );
}

function CheckIcon() {
    return (
        <svg className="feature-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M20 6L9 17l-5-5"/>
        </svg>
    );
}
