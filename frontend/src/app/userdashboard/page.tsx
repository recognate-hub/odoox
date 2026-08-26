"use client";

import React, { useState, useEffect } from 'react';
import Link from "next/link";
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { 
    LayoutDashboard, LogOut, Plus, Key, Copy, Eye, EyeOff, 
    AlertCircle, Shield, KeyRound, Server, Terminal, Play, 
    Sparkles, CheckCircle2, Code2, Globe, Cpu
} from 'lucide-react';
import { toast } from 'sonner';
import WorkspaceCard, { Workspace } from '@/components/WorkspaceCard';

type ClientTab = 'claude-desktop' | 'cursor' | 'windsurf' | 'cline' | 'web' | 'python';

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
    
    // Tab State for Client Config
    const [activeClientTab, setActiveClientTab] = useState<ClientTab>('claude-desktop');

    // Live Playground State
    const [selectedTool, setSelectedTool] = useState('get_sales_dashboard');
    const [toolArgs, setToolArgs] = useState('{}');
    const [playgroundOutput, setPlaygroundOutput] = useState<any>(null);
    const [isPlaying, setIsPlaying] = useState(false);

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
                fetchWorkspaces();
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
            await fetch('/api/logout', { method: 'POST' });
            router.push('/login');
        } catch (e) {
            console.error("Logout failed", e);
        }
    };

    const handleGenerateApiKey = async () => {
        setIsGeneratingKey(true);
        try {
            const res = await fetch('/api/workspace/api-key', {
                method: 'POST'
            });
            const data = await res.json();
            if (data.status === 'success') {
                setApiKey(data.api_key);
                localStorage.setItem('workspace_api_key', data.api_key);
                toast.success("Permanent API Key generated successfully!");
            } else {
                toast.error(data.detail || "Failed to generate API Key.");
            }
        } catch (e) {
            toast.error("Error generating API key.");
        } finally {
            setIsGeneratingKey(false);
        }
    };

    const handleRevokeApiKey = async () => {
        if (!confirm("Are you sure you want to revoke this API Key? Any external LLM or Claude Desktop instance using it will immediately lose access.")) return;

        setIsRevokingKey(true);
        try {
            const res = await fetch('/api/workspace/api-key', {
                method: 'DELETE',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ api_key: apiKey })
            });
            const data = await res.json();
            if (data.status === 'success') {
                setApiKey("");
                localStorage.removeItem('workspace_api_key');
                toast.success("API Key has been revoked.");
            } else {
                toast.error(data.detail || "Failed to revoke API Key.");
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

    // Client Config Snippets
    const sseUrl = `${frontendUrl}/sse?token=${apiKey || 'YOUR_API_KEY'}`;

    const configSnippets: Record<ClientTab, { title: string; filename: string; code: string }> = {
        'claude-desktop': {
            title: "Claude Desktop",
            filename: "claude_desktop_config.json",
            code: JSON.stringify({
                mcpServers: {
                    "odoox": {
                        command: "npx",
                        args: ["-y", "odoox-mcp-connector", "--url", sseUrl]
                    }
                }
            }, null, 2)
        },
        'cursor': {
            title: "Cursor IDE",
            filename: ".cursor/mcp.json",
            code: JSON.stringify({
                mcpServers: {
                    "odoox": {
                        type: "command",
                        command: "npx",
                        args: ["-y", "odoox-mcp-connector", "--url", sseUrl]
                    }
                }
            }, null, 2)
        },
        'windsurf': {
            title: "Windsurf / Codeium",
            filename: "mcp_config.json",
            code: JSON.stringify({
                mcpServers: {
                    "odoox": {
                        command: "npx",
                        args: ["-y", "odoox-mcp-connector", "--url", sseUrl]
                    }
                }
            }, null, 2)
        },
        'cline': {
            title: "Cline / Roo-Code / VS Code",
            filename: "cline_mcp_settings.json",
            code: JSON.stringify({
                mcpServers: {
                    "odoox": {
                        command: "npx",
                        args: ["-y", "odoox-mcp-connector", "--url", sseUrl],
                        disabled: false,
                        autoApprove: []
                    }
                }
            }, null, 2)
        },
        'web': {
            title: "Claude Web (SSE Direct)",
            filename: "Remote SSE URL",
            code: sseUrl
        },
        'python': {
            title: "Python SDK (FastMCP / Direct)",
            filename: "agent.py",
            code: `import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client

async def main():
    async with sse_client("${sseUrl}") as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print(f"Connected to OdooX! {len(tools.tools)} ERP tools available.")

asyncio.run(main())`
        }
    };

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
                        <div className="mt-2 text-[10px] font-bold text-primary-container uppercase tracking-[0.2em]">Workspace & Integrations</div>
                    </div>
                    
                    <nav className="px-4 flex-1 mt-4 space-y-1">
                        <div className="flex items-center gap-3 px-4 py-3 rounded-xl bg-primary-container text-black font-semibold shadow-[0_0_20px_rgba(132,204,22,0.2)]">
                            <LayoutDashboard className="w-5 h-5" /> Integration Console
                        </div>
                        <Link href="/production-planning" className="flex items-center gap-3 px-4 py-3 rounded-xl text-on-surface-variant hover:text-white hover:bg-white/5 transition-colors font-medium">
                            <Cpu className="w-5 h-5" /> Production Planning
                        </Link>
                    </nav>
                    
                    <div className="p-6 mt-auto">
                        <div className="p-4 rounded-xl bg-white/5 border border-white/10 mb-4">
                            <div className="text-xs text-on-surface-variant mb-1">Active Plan</div>
                            <div className="font-semibold text-white capitalize flex items-center justify-between">
                                {planType}
                                <span className="text-xs bg-white/10 px-2 py-0.5 rounded-full">{workspaces.length} / {limit} DBs</span>
                            </div>
                        </div>
                        
                        <button 
                            onClick={handleLogout}
                            className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-on-surface-variant hover:text-white transition-colors text-sm font-medium"
                        >
                            <LogOut className="w-4 h-4" /> Sign Out
                        </button>
                    </div>
                </aside>

                {/* Main Content Area */}
                <main className="flex-1 p-6 md:p-12 overflow-y-auto">
                    <div className="max-w-5xl mx-auto space-y-10">
                        
                        {/* Header Banner */}
                        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-white/10 pb-8">
                            <div>
                                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-primary-container/30 bg-primary-container/10 text-primary-container text-xs font-semibold uppercase tracking-wider mb-3">
                                    <Sparkles className="w-3.5 h-3.5" /> World's Top 1 Odoo MCP Platform
                                </div>
                                <h1 className="text-3xl font-bold tracking-tight text-white">ERP Database & AI Bridge</h1>
                                <p className="text-on-surface-variant mt-1">Connect your verified Odoo instances to Claude Desktop, Cursor, and LLMs.</p>
                            </div>
                            
                            {workspaces.length < limit && (
                                <button 
                                    onClick={handleAddWorkspace}
                                    className="flex items-center gap-2 px-5 py-2.5 bg-primary-container hover:bg-primary-fixed text-black font-semibold rounded-xl transition-all shadow-[0_0_20px_rgba(132,204,22,0.3)] shrink-0 self-start sm:self-auto"
                                >
                                    <Plus className="w-4 h-4" /> Connect Database
                                </button>
                            )}
                        </div>

                        {/* Database Workspaces Grid */}
                        <div className="space-y-6">
                            <h2 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
                                <Server className="w-5 h-5 text-primary-container" /> Connected Databases
                            </h2>

                            {isLoading ? (
                                <div className="p-12 text-center text-on-surface-variant">Loading workspace configurations...</div>
                            ) : workspaces.length === 0 ? (
                                <div className="p-12 border border-dashed border-white/20 rounded-3xl bg-white/5 backdrop-blur-sm text-center">
                                    <Server className="w-10 h-10 text-on-surface-variant mx-auto mb-4" />
                                    <h3 className="text-lg font-semibold mb-2">No Databases Connected</h3>
                                    <p className="text-sm text-on-surface-variant mb-6">Add your first Odoo database to generate secure MCP endpoints.</p>
                                    <button className="px-6 py-3 bg-primary-container text-black font-bold rounded-xl hover:bg-primary-fixed transition-all" onClick={handleAddWorkspace}>
                                        Connect Odoo Database
                                    </button>
                                </div>
                            ) : (
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
                            )}
                        </div>

                        {/* Universal Client Integration Hub */}
                        {workspaces.length > 0 && (
                            <div className="rounded-3xl border border-white/10 bg-black/40 backdrop-blur-2xl p-8 relative overflow-hidden group">
                                <div className="absolute top-0 right-0 w-64 h-64 bg-primary-container/5 rounded-full blur-[100px] pointer-events-none" />
                                
                                <div className="flex items-center gap-4 mb-8">
                                    <div className="p-3 bg-primary-container/10 border border-primary-container/20 rounded-xl">
                                        <KeyRound className="w-6 h-6 text-primary-container" />
                                    </div>
                                    <div>
                                        <h2 className="text-2xl font-bold tracking-tight">Universal AI Client Exporter</h2>
                                        <p className="text-on-surface-variant text-sm">Generate 1-click configuration files for all major MCP clients.</p>
                                    </div>
                                </div>

                                {!apiKey ? (
                                    <div className="p-8 border border-white/10 bg-white/5 rounded-2xl text-center">
                                        <Shield className="w-10 h-10 text-on-surface-variant mx-auto mb-4" />
                                        <h3 className="text-lg font-semibold mb-2">Generate Permanent API Key</h3>
                                        <p className="text-sm text-on-surface-variant mb-6 max-w-md mx-auto">Generate a cryptographic key to securely connect Claude Desktop, Cursor, or autonomous agents.</p>
                                        <button 
                                            className="px-6 py-3 bg-primary-container text-black font-bold rounded-xl hover:bg-primary-fixed transition-all shadow-[0_0_20px_rgba(132,204,22,0.3)] disabled:opacity-50"
                                            onClick={handleGenerateApiKey}
                                            disabled={isGeneratingKey}
                                        >
                                            {isGeneratingKey ? "Generating Key..." : "Generate Permanent API Key"}
                                        </button>
                                    </div>
                                ) : (
                                    <div className="space-y-8">
                                        {/* Secret API Key Input */}
                                        <div className="space-y-2">
                                            <label className="text-xs font-semibold text-on-surface-variant uppercase tracking-wider">Your Secret API Key</label>
                                            <div className="flex flex-col sm:flex-row gap-3">
                                                <div className="relative flex-1">
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
                                                    <Copy className="w-4 h-4" /> Copy Key
                                                </button>
                                            </div>
                                        </div>

                                        {/* Client Config Tabs */}
                                        <div className="space-y-4">
                                            <label className="text-xs font-semibold text-on-surface-variant uppercase tracking-wider">Select AI Client Preset</label>
                                            
                                            <div className="flex flex-wrap gap-2 border-b border-white/10 pb-4">
                                                {(Object.keys(configSnippets) as ClientTab[]).map((tab) => (
                                                    <button
                                                        key={tab}
                                                        onClick={() => setActiveClientTab(tab)}
                                                        className={`px-4 py-2 text-xs font-semibold rounded-lg transition-all ${activeClientTab === tab ? 'bg-primary-container text-black shadow-[0_0_15px_rgba(132,204,22,0.3)]' : 'bg-white/5 text-on-surface-variant hover:text-white hover:bg-white/10'}`}
                                                    >
                                                        {configSnippets[tab].title}
                                                    </button>
                                                ))}
                                            </div>

                                            <div className="relative">
                                                <div className="flex justify-between items-center bg-[#050505] px-4 py-2.5 rounded-t-xl border-t border-x border-white/10 text-xs text-on-surface-variant">
                                                    <span>Target File: <code className="text-white font-mono">{configSnippets[activeClientTab].filename}</code></span>
                                                    <button 
                                                        className="px-3 py-1 bg-white/10 hover:bg-white/20 text-white text-xs font-medium rounded-md transition-colors flex items-center gap-1.5"
                                                        onClick={() => copyToClipboard(configSnippets[activeClientTab].code, `${configSnippets[activeClientTab].title} config copied!`)}
                                                    >
                                                        <Copy className="w-3.5 h-3.5" /> Copy Config
                                                    </button>
                                                </div>
                                                <textarea 
                                                    value={configSnippets[activeClientTab].code}
                                                    readOnly 
                                                    className="w-full bg-[#0A0A0A] border border-white/10 rounded-b-xl p-4 text-xs text-primary-container font-mono focus:outline-none min-h-[160px] resize-none"
                                                />
                                            </div>
                                        </div>

                                        {/* Revoke Button */}
                                        <div className="pt-4 border-t border-white/10 flex justify-between items-center">
                                            <span className="text-xs text-on-surface-variant">Need to rotate keys? Revoking will immediately disable all active agent sessions.</span>
                                            <button 
                                                className="px-4 py-2 text-xs font-semibold text-error border border-error/30 hover:bg-error/10 rounded-lg transition-colors flex items-center gap-1.5"
                                                onClick={handleRevokeApiKey}
                                                disabled={isRevokingKey}
                                            >
                                                <AlertCircle className="w-3.5 h-3.5" /> {isRevokingKey ? "Revoking..." : "Revoke Key"}
                                            </button>
                                        </div>
                                    </div>
                                )}
                            </div>
                        )}

                    </div>
                </main>
            </div>
        </div>
    );
}
