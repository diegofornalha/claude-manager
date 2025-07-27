"""Tests for MCP server configuration validation."""

import pytest

from claude_manager.mcp_validation import MCPValidator, MCPValidationError


class TestMCPValidator:
    """Test MCP configuration validation."""
    
    def test_valid_minimal_config(self):
        """Test validation of minimal valid configuration."""
        config = {"command": "npx"}
        is_valid, error = MCPValidator.validate_config(config, "test-server")
        assert is_valid is True
        assert error is None
    
    def test_valid_full_config(self):
        """Test validation of full configuration with all fields."""
        config = {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem"],
            "env": {"WORKSPACE_DIR": "/home/user"},
            "cwd": "/tmp",
            "timeout": 30
        }
        is_valid, error = MCPValidator.validate_config(config, "test-server")
        assert is_valid is True
        assert error is None
    
    def test_missing_required_field(self):
        """Test validation fails when required field is missing."""
        config = {"args": ["test"]}
        is_valid, error = MCPValidator.validate_config(config, "test-server")
        assert is_valid is False
        assert "Missing required fields: command" in error
    
    def test_invalid_command_type(self):
        """Test validation fails for invalid command type."""
        config = {"command": 123}
        is_valid, error = MCPValidator.validate_config(config, "test-server")
        assert is_valid is False
        assert "Command must be a non-empty string" in error
    
    def test_empty_command(self):
        """Test validation fails for empty command."""
        config = {"command": ""}
        is_valid, error = MCPValidator.validate_config(config, "test-server")
        assert is_valid is False
        assert "Command must be a non-empty string" in error
    
    def test_invalid_args_type(self):
        """Test validation fails for invalid args type."""
        config = {"command": "npx", "args": "not-a-list"}
        is_valid, error = MCPValidator.validate_config(config, "test-server")
        assert is_valid is False
        assert "Args must be an array" in error
    
    def test_invalid_args_items(self):
        """Test validation fails for non-string args items."""
        config = {"command": "npx", "args": ["valid", 123, "string"]}
        is_valid, error = MCPValidator.validate_config(config, "test-server")
        assert is_valid is False
        assert "All args must be strings" in error
    
    def test_invalid_env_type(self):
        """Test validation fails for invalid env type."""
        config = {"command": "npx", "env": "not-a-dict"}
        is_valid, error = MCPValidator.validate_config(config, "test-server")
        assert is_valid is False
        assert "Env must be an object" in error
    
    def test_invalid_env_values(self):
        """Test validation fails for non-string env values."""
        config = {"command": "npx", "env": {"KEY": 123}}
        is_valid, error = MCPValidator.validate_config(config, "test-server")
        assert is_valid is False
        assert "All env keys and values must be strings" in error
    
    def test_invalid_timeout(self):
        """Test validation fails for invalid timeout."""
        config = {"command": "npx", "timeout": -5}
        is_valid, error = MCPValidator.validate_config(config, "test-server")
        assert is_valid is False
        assert "Timeout must be a positive number" in error
    
    def test_unknown_fields(self):
        """Test validation fails for unknown fields."""
        config = {"command": "npx", "unknown_field": "value"}
        is_valid, error = MCPValidator.validate_config(config, "test-server")
        assert is_valid is False
        assert "Unknown fields: unknown_field" in error
    
    def test_filesystem_server_warning(self):
        """Test warning for filesystem server without WORKSPACE_DIR."""
        config = {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem"]
        }
        is_valid, error = MCPValidator.validate_config(config, "test-server")
        assert is_valid is True
        assert "server-filesystem usually requires WORKSPACE_DIR" in error
    
    def test_github_server_warning(self):
        """Test warning for github server without token."""
        config = {
            "command": "npx",
            "args": ["@modelcontextprotocol/server-github"]
        }
        is_valid, error = MCPValidator.validate_config(config, "test-server")
        assert is_valid is True
        assert "server-github requires GITHUB_TOKEN" in error
    
    def test_postgres_server_warning(self):
        """Test warning for postgres server without database URL."""
        config = {
            "command": "npx",
            "args": ["@modelcontextprotocol/server-postgres"]
        }
        is_valid, error = MCPValidator.validate_config(config, "test-server")
        assert is_valid is True
        assert "server-postgres requires DATABASE_URL" in error
    
    def test_validate_json_string_valid(self):
        """Test validation of valid JSON string."""
        json_str = '{"command": "npx", "args": ["test"]}'
        is_valid, error = MCPValidator.validate_json_string(json_str, "test-server")
        assert is_valid is True
        assert error is None
    
    def test_validate_json_string_invalid(self):
        """Test validation of invalid JSON string."""
        json_str = '{"command": "npx", invalid json}'
        is_valid, error = MCPValidator.validate_json_string(json_str, "test-server")
        assert is_valid is False
        assert "Invalid JSON" in error
    
    def test_get_template(self):
        """Test getting configuration templates."""
        filesystem_template = MCPValidator.get_template("filesystem")
        assert filesystem_template is not None
        assert filesystem_template["command"] == "npx"
        assert "@modelcontextprotocol/server-filesystem" in filesystem_template["args"]
        
        unknown_template = MCPValidator.get_template("unknown")
        assert unknown_template is None
    
    def test_list_templates(self):
        """Test listing available templates."""
        templates = MCPValidator.list_templates()
        assert "filesystem" in templates
        assert "github" in templates
        assert "postgres" in templates
        assert "claude-flow" in templates
        assert "memory" in templates
        assert "custom" in templates