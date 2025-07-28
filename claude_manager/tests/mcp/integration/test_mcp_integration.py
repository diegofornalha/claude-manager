"""Integration tests for MCP functionality."""
import pytest
import asyncio
import json
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from claude_manager.config import ClaudeConfigManager
from claude_manager.models import Project
from claude_manager.tests.mcp.mocks import (
    MockMemoryMCPServer,
    MockMCPConnection,
    MockMCPServerPool,
    MockMCPEventBus,
    MockMCPNotificationService,
    MCPEventType
)


class TestMCPIntegration:
    """Integration tests for MCP functionality."""
    
    @pytest.mark.asyncio
    async def test_full_mcp_workflow(self, tmp_path):
        """Test complete MCP workflow from config to operation."""
        # Setup config
        config_file = tmp_path / "claude-code.json" 
        project_dir = tmp_path / "test-project"
        project_dir.mkdir(exist_ok=True)
        project_path = str(project_dir)
        
        config_data = {
            "version": "1.0",
            "projects": {
                project_path: {
                    "mcpServers": {
                        "memory": {
                            "command": "memory-mcp",
                            "args": ["--storage", "/tmp/memory"]
                        }
                    },
                    "enabledMcpjsonServers": ["memory"],
                    "enableAllProjectMcpServers": True
                }
            }
        }
        config_file.write_text(json.dumps(config_data))
        
        # Initialize components
        config_manager = ClaudeConfigManager(config_file)
        
        # Ensure config was loaded properly
        assert config_manager.load_config(), "Failed to load config"
        
        event_bus = MockMCPEventBus()
        await event_bus.start()
        
        notification_service = MockMCPNotificationService(event_bus)
        server_pool = MockMCPServerPool()
        
        # Get project
        projects = config_manager.get_projects()
        assert len(projects) > 0, f"No projects loaded. Config data: {config_manager.config_data}"
        # Projects are keyed by their path in the config
        project = list(projects.values())[0]
        
        # Setup MCP servers from config
        for server_name, server_config in project.mcp_servers.items():
            server = MockMemoryMCPServer()
            server_pool.add_server(server_name, server)
            
        # Start servers
        await server_pool.start_all()
        await notification_service.notify_server_start("memory", project.mcp_servers["memory"])
        
        # Get connection and use it
        connection = await server_pool.get_connection("memory")
        
        # Store some data
        result = await connection.call("store", {
            "key": "project:settings",
            "value": {"theme": "dark", "language": "en"}
        })
        assert result["success"] is True
        
        # Retrieve data
        result = await connection.call("retrieve", {"key": "project:settings"})
        assert result["success"] is True
        assert result["data"]["value"]["theme"] == "dark"
        
        # Check events
        events = event_bus.get_events()
        assert any(e.type == MCPEventType.SERVER_STARTED for e in events)
        
        # Cleanup
        await server_pool.stop_all()
        await event_bus.stop()
        
    @pytest.mark.asyncio
    async def test_multiple_mcp_servers(self, sample_project_with_mcp):
        """Test managing multiple MCP servers."""
        project = sample_project_with_mcp
        server_pool = MockMCPServerPool()
        
        # Setup servers from project config
        for server_name in project.mcp_servers:
            server = MockMemoryMCPServer(f"/tmp/{server_name}")
            server_pool.add_server(server_name, server)
            
        # Start all servers
        await server_pool.start_all()
        
        # Use both servers
        memory_conn = await server_pool.get_connection("memory")
        fs_conn = await server_pool.get_connection("filesystem")
        
        # Store in memory server
        await memory_conn.call("store", {"key": "mem:test", "value": "memory-data"})
        
        # Store in filesystem server
        await fs_conn.call("store", {"key": "fs:test", "value": "fs-data"})
        
        # Verify isolation
        memory_result = await memory_conn.call("list", {})
        fs_result = await fs_conn.call("list", {})
        
        assert "mem:test" in memory_result["keys"]
        assert "fs:test" in fs_result["keys"]
        assert "fs:test" not in memory_result["keys"]
        assert "mem:test" not in fs_result["keys"]
        
        await server_pool.stop_all()
        
    @pytest.mark.asyncio
    async def test_mcp_server_enable_disable(self, sample_project_with_mcp):
        """Test enabling and disabling MCP servers."""
        project = sample_project_with_mcp
        
        # Check initial state
        assert "memory" in project.enabled_mcpjson_servers
        assert "filesystem" in project.disabled_mcpjson_servers
        
        # Simulate server management based on enabled/disabled lists
        active_servers = []
        
        for server_name in project.mcp_servers:
            if server_name in project.enabled_mcpjson_servers:
                active_servers.append(server_name)
            elif project.enable_all_project_mcp_servers and server_name not in project.disabled_mcpjson_servers:
                active_servers.append(server_name)
                
        # With current config, only "memory" should be active
        assert active_servers == ["memory"]
        
        # Test with enable_all_project_mcp_servers = True
        project.enable_all_project_mcp_servers = True
        active_servers = []
        
        for server_name in project.mcp_servers:
            if server_name not in project.disabled_mcpjson_servers:
                active_servers.append(server_name)
                
        # Now both should be active since only filesystem is disabled
        assert "memory" in active_servers
        assert "filesystem" not in active_servers
        
    @pytest.mark.asyncio
    async def test_mcp_connection_failure_recovery(self):
        """Test MCP connection failure and recovery."""
        server = MockMemoryMCPServer()
        connection = MockMCPConnection(server)
        
        # Connect successfully
        await connection.connect()
        assert connection.is_connected()
        
        # Store data
        await connection.call("store", {"key": "test", "value": "data"})
        
        # Simulate server failure
        await server.stop()
        connection.connected = False
        
        # Try to use connection (should fail)
        with pytest.raises(RuntimeError, match="Not connected"):
            await connection.call("retrieve", {"key": "test"})
            
        # Recover by restarting and reconnecting
        await server.start()
        await connection.connect()
        
        # Data should be lost (server restarted)
        result = await connection.call("retrieve", {"key": "test"})
        assert result["success"] is False
        
        # But we can store new data
        await connection.call("store", {"key": "test", "value": "new-data"})
        result = await connection.call("retrieve", {"key": "test"})
        assert result["success"] is True
        assert result["data"]["value"] == "new-data"
        
    @pytest.mark.asyncio
    async def test_mcp_context_uri_usage(self, sample_project_with_mcp):
        """Test using MCP context URIs."""
        project = sample_project_with_mcp
        server = MockMemoryMCPServer()
        connection = MockMCPConnection(server)
        await connection.connect()
        
        # Store data for each context URI
        for uri in project.mcp_context_uris:
            # Extract a key from URI (simplified)
            key = uri.replace("://", ":").replace("/", ":")
            await connection.call("store", {
                "key": key,
                "value": {"uri": uri, "data": "context-specific-data"}
            })
            
        # Retrieve and verify
        for uri in project.mcp_context_uris:
            key = uri.replace("://", ":").replace("/", ":")
            result = await connection.call("retrieve", {"key": key})
            assert result["success"] is True
            assert result["data"]["value"]["uri"] == uri
            
        await connection.disconnect()
        
    @pytest.mark.asyncio
    async def test_mcp_performance_monitoring(self):
        """Test monitoring MCP performance."""
        from claude_manager.tests.mcp.mocks import MockMCPMetricsCollector
        
        server = MockMemoryMCPServer()
        connection = MockMCPConnection(server)
        metrics = MockMCPMetricsCollector()
        
        # Monitor connection
        start_time = asyncio.get_event_loop().time()
        await connection.connect()
        connection_time = asyncio.get_event_loop().time() - start_time
        metrics.record_connection(connection_time)
        
        # Monitor operations
        operations = [
            ("store", {"key": f"key{i}", "value": f"value{i}"})
            for i in range(10)
        ]
        
        for method, params in operations:
            start_time = asyncio.get_event_loop().time()
            result = await connection.call(method, params)
            operation_time = asyncio.get_event_loop().time() - start_time
            metrics.record_request(operation_time, success=result.get("success", False))
            
        # Check metrics
        summary = metrics.get_metrics_summary()
        assert summary["counters"]["total_requests"] == 10
        assert summary["counters"]["successful_requests"] == 10
        assert summary["timings"]["request_processing_time"]["count"] == 10
        
        await connection.disconnect()
        metrics.record_disconnection()
        
    @pytest.mark.asyncio
    async def test_mcp_config_update_and_reload(self, tmp_path):
        """Test updating MCP config and reloading servers."""
        # Initial config
        config_file = tmp_path / "claude-code.json"
        project_dir = tmp_path / "test"
        project_dir.mkdir(exist_ok=True)
        project_path = str(project_dir)
        
        config_data = {
            "version": "1.0",
            "projects": {
                project_path: {
                    "mcpServers": {
                        "server1": {"command": "cmd1"}
                    }
                }
            }
        }
        config_file.write_text(json.dumps(config_data))
        
        config_manager = ClaudeConfigManager(config_file)
        server_pool = MockMCPServerPool()
        
        # Setup initial servers
        projects = config_manager.get_projects()
        project = list(projects.values())[0]
        
        for server_name in project.mcp_servers:
            server_pool.add_server(server_name, MockMemoryMCPServer())
            
        await server_pool.start_all()
        initial_status = server_pool.get_status()
        assert "server1" in initial_status
        
        # Update config with new server
        project.mcp_servers["server2"] = {"command": "cmd2"}
        config_manager.update_project(project)
        
        # Simulate reload by creating new pool
        new_pool = MockMCPServerPool()
        
        # Reload projects
        config_manager.load_config()
        updated_projects = config_manager.get_projects()
        updated_project = list(updated_projects.values())[0]
        
        # Setup servers from updated config
        for server_name in updated_project.mcp_servers:
            new_pool.add_server(server_name, MockMemoryMCPServer())
            
        await new_pool.start_all()
        new_status = new_pool.get_status()
        
        assert "server1" in new_status
        assert "server2" in new_status
        
        # Cleanup
        await server_pool.stop_all()
        await new_pool.stop_all()
        
    @pytest.mark.asyncio
    async def test_mcp_error_handling_chain(self):
        """Test error handling through the MCP chain."""
        event_bus = MockMCPEventBus()
        await event_bus.start()
        
        notification_service = MockMCPNotificationService(event_bus)
        server = MockMemoryMCPServer()
        
        # Don't start server to simulate error
        connection = MockMCPConnection(server)
        
        # Try to connect (server not running)
        try:
            # Force connection without starting server
            connection.connected = True
            await connection.call("store", {"key": "test", "value": "data"})
        except Exception as e:
            # Notify error
            await notification_service.notify_server_error("test-server", str(e))
            
        # Check error was recorded
        events = event_bus.get_events(MCPEventType.SERVER_ERROR)
        assert len(events) == 1
        assert "Server not running" in events[0].data["error"]
        
        notifications = notification_service.get_notifications("server_error")
        assert len(notifications) == 1
        
        await event_bus.stop()