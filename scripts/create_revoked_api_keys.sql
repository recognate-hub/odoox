CREATE TABLE IF NOT EXISTS revoked_api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    api_key TEXT NOT NULL UNIQUE,
    revoked_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    workspace_id UUID REFERENCES user_workspaces(id) ON DELETE CASCADE
);

-- Enable RLS
ALTER TABLE revoked_api_keys ENABLE ROW LEVEL SECURITY;

-- Allow read access for authenticated users or service role
CREATE POLICY "Allow read for all authenticated users" 
ON revoked_api_keys FOR SELECT 
USING (true);

-- Allow insert access for service role or authenticated users
CREATE POLICY "Allow insert for all authenticated users" 
ON revoked_api_keys FOR INSERT 
WITH CHECK (true);
