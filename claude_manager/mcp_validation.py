"""MCP server configuration validation."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Tuple


class MCPValidationError(Exception):
    """Exception raised for MCP configuration validation errors."""
    pass


class MCPValidator:
    """Validator for MCP server configurations."""
    
    REQUIRED_FIELDS = {"command"}
    OPTIONAL_FIELDS = {"args", "env", "cwd", "timeout"}
    
    # Common MCP server commands
    KNOWN_SERVERS = {
        "npx": {
            "@modelcontextprotocol/server-filesystem",
            "@modelcontextprotocol/server-github", 
            "@modelcontextprotocol/server-postgres",
            "@modelcontextprotocol/server-sqlite",
            "@modelcontextprotocol/server-memory",
            "@modelcontextprotocol/server-puppeteer",
            "@modelcontextprotocol/server-everart",
            "@modelcontextprotocol/server-everything",
            "@modelcontextprotocol/server-fetch",
            "@modelcontextprotocol/server-slack",
            "claude-flow@alpha",
        },
        "node": set(),
        "python": set(),
        "python3": set(),
    }
    
    @classmethod
    def validate_config(cls, config: Dict[str, Any], server_name: str) -> Tuple[bool, Optional[str]]:
        """
        Validate MCP server configuration.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check if config is a dictionary
            if not isinstance(config, dict):
                return False, "Configuration must be a JSON object"
            
            # Check required fields
            missing_fields = cls.REQUIRED_FIELDS - set(config.keys())
            if missing_fields:
                return False, f"Missing required fields: {', '.join(missing_fields)}"
            
            # Check for unknown fields
            all_allowed = cls.REQUIRED_FIELDS | cls.OPTIONAL_FIELDS
            unknown_fields = set(config.keys()) - all_allowed
            if unknown_fields:
                return False, f"Unknown fields: {', '.join(unknown_fields)}"
            
            # Validate command
            command = config.get("command", "")
            if not isinstance(command, str) or not command.strip():
                return False, "Command must be a non-empty string"
            
            # Validate args if present
            if "args" in config:
                args = config["args"]
                if not isinstance(args, list):
                    return False, "Args must be an array"
                if not all(isinstance(arg, str) for arg in args):
                    return False, "All args must be strings"
            
            # Validate env if present
            if "env" in config:
                env = config["env"]
                if not isinstance(env, dict):
                    return False, "Env must be an object"
                if not all(isinstance(k, str) and isinstance(v, str) for k, v in env.items()):
                    return False, "All env keys and values must be strings"
            
            # Validate cwd if present
            if "cwd" in config:
                cwd = config["cwd"]
                if not isinstance(cwd, str):
                    return False, "Cwd must be a string"
            
            # Validate timeout if present
            if "timeout" in config:
                timeout = config["timeout"]
                if not isinstance(timeout, (int, float)) or timeout <= 0:
                    return False, "Timeout must be a positive number"
            
            # Warn about known servers
            warnings = cls._check_known_servers(config)
            if warnings:
                return True, f"Configuration valid. Note: {warnings}"
            
            return True, None
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    @classmethod
    def _check_known_servers(cls, config: Dict[str, Any]) -> Optional[str]:
        """Check for common issues with known servers."""
        command = config.get("command", "")
        args = config.get("args", [])
        
        warnings = []
        
        if command == "npx" and args:
            server_package = args[0] if args else ""
            # Remove version suffix for checking
            base_package = server_package.split("@")[0] if "@" in server_package and not server_package.startswith("@") else server_package
            
            if base_package in cls.KNOWN_SERVERS.get("npx", set()):
                # Check for common env requirements
                if base_package == "@modelcontextprotocol/server-filesystem":
                    if not config.get("env", {}).get("WORKSPACE_DIR"):
                        warnings.append("server-filesystem usually requires WORKSPACE_DIR env variable")
                elif base_package == "@modelcontextprotocol/server-github":
                    if not config.get("env", {}).get("GITHUB_TOKEN"):
                        warnings.append("server-github requires GITHUB_TOKEN env variable")
                elif base_package == "@modelcontextprotocol/server-postgres":
                    if not config.get("env", {}).get("DATABASE_URL"):
                        warnings.append("server-postgres requires DATABASE_URL env variable")
        
        return "; ".join(warnings) if warnings else None
    
    @classmethod
    def validate_json_string(cls, json_str: str, server_name: str) -> Tuple[bool, Optional[str]]:
        """Validate a JSON string configuration."""
        try:
            config = json.loads(json_str)
            return cls.validate_config(config, server_name)
        except json.JSONDecodeError as e:
            return False, f"Invalid JSON: {str(e)}"
    
    @classmethod
    def get_template(cls, server_type: str) -> Optional[Dict[str, Any]]:
        """Get a template configuration for common server types."""
        templates = {
            "filesystem": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem"],
                "env": {
                    "WORKSPACE_DIR": "/path/to/workspace"
                }
            },
            "github": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-github"],
                "env": {
                    "GITHUB_TOKEN": "ghp_your_token_here"
                }
            },
            "postgres": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-postgres"],
                "env": {
                    "DATABASE_URL": "postgresql://user:pass@localhost/db"
                }
            },
            "claude-flow": {
                "command": "npx",
                "args": ["claude-flow@alpha", "mcp", "start"]
            },
            "memory": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-memory"]
            },
            "custom": {
                "command": "your-command",
                "args": ["arg1", "arg2"],
                "env": {
                    "KEY": "value"
                }
            }
        }
        return templates.get(server_type)
    
    @classmethod
    def list_templates(cls) -> List[str]:
        """List available template names."""
        return ["filesystem", "github", "postgres", "claude-flow", "memory", "custom"]