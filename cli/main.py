import os
import subprocess
import sys

import typer
from rich.console import Console

console = Console()
app = typer.Typer(help="Odoo-Claude CRM Middleware CLI")

@app.command()
def install():
    """Create .env from .env.example if it doesn't exist and run poetry install."""
    if not os.path.exists(".env") and os.path.exists(".env.example"):
        with open(".env.example", "r") as src, open(".env", "w") as dst:
            dst.write(src.read())
        console.print("[green]Created .env from .env.example[/green]")
    else:
        console.print("[yellow].env already exists or .env.example is missing[/yellow]")
        
    console.print("[cyan]Running poetry install...[/cyan]")
    subprocess.run(["python", "-m", "poetry", "install"], check=True)
    console.print("[bold green]Install complete.[/bold green]")


@app.command()
def run(
    host: str = typer.Option("0.0.0.0", help="Host IP to bind to"),
    port: int = typer.Option(8000, help="Port to bind to"),
    reload: bool = typer.Option(True, help="Enable auto-reload")
):
    """Start the FastAPI server."""
    console.print(f"[cyan]Starting FastAPI server on {host}:{port}...[/cyan]")
    import uvicorn
    uvicorn.run("main:app", host=host, port=port, reload=reload)


@app.command()
def test():
    """Run the pytest test suite."""
    console.print("[cyan]Running pytest...[/cyan]")
    result = subprocess.run(["python", "-m", "poetry", "run", "pytest"])
    if result.returncode == 0:
        console.print("[bold green]All tests passed![/bold green]")
    else:
        console.print("[bold red]Tests failed![/bold red]")
        sys.exit(result.returncode)


@app.command()
def healthcheck():
    """Check Odoo and Claude connectivity."""
    from config.settings import get_settings
    from odoo.xmlrpc import XmlRpcOdooConnector
    
    settings = get_settings()
    console.print("[cyan]Checking Odoo connection...[/cyan]")
    try:
        odoo = XmlRpcOdooConnector(settings)
        odoo._authenticate()
        console.print("[green]Odoo connected successfully.[/green]")
    except Exception as e:
        console.print(f"[bold red]Odoo connection failed: {e}[/bold red]")
        sys.exit(1)
        
    console.print("[cyan]Checking Claude configuration...[/cyan]")
    if settings.ANTHROPIC_API_KEY.get_secret_value().startswith("sk-ant-"):
        console.print("[green]Claude API Key format is valid.[/green]")
    else:
        console.print("[bold red]Claude API Key format is invalid.[/bold red]")
        sys.exit(1)


@app.command()
def validate_config():
    """Validate the Pydantic settings."""
    try:
        from config.settings import get_settings
        settings = get_settings()
        settings.validate_config()
        console.print("[bold green]Configuration is valid.[/bold green]")
    except Exception as e:
        console.print(f"[bold red]Configuration validation failed: {e}[/bold red]")
        sys.exit(1)


@app.command()
def seed():
    """Seed Odoo database with sample CRM leads."""
    from config.settings import get_settings
    from odoo.xmlrpc import XmlRpcOdooConnector
    from repositories.odoo import OdooRepository
    
    console.print("[cyan]Seeding Odoo database with sample leads...[/cyan]")
    try:
        settings = get_settings()
        odoo_connector = XmlRpcOdooConnector(settings)
        repo = OdooRepository(odoo_connector)
        
        leads = [
            {"name": "Alpha Corp Integration", "email": "contact@alpha.example.com", "phone": "555-0101"},
            {"name": "Beta Inc Support Contract", "email": "info@beta.example.com", "phone": "555-0202"},
            {"name": "Gamma LLC Hardware Upgrade", "email": "sales@gamma.example.com", "phone": "555-0303"}
        ]
        
        for lead in leads:
            lead_id = repo.create_lead(
                name=lead["name"],
                email_from=lead["email"],
                phone=lead["phone"],
                description="Sample lead created via CLI"
            )
            console.print(f"[green]Created lead ID {lead_id}: {lead['name']}[/green]")
            
        console.print("[bold green]Seeding complete.[/bold green]")
    except Exception as e:
        console.print(f"[bold red]Seeding failed: {e}[/bold red]")
        sys.exit(1)


@app.command()
def generate_api_key(email: str = typer.Option(..., help="User email to generate API Key for")):
    """Generate a stateless API Key for a specific user's workspace."""
    from core.supabase import get_supabase
    from core.encryption import encrypt
    from core.context import WorkspaceContext
    
    console.print(f"[cyan]Looking up workspaces for {email}...[/cyan]")
    try:
        supabase = get_supabase() # using service role
        
        # 1. Fetch user by email via admin API
        users_resp = supabase.auth.admin.list_users()
        user_id = None
        for u in users_resp:
            if getattr(u, 'email', None) == email:
                user_id = u.id
                break
                
        if not user_id:
            console.print(f"[bold red]User {email} not found in Supabase Auth.[/bold red]")
            sys.exit(1)
            
        # 2. Fetch workspace
        workspace_response = supabase.table("user_workspaces").select("*").eq("user_id", user_id).limit(1).execute()
        if not workspace_response.data:
            console.print(f"[bold red]No workspace found for user {email}.[/bold red]")
            sys.exit(1)
            
        workspace_data = workspace_response.data[0]
        workspace = WorkspaceContext(
            odoo_url=workspace_data["odoo_url"],
            odoo_db=workspace_data["odoo_db"],
            odoo_username=workspace_data["odoo_username"],
            odoo_password=workspace_data["odoo_password"],
            user_id=user_id
        )
        
        # 3. Encrypt payload
        encrypted_payload = encrypt(workspace.model_dump_json())
        api_key = f"odx_{encrypted_payload}"
        
        console.print("[bold green]Success! Generated API Key:[/bold green]")
        console.print(f"[yellow]{api_key}[/yellow]")
        console.print("\n[cyan]Use this token in your claude_desktop_config.json:[/cyan]")
        console.print(f'  "https://your-server.com/sse?token={api_key}"')
        
    except Exception as e:
        console.print(f"[bold red]Failed: {e}[/bold red]")
        sys.exit(1)

if __name__ == "__main__":
    app()
