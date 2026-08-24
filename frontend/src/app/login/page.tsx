"use client";

import React, { useEffect, useRef, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import Image from 'next/image';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowRight, Mail, ShieldAlert, ArrowLeft, Loader2 } from 'lucide-react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Float, Environment } from '@react-three/drei';
import * as THREE from 'three';

// --- 3D BACKGROUND (Identical to Hero) ---
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

// --- MAIN LOGIN PAGE ---
export default function LoginPage() {
    const [step, setStep] = useState(1);
    const [email, setEmail] = useState('');
    const [code, setCode] = useState(['', '', '', '', '', '']);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [checkingSession, setCheckingSession] = useState(true);
    
    const router = useRouter();
    const inputRefs = useRef<(HTMLInputElement | null)[]>([]);

    useEffect(() => {
        const checkExistingSession = async () => {
            try {
                const res = await fetch('/api/auth/me');
                if (res.ok) {
                    const isPaid = document.cookie.includes('is_paid=true');
                    window.location.href = isPaid ? '/userdashboard' : '/payment';
                    return;
                }
            } catch {}
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
        } catch (err) {
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
                const searchParams = new URLSearchParams(window.location.search);
                const nextUrl = searchParams.get('next');
                window.location.href = nextUrl || data.redirect || '/payment';
            } else if (data.status === 'conflict') {
                setStep(3);
            } else {
                setError(data.message || "Invalid code.");
            }
        } catch (err) {
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
            const res = await fetch('/api/login/confirm-session', { method: 'POST' });
            const data = await res.json();
            if (data.status === 'success') {
                const searchParams = new URLSearchParams(window.location.search);
                const nextUrl = searchParams.get('next');
                window.location.href = nextUrl || data.redirect || '/payment';
            } else {
                setError(data.message || "Failed to override session.");
            }
        } catch (err) {
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

    if (checkingSession) return null;

    return (
        <div className="relative w-full min-h-screen flex items-center justify-center overflow-hidden bg-black font-body-md text-body-md selection:bg-primary-container selection:text-black">
            
            {/* 3D R3F Canvas Background */}
            <div className="absolute inset-0 z-0 opacity-60">
                <Canvas camera={{ position: [0, 0, 10], fov: 45 }} dpr={[1, 2]}>
                    <BackgroundShapes />
                </Canvas>
            </div>

            {/* Back to Home Link */}
            <Link 
              href="/" 
              className="absolute top-8 left-8 z-50 flex items-center gap-2 text-white/50 hover:text-white transition-colors text-sm font-medium"
            >
              <ArrowLeft className="w-4 h-4" /> Back to Home
            </Link>

            {/* Main Glass Login Card */}
            <motion.div 
                transition={{ type: 'spring', stiffness: 200, damping: 20 }}
                initial={{ opacity: 0, scale: 0.95, y: 30 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                className="relative z-10 w-full max-w-md mx-4 rounded-3xl shadow-[0_30px_60px_rgba(0,0,0,0.8)] overflow-hidden"
            >
                {/* Clean Glass Background Layer */}
                <div 
                    className="absolute inset-0 z-[-1] rounded-3xl border border-white/10 bg-black/40"
                    style={{ 
                        backdropFilter: 'blur(30px)', 
                        WebkitBackdropFilter: 'blur(30px)',
                        boxShadow: 'inset 0 0 0 1px rgba(255,255,255,0.05), inset 0 1px 0 rgba(255,255,255,0.2)'
                    }}
                >
                    <div className="absolute inset-0 opacity-[0.03] noise-bg mix-blend-overlay"></div>
                </div>

                {/* Content Area */}
                <div className="p-8 md:p-10 space-y-8 bg-gradient-to-b from-white/[0.02] to-transparent">
                    
                    {/* Header */}
                    <div className="flex flex-col items-center text-center space-y-4">
                        <Link href="/">
                            <Image 
                                src="/logo.png" 
                                alt="OdooX Logo" 
                                width={200} 
                                height={48} 
                                className="h-10 w-auto object-contain scale-[1.5]"
                                priority
                            />
                        </Link>
                        <h1 className="text-2xl font-bold text-white tracking-tight">Access your gateway</h1>
                    </div>

                    {/* Alerts */}
                    <AnimatePresence mode="wait">
                        {error && (
                            <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }} className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm text-center">
                                {error}
                            </motion.div>
                        )}
                        {success && (
                            <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }} className="p-3 rounded-lg bg-green-500/10 border border-green-500/20 text-green-400 text-sm text-center">
                                {success}
                            </motion.div>
                        )}
                    </AnimatePresence>

                    {/* Step 1: Request OTP */}
                    {step === 1 && (
                        <motion.form 
                            initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 20 }}
                            onSubmit={handleRequestOtp} 
                            className="space-y-6"
                        >
                            <div className="space-y-2">
                                <label htmlFor="email" className="text-sm font-semibold text-white/70">Work Email</label>
                                <div className="relative">
                                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                                        <Mail className="h-5 w-5 text-white/30" />
                                    </div>
                                    <input 
                                        type="email" 
                                        id="email" 
                                        className="w-full bg-black/50 border border-white/10 rounded-xl py-3 pl-12 pr-4 text-white placeholder-white/20 focus:outline-none focus:ring-2 focus:ring-primary-container focus:border-transparent transition-all" 
                                        required 
                                        placeholder="admin@company.com"
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                    />
                                </div>
                            </div>
                            
                            <button 
                                type="submit" 
                                disabled={isLoading}
                                className="w-full bg-gradient-to-r from-primary-container to-primary text-black font-bold py-3.5 rounded-xl flex items-center justify-center gap-2 hover:opacity-90 transition-opacity disabled:opacity-50"
                            >
                                {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : "Continue with Email"}
                            </button>
                        </motion.form>
                    )}

                    {/* Step 2: Verify OTP */}
                    {step === 2 && (
                        <motion.form 
                            initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }}
                            onSubmit={handleVerifyOtp} 
                            className="space-y-6"
                        >
                            <div className="space-y-4 text-center">
                                <label className="text-sm font-semibold text-white/70">
                                    Enter the 6-digit verification code
                                </label>
                                <div className="flex justify-between gap-2" onPaste={handlePaste}>
                                    {code.map((digit, idx) => (
                                        <motion.input
                                            key={idx}
                                            ref={(el) => { inputRefs.current[idx] = el; }}
                                            type="text"
                                            maxLength={1}
                                            className="w-12 h-14 bg-black/50 border border-white/10 rounded-xl text-center text-xl font-bold text-white focus:outline-none focus:ring-2 focus:ring-primary-container focus:border-transparent transition-colors"
                                            value={digit}
                                            onChange={(e) => handleCodeChange(idx, e.target.value)}
                                            onKeyDown={(e) => handleKeyDown(idx, e)}
                                            required
                                            whileFocus={{ scale: 1.1, y: -2 }}
                                            whileHover={{ scale: 1.05 }}
                                            transition={{ type: "spring", stiffness: 300, damping: 15 }}
                                        />
                                    ))}
                                </div>
                            </div>
                            
                            <button 
                                id="verify-btn" 
                                type="submit" 
                                disabled={isLoading}
                                className="w-full bg-gradient-to-r from-primary-container to-primary text-black font-bold py-3.5 rounded-xl flex items-center justify-center gap-2 hover:opacity-90 transition-opacity disabled:opacity-50"
                            >
                                {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : "Verify & Login"}
                            </button>

                            <div className="flex justify-center items-center gap-6 text-sm">
                                <button type="button" onClick={handleBack} className="text-white/50 hover:text-white transition-colors flex items-center gap-1">
                                    <ArrowLeft className="w-4 h-4" /> Back
                                </button>
                                <button type="button" onClick={handleRequestOtp} className="text-primary-container hover:text-primary transition-colors flex items-center gap-1">
                                    Resend Code
                                </button>
                            </div>
                        </motion.form>
                    )}

                    {/* Step 3: Force Logout */}
                    {step === 3 && (
                        <motion.div 
                            initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }}
                            className="space-y-6 text-center"
                        >
                            <div className="w-16 h-16 mx-auto bg-orange-500/10 border border-orange-500/20 rounded-full flex items-center justify-center">
                                <ShieldAlert className="w-8 h-8 text-orange-400" />
                            </div>
                            <div>
                                <h4 className="text-xl font-bold text-white mb-2">Active Session Detected</h4>
                                <p className="text-sm text-white/50">
                                    You are currently logged in on another device. For security reasons, you can only have one active session.
                                </p>
                            </div>
                            <div className="space-y-3">
                                <button 
                                    onClick={handleForceLogout}
                                    disabled={isLoading}
                                    className="w-full bg-orange-500 text-white font-bold py-3.5 rounded-xl flex items-center justify-center gap-2 hover:bg-orange-600 transition-colors disabled:opacity-50"
                                >
                                    {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : "Force Logout Other Device"}
                                </button>
                                <button 
                                    onClick={handleBack}
                                    disabled={isLoading}
                                    className="w-full bg-white/5 text-white font-bold py-3.5 rounded-xl flex items-center justify-center gap-2 hover:bg-white/10 transition-colors disabled:opacity-50 border border-white/10"
                                >
                                    Cancel
                                </button>
                            </div>
                        </motion.div>
                    )}

                    <div className="pt-6 border-t border-white/10 text-center">
                        <span className="text-xs text-white/30 tracking-wider uppercase font-semibold">Secure authentication</span>
                    </div>

                </div>
            </motion.div>
        </div>
    );
}
