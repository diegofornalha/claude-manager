"""MCP Test Fixtures and Configuration."""
import json
import pytest
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import Mock, AsyncMock
import asyncio
from dataclasses import dataclass, field

from claude_manager.models import Project


@dataclass
class MockMCPServer:
    """Mock MCP Server for testing."""
    name: str
    command: str
    args: List[str] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)
    enabled: bool = True
    running: bool = False
    
    async def start(self):
        """Simulate server start."""
        self.running = True
        await asyncio.sleep(0.1)  # Simulate startup time
        
    async def stop(self):
        """Simulate server stop."""
        self.running = False
        await asyncio.sleep(0.05)  # Simulate shutdown time
        
    def get_status(self) -> Dict[str, Any]:
        """Get server status."""
        return {
            "name": self.name,
            "enabled": self.enabled,
            "running": self.running,
            "command": self.command,
            "args": self.args,
            "env": self.env
        }


@pytest.fixture
def mcp_server_config() -> Dict[str, Any]:
    """Sample MCP server configuration."""
    return {
        "memory": {
            "command": "memory-mcp",
            "args": ["--storage", "/tmp/memory"],
            "env": {"MCP_MODE": "test"}
        },
        "filesystem": {
            "command": "filesystem-mcp",
            "args": ["--root", "/tmp/fs"],
            "env": {}
        },
        "github": {
            "command": "github-mcp",
            "args": ["--token", "test-token"],
            "env": {"GITHUB_API_URL": "https://api.github.com"}
        }
    }


@pytest.fixture
def mock_mcp_servers(mcp_server_config) -> Dict[str, MockMCPServer]:
    """Create mock MCP servers."""
    servers = {}
    for name, config in mcp_server_config.items():
        servers[name] = MockMCPServer(
            name=name,
            command=config["command"],
            args=config.get("args", []),
            env=config.get("env", {})
        )
    return servers


@pytest.fixture
def sample_project_with_mcp(tmp_path) -> Project:
    """Create a sample project with MCP configuration."""
    return Project(
        name="test-project-mcp",
        path=str(tmp_path / "test-project-mcp"),
        description="Test project with MCP servers",
        mcp_servers={
            "memory": {
                "command": "memory-mcp",
                "args": ["--storage", "/tmp/memory"],
                "env": {"MCP_MODE": "test"}
            },
            "filesystem": {
                "command": "filesystem-mcp",
                "args": ["--root", "/tmp/fs"],
                "env": {}
            }
        },
        enabled_mcpjson_servers=["memory"],
        disabled_mcpjson_servers=["filesystem"],
        enable_all_project_mcp_servers=False,
        mcp_context_uris=["test://context/1", "test://context/2"]
    )


@pytest.fixture
async def mcp_server_manager(mock_mcp_servers):
    """Mock MCP server manager."""
    class MockMCPServerManager:
        def __init__(self):
            self.servers = mock_mcp_servers
            self.started_servers = []
            
        async def start_server(self, name: str):
            """Start a server by name."""
            if name in self.servers and not self.servers[name].running:
                await self.servers[name].start()
                self.started_servers.append(name)
                
        async def stop_server(self, name: str):
            """Stop a server by name."""
            if name in self.servers and self.servers[name].running:
                await self.servers[name].stop()
                if name in self.started_servers:
                    self.started_servers.remove(name)
                    
        async def start_all(self):
            """Start all enabled servers."""
            for name, server in self.servers.items():
                if server.enabled:
                    await self.start_server(name)
                    
        async def stop_all(self):
            """Stop all running servers."""
            for name in list(self.started_servers):
                await self.stop_server(name)
                
        def get_status(self) -> Dict[str, Any]:
            """Get status of all servers."""
            return {
                name: server.get_status() 
                for name, server in self.servers.items()
            }
            
    manager = MockMCPServerManager()
    yield manager
    # Cleanup: stop all servers
    await manager.stop_all()


@pytest.fixture
def mcp_test_data_dir() -> Path:
    """Get the MCP test data directory."""
    return Path(__file__).parent / "test_data"


@pytest.fixture
def create_test_mcp_config(tmp_path):
    """Factory fixture to create test MCP configurations."""
    def _create_config(name: str, servers: Dict[str, Any]) -> Path:
        config_path = tmp_path / f"{name}.mcpconfig.json"
        config_data = {
            "name": name,
            "version": "1.0",
            "servers": servers,
            "metadata": {
                "created": "2024-01-01T00:00:00Z",
                "description": f"Test MCP config for {name}"
            }
        }
        config_path.write_text(json.dumps(config_data, indent=2))
        return config_path
    
    return _create_config


@pytest.fixture
def mock_mcp_connection():
    """Mock MCP connection for testing."""
    connection = AsyncMock()
    connection.connect = AsyncMock(return_value=True)
    connection.disconnect = AsyncMock()
    connection.send_request = AsyncMock()
    connection.receive_response = AsyncMock()
    connection.is_connected = Mock(return_value=True)
    return connection


@pytest.fixture
def mcp_performance_metrics():
    """Track MCP performance metrics during tests."""
    metrics = {
        "start_times": [],
        "stop_times": [],
        "request_times": [],
        "response_times": [],
        "errors": []
    }
    
    return metrics


@pytest.fixture
def mcp_security_validator():
    """Mock security validator for MCP operations."""
    class MockSecurityValidator:
        def __init__(self):
            self.allowed_commands = ["memory-mcp", "filesystem-mcp", "github-mcp"]
            self.forbidden_paths = ["/etc", "/sys", "/root"]
            
        def validate_command(self, command: str) -> bool:
            """Validate if command is allowed."""
            return command in self.allowed_commands
            
        def validate_path(self, path: str) -> bool:
            """Validate if path is safe."""
            return not any(path.startswith(fp) for fp in self.forbidden_paths)
            
        def validate_env(self, env: Dict[str, str]) -> bool:
            """Validate environment variables."""
            dangerous_vars = ["LD_PRELOAD", "LD_LIBRARY_PATH", "PATH"]
            return not any(var in env for var in dangerous_vars)
            
    return MockSecurityValidator()


# Async test helpers
@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()