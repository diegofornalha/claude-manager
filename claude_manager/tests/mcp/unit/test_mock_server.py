"""Unit tests for mock MCP server implementation."""
import pytest
import asyncio
from claude_manager.tests.mcp.mocks import (
    MockMemoryMCPServer,
    MockMCPConnection,
    MockMCPServerPool,
    MCPRequest,
    MCPResponse
)


class TestMockMemoryMCPServer:
    """Test the mock Memory MCP server."""
    
    @pytest.mark.asyncio
    async def test_server_lifecycle(self):
        """Test server start and stop."""
        server = MockMemoryMCPServer()
        assert not server.running
        
        await server.start()
        assert server.running
        
        await server.stop()
        assert not server.running
        
    @pytest.mark.asyncio
    async def test_store_and_retrieve(self):
        """Test storing and retrieving values."""
        server = MockMemoryMCPServer()
        await server.start()
        
        # Store a value
        store_request = MCPRequest(
            id="req1",
            method="store",
            params={"key": "test-key", "value": "test-value"}
        )
        response = await server.handle_request(store_request)
        
        assert response.error is None
        assert response.result["success"] is True
        assert response.result["key"] == "test-key"
        
        # Retrieve the value
        retrieve_request = MCPRequest(
            id="req2",
            method="retrieve",
            params={"key": "test-key"}
        )
        response = await server.handle_request(retrieve_request)
        
        assert response.error is None
        assert response.result["success"] is True
        assert response.result["data"]["value"] == "test-value"
        
        await server.stop()
        
    @pytest.mark.asyncio
    async def test_list_keys(self):
        """Test listing keys with prefix filtering."""
        server = MockMemoryMCPServer()
        await server.start()
        
        # Store multiple values
        keys = ["app:config", "app:state", "user:prefs", "user:data"]
        for key in keys:
            request = MCPRequest(
                id=f"store_{key}",
                method="store",
                params={"key": key, "value": f"value_{key}"}
            )
            await server.handle_request(request)
            
        # List all keys
        list_request = MCPRequest(id="list1", method="list", params={})
        response = await server.handle_request(list_request)
        
        assert response.result["success"] is True
        assert response.result["count"] == 4
        assert set(response.result["keys"]) == set(keys)
        
        # List with prefix
        list_request = MCPRequest(
            id="list2",
            method="list",
            params={"prefix": "app:"}
        )
        response = await server.handle_request(list_request)
        
        assert response.result["count"] == 2
        assert set(response.result["keys"]) == {"app:config", "app:state"}
        
        await server.stop()
        
    @pytest.mark.asyncio
    async def test_delete_key(self):
        """Test deleting keys."""
        server = MockMemoryMCPServer()
        await server.start()
        
        # Store a value
        await server.handle_request(MCPRequest(
            id="store1",
            method="store",
            params={"key": "delete-me", "value": "temp"}
        ))
        
        # Verify it exists
        response = await server.handle_request(MCPRequest(
            id="check1",
            method="retrieve",
            params={"key": "delete-me"}
        ))
        assert response.result["success"] is True
        
        # Delete it
        response = await server.handle_request(MCPRequest(
            id="delete1",
            method="delete",
            params={"key": "delete-me"}
        ))
        assert response.result["success"] is True
        
        # Verify it's gone
        response = await server.handle_request(MCPRequest(
            id="check2",
            method="retrieve",
            params={"key": "delete-me"}
        ))
        assert response.result["success"] is False
        assert response.result["error"] == "Key not found"
        
        await server.stop()
        
    @pytest.mark.asyncio
    async def test_clear_memory(self):
        """Test clearing all memory."""
        server = MockMemoryMCPServer()
        await server.start()
        
        # Store multiple values
        for i in range(5):
            await server.handle_request(MCPRequest(
                id=f"store{i}",
                method="store",
                params={"key": f"key{i}", "value": f"value{i}"}
            ))
            
        # Clear without confirmation (should fail)
        response = await server.handle_request(MCPRequest(
            id="clear1",
            method="clear",
            params={}
        ))
        assert response.error is not None
        
        # Clear with confirmation
        response = await server.handle_request(MCPRequest(
            id="clear2",
            method="clear",
            params={"confirm": True}
        ))
        assert response.result["success"] is True
        assert response.result["cleared"] == 5
        
        # Verify all cleared
        response = await server.handle_request(MCPRequest(
            id="list1",
            method="list",
            params={}
        ))
        assert response.result["count"] == 0
        
        await server.stop()
        
    @pytest.mark.asyncio
    async def test_server_stats(self):
        """Test getting server statistics."""
        server = MockMemoryMCPServer()
        await server.start()
        
        # Make some requests
        await server.handle_request(MCPRequest(
            id="store1",
            method="store",
            params={"key": "k1", "value": "v1"}
        ))
        await server.handle_request(MCPRequest(
            id="retrieve1",
            method="retrieve",
            params={"key": "k1"}
        ))
        
        # Get stats
        response = await server.handle_request(MCPRequest(
            id="stats1",
            method="stats",
            params={}
        ))
        
        stats = response.result["stats"]
        assert stats["total_keys"] == 1
        assert stats["running"] is True
        assert stats["request_count"] == 3  # store, retrieve, stats
        assert stats["response_count"] == 3
        
        await server.stop()
        
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling in mock server."""
        server = MockMemoryMCPServer()
        await server.start()
        
        # Invalid method
        response = await server.handle_request(MCPRequest(
            id="invalid1",
            method="invalid_method",
            params={}
        ))
        assert response.error is not None
        assert "Method not found" in response.error["message"]
        
        # Missing required parameter
        response = await server.handle_request(MCPRequest(
            id="invalid2",
            method="store",
            params={"value": "no-key"}  # Missing key
        ))
        assert response.error is not None
        assert "Key is required" in response.error["message"]
        
        await server.stop()
        
    @pytest.mark.asyncio
    async def test_server_not_running(self):
        """Test handling requests when server is not running."""
        server = MockMemoryMCPServer()
        # Don't start the server
        
        response = await server.handle_request(MCPRequest(
            id="req1",
            method="store",
            params={"key": "k", "value": "v"}
        ))
        
        assert response.error is not None
        assert "Server not running" in response.error["message"]


class TestMockMCPConnection:
    """Test the mock MCP connection."""
    
    @pytest.mark.asyncio
    async def test_connection_lifecycle(self):
        """Test connection connect and disconnect."""
        connection = MockMCPConnection()
        assert not connection.connected
        
        success = await connection.connect()
        assert success
        assert connection.connected
        assert connection.server.running
        
        await connection.disconnect()
        assert not connection.connected
        
    @pytest.mark.asyncio
    async def test_send_and_receive(self):
        """Test sending requests and receiving responses."""
        connection = MockMCPConnection()
        await connection.connect()
        
        # Send request
        request_id = await connection.send_request(
            "store",
            {"key": "test", "value": "data"}
        )
        assert request_id.startswith("req_")
        
        # Receive response
        response = await connection.receive_response(request_id)
        assert response.id == request_id
        assert response.error is None
        assert response.result["success"] is True
        
        await connection.disconnect()
        
    @pytest.mark.asyncio
    async def test_call_convenience_method(self):
        """Test the call convenience method."""
        connection = MockMCPConnection()
        await connection.connect()
        
        # Store value
        result = await connection.call("store", {"key": "k", "value": "v"})
        assert result["success"] is True
        
        # Retrieve value
        result = await connection.call("retrieve", {"key": "k"})
        assert result["success"] is True
        assert result["data"]["value"] == "v"
        
        await connection.disconnect()
        
    @pytest.mark.asyncio
    async def test_connection_errors(self):
        """Test connection error handling."""
        connection = MockMCPConnection()
        
        # Try to send without connecting
        with pytest.raises(RuntimeError, match="Not connected"):
            await connection.send_request("test", {})
            
        # Try to receive without connecting
        with pytest.raises(RuntimeError, match="Not connected"):
            await connection.receive_response("req_1")
            
        # Connect and try invalid request
        await connection.connect()
        with pytest.raises(Exception, match="MCP Error"):
            await connection.call("invalid_method", {})
            
        await connection.disconnect()


class TestMockMCPServerPool:
    """Test the mock MCP server pool."""
    
    @pytest.mark.asyncio
    async def test_server_pool_management(self):
        """Test managing multiple servers in a pool."""
        pool = MockMCPServerPool()
        
        # Add servers
        server1 = MockMemoryMCPServer("/tmp/memory1")
        server2 = MockMemoryMCPServer("/tmp/memory2")
        
        pool.add_server("memory1", server1)
        pool.add_server("memory2", server2)
        
        # Start all servers
        await pool.start_all()
        assert server1.running
        assert server2.running
        
        # Get connections
        conn1 = await pool.get_connection("memory1")
        conn2 = await pool.get_connection("memory2")
        
        assert conn1.is_connected()
        assert conn2.is_connected()
        
        # Use connections
        await conn1.call("store", {"key": "k1", "value": "v1"})
        await conn2.call("store", {"key": "k2", "value": "v2"})
        
        # Get status
        status = pool.get_status()
        assert status["memory1"]["running"] is True
        assert status["memory1"]["connected"] is True
        assert status["memory1"]["memory_keys"] == 1
        assert status["memory2"]["memory_keys"] == 1
        
        # Stop all
        await pool.stop_all()
        assert not server1.running
        assert not server2.running
        assert not conn1.is_connected()
        assert not conn2.is_connected()
        
    @pytest.mark.asyncio
    async def test_pool_connection_reuse(self):
        """Test that connections are reused in the pool."""
        pool = MockMCPServerPool()
        pool.add_server("test", MockMemoryMCPServer())
        
        # Get connection twice
        conn1 = await pool.get_connection("test")
        conn2 = await pool.get_connection("test")
        
        # Should be the same connection
        assert conn1 is conn2
        
        await pool.stop_all()
        
    @pytest.mark.asyncio
    async def test_pool_invalid_server(self):
        """Test getting connection for non-existent server."""
        pool = MockMCPServerPool()
        
        with pytest.raises(ValueError, match="Server invalid not found"):
            await pool.get_connection("invalid")