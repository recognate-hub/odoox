'use client';

import React, { useRef } from 'react';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { ArrowRight, BookOpen } from 'lucide-react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Float, Environment, MeshTransmissionMaterial } from '@react-three/drei';
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

  // Material for the chrome/metallic look
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

      {/* Main floating knot */}
      <Float speed={1.5} rotationIntensity={0.5} floatIntensity={1}>
        <mesh ref={knotRef} position={[0, 0, -2]} scale={1.5}>
          <torusKnotGeometry args={[1, 0.4, 200, 32]} />
          <meshStandardMaterial {...materialProps} />
        </mesh>
      </Float>

      {/* Accompanying spheres */}
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
  return (
    <div className="relative w-full min-h-[100vh] flex items-center justify-center py-24 px-4 overflow-hidden bg-black mt-[-80px]">
      
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
        className="relative z-10 w-[95%] max-w-7xl rounded-2xl shadow-[0_30px_60px_rgba(0,0,0,0.6)] overflow-hidden mt-16"
      >
        {/* Clean Glass Background Layer */}
        <div 
          className="absolute inset-0 z-[-1] rounded-2xl border border-white/10 bg-black/40"
          style={{ 
            backdropFilter: 'blur(30px)', 
            WebkitBackdropFilter: 'blur(30px)',
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
          <div className="mx-auto text-[10px] font-code-sm text-white/40 uppercase tracking-widest pl-6">OdooX Gateway</div>
        </div>

        {/* Content Area */}
        <div className="p-10 md:p-24 flex flex-col items-center text-center space-y-10 bg-gradient-to-b from-white/[0.02] to-transparent">
          
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2, ease }}
            className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-primary-container/30 bg-primary-container/10 text-primary-container text-sm font-medium shadow-[0_0_20px_rgba(132,204,22,0.15)]"
          >
            <span className="w-2 h-2 rounded-full bg-primary-container animate-pulse"></span>
            Now live — 13 Odoo modules supported natively
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.35, ease }}
            className="font-display-lg text-display-lg md:text-6xl lg:text-7xl leading-tight max-w-4xl text-white"
          >
            Give Claude <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary-container to-white glow-text">
              full access to Odoo
            </span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.5, ease }}
            className="text-white/70 text-lg max-w-2xl font-light"
          >
            OdooX is a secure MCP gateway that connects Claude directly to your Odoo ERP over XML-RPC.
            Read leads, create invoices, check inventory, manage manufacturing — all through natural conversation.
            No custom modules. No code changes. Just connect and go.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.65, ease }}
            className="flex flex-col sm:flex-row gap-stack-md pt-6"
          >
            <Link
              className="bg-gradient-to-r from-primary-container to-primary text-black px-8 py-4 rounded-lg font-semibold flex items-center justify-center gap-2 hover:opacity-90 glow-button shadow-[0_0_30px_rgba(132,204,22,0.25)]"
              href={hasToken ? (isPaid ? "/userdashboard" : "/payment") : "/login"}
            >
              Connect Your Odoo <ArrowRight className="w-5 h-5" />
            </Link>
            <Link
              className="px-8 py-4 rounded-lg font-semibold flex items-center justify-center gap-2 border border-white/10 text-white hover:border-primary-container/50 hover:bg-white/5 transition-all"
              href="#platform"
            >
              <BookOpen className="w-5 h-5" /> See How It Works
            </Link>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.8, ease }}
            className="flex flex-wrap justify-center gap-4 pt-8"
          >
            {[
              { label: 'MCP Tools', value: '40+' },
              { label: 'Modules', value: '13' },
              { label: 'Odoo Versions', value: 'v12–v17' },
              { label: 'Avg Latency', value: '<50ms' },
            ].map((stat) => (
              <div key={stat.label} className="flex items-center gap-2 px-4 py-2 rounded-full border border-white/10 bg-white/5 text-sm backdrop-blur-md">
                <span className="text-white font-semibold">{stat.value}</span>
                <span className="text-white/60">{stat.label}</span>
              </div>
            ))}
          </motion.div>
        </div>
      </motion.div>
    </div>
  );
}
