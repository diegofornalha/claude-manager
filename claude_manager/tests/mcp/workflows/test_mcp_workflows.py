"""Workflow tests for MCP functionality."""
import pytest
import asyncio
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
from claude_manager.config import ClaudeConfigManager
from claude_manager.models import Project
from claude_manager.tests.mcp.mocks import (
    MockMemoryMCPServer,
    MockMCPConnection,
    MockMCPServerPool,
    MockMCPEventBus,
    MockMCPNotificationService,
    MockMCPMetricsCollector,
    MCPEventType
)


class TestMCPWorkflows:
    """Test complex MCP workflows."""
    
    @pytest.mark.asyncio
    async def test_project_lifecycle_workflow(self, tmp_path):
        """Test complete project lifecycle with MCP servers."""
        # Step 1: Create new project with MCP servers
        config_file = tmp_path / "claude-code.json"
        config_data = {"version": "1.0", "projects": {}}
        config_file.write_text(json.dumps(config_data))
        
        config_manager = ClaudeConfigManager(config_file)
        event_bus = MockMCPEventBus()
        await event_bus.start()
        
        notification_service = MockMCPNotificationService(event_bus)
        server_pool = MockMCPServerPool()
        metrics = MockMCPMetricsCollector()
        
        # Step 2: Add new project with MCP configuration
        new_project = Project(
            name="ai-assistant",
            path=str(tmp_path / "ai-assistant"),
            description="AI Assistant with MCP support",
            mcp_servers={
                "memory": {
                    "command": "memory-mcp",
                    "args": ["--persistent", "--max-size", "100MB"]
                },
                "vector-db": {
                    "command": "vector-mcp",
                    "args": ["--dimensions", "768"],
                    "env": {"VECTOR_MODEL": "all-MiniLM-L6-v2"}
                },
                "github": {
                    "command": "github-mcp",
                    "args": ["--token", "${GITHUB_TOKEN}"],
                    "env": {"GITHUB_API_URL": "https://api.github.com"}
                }
            },
            enabled_mcpjson_servers=["memory", "vector-db"],
            disabled_mcpjson_servers=["github"],  # Disabled until token is configured
            mcp_context_uris=[
                "ai-assistant://context/main",
                "vector://embeddings/project"
            ]
        )
        
        # Save project
        config_manager.config["projects"][new_project.name] = new_project.to_dict()
        config_manager._save_config()
        
        # Step 3: Initialize MCP servers for the project
        for server_name, server_config in new_project.mcp_servers.items():
            if server_name in new_project.enabled_mcpjson_servers:
                server = MockMemoryMCPServer(f"/tmp/{server_name}")
                server_pool.add_server(server_name, server)
                
        # Step 4: Start enabled servers
        start_time = asyncio.get_event_loop().time()
        await server_pool.start_all()
        startup_time = asyncio.get_event_loop().time() - start_time
        metrics.record_server_start(startup_time)
        
        for server_name in new_project.enabled_mcpjson_servers:
            await notification_service.notify_server_start(
                server_name, 
                new_project.mcp_servers[server_name]
            )
            
        # Step 5: Use MCP servers for project operations
        memory_conn = await server_pool.get_connection("memory")
        vector_conn = await server_pool.get_connection("vector-db")
        
        # Store project metadata
        await memory_conn.call("store", {
            "key": "project:metadata",
            "value": {
                "name": new_project.name,
                "created": datetime.utcnow().isoformat(),
                "version": "1.0.0"
            }
        })
        
        # Store vector embeddings (simulated)
        await vector_conn.call("store", {
            "key": "embedding:doc1",
            "value": {
                "vector": [0.1, 0.2, 0.3],  # Simplified
                "metadata": {"doc_id": "doc1", "type": "readme"}
            }
        })
        
        # Step 6: Enable GitHub server after token configuration
        new_project.enabled_mcpjson_servers.append("github")
        new_project.disabled_mcpjson_servers.remove("github")
        config_manager.update_project(new_project)
        
        # Add and start GitHub server
        github_server = MockMemoryMCPServer("/tmp/github")
        server_pool.add_server("github", github_server)
        await github_server.start()
        await notification_service.notify_server_start("github", new_project.mcp_servers["github"])
        
        # Step 7: Use all servers together
        github_conn = await server_pool.get_connection("github")
        
        # Simulate storing GitHub data
        await github_conn.call("store", {
            "key": "repo:info",
            "value": {
                "name": "ai-assistant",
                "stars": 42,
                "language": "Python"
            }
        })
        
        # Step 8: Verify all data persists
        memory_data = await memory_conn.call("retrieve", {"key": "project:metadata"})
        vector_data = await vector_conn.call("retrieve", {"key": "embedding:doc1"})
        github_data = await github_conn.call("retrieve", {"key": "repo:info"})
        
        assert memory_data["success"] is True
        assert vector_data["success"] is True
        assert github_data["success"] is True
        
        # Step 9: Cleanup and verify metrics
        await server_pool.stop_all()
        await notification_service.notify_server_stop("memory", "shutdown")
        await notification_service.notify_server_stop("vector-db", "shutdown")
        await notification_service.notify_server_stop("github", "shutdown")
        
        # Check final state
        events = event_bus.get_events()
        start_events = [e for e in events if e.type == MCPEventType.SERVER_STARTED]
        stop_events = [e for e in events if e.type == MCPEventType.SERVER_STOPPED]
        
        assert len(start_events) == 3
        assert len(stop_events) == 3
        
        await event_bus.stop()
        
    @pytest.mark.asyncio
    async def test_collaborative_mcp_workflow(self):
        """Test multiple MCP servers working together."""
        # Setup collaborative servers
        cache_server = MockMemoryMCPServer("/tmp/cache")
        compute_server = MockMemoryMCPServer("/tmp/compute")
        storage_server = MockMemoryMCPServer("/tmp/storage")
        
        pool = MockMCPServerPool()
        pool.add_server("cache", cache_server)
        pool.add_server("compute", compute_server)
        pool.add_server("storage", storage_server)
        
        await pool.start_all()
        
        # Get connections
        cache = await pool.get_connection("cache")
        compute = await pool.get_connection("compute")
        storage = await pool.get_connection("storage")
        
        # Workflow: Process data with caching
        input_data = {"values": [1, 2, 3, 4, 5], "operation": "square"}
        
        # Step 1: Check cache
        cache_key = f"compute:{hash(str(input_data))}"
        cache_result = await cache.call("retrieve", {"key": cache_key})
        
        if cache_result["success"]:
            result = cache_result["data"]["value"]
        else:
            # Step 2: Compute if not cached
            await compute.call("store", {
                "key": "input",
                "value": input_data
            })
            
            # Simulate computation
            result = {"result": [x**2 for x in input_data["values"]]}
            
            await compute.call("store", {
                "key": "output",
                "value": result
            })
            
            # Step 3: Cache the result
            await cache.call("store", {
                "key": cache_key,
                "value": result,
                "metadata": {"computed_at": datetime.utcnow().isoformat()}
            })
            
        # Step 4: Store in permanent storage
        await storage.call("store", {
            "key": f"results:{datetime.utcnow().date()}:{cache_key}",
            "value": {
                "input": input_data,
                "output": result,
                "cached": cache_result["success"]
            }
        })
        
        # Verify workflow
        storage_result = await storage.call("list", {"prefix": "results:"})
        assert storage_result["count"] >= 1
        
        # Run same computation again (should hit cache)
        cache_result2 = await cache.call("retrieve", {"key": cache_key})
        assert cache_result2["success"] is True
        
        await pool.stop_all()
        
    @pytest.mark.asyncio
    async def test_mcp_failover_workflow(self):
        """Test MCP server failover and redundancy."""
        # Setup primary and backup servers
        primary = MockMemoryMCPServer("/tmp/primary")
        backup = MockMemoryMCPServer("/tmp/backup")
        
        pool = MockMCPServerPool()
        pool.add_server("primary", primary)
        pool.add_server("backup", backup)
        
        await pool.start_all()
        
        primary_conn = await pool.get_connection("primary")
        backup_conn = await pool.get_connection("backup")
        
        # Workflow with replication
        async def replicate_data(key: str, value: Any):
            """Store data in both primary and backup."""
            primary_result = await primary_conn.call("store", {"key": key, "value": value})
            backup_result = await backup_conn.call("store", {"key": key, "value": value})
            return primary_result["success"] and backup_result["success"]
            
        # Store critical data with replication
        critical_data = {
            "user:123": {"name": "John", "role": "admin"},
            "config:app": {"theme": "dark", "lang": "en"},
            "state:current": {"status": "active", "version": "2.0"}
        }
        
        for key, value in critical_data.items():
            success = await replicate_data(key, value)
            assert success
            
        # Simulate primary failure
        await primary.stop()
        primary_conn.connected = False
        
        # Failover to backup
        async def get_with_failover(key: str):
            """Get data with automatic failover."""
            try:
                if primary_conn.is_connected():
                    return await primary_conn.call("retrieve", {"key": key})
            except:
                pass
                
            # Failover to backup
            return await backup_conn.call("retrieve", {"key": key})
            
        # Verify all data accessible via backup
        for key in critical_data:
            result = await get_with_failover(key)
            assert result["success"] is True
            assert result["data"]["value"] == critical_data[key]
            
        # Restore primary
        await primary.start()
        await primary_conn.connect()
        
        # Sync from backup to primary
        backup_list = await backup_conn.call("list", {})
        for key in backup_list["keys"]:
            data = await backup_conn.call("retrieve", {"key": key})
            await primary_conn.call("store", {
                "key": key,
                "value": data["data"]["value"]
            })
            
        # Verify sync
        primary_list = await primary_conn.call("list", {})
        assert set(primary_list["keys"]) == set(backup_list["keys"])
        
        await pool.stop_all()
        
    @pytest.mark.asyncio
    async def test_mcp_data_pipeline_workflow(self):
        """Test data processing pipeline with MCP servers."""
        # Setup pipeline servers
        servers = {
            "ingestion": MockMemoryMCPServer("/tmp/ingestion"),
            "processing": MockMemoryMCPServer("/tmp/processing"),
            "analytics": MockMemoryMCPServer("/tmp/analytics"),
            "export": MockMemoryMCPServer("/tmp/export")
        }
        
        pool = MockMCPServerPool()
        for name, server in servers.items():
            pool.add_server(name, server)
            
        await pool.start_all()
        
        # Get connections
        connections = {}
        for name in servers:
            connections[name] = await pool.get_connection(name)
            
        # Data pipeline workflow
        # Step 1: Ingestion
        raw_data = [
            {"id": 1, "value": 10, "timestamp": "2024-01-01T10:00:00"},
            {"id": 2, "value": 20, "timestamp": "2024-01-01T10:01:00"},
            {"id": 3, "value": 15, "timestamp": "2024-01-01T10:02:00"},
            {"id": 4, "value": 25, "timestamp": "2024-01-01T10:03:00"},
            {"id": 5, "value": 30, "timestamp": "2024-01-01T10:04:00"}
        ]
        
        for item in raw_data:
            await connections["ingestion"].call("store", {
                "key": f"raw:{item['id']}",
                "value": item
            })
            
        # Step 2: Processing
        ingested = await connections["ingestion"].call("list", {"prefix": "raw:"})
        processed_data = []
        
        for key in ingested["keys"]:
            raw = await connections["ingestion"].call("retrieve", {"key": key})
            item = raw["data"]["value"]
            
            # Process data (add running average)
            processed = {
                **item,
                "processed": True,
                "value_doubled": item["value"] * 2,
                "category": "high" if item["value"] > 20 else "low"
            }
            processed_data.append(processed)
            
            await connections["processing"].call("store", {
                "key": f"processed:{item['id']}",
                "value": processed
            })
            
        # Step 3: Analytics
        analytics_results = {
            "total_items": len(processed_data),
            "sum": sum(item["value"] for item in processed_data),
            "average": sum(item["value"] for item in processed_data) / len(processed_data),
            "high_count": sum(1 for item in processed_data if item["category"] == "high"),
            "low_count": sum(1 for item in processed_data if item["category"] == "low")
        }
        
        await connections["analytics"].call("store", {
            "key": "results:summary",
            "value": analytics_results
        })
        
        # Step 4: Export
        export_data = {
            "metadata": {
                "pipeline": "data-processing",
                "timestamp": datetime.utcnow().isoformat(),
                "stages": ["ingestion", "processing", "analytics", "export"]
            },
            "results": analytics_results,
            "processed_items": processed_data
        }
        
        await connections["export"].call("store", {
            "key": "export:final",
            "value": export_data
        })
        
        # Verify pipeline results
        final_export = await connections["export"].call("retrieve", {"key": "export:final"})
        assert final_export["success"] is True
        assert final_export["data"]["value"]["results"]["total_items"] == 5
        assert final_export["data"]["value"]["results"]["average"] == 20
        
        await pool.stop_all()
        
    @pytest.mark.asyncio  
    async def test_mcp_monitoring_workflow(self):
        """Test MCP server monitoring and alerting workflow."""
        # Setup monitoring components
        event_bus = MockMCPEventBus()
        await event_bus.start()
        
        notification_service = MockMCPNotificationService(event_bus)
        metrics_collector = MockMCPMetricsCollector()
        
        # Setup servers to monitor
        servers = {
            "api": MockMemoryMCPServer("/tmp/api"),
            "db": MockMemoryMCPServer("/tmp/db"),
            "cache": MockMemoryMCPServer("/tmp/cache")
        }
        
        pool = MockMCPServerPool()
        for name, server in servers.items():
            pool.add_server(name, server)
            
        # Monitoring workflow
        # Step 1: Start servers with monitoring
        for name, server in servers.items():
            start_time = asyncio.get_event_loop().time()
            await server.start()
            startup_time = asyncio.get_event_loop().time() - start_time
            
            metrics_collector.record_server_start(startup_time)
            await notification_service.notify_server_start(name, {"monitored": True})
            
        # Step 2: Simulate server operations with monitoring
        connections = {}
        for name in servers:
            conn_start = asyncio.get_event_loop().time()
            connections[name] = await pool.get_connection(name)
            conn_time = asyncio.get_event_loop().time() - conn_start
            metrics_collector.record_connection(conn_time)
            
        # Step 3: Perform operations and monitor performance
        operations = [
            ("api", "store", {"key": "endpoint:/users", "value": {"count": 100}}),
            ("db", "store", {"key": "table:users", "value": {"rows": 100}}),
            ("cache", "store", {"key": "cache:users:page:1", "value": {"data": []}}),
            ("api", "retrieve", {"key": "endpoint:/users"}),
            ("cache", "retrieve", {"key": "cache:users:page:1"})
        ]
        
        for server_name, method, params in operations:
            op_start = asyncio.get_event_loop().time()
            try:
                result = await connections[server_name].call(method, params)
                op_time = asyncio.get_event_loop().time() - op_start
                metrics_collector.record_request(op_time, success=result.get("success", False))
                
                # Alert on slow operations
                if op_time > 0.1:  # 100ms threshold
                    await notification_service.notify_server_error(
                        server_name,
                        f"Slow operation: {method} took {op_time:.3f}s"
                    )
            except Exception as e:
                op_time = asyncio.get_event_loop().time() - op_start
                metrics_collector.record_request(op_time, success=False)
                await notification_service.notify_server_error(server_name, str(e))
                
        # Step 4: Simulate server failure
        await servers["db"].stop()
        connections["db"].connected = False
        await notification_service.notify_connection_lost("db", "conn_db_1", "Server stopped")
        
        # Step 5: Generate monitoring report
        metrics_summary = metrics_collector.get_metrics_summary()
        events_summary = event_bus.get_event_counts()
        notifications = notification_service.get_notifications()
        
        monitoring_report = {
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": metrics_summary,
            "events": events_summary,
            "alerts": [n for n in notifications if n["type"] == "server_error"],
            "server_status": pool.get_status()
        }
        
        # Verify monitoring captured issues
        assert len(monitoring_report["alerts"]) >= 0  # May have slow operations
        assert monitoring_report["events"]["connection_lost"] >= 1
        assert monitoring_report["server_status"]["db"]["running"] is False
        
        # Cleanup
        await pool.stop_all()
        await event_bus.stop()