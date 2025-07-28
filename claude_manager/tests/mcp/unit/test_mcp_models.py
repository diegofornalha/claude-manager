"""Unit tests for MCP models."""
import pytest
import json
from pathlib import Path
from claude_manager.models import Project


class TestMCPModels:
    """Test MCP-related model functionality."""
    
    def test_project_with_mcp_servers(self):
        """Test Project model with MCP server configuration."""
        project = Project(
            path="/path/to/project",
            mcp_servers={
                "memory": {
                    "command": "memory-mcp",
                    "args": ["--storage", "/tmp/memory"]
                },
                "filesystem": {
                    "command": "fs-mcp",
                    "args": ["--root", "/tmp/fs"],
                    "env": {"FS_MODE": "readonly"}
                }
            }
        )
        
        assert project.mcp_servers is not None
        assert len(project.mcp_servers) == 2
        assert "memory" in project.mcp_servers
        assert "filesystem" in project.mcp_servers
        assert project.mcp_servers["memory"]["command"] == "memory-mcp"
        assert project.mcp_servers["filesystem"]["env"]["FS_MODE"] == "readonly"
        
    def test_project_mcp_server_lists(self):
        """Test Project model with enabled/disabled server lists."""
        project = Project(
            path="/path/to/project",
            enabled_mcpjson_servers=["server1", "server2"],
            disabled_mcpjson_servers=["server3"],
            enable_all_project_mcp_servers=True
        )
        
        assert project.enabled_mcpjson_servers == ["server1", "server2"]
        assert project.disabled_mcpjson_servers == ["server3"]
        assert project.enable_all_project_mcp_servers is True
        
    def test_project_mcp_context_uris(self):
        """Test Project model with MCP context URIs."""
        uris = ["test://context/1", "test://context/2", "file:///path/to/context"]
        project = Project(
            path="/path/to/project",
            mcp_context_uris=uris
        )
        
        assert project.mcp_context_uris == uris
        assert len(project.mcp_context_uris) == 3
        
    def test_project_to_dict_with_mcp(self):
        """Test Project.to_dict() includes MCP fields."""
        project = Project(
            path="/path/to/project",
            mcp_servers={"memory": {"command": "memory-mcp"}},
            enabled_mcpjson_servers=["server1"],
            disabled_mcpjson_servers=["server2"],
            enable_all_project_mcp_servers=False,
            mcp_context_uris=["test://uri"]
        )
        
        data = project.to_dict()
        
        assert "mcpServers" in data
        assert data["mcpServers"] == {"memory": {"command": "memory-mcp"}}
        assert data["enabledMcpjsonServers"] == ["server1"]
        assert data["disabledMcpjsonServers"] == ["server2"]
        assert data["enableAllProjectMcpServers"] is False
        assert data["mcpContextUris"] == ["test://uri"]
        
    def test_project_from_dict_with_mcp(self):
        """Test Project.from_dict() handles MCP fields."""
        data = {
            "mcpServers": {
                "github": {
                    "command": "github-mcp",
                    "args": ["--token", "test"],
                    "env": {"GITHUB_API": "https://api.github.com"}
                }
            },
            "enabledMcpjsonServers": ["github"],
            "disabledMcpjsonServers": [],
            "enableAllProjectMcpServers": True,
            "mcpContextUris": ["github://repo/test"]
        }
        
        project = Project.from_dict("/path/to/project", data)
        
        assert project.path == "/path/to/project"
        assert project.mcp_servers["github"]["command"] == "github-mcp"
        assert project.mcp_servers["github"]["args"] == ["--token", "test"]
        assert project.mcp_servers["github"]["env"]["GITHUB_API"] == "https://api.github.com"
        assert project.enabled_mcpjson_servers == ["github"]
        assert project.disabled_mcpjson_servers == []
        assert project.enable_all_project_mcp_servers is True
        assert project.mcp_context_uris == ["github://repo/test"]
        
    def test_project_mcp_fields_optional(self):
        """Test that MCP fields are optional in Project model."""
        project = Project(
            path="/path/to/project"
        )
        
        # Should have empty defaults for MCP fields
        assert project.mcp_servers == {}
        assert project.enabled_mcpjson_servers == []
        assert project.disabled_mcpjson_servers == []
        assert project.enable_all_project_mcp_servers is False
        assert project.mcp_context_uris == []
        
        # to_dict should include all fields
        data = project.to_dict()
        assert data["mcpServers"] == {}
        assert data["enabledMcpjsonServers"] == []
        assert data["disabledMcpjsonServers"] == []
        assert data["enableAllProjectMcpServers"] is False
        assert data["mcpContextUris"] == []
        
    def test_project_mcp_server_validation(self):
        """Test validation of MCP server configurations."""
        # Valid configuration
        valid_servers = {
            "test": {
                "command": "test-mcp",
                "args": ["--arg1", "value1"],
                "env": {"KEY": "value"}
            }
        }
        
        project = Project(
            path="/test",
            mcp_servers=valid_servers
        )
        
        assert project.mcp_servers == valid_servers
        
        # Invalid configurations should be handled gracefully
        # (In real implementation, might want to add validation)
        invalid_servers = {
            "empty": {},  # Missing command
            "null_command": {"command": None},
            "bad_args": {"command": "test", "args": "not-a-list"}
        }
        
        # For now, the model accepts these (might want to add validation later)
        project2 = Project(
            path="/test2",
            mcp_servers=invalid_servers
        )
        
        assert project2.mcp_servers == invalid_servers
        
    def test_project_mcp_uri_formats(self):
        """Test various MCP context URI formats."""
        uris = [
            "test://simple",
            "file:///absolute/path",
            "http://example.com/context",
            "custom-protocol://complex/path/with/segments",
            "urn:mcp:context:12345"
        ]
        
        project = Project(
            path="/test",
            mcp_context_uris=uris
        )
        
        assert project.mcp_context_uris == uris
        assert all(isinstance(uri, str) for uri in project.mcp_context_uris)
        
    def test_project_mcp_server_merge(self):
        """Test merging MCP server configurations."""
        project = Project(
            path="/test",
            mcp_servers={
                "server1": {"command": "cmd1"},
                "server2": {"command": "cmd2"}
            }
        )
        
        # Simulate updating with new servers
        new_servers = {
            "server2": {"command": "cmd2-updated", "args": ["--new"]},
            "server3": {"command": "cmd3"}
        }
        
        # Manual merge (in real app, might have a merge method)
        merged = {**project.mcp_servers, **new_servers}
        project.mcp_servers = merged
        
        assert len(project.mcp_servers) == 3
        assert project.mcp_servers["server1"]["command"] == "cmd1"
        assert project.mcp_servers["server2"]["command"] == "cmd2-updated"
        assert project.mcp_servers["server2"]["args"] == ["--new"]
        assert project.mcp_servers["server3"]["command"] == "cmd3"