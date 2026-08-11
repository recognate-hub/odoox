"use client";

import React, { useState, useEffect } from 'react';
import './dashboard.css';
import Link from "next/link";
import { useRouter } from 'next/navigation';
import WorkspaceCard, { Workspace } from '@/components/WorkspaceCard';



export default function UserDashboard() {
    const router = useRouter();

    const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
    const [limit, setLimit] = useState(1);
    const [planType, setPlanType] = useState('single');
    const [token, setToken] = useState('');
    const [isLoading, setIsLoading] = useState(true);
    const [showToast, setShowToast] = useState(false);
    const [toastMessage, setToastMessage] = useState("");
    
    // API Key State
    const [apiKey, setApiKey] = useState("");
    const [isGeneratingKey, setIsGeneratingKey] = useState(false);

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
        } finally {
            setIsLoading(false);
        }
    }, [router]);

    useEffect(() => {
        const storedApiKey = localStorage.getItem('workspace_api_key');
        if (storedApiKey) {
            setApiKey(storedApiKey);
        }
        fetchWorkspaces();
    }, [fetchWorkspaces]);

    const handleAddWorkspace = () => {
        if (workspaces.length >= limit) {
            alert(`Plan limit reached. Your ${planType} plan allows up to ${limit} connected database(s).`);
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
                setToastMessage("Workspace saved successfully!");
                setShowToast(true);
                setApiKey("");
                localStorage.removeItem('workspace_api_key');
                setTimeout(() => setShowToast(false), 3000);
                fetchWorkspaces(); // Refresh to get proper ID and URL
            } else {
                alert("Error: " + data.message);
            }
        } catch (err) {
            alert("Connection failed.");
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
                setToastMessage("Workspace deleted.");
                setShowToast(true);
                setApiKey("");
                localStorage.removeItem('workspace_api_key');
                setTimeout(() => setShowToast(false), 3000);
                fetchWorkspaces();
            } else {
                alert("Error: " + data.message);
            }
        } catch (err) {
            alert("Deletion failed.");
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
                setToastMessage("API Key generated successfully.");
                setShowToast(true);
                setTimeout(() => setShowToast(false), 3000);
            } else {
                alert("Failed to generate API key.");
            }
        } catch (e) {
            alert("Error generating API key.");
        } finally {
            setIsGeneratingKey(false);
        }
    };

    const handleRevokeApiKey = async () => {
        if (!apiKey) return;
        if (!confirm("Are you sure you want to revoke this API key? Any applications using it will lose access immediately.")) return;
        
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
                setToastMessage("API Key revoked successfully.");
                setShowToast(true);
                setTimeout(() => setShowToast(false), 3000);
            } else {
                alert("Failed to revoke API key.");
            }
        } catch (e) {
            alert("Error revoking API key.");
        }
    };

    if (isLoading) {
        return (
            <div className="dashboard-theme" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
                <div style={{ color: 'var(--brand-primary)', fontFamily: 'Outfit' }}>Loading Workspace...</div>
            </div>
        );
    }

    return (
        <div className="dashboard-theme">
            <div className="bg-grid"></div>
            
            <div className="content-wrapper">
                <div className="dashboard-layout">
                    {/* Sidebar */}
                    <aside className="sidebar">
                        <div className="sidebar-brand">
                            <div className="brand-text">
                                <Link href="/">
                                    <img src="/logo.png" alt="OdooX Logo" style={{ height: '40px', width: 'auto' }} />
                                </Link>
                            </div>
                            <div className="brand-sub">WORKSPACE</div>
                        </div>
                        <nav>
                            <Link href="/userdashboard" className="nav-link active">
                                <span className="nav-icon">
                                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
                                </span> Integration
                            </Link>
                        </nav>
                        
                        <div style={{ padding: '1.5rem', marginTop: 'auto' }}>
                            <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
                                Plan: <strong style={{color: 'var(--text-primary)', textTransform: 'capitalize'}}>{planType}</strong>
                            </div>
                            <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                                Usage: {workspaces.length} / {limit} Databases
                            </div>
                        </div>

                        <div className="sidebar-footer">
                            <a href="#" onClick={handleLogout} className="nav-link" style={{ color: 'var(--accent-red)' }}>
                                <span className="nav-icon">
                                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
                                </span> Log Out
                            </a>
                        </div>
                    </aside>
                    
                    {/* Main Content */}
                    <main className="main-content">
                        <header className="page-header animate-fade-in-up" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <div>
                                <h1>Odoo Integration</h1>
                                <p>Configure your secure connections to enable the Claude MCP endpoint.</p>
                            </div>
                            <button 
                                className="btn btn-primary"
                                onClick={handleAddWorkspace}
                                disabled={workspaces.length >= limit}
                            >
                                + Connect Database
                            </button>
                        </header>
                        
                        <div className="content-grid" style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
                            {workspaces.length === 0 && (
                                <div className="glass-card" style={{ textAlign: 'center', padding: '3rem 1rem' }}>
                                    <p style={{ color: 'var(--text-secondary)', marginBottom: '1rem' }}>No databases connected yet.</p>
                                    <button className="btn btn-outline" onClick={handleAddWorkspace}>Add your first Odoo Database</button>
                                </div>
                            )}

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

                            {workspaces.length > 0 && (
                                <div className="glass-card" style={{ padding: '2rem', marginTop: '1rem', borderTop: '1px solid rgba(255, 255, 255, 0.1)' }}>
                                    <h3 style={{ color: 'var(--text-primary)', marginBottom: '1rem' }}>API Integrations</h3>
                                    <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem', fontSize: '0.9rem' }}>
                                        Generate a permanent API Key to connect external tools like Claude Desktop directly to your Odoo environment. Keep this key safe.
                                    </p>
                                    
                                    {!apiKey ? (
                                        <button 
                                            className="btn btn-primary" 
                                            onClick={handleGenerateApiKey}
                                            disabled={isGeneratingKey}
                                        >
                                            {isGeneratingKey ? "Generating..." : "Generate Permanent API Key"}
                                        </button>
                                    ) : (
                                        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                                            <div>
                                                <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>Raw API Key</label>
                                                <div style={{ display: 'flex', gap: '1rem' }}>
                                                    <input 
                                                        type="text" 
                                                        value={apiKey} 
                                                        readOnly 
                                                        className="form-input" 
                                                        style={{ flex: 1, fontFamily: 'monospace' }}
                                                    />
                                                    <button 
                                                        className="btn btn-outline"
                                                        onClick={() => {
                                                            navigator.clipboard.writeText(apiKey);
                                                            setToastMessage("API Key copied!");
                                                            setShowToast(true);
                                                            setTimeout(() => setShowToast(false), 3000);
                                                        }}
                                                    >
                                                        Copy Key
                                                    </button>
                                                </div>
                                            </div>

                                            <div>
                                                <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>Claude Web Custom Connector URL</label>
                                                <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
                                                    Paste this into the <strong>Remote MCP server URL</strong> field in Claude Web. <br/>
                                                    <em>Note: Claude Web requires HTTPS. If running locally, you must proxy localhost:8000 through ngrok (e.g. `ngrok http 8000`) and replace localhost below with your ngrok HTTPS URL.</em>
                                                </p>
                                                <div style={{ display: 'flex', gap: '1rem' }}>
                                                    <input 
                                                        type="text" 
                                                        value={`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/sse?token=${apiKey}`}
                                                        readOnly 
                                                        className="form-input" 
                                                        style={{ flex: 1, fontFamily: 'monospace' }}
                                                    />
                                                    <button 
                                                        className="btn btn-primary"
                                                        onClick={() => {
                                                            const fullUrl = `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/sse?token=${apiKey}`;
                                                            navigator.clipboard.writeText(fullUrl);
                                                            setToastMessage("Full URL copied!");
                                                            setShowToast(true);
                                                            setTimeout(() => setShowToast(false), 3000);
                                                        }}
                                                    >
                                                        Copy URL
                                                    </button>
                                                </div>
                                            </div>

                                            <div style={{ marginTop: '1rem' }}>
                                                <label style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>Claude Desktop Configuration (claude_desktop_config.json)</label>
                                                <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>For local Claude Desktop app usage, bypassing HTTPS requirements.</p>
                                                <div style={{ position: 'relative', marginTop: '0.5rem' }}>
                                                    <textarea 
                                                        value={`{
  "mcpServers": {
    "odoox-cloud": {
      "command": "npx",
      "args": [
        "-y",
        "odoox-mcp-connector",
        "--url",
        "${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/sse?token=${apiKey}"
      ]
    }
  }
}`}
                                                        readOnly 
                                                        className="form-input" 
                                                        style={{ width: '100%', fontFamily: 'monospace', minHeight: '220px', resize: 'none', padding: '1rem', background: '#000', color: '#a3e635' }}
                                                    />
                                                    <button 
                                                        className="btn btn-primary"
                                                        style={{ position: 'absolute', top: '10px', right: '10px', padding: '0.5rem 1rem', fontSize: '0.8rem' }}
                                                        onClick={() => {
                                                            const configStr = `{
  "mcpServers": {
    "odoox-cloud": {
      "command": "npx",
      "args": [
        "-y",
        "odoox-mcp-connector",
        "--url",
        "${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/sse?token=${apiKey}"
      ]
    }
  }
}`;
                                                            navigator.clipboard.writeText(configStr);
                                                            setToastMessage("Configuration copied!");
                                                            setShowToast(true);
                                                            setTimeout(() => setShowToast(false), 3000);
                                                        }}
                                                    >
                                                        Copy Config
                                                    </button>
                                                </div>
                                            </div>

                                            <div style={{ marginTop: '0.5rem' }}>
                                                <button className="btn btn-outline" style={{ color: 'var(--accent-red)', borderColor: 'rgba(239, 68, 68, 0.3)' }} onClick={handleRevokeApiKey}>
                                                    Revoke Key
                                                </button>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    </main>
                </div>
                
                <div id="toast" className={showToast ? 'show' : ''}>
                    {toastMessage}
                </div>
            </div>
        </div>
    );
}

