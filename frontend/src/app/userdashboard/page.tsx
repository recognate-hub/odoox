"use client";

import React, { useState, useEffect } from 'react';
import Link from "next/link";
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { LayoutDashboard, LogOut, Plus, Key, Copy, Eye, EyeOff, AlertCircle, Shield, KeyRound, Server } from 'lucide-react';
import { toast } from 'sonner';
import WorkspaceCard, { Workspace } from '@/components/WorkspaceCard';

export default function UserDashboard() {
    const router = useRouter();

    const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
    const [limit, setLimit] = useState(1);
    const [planType, setPlanType] = useState('single');
    const [token, setToken] = useState('');
    const [isLoading, setIsLoading] = useState(true);
    
    // API Key State
    const [apiKey, setApiKey] = useState("");
    const [isGeneratingKey, setIsGeneratingKey] = useState(false);
    const [showApiKey, setShowApiKey] = useState(false);
    const [isRevokingKey, setIsRevokingKey] = useState(false);
    
    // Frontend URL for SSE
    const [frontendUrl, setFrontendUrl] = useState("");

    const fetchWorkspaces = React.useCallback(async () => {
        try {
            const res = await fetch('/api/workspace');
            if (res.status === 401) {
                await fetch('/api/logout', { method: 'POST' });
                router.push('/login?next=/userdashboard');
                return;
            }
            const data = await res.json();
            if (data.status === 'success') {
                setWorkspaces(data.workspaces || []);
                setLimit(data.limit || 1);
                setPlanType(data.plan_type || 'single');
                setToken(data.token);
            }
        } catch (err) {
            console.error("Failed to load workspace", err);
            toast.error("Failed to load workspace data.");
        } finally {
            setIsLoading(false);
        }
    }, [router]);

    useEffect(() => {
        if (typeof window !== 'undefined') {
            setFrontendUrl(window.location.origin);
        }
        const storedApiKey = localStorage.getItem('workspace_api_key');
        if (storedApiKey) {
            setApiKey(storedApiKey);
        }
        fetchWorkspaces();
    }, [fetchWorkspaces]);

    const handleAddWorkspace = () => {
        if (workspaces.length >= limit) {
            toast.error(`Plan limit reached. Your ${planType} plan allows up to ${limit} connected database(s).`);
            return;
        }
        setWorkspaces([...workspaces, {
            odoo_url: '',
            odoo_db: '',
            odoo_username: '',
            odoo_password: ''
        }]);
    };

    const handleChange = (index: number, field: keyof Workspace, value: string) => {
        const newWorkspaces = [...workspaces];
        newWorkspaces[index] = { ...newWorkspaces[index], [field]: value };
        setWorkspaces(newWorkspaces);
    };

    const handleSave = async (index: number) => {
        const ws = workspaces[index];
        const formData = new URLSearchParams();
        if (ws.id) formData.append('workspace_id', ws.id.toString());
        formData.append('odoo_url', ws.odoo_url);
        formData.append('odoo_db', ws.odoo_db);
        formData.append('odoo_username', ws.odoo_username);
        formData.append('odoo_password', ws.odoo_password || (ws.has_password ? '********' : ''));

        try {
            const res = await fetch('/api/workspace/save', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: formData.toString()
            });
            const data = await res.json();
            
            if (data.status === 'success') {
                toast.success("Workspace saved successfully!");
                setApiKey("");
                localStorage.removeItem('workspace_api_key');
                fetchWorkspaces(); // Refresh to get proper ID and URL
            } else {
                toast.error("Error: " + data.message);
            }
        } catch (err) {
            toast.error("Connection failed.");
        }
    };

    const handleDelete = async (index: number) => {
        const ws = workspaces[index];
        if (!ws.id) {
            // Just remove from local state if not saved yet
            const newWorkspaces = [...workspaces];
            newWorkspaces.splice(index, 1);
            setWorkspaces(newWorkspaces);
            return;
        }

        if (!confirm("Are you sure you want to delete this workspace?")) return;

        try {
            const res = await fetch('/api/workspace/delete', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ workspace_id: ws.id })
            });
            const data = await res.json();
            
            if (data.status === 'success') {
                toast.success("Workspace deleted.");
                setApiKey("");
                localStorage.removeItem('workspace_api_key');
                fetchWorkspaces();
            } else {
                toast.error("Error: " + data.message);
            }
        } catch (err) {
            toast.error("Deletion failed.");
        }
    };

    const handleLogout = async (e: React.MouseEvent) => {
        e.preventDefault();
        try {
            localStorage.removeItem('workspace_api_key');
            await fetch('/api/logout', { method: 'POST' });
        } catch (err) {
            console.error("Logout error", err);
        } finally {
            router.push('/login');
        }
    };

    const handleGenerateApiKey = async () => {
        setIsGeneratingKey(true);
        try {
            const res = await fetch('/api/workspace/api-key');
            const data = await res.json();
            if (res.ok && data.api_key) {
                setApiKey(data.api_key);
                localStorage.setItem('workspace_api_key', data.api_key);
                toast.success("API Key generated successfully.");
            } else {
                toast.error("Failed to generate API key: " + (data.detail || data.message || "Unknown error"));
            }
        } catch (e) {
            toast.error("Error generating API key.");
        } finally {
            setIsGeneratingKey(false);
        }
    };

    const handleRevokeApiKey = async () => {
        if (!apiKey) return;
        if (!confirm("Are you sure you want to revoke this API key? Any applications using it will lose access immediately.")) return;
        
        setIsRevokingKey(true);
        try {
            const formData = new URLSearchParams();
            formData.append('api_key', apiKey);
            
            const res = await fetch('/api/workspace/api-key/revoke', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: formData.toString()
            });
            
            if (res.ok) {
                setApiKey("");
                localStorage.removeItem('workspace_api_key');
                toast.success("API Key revoked successfully.");
            } else {
                toast.error("Failed to revoke API key.");
            }
        } catch (e) {
            toast.error("Error revoking API key.");
        } finally {
            setIsRevokingKey(false);
        }
    };

    const copyToClipboard = (text: string, message: string) => {
        navigator.clipboard.writeText(text);
        toast.success(message);
    };

    if (isLoading) {
        return (
            <div className="min-h-screen bg-[#0A0A0A] flex items-center justify-center">
                <div className="flex flex-col items-center gap-6">
                    <div className="w-16 h-16 border-4 border-white/10 border-t-primary-container rounded-full animate-spin" />
                    <p className="text-on-surface-variant font-medium animate-pulse">Initializing Secure Gateway...</p>
                </div>
            </div>
        );
    }

    const claudeConfigString = `{
  "mcpServers": {
    "odoox-cloud": {
      "command": "npx",
      "args": [
        "-y",
        "odoox-mcp-connector",
        "--url",
        "${frontendUrl}/sse?token=${apiKey}"
      ]
    }
  }
}`;

    return (
        <div className="min-h-screen bg-[#0A0A0A] text-white selection:bg-primary-container/30">
            {/* Background Effects */}
            <div className="fixed inset-0 z-0 bg-grid-pattern opacity-30 pointer-events-none" />
            <div className="fixed top-[-20%] left-[-10%] w-[50%] h-[50%] rounded-full bg-primary-container/5 blur-[120px] z-0 pointer-events-none" />
            
            <div className="flex flex-col md:flex-row min-h-screen relative z-10">
                {/* Sidebar */}
                <aside className="w-full md:w-72 bg-black/50 backdrop-blur-2xl border-b md:border-b-0 md:border-r border-white/10 flex flex-col shrink-0 sticky top-0 md:h-screen z-20">
                    <div className="p-8 pb-4">
                        <Link href="/" className="flex items-center gap-3 group">
                            <img src="/logo.png" alt="OdooX Logo" className="h-8 w-auto object-contain transition-transform group-hover:scale-105" />
                        </Link>
                        <div className="mt-2 text-[10px] font-bold text-primary-container uppercase tracking-[0.2em]">Workspace</div>
                    </div>
                    
                    <nav className="px-4 flex-1 mt-4">
                        <Link href="/userdashboard" className="flex items-center gap-3 px-4 py-3 rounded-xl bg-primary-container text-black font-semibold shadow-[0_0_20px_rgba(132,204,22,0.2)]">
                            <LayoutDashboard className="w-5 h-5" /> Integration
                        </Link>
                    </nav>
                    
                    <div className="p-6 mt-auto">
                        <div className="p-4 rounded-xl bg-white/5 border border-white/10 mb-4">
                            <div className="text-xs text-on-surface-variant mb-1">Current Plan</div>
                            <div className="font-semibold text-white capitalize flex items-center justify-between">
                                {planType}
                                <span className="text-xs bg-white/10 px-2 py-0.5 rounded-full">{workspaces.length} / {limit} DBs</span>
                            </div>
                        </div>
                        
                        <button 
                            onClick={handleLogout} 
                            className="flex items-center gap-3 px-4 py-3 w-full rounded-xl text-error hover:bg-error/10 transition-colors font-medium"
                        >
                            <LogOut className="w-5 h-5" /> Log Out
                        </button>
                    </div>
                </aside>
                
                {/* Main Content */}
                <main className="flex-1 p-6 md:p-12 overflow-y-auto w-full">
                    <div className="max-w-4xl mx-auto space-y-12">
                        
                        <header className="flex flex-col md:flex-row md:items-end justify-between gap-6 animate-fade-in-up">
                            <div>
                                <h1 className="text-4xl md:text-5xl font-bold tracking-tight mb-3">Odoo Gateway</h1>
                                <p className="text-on-surface-variant text-lg">Configure your secure connections to enable the Claude MCP endpoint.</p>
                            </div>
                            <button 
                                className="flex items-center gap-2 px-6 py-3 bg-white text-black font-bold rounded-xl hover:bg-gray-200 transition-all hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed shrink-0"
                                onClick={handleAddWorkspace}
                                disabled={workspaces.length >= limit}
                            >
                                <Plus className="w-5 h-5" /> Connect Database
                            </button>
                        </header>
                        
                        <div className="space-y-8">
                            {workspaces.length === 0 && (
                                <motion.div 
                                    initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
                                    className="p-12 border border-dashed border-white/20 rounded-3xl bg-white/5 backdrop-blur-sm text-center"
                                >
                                    <div className="w-16 h-16 bg-white/5 border border-white/10 rounded-2xl flex items-center justify-center mx-auto mb-6">
                                        <Server className="w-8 h-8 text-on-surface-variant" />
                                    </div>
                                    <h3 className="text-xl font-semibold mb-2">No Databases Connected</h3>
                                    <p className="text-on-surface-variant mb-6">Add your first Odoo ERP database to start generating secure AI endpoints.</p>
                                    <button className="px-6 py-3 border border-white/20 bg-white/5 hover:bg-white/10 rounded-xl font-medium transition-colors" onClick={handleAddWorkspace}>
                                        Add your first Odoo Database
                                    </button>
                                </motion.div>
                            )}

                            <div className="space-y-6">
                                {workspaces.map((ws, index) => (
                                    <WorkspaceCard 
                                        key={ws.id || `new-${index}`}
                                        workspace={ws}
                                        index={index}
                                        token={token}
                                        onChange={handleChange}
                                        onSave={handleSave}
                                        onDelete={handleDelete}
                                    />
                                ))}
                            </div>

                            {/* API Key Section */}
                            <AnimatePresence>
                                {workspaces.length > 0 && (
                                    <motion.div 
                                        initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
                                        className="rounded-3xl border border-white/10 bg-black/40 backdrop-blur-2xl p-8 relative overflow-hidden group mt-12"
                                    >
                                        <div className="absolute top-0 right-0 w-64 h-64 bg-primary-container/5 rounded-full blur-[100px] pointer-events-none" />
                                        
                                        <div className="flex items-center gap-4 mb-8">
                                            <div className="p-3 bg-primary-container/10 border border-primary-container/20 rounded-xl">
                                                <KeyRound className="w-6 h-6 text-primary-container" />
                                            </div>
                                            <div>
                                                <h3 className="text-2xl font-bold tracking-tight">API Integration</h3>
                                                <p className="text-on-surface-variant">Generate a permanent API Key for Claude Desktop or custom agents.</p>
                                            </div>
                                        </div>
                                        
                                        {!apiKey ? (
                                            <div className="p-8 border border-white/10 bg-white/5 rounded-2xl text-center">
                                                <Shield className="w-10 h-10 text-on-surface-variant mx-auto mb-4" />
                                                <h4 className="text-lg font-semibold mb-2">Secure API Access</h4>
                                                <p className="text-sm text-on-surface-variant mb-6 max-w-md mx-auto">Generate a cryptographic key to securely connect external LLMs to your verified Odoo databases.</p>
                                                <button 
                                                    className="px-6 py-3 bg-primary-container text-black font-bold rounded-xl hover:bg-primary-fixed transition-all hover:shadow-[0_0_20px_rgba(132,204,22,0.4)] disabled:opacity-50"
                                                    onClick={handleGenerateApiKey}
                                                    disabled={isGeneratingKey}
                                                >
                                                    {isGeneratingKey ? "Generating Key..." : "Generate Permanent API Key"}
                                                </button>
                                            </div>
                                        ) : (
                                            <div className="space-y-8">
                                                {/* Raw API Key */}
                                                <div className="space-y-2">
                                                    <label className="text-xs font-semibold text-on-surface-variant uppercase tracking-wider">Secret API Key</label>
                                                    <div className="flex flex-col sm:flex-row gap-3">
                                                        <div className="relative flex-1 group/input">
                                                            <input 
                                                                type={showApiKey ? "text" : "password"}
                                                                value={apiKey}
                                                                readOnly 
                                                                className="w-full bg-black/60 border border-white/10 rounded-xl pl-4 pr-12 py-3.5 text-sm text-primary-container font-mono focus:outline-none"
                                                            />
                                                            <button 
                                                                className="absolute right-3 top-1/2 -translate-y-1/2 p-1.5 text-on-surface-variant hover:text-white rounded-md transition-colors"
                                                                onClick={() => setShowApiKey(!showApiKey)}
                                                            >
                                                                {showApiKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                                                            </button>
                                                        </div>
                                                        <button 
                                                            className="px-5 py-3 sm:py-0 bg-white/10 hover:bg-white/20 text-white font-medium rounded-xl transition-colors flex items-center justify-center gap-2 shrink-0"
                                                            onClick={() => copyToClipboard(apiKey, "API Key copied!")}
                                                        >
                                                            <Copy className="w-4 h-4" /> Copy
                                                        </button>
                                                    </div>
                                                </div>

                                                {/* Claude Custom Connector URL */}
                                                <div className="space-y-2">
                                                    <label className="text-xs font-semibold text-on-surface-variant uppercase tracking-wider">Claude Web Endpoint</label>
                                                    <p className="text-sm text-on-surface-variant mb-2">Paste this into the <strong>Remote MCP server URL</strong> field in Claude Web (requires HTTPS).</p>
                                                    <div className="flex flex-col sm:flex-row gap-3">
                                                        <input 
                                                            type="text" 
                                                            value={`${frontendUrl}/sse?token=${apiKey}`}
                                                            readOnly 
                                                            className="flex-1 bg-black/60 border border-white/10 rounded-xl px-4 py-3.5 text-sm text-primary-container font-mono focus:outline-none select-all"
                                                        />
                                                        <button 
                                                            className="px-5 py-3 sm:py-0 bg-white/10 hover:bg-white/20 text-white font-medium rounded-xl transition-colors flex items-center justify-center gap-2 shrink-0"
                                                            onClick={() => copyToClipboard(`${frontendUrl}/sse?token=${apiKey}`, "URL copied!")}
                                                        >
                                                            <Copy className="w-4 h-4" /> Copy
                                                        </button>
                                                    </div>
                                                </div>

                                                {/* Claude Desktop Config */}
                                                <div className="space-y-2">
                                                    <label className="text-xs font-semibold text-on-surface-variant uppercase tracking-wider">Claude Desktop Configuration</label>
                                                    <p className="text-sm text-on-surface-variant mb-2">For local Claude Desktop app usage (bypasses HTTPS requirements).</p>
                                                    <div className="relative">
                                                        <textarea 
                                                            value={claudeConfigString}
                                                            readOnly 
                                                            className="w-full bg-[#0A0A0A] border border-white/10 rounded-xl p-5 text-sm text-primary-container font-mono focus:outline-none min-h-[200px] resize-none"
                                                        />
                                                        <button 
                                                            className="absolute top-4 right-4 px-4 py-2 bg-white/10 hover:bg-white/20 text-white text-xs font-medium rounded-lg transition-colors flex items-center gap-2"
                                                            onClick={() => copyToClipboard(claudeConfigString, "Configuration copied!")}
                                                        >
                                                            <Copy className="w-4 h-4" /> Copy Config
                                                        </button>
                                                    </div>
                                                </div>

                                                <div className="pt-4 border-t border-white/10">
                                                    <button 
                                                        className="px-6 py-2.5 text-sm font-semibold text-error border border-error/30 hover:bg-error/10 rounded-xl transition-colors flex items-center gap-2"
                                                        onClick={handleRevokeApiKey}
                                                        disabled={isRevokingKey}
                                                    >
                                                        <AlertCircle className="w-4 h-4" /> {isRevokingKey ? "Revoking..." : "Revoke Key"}
                                                    </button>
                                                </div>
                                            </div>
                                        )}
                                    </motion.div>
                                )}
                            </AnimatePresence>
                        </div>
                    </div>
                </main>
            </div>
        </div>
    );
}
