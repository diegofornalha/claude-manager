"""Mock MCP Server Implementation for Testing."""
import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field
import uuid

logger = logging.getLogger(__name__)


@dataclass
class MCPRequest:
    """MCP Request structure."""
    id: str
    method: str
    params: Dict[str, Any] = field(default_factory=dict)
    
    
@dataclass
class MCPResponse:
    """MCP Response structure."""
    id: str
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    

class MockMemoryMCPServer:
    """Mock implementation of a Memory MCP server."""
    
    def __init__(self, storage_path: str = "/tmp/memory"):
        self.storage_path = storage_path
        self.memory_store: Dict[str, Any] = {}
        self.running = False
        self.request_handlers: Dict[str, Callable] = {
            "store": self._handle_store,
            "retrieve": self._handle_retrieve,
            "list": self._handle_list,
            "delete": self._handle_delete,
            "clear": self._handle_clear,
            "stats": self._handle_stats
        }
        self._request_log: List[MCPRequest] = []
        self._response_log: List[MCPResponse] = []
        
    async def start(self):
        """Start the mock server."""
        logger.info(f"Starting MockMemoryMCPServer with storage at {self.storage_path}")
        self.running = True
        await asyncio.sleep(0.1)  # Simulate startup time
        
    async def stop(self):
        """Stop the mock server."""
        logger.info("Stopping MockMemoryMCPServer")
        self.running = False
        await asyncio.sleep(0.05)  # Simulate shutdown time
        
    async def handle_request(self, request: MCPRequest) -> MCPResponse:
        """Handle incoming MCP request."""
        if not self.running:
            return MCPResponse(
                id=request.id,
                error={"code": -32603, "message": "Server not running"}
            )
            
        self._request_log.append(request)
        
        handler = self.request_handlers.get(request.method)
        if not handler:
            response = MCPResponse(
                id=request.id,
                error={"code": -32601, "message": f"Method not found: {request.method}"}
            )
        else:
            try:
                result = await handler(request.params)
                response = MCPResponse(id=request.id, result=result)
            except Exception as e:
                response = MCPResponse(
                    id=request.id,
                    error={"code": -32603, "message": str(e)}
                )
                
        self._response_log.append(response)
        return response
        
    async def _handle_store(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Store a value in memory."""
        key = params.get("key")
        value = params.get("value")
        
        if not key:
            raise ValueError("Key is required")
            
        self.memory_store[key] = {
            "value": value,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": params.get("metadata", {})
        }
        
        return {"success": True, "key": key}
        
    async def _handle_retrieve(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve a value from memory."""
        key = params.get("key")
        
        if not key:
            raise ValueError("Key is required")
            
        if key not in self.memory_store:
            return {"success": False, "error": "Key not found"}
            
        return {
            "success": True,
            "key": key,
            "data": self.memory_store[key]
        }
        
    async def _handle_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List all keys in memory."""
        prefix = params.get("prefix", "")
        
        keys = [k for k in self.memory_store.keys() if k.startswith(prefix)]
        
        return {
            "success": True,
            "keys": keys,
            "count": len(keys)
        }
        
    async def _handle_delete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a key from memory."""
        key = params.get("key")
        
        if not key:
            raise ValueError("Key is required")
            
        if key in self.memory_store:
            del self.memory_store[key]
            return {"success": True, "key": key}
        else:
            return {"success": False, "error": "Key not found"}
            
    async def _handle_clear(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Clear all memory."""
        confirm = params.get("confirm", False)
        
        if not confirm:
            raise ValueError("Confirmation required")
            
        count = len(self.memory_store)
        self.memory_store.clear()
        
        return {"success": True, "cleared": count}
        
    async def _handle_stats(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get memory statistics."""
        return {
            "success": True,
            "stats": {
                "total_keys": len(self.memory_store),
                "storage_path": self.storage_path,
                "running": self.running,
                "request_count": len(self._request_log),
                "response_count": len(self._response_log)
            }
        }
        
    def get_logs(self) -> Dict[str, List]:
        """Get request and response logs."""
        return {
            "requests": [
                {
                    "id": req.id,
                    "method": req.method,
                    "params": req.params
                }
                for req in self._request_log
            ],
            "responses": [
                {
                    "id": resp.id,
                    "result": resp.result,
                    "error": resp.error
                }
                for resp in self._response_log
            ]
        }


class MockMCPConnection:
    """Mock MCP connection for testing."""
    
    def __init__(self, server: Optional[MockMemoryMCPServer] = None):
        self.server = server or MockMemoryMCPServer()
        self.connected = False
        self._request_id_counter = 0
        
    async def connect(self) -> bool:
        """Connect to the mock server."""
        if not self.server.running:
            await self.server.start()
        self.connected = True
        return True
        
    async def disconnect(self):
        """Disconnect from the mock server."""
        self.connected = False
        
    async def send_request(self, method: str, params: Dict[str, Any]) -> str:
        """Send a request to the server."""
        if not self.connected:
            raise RuntimeError("Not connected")
            
        self._request_id_counter += 1
        request_id = f"req_{self._request_id_counter}"
        
        request = MCPRequest(id=request_id, method=method, params=params)
        # Store request for async processing
        self._pending_request = request
        
        return request_id
        
    async def receive_response(self, request_id: str) -> MCPResponse:
        """Receive response for a request."""
        if not self.connected:
            raise RuntimeError("Not connected")
            
        # Process the pending request
        if hasattr(self, '_pending_request') and self._pending_request.id == request_id:
            response = await self.server.handle_request(self._pending_request)
            delattr(self, '_pending_request')
            return response
        else:
            return MCPResponse(
                id=request_id,
                error={"code": -32600, "message": "Invalid request"}
            )
            
    async def call(self, method: str, params: Dict[str, Any] = None) -> Any:
        """Convenience method to send request and get response."""
        params = params or {}
        request_id = await self.send_request(method, params)
        response = await self.receive_response(request_id)
        
        if response.error:
            raise Exception(f"MCP Error: {response.error}")
            
        return response.result
        
    def is_connected(self) -> bool:
        """Check if connected."""
        return self.connected


class MockMCPServerPool:
    """Pool of mock MCP servers for testing."""
    
    def __init__(self):
        self.servers: Dict[str, MockMemoryMCPServer] = {}
        self.connections: Dict[str, MockMCPConnection] = {}
        
    def add_server(self, name: str, server: MockMemoryMCPServer):
        """Add a server to the pool."""
        self.servers[name] = server
        
    async def get_connection(self, name: str) -> MockMCPConnection:
        """Get or create a connection to a server."""
        if name not in self.connections:
            if name not in self.servers:
                raise ValueError(f"Server {name} not found")
                
            connection = MockMCPConnection(self.servers[name])
            await connection.connect()
            self.connections[name] = connection
            
        return self.connections[name]
        
    async def start_all(self):
        """Start all servers."""
        for server in self.servers.values():
            if not server.running:
                await server.start()
                
    async def stop_all(self):
        """Stop all servers and close connections."""
        # Disconnect all connections
        for connection in self.connections.values():
            if connection.is_connected():
                await connection.disconnect()
                
        # Stop all servers
        for server in self.servers.values():
            if server.running:
                await server.stop()
                
        self.connections.clear()
        
    def get_status(self) -> Dict[str, Any]:
        """Get status of all servers."""
        return {
            name: {
                "running": server.running,
                "connected": name in self.connections and self.connections[name].is_connected(),
                "memory_keys": len(server.memory_store)
            }
            for name, server in self.servers.items()
        }