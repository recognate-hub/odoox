import pytest
import os
from typer.testing import CliRunner
from cli.main import app
from unittest.mock import patch, MagicMock, mock_open

runner = CliRunner()

def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Usage" in result.stdout

@patch("cli.main.subprocess.run")
@patch("os.path.exists")
def test_cli_install_no_env_file(mock_exists, mock_run):
    # .env doesn't exist, .env.example exists
    mock_exists.side_effect = lambda path: path == ".env.example"
    
    m_open = mock_open(read_data="DUMMY_ENV_DATA")
    with patch("builtins.open", m_open):
        result = runner.invoke(app, ["install"])
        
    assert result.exit_code == 0
    m_open.assert_any_call(".env.example", "r")
    m_open.assert_any_call(".env", "w")
    # check that we wrote to .env
    handle = m_open()
    handle.write.assert_called_with("DUMMY_ENV_DATA")

@patch("cli.main.subprocess.run")
@patch("os.path.exists", return_value=True)
def test_cli_install_existing_env(mock_exists, mock_run):
    result = runner.invoke(app, ["install"])
    assert result.exit_code == 0

@patch("uvicorn.run")
def test_cli_run(mock_uvicorn):
    result = runner.invoke(app, ["run", "--host", "127.0.0.1", "--port", "8080", "--no-reload"])
    assert result.exit_code == 0
    mock_uvicorn.assert_called_once()

@patch("cli.main.subprocess.run")
def test_cli_test_success(mock_run):
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_run.return_value = mock_result
    result = runner.invoke(app, ["test"])
    assert result.exit_code == 0

@patch("cli.main.subprocess.run")
def test_cli_test_failure(mock_run):
    mock_result = MagicMock()
    mock_result.returncode = 1
    mock_run.return_value = mock_result
    result = runner.invoke(app, ["test"])
    assert result.exit_code == 1

@patch("odoo.xmlrpc.XmlRpcOdooConnector")
@patch("config.settings.get_settings")
def test_cli_healthcheck_success(mock_get_settings, mock_connector):
    mock_settings = MagicMock()
    mock_settings.ANTHROPIC_API_KEY.get_secret_value.return_value = "sk-ant-12345"
    mock_get_settings.return_value = mock_settings
    result = runner.invoke(app, ["healthcheck"])
    assert result.exit_code == 0

@patch("odoo.xmlrpc.XmlRpcOdooConnector")
@patch("config.settings.get_settings")
def test_cli_healthcheck_odoo_failure(mock_get_settings, mock_connector):
    mock_settings = MagicMock()
    mock_get_settings.return_value = mock_settings
    
    mock_instance = MagicMock()
    mock_instance._authenticate.side_effect = Exception("Odoo down")
    mock_connector.return_value = mock_instance
    
    result = runner.invoke(app, ["healthcheck"])
    assert result.exit_code == 1
    assert "Odoo connection failed" in result.stdout

@patch("odoo.xmlrpc.XmlRpcOdooConnector")
@patch("config.settings.get_settings")
def test_cli_healthcheck_claude_failure(mock_get_settings, mock_connector):
    mock_settings = MagicMock()
    mock_settings.ANTHROPIC_API_KEY.get_secret_value.return_value = "invalid-key"
    mock_get_settings.return_value = mock_settings
    
    result = runner.invoke(app, ["healthcheck"])
    assert result.exit_code == 1
    assert "Claude API Key format is invalid" in result.stdout

@patch("config.settings.get_settings")
def test_cli_validate_config_success(mock_get_settings):
    result = runner.invoke(app, ["validate-config"])
    assert result.exit_code == 0

@patch("config.settings.get_settings")
def test_cli_validate_config_failure(mock_get_settings):
    mock_settings = MagicMock()
    mock_settings.validate_config.side_effect = Exception("Invalid config")
    mock_get_settings.return_value = mock_settings
    
    result = runner.invoke(app, ["validate-config"])
    assert result.exit_code == 1
    assert "Configuration validation failed" in result.stdout

@patch("repositories.odoo.OdooRepository")
@patch("odoo.xmlrpc.XmlRpcOdooConnector")
@patch("config.settings.get_settings")
def test_cli_seed_success(mock_get_settings, mock_connector, mock_repo):
    mock_repo_instance = MagicMock()
    mock_repo.return_value = mock_repo_instance
    result = runner.invoke(app, ["seed"])
    assert result.exit_code == 0
    assert mock_repo_instance.create_lead.call_count == 3

@patch("repositories.odoo.OdooRepository")
@patch("odoo.xmlrpc.XmlRpcOdooConnector")
@patch("config.settings.get_settings")
def test_cli_seed_failure(mock_get_settings, mock_connector, mock_repo):
    mock_repo_instance = MagicMock()
    mock_repo_instance.create_lead.side_effect = Exception("DB error")
    mock_repo.return_value = mock_repo_instance
    
    result = runner.invoke(app, ["seed"])
    assert result.exit_code == 1
    assert "Seeding failed" in result.stdout

def test_main_import():
    import cli.main
    assert cli.main.app is not None
