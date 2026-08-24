import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Server, Key, Save, Trash2, CheckCircle2, AlertCircle, Copy, Link as LinkIcon, Database, RefreshCw, ChevronDown } from 'lucide-react';
import { toast } from 'sonner';

export interface Workspace {
    id?: string | number;
    odoo_url: string;
    odoo_db: string;
    odoo_username: string;
    odoo_password?: string;
    has_password?: boolean;
    connection_url?: string;
}

export default function WorkspaceCard({ 
    workspace, 
    index, 
    token, 
    onChange, 
    onSave, 
    onDelete 
}: { 
    workspace: Workspace; 
    index: number; 
    token: string;
    onChange: (index: number, field: keyof Workspace, value: string) => void;
    onSave: (index: number) => void;
    onDelete: (index: number) => void;
}) {
    const [copiedUrl, setCopiedUrl] = useState(false);
    const [isSaving, setIsSaving] = useState(false);
    const [isFetchingDb, setIsFetchingDb] = useState(false);
    const [availableDbs, setAvailableDbs] = useState<string[]>([]);
    const [dbFetchError, setDbFetchError] = useState('');
    const [isExpanded, setIsExpanded] = useState(true);
    const [isTesting, setIsTesting] = useState(false);

    const isSaved = !!workspace.id;

    const fetchDatabases = async (e?: React.MouseEvent) => {
        if (e) e.stopPropagation();
        if (!workspace.odoo_url) {
            toast.error('Please enter an Odoo URL first');
            return;
        }
        setIsFetchingDb(true);
        setDbFetchError('');
        try {
            const res = await fetch('/api/workspace/databases', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: workspace.odoo_url })
            });
            const data = await res.json();
            if (data.databases && data.databases.length > 0) {
                setAvailableDbs(data.databases);
                if (!workspace.odoo_db || !data.databases.includes(workspace.odoo_db)) {
                    onChange(index, 'odoo_db', data.databases[0]);
                }
                toast.success('Databases fetched successfully');
            } else if (data.error) {
                setDbFetchError(data.error);
                toast.error(data.error);
            } else {
                setDbFetchError('No databases found');
                toast.error('No databases found');
            }
        } catch (err) {
            setDbFetchError('Failed to fetch databases');
            toast.error('Failed to fetch databases');
        } finally {
            setIsFetchingDb(false);
        }
    };

    const copyDirectUrl = async () => {
        if (!workspace.connection_url) return;
        try {
            await navigator.clipboard.writeText(workspace.connection_url);
            setCopiedUrl(true);
            toast.success("Direct URL copied to clipboard!");
            setTimeout(() => setCopiedUrl(false), 2000);
        } catch (err) {
            toast.error("Failed to copy URL");
        }
    };

    const handleSaveClick = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsSaving(true);
        await onSave(index);
        setIsSaving(false);
    };

    const handleTestConnection = async () => {
        if (!workspace.odoo_url || !workspace.odoo_db || !workspace.odoo_username) {
            toast.error("Please fill in all connection details before testing.");
            return;
        }
        setIsTesting(true);
        try {
            const formData = new URLSearchParams();
            formData.append('odoo_url', workspace.odoo_url);
            formData.append('odoo_db', workspace.odoo_db);
            formData.append('odoo_username', workspace.odoo_username);
            formData.append('odoo_password', workspace.odoo_password || (workspace.has_password ? '********' : ''));

            const res = await fetch('/api/workspace/test', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: formData.toString()
            });
            const data = await res.json();
            
            if (data.status === 'success') {
                toast.success(data.message || "Connection successful!");
            } else {
                toast.error(data.message || "Connection failed.");
            }
        } catch (err) {
            toast.error("Network error during connection test.");
        } finally {
            setIsTesting(false);
        }
    };

    return (
        <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1, duration: 0.4, ease: "easeOut" }}
            className="group relative rounded-2xl border border-white/10 bg-surface-container-high/40 backdrop-blur-xl overflow-hidden transition-all duration-300 hover:border-primary-container/30 hover:shadow-[0_0_30px_rgba(132,204,22,0.05)]"
        >
            {/* Header / Accordion Toggle */}
            <div 
                className="flex items-center justify-between p-6 cursor-pointer select-none"
                onClick={() => setIsExpanded(!isExpanded)}
            >
                <div className="flex items-center gap-4">
                    <div className="flex items-center justify-center w-10 h-10 rounded-full bg-white/5 border border-white/10">
                        <Database className="w-5 h-5 text-primary-container" />
                    </div>
                    <div>
                        <h3 className="text-lg font-semibold text-white tracking-tight">Database #{index + 1}</h3>
                        <p className="text-sm text-on-surface-variant">
                            {workspace.odoo_url ? new URL(workspace.odoo_url.startsWith('http') ? workspace.odoo_url : `https://${workspace.odoo_url}`).hostname : "Configure Connection"}
                        </p>
                    </div>
                </div>
                <div className="flex items-center gap-4">
                    {isSaved ? (
                        <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-primary-container/10 border border-primary-container/20">
                            <div className="w-2 h-2 rounded-full bg-primary-container animate-pulse shadow-[0_0_8px_rgba(132,204,22,0.6)]" />
                            <span className="text-xs font-semibold text-primary-fixed">Active</span>
                        </div>
                    ) : (
                        <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10">
                            <div className="w-2 h-2 rounded-full bg-on-surface-variant" />
                            <span className="text-xs font-semibold text-on-surface-variant">Draft</span>
                        </div>
                    )}
                    <motion.div
                        animate={{ rotate: isExpanded ? 180 : 0 }}
                        transition={{ duration: 0.2 }}
                    >
                        <ChevronDown className="w-5 h-5 text-on-surface-variant group-hover:text-white transition-colors" />
                    </motion.div>
                </div>
            </div>

            {/* Accordion Content */}
            <AnimatePresence initial={false}>
                {isExpanded && (
                    <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: "auto", opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.3, ease: "easeInOut" }}
                        className="overflow-hidden"
                    >
                        <div className="p-6 pt-0 grid grid-cols-1 lg:grid-cols-2 gap-8 border-t border-white/5 mt-2">
                            {/* Left Column: Form */}
                            <div>
                                <form onSubmit={handleSaveClick} className="space-y-5 pt-4">
                                    <div className="space-y-1.5">
                                        <label className="text-sm font-medium text-on-surface-variant flex items-center gap-2">
                                            <Server className="w-4 h-4" /> Odoo Instance URL
                                        </label>
                                        <input 
                                            type="text" 
                                            className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-white placeholder:text-white/20 focus:outline-none focus:ring-2 focus:ring-primary-container/50 focus:border-primary-container transition-all" 
                                            placeholder="https://mycompany.odoo.com" 
                                            value={workspace.odoo_url}
                                            onChange={(e) => onChange(index, 'odoo_url', e.target.value)}
                                            onBlur={(e) => {
                                                const val = e.target.value.trim();
                                                if (val && !/^https?:\/\//i.test(val)) {
                                                    onChange(index, 'odoo_url', 'https://' + val);
                                                }
                                            }}
                                            required 
                                        />
                                    </div>
                                    
                                    <div className="space-y-1.5">
                                        <div className="flex items-center justify-between">
                                            <label className="text-sm font-medium text-on-surface-variant flex items-center gap-2">
                                                <Database className="w-4 h-4" /> Database Name
                                            </label>
                                            <button 
                                                type="button" 
                                                onClick={fetchDatabases} 
                                                disabled={isFetchingDb || !workspace.odoo_url}
                                                className="text-xs font-medium text-primary-container hover:text-primary-fixed disabled:opacity-50 flex items-center gap-1 transition-colors"
                                            >
                                                <RefreshCw className={`w-3 h-3 ${isFetchingDb ? 'animate-spin' : ''}`} />
                                                Fetch Dbs
                                            </button>
                                        </div>
                                        {availableDbs.length > 0 ? (
                                            <select 
                                                className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-primary-container/50 focus:border-primary-container transition-all appearance-none" 
                                                value={workspace.odoo_db}
                                                onChange={(e) => onChange(index, 'odoo_db', e.target.value)}
                                                required 
                                            >
                                                {availableDbs.map(db => (
                                                    <option key={db} value={db} className="bg-surface-container">{db}</option>
                                                ))}
                                            </select>
                                        ) : (
                                            <input 
                                                type="text" 
                                                className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-white placeholder:text-white/20 focus:outline-none focus:ring-2 focus:ring-primary-container/50 focus:border-primary-container transition-all" 
                                                placeholder="mycompany_db" 
                                                value={workspace.odoo_db}
                                                onChange={(e) => onChange(index, 'odoo_db', e.target.value)}
                                                required 
                                            />
                                        )}
                                    </div>
                                    
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        <div className="space-y-1.5">
                                            <label className="text-sm font-medium text-on-surface-variant flex items-center gap-2">
                                                <Key className="w-4 h-4" /> Username
                                            </label>
                                            <input 
                                                type="text" 
                                                className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-white placeholder:text-white/20 focus:outline-none focus:ring-2 focus:ring-primary-container/50 focus:border-primary-container transition-all" 
                                                placeholder="admin@company.com" 
                                                value={workspace.odoo_username}
                                                onChange={(e) => onChange(index, 'odoo_username', e.target.value)}
                                                required 
                                            />
                                        </div>
                                        <div className="space-y-1.5">
                                            <label className="text-sm font-medium text-on-surface-variant flex items-center gap-2">
                                                <Key className="w-4 h-4" /> Password / API Key
                                            </label>
                                            <input 
                                                type="password" 
                                                className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 text-white placeholder:text-white/20 focus:outline-none focus:ring-2 focus:ring-primary-container/50 focus:border-primary-container transition-all" 
                                                placeholder={workspace.has_password ? "Saved. Leave empty to keep" : "Required"} 
                                                value={workspace.odoo_password || ''}
                                                onChange={(e) => onChange(index, 'odoo_password', e.target.value)}
                                                required={!workspace.has_password} 
                                            />
                                        </div>
                                    </div>
                                    
                                    <div className="pt-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                                        <button 
                                            type="button" 
                                            onClick={() => onDelete(index)}
                                            className="px-4 py-2 text-sm font-medium text-error hover:bg-error/10 rounded-lg transition-colors flex items-center gap-2"
                                        >
                                            <Trash2 className="w-4 h-4" /> Remove
                                        </button>
                                        <div className="flex items-center gap-3 w-full sm:w-auto">
                                            <button 
                                                type="button" 
                                                onClick={handleTestConnection}
                                                disabled={isTesting || isSaving}
                                                className="px-5 py-2.5 text-sm font-semibold text-white bg-white/5 border border-white/10 hover:bg-white/10 rounded-xl transition-all disabled:opacity-50 disabled:pointer-events-none flex items-center gap-2 w-full sm:w-auto justify-center"
                                            >
                                                {isTesting ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Server className="w-4 h-4" />}
                                                {isTesting ? 'Testing...' : 'Test Connection'}
                                            </button>
                                            <button 
                                                type="submit" 
                                                disabled={isSaving}
                                                className="px-6 py-2.5 text-sm font-bold text-black bg-primary-container hover:bg-primary-fixed rounded-xl transition-all hover:shadow-[0_0_20px_rgba(132,204,22,0.4)] hover:-translate-y-0.5 disabled:opacity-50 disabled:pointer-events-none flex items-center gap-2 w-full sm:w-auto justify-center"
                                            >
                                                {isSaving ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
                                                {isSaving ? 'Saving...' : 'Securely Save'}
                                            </button>
                                        </div>
                                    </div>
                                </form>
                            </div>
                            
                            {/* Right Column: Connection Info */}
                            <div className="mt-4 bg-black/30 rounded-2xl p-6 border border-white/5 relative overflow-hidden group">
                                <div className="absolute top-0 right-0 w-32 h-32 bg-primary-container/5 rounded-full blur-3xl group-hover:bg-primary-container/10 transition-colors pointer-events-none" />
                                
                                <div className="flex items-center gap-3 mb-6">
                                    <div className="p-2 rounded-lg bg-white/5 border border-white/10">
                                        <LinkIcon className="w-5 h-5 text-white" />
                                    </div>
                                    <div>
                                        <h4 className="text-base font-semibold text-white">Claude Desktop MCP</h4>
                                        <p className="text-xs text-on-surface-variant">Real-time Odoo connection endpoint</p>
                                    </div>
                                </div>
                                
                                <div className="space-y-4 relative z-10">
                                    <div className="space-y-2">
                                        <label className="text-xs font-medium text-on-surface-variant uppercase tracking-wider">Direct Endpoint URL</label>
                                        <div className="relative group/input">
                                            <input 
                                                type="text" 
                                                className="w-full bg-black/60 border border-white/10 rounded-xl pl-4 pr-12 py-3 text-sm text-primary-fixed font-mono focus:outline-none cursor-text select-all" 
                                                value={workspace.connection_url || 'Save configuration to generate URL'} 
                                                readOnly 
                                            />
                                            {workspace.connection_url && (
                                                <button 
                                                    onClick={copyDirectUrl}
                                                    className="absolute right-2 top-1/2 -translate-y-1/2 p-2 text-on-surface-variant hover:text-white hover:bg-white/10 rounded-lg transition-colors"
                                                    title="Copy URL"
                                                >
                                                    <Copy className="w-4 h-4" />
                                                </button>
                                            )}
                                        </div>
                                    </div>
                                    
                                    <div className="p-4 rounded-xl border border-white/5 bg-white/5 flex gap-4 items-start">
                                        <div className="mt-1">
                                            {isSaved ? <CheckCircle2 className="w-5 h-5 text-primary-container" /> : <AlertCircle className="w-5 h-5 text-on-surface-variant" />}
                                        </div>
                                        <div>
                                            <div className="text-sm font-semibold text-white mb-1">
                                                {isSaved ? 'Endpoint Active & Encrypted' : 'Awaiting Configuration'}
                                            </div>
                                            <div className="text-xs text-on-surface-variant leading-relaxed">
                                                {isSaved 
                                                    ? 'Your Claude Desktop app can now connect to this workspace. All traffic is AES-256 encrypted end-to-end.' 
                                                    : 'Fill out your Odoo credentials and click save to generate a secure connection URL for this workspace.'}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </motion.div>
    );
}
