import typer
import subprocess
import os
import sys

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


if __name__ == "__main__":
    app()
