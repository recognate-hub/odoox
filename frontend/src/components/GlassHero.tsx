'use client';

import React, { useRef, useEffect } from 'react';
import { motion, useAnimation, useInView } from 'framer-motion';
import Link from 'next/link';
import { ArrowRight, BookOpen, Sparkles } from 'lucide-react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Float, Environment } from '@react-three/drei';
import * as THREE from 'three';

const ease = [0.25, 0.4, 0, 1] as const;

interface GlassHeroProps {
  hasToken: boolean;
  isPaid: boolean;
}

// 3D Background Objects
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

export function GlassHero({ hasToken, isPaid }: GlassHeroProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  
  return (
    <div ref={containerRef} className="relative w-full flex items-center justify-center pt-32 pb-16 px-4 overflow-hidden selection:bg-primary-container/30">
      
      {/* 3D Canvas */}
      <div className="absolute inset-0 z-0 opacity-80 mix-blend-screen pointer-events-none">
        <Canvas camera={{ position: [0, 0, 10], fov: 45 }} dpr={[1, 2]}>
          <BackgroundShapes />
        </Canvas>
      </div>

      <motion.div 
        transition={{ type: 'spring', stiffness: 200, damping: 20 }}
        initial={{ opacity: 0, scale: 0.95, y: 30 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        className="relative z-10 w-[95%] max-w-7xl rounded-[2rem] shadow-[0_40px_100px_-20px_rgba(0,0,0,1)] overflow-hidden mt-16 group"
      >
        {/* Dynamic Inner Glow that tracks mouse (simplified with CSS for performance) */}
        <div className="absolute inset-0 bg-gradient-to-br from-white/10 via-transparent to-primary-container/5 z-0 pointer-events-none" />

        <div className="absolute inset-0 z-[-1] rounded-[2rem] border border-white/10 bg-black/40 backdrop-blur-3xl shadow-[inset_0_1px_1px_rgba(255,255,255,0.1)]">
          <div className="absolute inset-0 opacity-[0.02] bg-[url('/noise.png')] mix-blend-overlay"></div>
        </div>

        {/* Mac-style Window Bar */}
        <div className="h-12 w-full bg-white/[0.02] border-b border-white/[0.05] flex items-center px-6 gap-2">
          <div className="flex gap-2">
            <div className="w-3 h-3 rounded-full bg-[#FF5F56] border border-[#E0443E]"></div>
            <div className="w-3 h-3 rounded-full bg-[#FFBD2E] border border-[#DEA123]"></div>
            <div className="w-3 h-3 rounded-full bg-[#27C93F] border border-[#1AAB29]"></div>
          </div>
          <div className="mx-auto flex items-center gap-2 px-4 py-1 rounded-full bg-white/5 border border-white/5 shadow-inner">
            <Sparkles className="w-3 h-3 text-primary-container" />
            <span className="text-[10px] font-semibold text-white/50 uppercase tracking-widest font-mono">OdooX Terminal</span>
          </div>
        </div>

        {/* Hero Content Area */}
        <div className="p-10 md:p-24 flex flex-col items-center text-center space-y-10 relative z-10">
          
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            transition={{ duration: 0.6, delay: 0.2, ease }}
            className="inline-flex items-center gap-3 px-5 py-2 rounded-full border border-primary-container/30 bg-primary-container/10 backdrop-blur-md shadow-[0_0_30px_rgba(132,204,22,0.15)] group-hover:border-primary-container/50 transition-colors"
          >
            <span className="relative flex h-2.5 w-2.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary-container opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-primary-fixed"></span>
            </span>
            <span className="text-primary-container text-sm font-semibold tracking-wide">v2.0 Live • 12 Odoo Modules Supported</span>
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.35, ease }}
            className="text-4xl sm:text-5xl md:text-7xl lg:text-[5rem] font-bold tracking-tighter leading-[1.1] max-w-5xl text-white font-sans"
          >
            Give Claude <br className="hidden md:block" />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary-container via-[#D9F99D] to-white relative">
              Full Access to Odoo
              <div className="absolute -bottom-2 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-primary-container to-transparent opacity-50 blur-[2px]" />
            </span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.5, ease }}
            className="text-on-surface-variant text-lg md:text-xl max-w-2xl font-medium leading-relaxed"
          >
            A secure MCP gateway connecting AI directly to your ERP via XML-RPC. Read leads, manage inventory, and query finances—through natural conversation.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.65, ease }}
            className="flex flex-col sm:flex-row gap-4 pt-6 w-full sm:w-auto"
          >
            <Link
              href={hasToken ? (isPaid ? "/userdashboard" : "/payment") : "/login"}
              className="group relative inline-flex items-center justify-center gap-2 bg-primary-container text-black px-8 py-4 rounded-xl font-bold hover:bg-primary-fixed transition-all hover:scale-105 active:scale-95 shadow-[0_0_40px_rgba(132,204,22,0.3)] overflow-hidden"
            >
              <div className="absolute inset-0 flex h-full w-full justify-center [transform:skew(-12deg)_translateX(-100%)] group-hover:duration-1000 group-hover:[transform:skew(-12deg)_translateX(100%)]">
                <div className="relative h-full w-8 bg-white/20" />
              </div>
              Connect Workspace <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </Link>
            
            <Link
              href="#platform"
              className="inline-flex items-center justify-center gap-2 px-8 py-4 rounded-xl font-semibold border border-white/10 text-white bg-white/5 hover:bg-white/10 hover:border-white/20 transition-all active:scale-95 backdrop-blur-sm"
            >
              <BookOpen className="w-5 h-5 text-on-surface-variant" /> See How It Works
            </Link>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.8, ease }}
            className="flex flex-wrap justify-center gap-4 pt-12 border-t border-white/5 w-full max-w-3xl"
          >
            {[
              { label: 'MCP Tools', value: '70+' },
              { label: 'Modules', value: '12' },
              { label: 'Odoo Support', value: 'v12–v18' },
              { label: 'Avg Latency', value: '<50ms' },
            ].map((stat, i) => (
              <motion.div 
                key={stat.label} 
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.9 + (i * 0.1) }}
                className="flex items-center gap-3 px-5 py-2.5 rounded-xl border border-white/5 bg-white/5 backdrop-blur-md"
              >
                <span className="text-white font-bold text-lg">{stat.value}</span>
                <span className="text-on-surface-variant text-sm font-medium">{stat.label}</span>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </motion.div>
    </div>
  );
}
