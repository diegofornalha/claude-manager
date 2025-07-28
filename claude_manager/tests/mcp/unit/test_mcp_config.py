"""Unit tests for MCP configuration management."""
import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch
from claude_manager.config import ClaudeConfigManager
from claude_manager.models import Project


class TestMCPConfig:
    """Test MCP configuration management."""
    
    @pytest.fixture
    def config_manager(self, tmp_path, sample_config_data):
        """Create a config manager with test data."""
        config_file = tmp_path / "claude-code.json"
        config_file.write_text(json.dumps(sample_config_data))
        return ClaudeConfigManager(config_file)
        
    def test_load_mcp_servers_from_config(self, config_manager):
        """Test loading MCP servers from configuration."""
        projects = config_manager.get_projects()
        
        # Find the project with MCP servers
        mcp_project = next((p for p in projects if p.mcp_servers), None)
        assert mcp_project is not None
        
        assert "github" in mcp_project.mcp_servers
        assert mcp_project.mcp_servers["github"]["command"] == "github-mcp"
        
    def test_update_project_mcp_servers(self, config_manager):
        """Test updating project MCP servers."""
        projects = config_manager.get_projects()
        project = projects[0]
        
        # Update MCP servers
        new_servers = {
            "memory": {"command": "memory-mcp", "args": ["--persistent"]},
            "cache": {"command": "cache-mcp", "env": {"CACHE_SIZE": "100MB"}}
        }
        project.mcp_servers = new_servers
        
        # Save the update
        success = config_manager.update_project(project)
        assert success
        
        # Reload and verify
        config_manager._load_config()
        updated_projects = config_manager.get_projects()
        updated_project = next(p for p in updated_projects if p.name == project.name)
        
        assert updated_project.mcp_servers == new_servers
        assert "memory" in updated_project.mcp_servers
        assert "cache" in updated_project.mcp_servers
        
    def test_update_mcp_server_lists(self, config_manager):
        """Test updating enabled/disabled MCP server lists."""
        projects = config_manager.get_projects()
        project = projects[0]
        
        # Update server lists
        project.enabled_mcpjson_servers = ["server1", "server2", "server3"]
        project.disabled_mcpjson_servers = ["server4"]
        project.enable_all_project_mcp_servers = True
        
        success = config_manager.update_project(project)
        assert success
        
        # Reload and verify
        config_manager._load_config()
        updated_project = next(
            p for p in config_manager.get_projects() 
            if p.name == project.name
        )
        
        assert updated_project.enabled_mcpjson_servers == ["server1", "server2", "server3"]
        assert updated_project.disabled_mcpjson_servers == ["server4"]
        assert updated_project.enable_all_project_mcp_servers is True
        
    def test_update_mcp_context_uris(self, config_manager):
        """Test updating MCP context URIs."""
        projects = config_manager.get_projects()
        project = projects[0]
        
        new_uris = [
            "test://context/new1",
            "test://context/new2",
            "file:///path/to/new/context"
        ]
        project.mcp_context_uris = new_uris
        
        success = config_manager.update_project(project)
        assert success
        
        # Reload and verify
        config_manager._load_config()
        updated_project = next(
            p for p in config_manager.get_projects() 
            if p.name == project.name
        )
        
        assert updated_project.mcp_context_uris == new_uris
        
    def test_get_stats_includes_mcp_servers(self, config_manager):
        """Test that get_stats includes MCP server count."""
        stats = config_manager.get_stats()
        
        assert "total_mcp_servers" in stats
        assert stats["total_mcp_servers"] >= 0
        
        # Add MCP servers to a project and verify stats update
        projects = config_manager.get_projects()
        project = projects[0]
        project.mcp_servers = {
            "server1": {"command": "cmd1"},
            "server2": {"command": "cmd2"},
            "server3": {"command": "cmd3"}
        }
        config_manager.update_project(project)
        
        new_stats = config_manager.get_stats()
        assert new_stats["total_mcp_servers"] >= 3
        
    def test_mcp_config_persistence(self, config_manager, tmp_path):
        """Test that MCP configurations persist across reloads."""
        projects = config_manager.get_projects()
        project = projects[0]
        
        # Set comprehensive MCP configuration
        project.mcp_servers = {
            "test-server": {
                "command": "test-mcp",
                "args": ["--arg1", "value1", "--arg2", "value2"],
                "env": {"ENV1": "val1", "ENV2": "val2"}
            }
        }
        project.enabled_mcpjson_servers = ["enabled1", "enabled2"]
        project.disabled_mcpjson_servers = ["disabled1"]
        project.enable_all_project_mcp_servers = True
        project.mcp_context_uris = ["uri1", "uri2", "uri3"]
        
        config_manager.update_project(project)
        
        # Create new config manager instance
        new_config_manager = ClaudeConfigManager(config_manager.config_file)
        new_projects = new_config_manager.get_projects()
        loaded_project = next(p for p in new_projects if p.name == project.name)
        
        # Verify all MCP fields persisted correctly
        assert loaded_project.mcp_servers == project.mcp_servers
        assert loaded_project.enabled_mcpjson_servers == project.enabled_mcpjson_servers
        assert loaded_project.disabled_mcpjson_servers == project.disabled_mcpjson_servers
        assert loaded_project.enable_all_project_mcp_servers == project.enable_all_project_mcp_servers
        assert loaded_project.mcp_context_uris == project.mcp_context_uris
        
    def test_mcp_config_with_empty_fields(self, config_manager):
        """Test handling of empty MCP fields."""
        projects = config_manager.get_projects()
        project = projects[0]
        
        # Set empty values
        project.mcp_servers = {}
        project.enabled_mcpjson_servers = []
        project.disabled_mcpjson_servers = []
        project.mcp_context_uris = []
        
        success = config_manager.update_project(project)
        assert success
        
        # Verify empty values are preserved
        config_manager._load_config()
        updated_project = next(
            p for p in config_manager.get_projects() 
            if p.name == project.name
        )
        
        assert updated_project.mcp_servers == {}
        assert updated_project.enabled_mcpjson_servers == []
        assert updated_project.disabled_mcpjson_servers == []
        assert updated_project.mcp_context_uris == []
        
    def test_mcp_config_with_none_values(self, config_manager):
        """Test handling of None values in MCP configuration."""
        projects = config_manager.get_projects()
        project = projects[0]
        
        # Set None for mcp_servers
        project.mcp_servers = None
        
        success = config_manager.update_project(project)
        assert success
        
        # Verify None is handled properly
        config_manager._load_config()
        updated_project = next(
            p for p in config_manager.get_projects() 
            if p.name == project.name
        )
        
        # None should be preserved or converted to empty dict
        assert updated_project.mcp_servers is None or updated_project.mcp_servers == {}
        
    def test_add_mcp_server_to_existing_project(self, config_manager):
        """Test adding an MCP server to a project that didn't have any."""
        # Create a project without MCP servers
        project = Project(
            name="no-mcp-project",
            path="/path/to/project",
            description="Project without MCP"
        )
        
        # Add it to config
        config_manager.config["projects"][project.name] = project.to_dict()
        config_manager._save_config()
        
        # Now add MCP servers
        project.mcp_servers = {"new-server": {"command": "new-mcp"}}
        success = config_manager.update_project(project)
        assert success
        
        # Verify it was added
        updated_project = next(
            p for p in config_manager.get_projects() 
            if p.name == project.name
        )
        assert updated_project.mcp_servers == {"new-server": {"command": "new-mcp"}}
        
    def test_remove_mcp_server_from_project(self, config_manager):
        """Test removing specific MCP servers from a project."""
        projects = config_manager.get_projects()
        project = projects[0]
        
        # Add multiple servers
        project.mcp_servers = {
            "server1": {"command": "cmd1"},
            "server2": {"command": "cmd2"},
            "server3": {"command": "cmd3"}
        }
        config_manager.update_project(project)
        
        # Remove one server
        del project.mcp_servers["server2"]
        config_manager.update_project(project)
        
        # Verify removal
        updated_project = next(
            p for p in config_manager.get_projects() 
            if p.name == project.name
        )
        assert "server1" in updated_project.mcp_servers
        assert "server2" not in updated_project.mcp_servers
        assert "server3" in updated_project.mcp_servers