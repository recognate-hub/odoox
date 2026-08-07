import pytest
from typer.testing import CliRunner
from cli.main import app
from unittest.mock import patch, MagicMock

runner = CliRunner()

def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Usage" in result.stdout

@patch("cli.main.subprocess.run")
@patch("os.path.exists", return_value=True)
def test_cli_install(mock_exists, mock_run):
    result = runner.invoke(app, ["install"])
    assert result.exit_code == 0

@patch("uvicorn.run")
def test_cli_run(mock_uvicorn):
    result = runner.invoke(app, ["run", "--host", "127.0.0.1", "--port", "8080", "--no-reload"])
    assert result.exit_code == 0
    mock_uvicorn.assert_called_once()

@patch("cli.main.subprocess.run")
def test_cli_test(mock_run):
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_run.return_value = mock_result
    result = runner.invoke(app, ["test"])
    assert result.exit_code == 0

@patch("odoo.xmlrpc.XmlRpcOdooConnector")
@patch("config.settings.get_settings")
def test_cli_healthcheck(mock_get_settings, mock_connector):
    mock_settings = MagicMock()
    mock_settings.ANTHROPIC_API_KEY.get_secret_value.return_value = "sk-ant-12345"
    mock_get_settings.return_value = mock_settings
    result = runner.invoke(app, ["healthcheck"])
    assert result.exit_code == 0

@patch("config.settings.get_settings")
def test_cli_validate_config(mock_get_settings):
    result = runner.invoke(app, ["validate-config"])
    assert result.exit_code == 0

@patch("repositories.odoo.OdooRepository")
@patch("odoo.xmlrpc.XmlRpcOdooConnector")
@patch("config.settings.get_settings")
def test_cli_seed(mock_get_settings, mock_connector, mock_repo):
    mock_repo_instance = MagicMock()
    mock_repo.return_value = mock_repo_instance
    result = runner.invoke(app, ["seed"])
    assert result.exit_code == 0
    assert mock_repo_instance.create_lead.call_count == 3
