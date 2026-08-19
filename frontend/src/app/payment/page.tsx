"use client";

import React, { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { supabase } from '@/lib/supabase';
import { motion } from 'framer-motion';
import { Canvas, useFrame } from '@react-three/fiber';
import { Float, Environment } from '@react-three/drei';
import * as THREE from 'three';
import { ArrowLeft, Check, Shield } from 'lucide-react';

declare global {
    interface Window {
        Razorpay: any;
    }
}

const ease = [0.25, 0.4, 0, 1] as const;

// 3D Background Objects (from GlassHero)
function BackgroundShapes() {
  const knotRef = useRef<THREE.Mesh>(null);
  const sphereRef1 = useRef<THREE.Mesh>(null);
  const sphereRef2 = useRef<THREE.Mesh>(null);

  useFrame(({ clock }) => {
    const t = clock.getElapsedTime();
    if (knotRef.current) {
      knotRef.current.rotation.x = t * 0.2;
      knotRef.current.rotation.y = t * 0.3;
    }
    if (sphereRef1.current) {
      sphereRef1.current.position.y = Math.sin(t * 0.5) * 1.5 + 2;
    }
    if (sphereRef2.current) {
      sphereRef2.current.position.y = Math.cos(t * 0.4) * 2 - 2;
    }
  });

  const materialProps = {
    color: '#ffffff',
    roughness: 0,
    metalness: 1,
    envMapIntensity: 2,
    clearcoat: 1,
    clearcoatRoughness: 0.1,
  };

  return (
    <>
      <ambientLight intensity={0.2} />
      <directionalLight position={[10, 10, 5]} intensity={2} color="#ffffff" />
      <directionalLight position={[-10, -10, -5]} intensity={1} color="#84cc16" />
      
      <Environment preset="studio" />

      <Float speed={1.5} rotationIntensity={0.5} floatIntensity={1}>
        <mesh ref={knotRef} position={[0, 0, -2]} scale={1.5}>
          <torusKnotGeometry args={[1, 0.4, 200, 32]} />
          <meshStandardMaterial {...materialProps} />
        </mesh>
      </Float>

      <Float speed={2} rotationIntensity={1} floatIntensity={2}>
        <mesh ref={sphereRef1} position={[-4, 2, -1]}>
          <sphereGeometry args={[1, 64, 64]} />
          <meshStandardMaterial {...materialProps} color="#84cc16" metalness={0.8} />
        </mesh>
      </Float>

      <Float speed={1.5} rotationIntensity={1} floatIntensity={1.5}>
        <mesh ref={sphereRef2} position={[4, -2, -3]}>
          <sphereGeometry args={[1.5, 64, 64]} />
          <meshStandardMaterial {...materialProps} color="#a3e635" metalness={0.9} />
        </mesh>
      </Float>
    </>
  );
}

export default function PaymentPage() {
    const router = useRouter();
    const [isLoading, setIsLoading] = useState(false);
    const [paymentStatus, setPaymentStatus] = useState<'idle' | 'processing' | 'success' | 'error'>('idle');
    const [errorMessage, setErrorMessage] = useState('');
    const [selectedPlanPrice, setSelectedPlanPrice] = useState<number | null>(null);
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [isCheckingAuth, setIsCheckingAuth] = useState(true);
    const [singlePrice, setSinglePrice] = useState<number | null>(null);

    useEffect(() => {
        const fetchPrices = async () => {
            try {
                const { data, error } = await supabase.from('app_config').select('*').in('key', ['single_plan_price']);
                if (data && !error) {
                    const single = data.find(d => d.key === 'single_plan_price');
                    if (single) setSinglePrice(parseFloat(single.value));
                }
            } catch (err) {
                console.error('Could not fetch dynamic prices');
            }
        };
        fetchPrices();
    }, []);

    useEffect(() => {
        fetch('/api/auth/me')
            .then(res => res.json())
            .then(data => {
                if (data.status === 'success') {
                    setIsAuthenticated(true);
                }
            })
            .catch(() => {})
            .finally(() => setIsCheckingAuth(false));
    }, []);

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
        <div className="relative w-full min-h-[100vh] flex items-center justify-center py-24 px-4 overflow-hidden bg-black font-body-md text-body-md antialiased selection:bg-primary-container selection:text-black">
            
            {/* Ambient Background Glows (matching page.tsx) */}
            <div className="fixed inset-0 z-[-1] pointer-events-none bg-grid-pattern opacity-20"></div>
            <div className="fixed top-[-20%] left-[-10%] w-[50%] h-[50%] rounded-full bg-primary-container/10 blur-[120px] z-[-1] pointer-events-none"></div>
            <div className="fixed bottom-[-20%] right-[-10%] w-[40%] h-[40%] rounded-full bg-primary-container/5 blur-[100px] z-[-1] pointer-events-none"></div>

            {/* Top Navigation */}
            <header className="fixed top-0 left-0 w-full z-50 border-b border-white/10 bg-black/40 backdrop-blur-md">
                <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
                    <Link href="/" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
                        <ArrowLeft className="w-5 h-5 text-white/70" />
                        <span className="text-white/70 font-medium">Back to Home</span>
                    </Link>
                    <Link href="/" className="flex items-center gap-2">
                        <img src="/logo.png" alt="OdooX Logo" className="h-8 w-auto object-contain" />
                    </Link>
                </div>
            </header>

            {/* 3D R3F Canvas Background */}
            <div className="absolute inset-0 z-0">
                <Canvas camera={{ position: [0, 0, 10], fov: 45 }} dpr={[1, 2]}>
                    <BackgroundShapes />
                </Canvas>
            </div>

            {/* Main Glass Window */}
            <motion.div 
                transition={{ type: 'spring', stiffness: 200, damping: 20 }}
                initial={{ opacity: 0, scale: 0.95, y: 30 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                className="relative z-10 w-[95%] max-w-4xl rounded-2xl shadow-[0_30px_60px_rgba(0,0,0,0.6)] overflow-hidden mt-8"
            >
                {/* Clean Glass Background Layer */}
                <div 
                    className="absolute inset-0 z-[-1] rounded-2xl border border-white/10 bg-black/60"
                    style={{ 
                        backdropFilter: 'blur(40px)', 
                        WebkitBackdropFilter: 'blur(40px)',
                        boxShadow: 'inset 0 0 0 1px rgba(255,255,255,0.05), inset 0 1px 0 rgba(255,255,255,0.2)'
                    }}
                >
                    {/* Subtle noise over the glass */}
                    <div className="absolute inset-0 opacity-[0.03] noise-bg mix-blend-overlay"></div>
                </div>

                {/* Top Window Bar */}
                <div className="h-10 w-full bg-white/[0.02] border-b border-white/[0.05] flex items-center px-4 gap-2">
                    <div className="w-3 h-3 rounded-full bg-red-500/80 shadow-[0_0_10px_rgba(239,68,68,0.5)]"></div>
                    <div className="w-3 h-3 rounded-full bg-yellow-500/80 shadow-[0_0_10px_rgba(234,179,8,0.5)]"></div>
                    <div className="w-3 h-3 rounded-full bg-green-500/80 shadow-[0_0_10px_rgba(34,197,94,0.5)]"></div>
                    <div className="mx-auto text-[10px] font-code-sm text-white/40 uppercase tracking-widest pl-6">Secure Checkout</div>
                </div>

                {/* Content Area */}
                <div className="p-8 md:p-16 flex flex-col items-center text-center space-y-8 bg-gradient-to-b from-white/[0.02] to-transparent">
                    
                    <div className="space-y-4">
                        <motion.h1
                            initial={{ opacity: 0, y: 16 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.6, delay: 0.2, ease }}
                            className="text-4xl md:text-5xl font-display-lg font-bold text-white tracking-tight"
                        >
                            Choose your <br className="hidden md:block" />
                            <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary-container to-white glow-text">
                                Access Plan.
                            </span>
                        </motion.h1>
                        <motion.p
                            initial={{ opacity: 0, y: 16 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.6, delay: 0.3, ease }}
                            className="text-white/60 text-lg max-w-xl mx-auto"
                        >
                            Get 5 years of unrestricted access to the OdooX AI Gateway. No recurring bills, no surprises.
                        </motion.p>
                    </div>

                    {/* Status Messages */}
                    {paymentStatus === 'success' && (
                        <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="flex items-center gap-3 px-6 py-4 bg-primary-container/10 border border-primary-container/30 text-primary-container rounded-lg font-medium shadow-[0_0_20px_rgba(132,204,22,0.15)]">
                            <Check className="w-5 h-5" /> Payment successful! Redirecting...
                        </motion.div>
                    )}
                    {paymentStatus === 'error' && (
                        <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="flex items-center gap-3 px-6 py-4 bg-red-500/10 border border-red-500/30 text-red-400 rounded-lg font-medium">
                            <Shield className="w-5 h-5" /> {errorMessage}
                        </motion.div>
                    )}

                    {/* Pricing Card */}
                    <motion.div
                        initial={{ opacity: 0, y: 24 }}
                        animate={{ opacity: 1, y: 0 }}
                        whileHover={{ y: -5 }}
                        transition={{ duration: 0.5, ease }}
                        className="w-full max-w-lg bg-[#050505]/90 backdrop-blur-2xl border border-primary-container/40 rounded-3xl relative shadow-[0_0_50px_rgba(132,204,22,0.15)] hover:shadow-[0_0_80px_rgba(132,204,22,0.25)] hover:border-primary-container/70 transition-all duration-500 group"
                    >
                        {/* Inner wrapper for overflow hidden backgrounds */}
                        <div className="absolute inset-0 rounded-3xl overflow-hidden pointer-events-none">
                            {/* Card Background Glows */}
                            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-primary-container to-transparent opacity-80" />
                            <div className="absolute top-[-20%] left-[-10%] w-[60%] h-[60%] bg-primary-container/10 blur-[80px] pointer-events-none group-hover:bg-primary-container/20 transition-all duration-500" />
                        </div>
                        
                        {/* Badge outside overflow-hidden */}
                        <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-gradient-to-r from-primary-container to-primary text-black text-[10px] sm:text-xs font-bold uppercase tracking-[0.2em] py-1.5 px-6 rounded-full shadow-[0_0_20px_rgba(132,204,22,0.6)] border border-white/20 z-10">
                            Early Adopter
                        </div>

                        {/* Content container */}
                        <div className="p-8 md:p-10 relative z-10">
                            <div className="mb-8 relative z-10">
                                <h3 className="text-2xl font-bold text-white mb-3 tracking-tight">Lifetime Pro Access</h3>
                                <p className="text-white/60 text-sm leading-relaxed">Everything you need to seamlessly connect Claude to your Odoo ERP and automate your workflows.</p>
                            </div>

                        <div className="bg-gradient-to-b from-white/[0.08] to-white/[0.02] border border-white/10 rounded-2xl p-8 mb-8 flex flex-col items-center relative shadow-[inset_0_1px_0_rgba(255,255,255,0.1)] z-10 backdrop-blur-md">
                            <div className="flex items-baseline gap-1 text-white">
                                <span className="text-3xl font-semibold text-primary-container/80 translate-y-[-8px]">₹</span>
                                <span className="text-6xl font-extrabold tracking-tighter drop-shadow-md">
                                    {singlePrice === null ? '...' : singlePrice.toLocaleString()}
                                </span>
                            </div>
                            <div className="text-primary-container/80 text-sm mt-4 font-semibold tracking-wide uppercase">One-time payment · 5 Years of Access</div>
                        </div>

                        {/* CTA Button */}
                        {isCheckingAuth ? (
                            <button className="w-full bg-white/10 text-white/40 py-4 rounded-xl font-semibold flex justify-center cursor-not-allowed border border-white/5">
                                <div className="w-5 h-5 border-2 border-white/20 border-t-white/80 rounded-full animate-spin"></div>
                            </button>
                        ) : !isAuthenticated ? (
                            <button 
                                onClick={() => router.push('/login')}
                                className="w-full bg-white/5 text-white border border-white/20 hover:bg-white/10 py-4 rounded-xl font-semibold transition-all shadow-lg"
                            >
                                Login to Continue
                            </button>
                        ) : (
                            <button 
                                onClick={() => singlePrice !== null && handlePayment(singlePrice, 'OdooX Pro - Single User')}
                                disabled={isLoading || isCheckingAuth || singlePrice === null}
                                className="w-full bg-gradient-to-r from-primary-container to-primary text-black hover:opacity-90 py-4 rounded-xl font-bold transition-all shadow-[0_0_20px_rgba(132,204,22,0.3)] glow-button disabled:opacity-50 flex justify-center items-center gap-2"
                            >
                                {isLoading && selectedPlanPrice === singlePrice ? (
                                    <>
                                        <div className="w-5 h-5 border-2 border-black/20 border-t-black rounded-full animate-spin"></div>
                                        Processing...
                                    </>
                                ) : (
                                    `Unlock Lifetime Access`
                                )}
                            </button>
                        )}

                        {/* Features List */}
                        <div className="mt-8">
                            <div className="flex items-center gap-4 mb-6">
                                <div className="flex-1 h-px bg-white/10"></div>
                                <span className="text-white/40 text-xs font-semibold uppercase tracking-widest">Included</span>
                                <div className="flex-1 h-px bg-white/10"></div>
                            </div>
                            
                            <ul className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-left">
                                {[
                                    'Unlimited Claude MCP Queries',
                                    'Connect 1 Production Database',
                                    'All 13+ Odoo Modules Supported',
                                    'End-to-End Encrypted Secure Tunnel',
                                    'Free Future Gateway Updates',
                                    'Priority Community Support'
                                ].map((feature) => (
                                    <li key={feature} className="flex items-center gap-3 text-white/70 text-sm font-medium">
                                        <div className="w-5 h-5 rounded-full bg-primary-container/20 flex items-center justify-center flex-shrink-0">
                                            <Check className="w-3 h-3 text-primary-container" />
                                        </div>
                                        {feature}
                                    </li>
                                ))}
                            </ul>
                        </div>
                        </div>
                    </motion.div>

                    {/* Trust Indicators */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ duration: 0.6, delay: 0.6, ease }}
                        className="flex flex-wrap items-center justify-center gap-8 pt-4 text-white/40 text-sm font-medium"
                    >
                        <div className="flex items-center gap-2">
                            <Shield className="w-4 h-4" /> Secure Payment via Razorpay
                        </div>
                        <div className="flex items-center gap-2">
                            <div className="w-2 h-2 rounded-full bg-primary-container"></div> Instant Activation
                        </div>
                    </motion.div>

                </div>
            </motion.div>
        </div>
    );
}
