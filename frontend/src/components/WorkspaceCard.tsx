import React, { useState } from 'react';

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

    const isSaved = !!workspace.id;

    const fetchDatabases = async () => {
        if (!workspace.odoo_url) {
            setDbFetchError('Please enter an Odoo URL first');
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
            } else if (data.error) {
                setDbFetchError(data.error);
            } else {
                setDbFetchError('No databases found');
            }
        } catch (err) {
            setDbFetchError('Failed to fetch databases');
        } finally {
            setIsFetchingDb(false);
        }
    };



    const copyDirectUrl = async () => {
        if (!workspace.connection_url) return;
        try {
            await navigator.clipboard.writeText(workspace.connection_url);
            setCopiedUrl(true);
            setTimeout(() => setCopiedUrl(false), 2000);
        } catch (err) {
            console.error("Failed to copy URL", err);
        }
    };

    const handleSaveClick = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsSaving(true);
        await onSave(index);
        setIsSaving(false);
    };

    return (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
            {/* Left Column: Credentials */}
            <div className="glass-card animate-fade-in-up delay-1">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                    <h3 className="card-title" style={{ margin: 0 }}>Database #{index + 1}</h3>
                    <button 
                        type="button" 
                        onClick={() => onDelete(index)} 
                        style={{ background: 'none', border: 'none', color: 'var(--accent-red)', cursor: 'pointer', fontSize: '0.85rem' }}
                    >
                        Remove
                    </button>
                </div>
                <form onSubmit={handleSaveClick}>
                    <div className="form-group">
                        <label className="form-label">Odoo Instance URL / IP Address</label>
                        <input 
                            type="text" 
                            className="form-input" 
                            placeholder="http://192.168.1.100:8069 or https://mycompany.odoo.com" 
                            value={workspace.odoo_url}
                            onChange={(e) => onChange(index, 'odoo_url', e.target.value)}
                            onBlur={(e) => {
                                const val = e.target.value.trim();
                                if (val && !/^https?:\/\//i.test(val)) {
                                    onChange(index, 'odoo_url', 'http://' + val);
                                }
                            }}
                            required 
                        />
                    </div>
                    
                    <div className="form-group">
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <label className="form-label">Database Name</label>
                            <button 
                                type="button" 
                                onClick={fetchDatabases} 
                                disabled={isFetchingDb || !workspace.odoo_url}
                                style={{ background: 'none', border: 'none', color: 'var(--brand-primary)', cursor: 'pointer', fontSize: '0.8rem', padding: 0 }}
                            >
                                {isFetchingDb ? 'Fetching...' : 'Fetch Databases'}
                            </button>
                        </div>
                        {availableDbs.length > 0 ? (
                            <select 
                                className="form-input" 
                                value={workspace.odoo_db}
                                onChange={(e) => onChange(index, 'odoo_db', e.target.value)}
                                required 
                            >
                                {availableDbs.map(db => (
                                    <option key={db} value={db}>{db}</option>
                                ))}
                            </select>
                        ) : (
                            <input 
                                type="text" 
                                className="form-input" 
                                placeholder="mycompany_db" 
                                value={workspace.odoo_db}
                                onChange={(e) => onChange(index, 'odoo_db', e.target.value)}
                                required 
                            />
                        )}
                        {dbFetchError && <div style={{ color: 'var(--accent-red)', fontSize: '0.75rem', marginTop: '0.25rem' }}>{dbFetchError}</div>}
                    </div>
                    
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                        <div className="form-group">
                            <label className="form-label">Username</label>
                            <input 
                                type="text" 
                                className="form-input" 
                                placeholder="admin@mycompany.com" 
                                value={workspace.odoo_username}
                                onChange={(e) => onChange(index, 'odoo_username', e.target.value)}
                                required 
                            />
                        </div>
                        <div className="form-group">
                            <label className="form-label">Password / API Key</label>
                            <input 
                                type="password" 
                                className="form-input" 
                                placeholder={workspace.has_password ? "(Saved. Leave empty to keep)" : "Required"} 
                                value={workspace.odoo_password || ''}
                                onChange={(e) => onChange(index, 'odoo_password', e.target.value)}
                                required={!workspace.has_password} 
                            />
                        </div>
                    </div>
                    
                    <button type="submit" className="btn btn-primary btn-block mt-2" disabled={isSaving}>
                        {isSaving ? 'Saving...' : 'Securely Save & Connect'}
                    </button>
                </form>
            </div>
            
            {/* Right Column: Connection */}
            <div className="glass-card animate-fade-in-up delay-2">
                <h3 className="card-title">Claude Desktop MCP</h3>
                <p style={{ fontSize: '0.9rem', marginBottom: '1.5rem', color: 'var(--text-secondary)' }}>
                    Use this endpoint in your Claude Desktop configuration to enable real-time Odoo access.
                </p>
                
                <div>
                    <label className="form-label">Connection URL</label>
                    <input 
                        type="text" 
                        className="code-input" 
                        value={workspace.connection_url || 'Save to generate URL'} 
                        readOnly 
                        onClick={(e) => e.currentTarget.select()}
                    />
                </div>
                
                <div className={`status-banner ${isSaved ? 'ready' : ''}`}>
                    <div 
                        className="status-dot" 
                        style={!isSaved ? { background: 'var(--text-muted)', animation: 'none', boxShadow: 'none' } : {}}
                    ></div>
                    <div>
                        {isSaved ? (
                            <>
                                <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>Endpoint Active</div>
                                <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Traffic is AES-256 encrypted.</div>
                            </>
                        ) : (
                            <>
                                <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>Awaiting Configuration</div>
                                <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Save your Odoo credentials first.</div>
                            </>
                        )}
                    </div>
                </div>
                
                {isSaved && (
                    <div className="action-grid">
                        <button onClick={copyDirectUrl} className="btn btn-outline" style={{ gridColumn: '1 / -1', fontSize: '0.85rem' }}>
                            {copiedUrl ? 'Copied URL!' : 'Copy Direct URL'}
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
}
