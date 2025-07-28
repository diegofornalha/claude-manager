"""Mock MCP Events and Notifications for Testing."""
import asyncio
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class MCPEventType(Enum):
    """Types of MCP events."""
    SERVER_STARTED = "server_started"
    SERVER_STOPPED = "server_stopped"
    SERVER_ERROR = "server_error"
    CONNECTION_ESTABLISHED = "connection_established"
    CONNECTION_LOST = "connection_lost"
    REQUEST_RECEIVED = "request_received"
    RESPONSE_SENT = "response_sent"
    MEMORY_STORED = "memory_stored"
    MEMORY_RETRIEVED = "memory_retrieved"
    MEMORY_DELETED = "memory_deleted"
    

@dataclass
class MCPEvent:
    """MCP Event structure."""
    type: MCPEventType
    timestamp: datetime
    server_name: str
    data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "type": self.type.value,
            "timestamp": self.timestamp.isoformat(),
            "server_name": self.server_name,
            "data": self.data
        }


class MockMCPEventBus:
    """Mock event bus for MCP events."""
    
    def __init__(self):
        self.events: List[MCPEvent] = []
        self.subscribers: Dict[MCPEventType, List[Callable]] = {}
        self._running = False
        self._event_queue: asyncio.Queue = asyncio.Queue()
        
    async def start(self):
        """Start the event bus."""
        self._running = True
        asyncio.create_task(self._process_events())
        
    async def stop(self):
        """Stop the event bus."""
        self._running = False
        await self._event_queue.join()
        
    async def emit(self, event: MCPEvent):
        """Emit an event."""
        self.events.append(event)
        await self._event_queue.put(event)
        
    def subscribe(self, event_type: MCPEventType, handler: Callable):
        """Subscribe to an event type."""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)
        
    def unsubscribe(self, event_type: MCPEventType, handler: Callable):
        """Unsubscribe from an event type."""
        if event_type in self.subscribers:
            self.subscribers[event_type].remove(handler)
            
    async def _process_events(self):
        """Process events from the queue."""
        while self._running:
            try:
                event = await asyncio.wait_for(
                    self._event_queue.get(), 
                    timeout=0.1
                )
                
                # Notify subscribers
                handlers = self.subscribers.get(event.type, [])
                for handler in handlers:
                    try:
                        if asyncio.iscoroutinefunction(handler):
                            await handler(event)
                        else:
                            handler(event)
                    except Exception as e:
                        # Log error but continue processing
                        print(f"Error in event handler: {e}")
                        
            except asyncio.TimeoutError:
                continue
                
    def get_events(self, event_type: Optional[MCPEventType] = None) -> List[MCPEvent]:
        """Get events, optionally filtered by type."""
        if event_type:
            return [e for e in self.events if e.type == event_type]
        return self.events.copy()
        
    def clear_events(self):
        """Clear all stored events."""
        self.events.clear()
        
    def get_event_counts(self) -> Dict[str, int]:
        """Get count of each event type."""
        counts = {}
        for event in self.events:
            counts[event.type.value] = counts.get(event.type.value, 0) + 1
        return counts


class MockMCPNotificationService:
    """Mock notification service for MCP operations."""
    
    def __init__(self, event_bus: MockMCPEventBus):
        self.event_bus = event_bus
        self.notifications: List[Dict[str, Any]] = []
        
    async def notify_server_start(self, server_name: str, config: Dict[str, Any]):
        """Notify that a server has started."""
        event = MCPEvent(
            type=MCPEventType.SERVER_STARTED,
            timestamp=datetime.utcnow(),
            server_name=server_name,
            data={"config": config}
        )
        await self.event_bus.emit(event)
        self._store_notification("server_start", server_name, config)
        
    async def notify_server_stop(self, server_name: str, reason: str = "normal"):
        """Notify that a server has stopped."""
        event = MCPEvent(
            type=MCPEventType.SERVER_STOPPED,
            timestamp=datetime.utcnow(),
            server_name=server_name,
            data={"reason": reason}
        )
        await self.event_bus.emit(event)
        self._store_notification("server_stop", server_name, {"reason": reason})
        
    async def notify_server_error(self, server_name: str, error: str):
        """Notify that a server encountered an error."""
        event = MCPEvent(
            type=MCPEventType.SERVER_ERROR,
            timestamp=datetime.utcnow(),
            server_name=server_name,
            data={"error": error}
        )
        await self.event_bus.emit(event)
        self._store_notification("server_error", server_name, {"error": error})
        
    async def notify_connection_established(self, server_name: str, connection_id: str):
        """Notify that a connection was established."""
        event = MCPEvent(
            type=MCPEventType.CONNECTION_ESTABLISHED,
            timestamp=datetime.utcnow(),
            server_name=server_name,
            data={"connection_id": connection_id}
        )
        await self.event_bus.emit(event)
        self._store_notification("connection_established", server_name, {"connection_id": connection_id})
        
    async def notify_connection_lost(self, server_name: str, connection_id: str, reason: str):
        """Notify that a connection was lost."""
        event = MCPEvent(
            type=MCPEventType.CONNECTION_LOST,
            timestamp=datetime.utcnow(),
            server_name=server_name,
            data={"connection_id": connection_id, "reason": reason}
        )
        await self.event_bus.emit(event)
        self._store_notification("connection_lost", server_name, {
            "connection_id": connection_id, 
            "reason": reason
        })
        
    def _store_notification(self, type: str, server_name: str, data: Dict[str, Any]):
        """Store a notification."""
        self.notifications.append({
            "type": type,
            "server_name": server_name,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data
        })
        
    def get_notifications(self, type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get notifications, optionally filtered by type."""
        if type:
            return [n for n in self.notifications if n["type"] == type]
        return self.notifications.copy()
        
    def clear_notifications(self):
        """Clear all notifications."""
        self.notifications.clear()


class MockMCPMetricsCollector:
    """Mock metrics collector for MCP operations."""
    
    def __init__(self):
        self.metrics: Dict[str, List[float]] = {
            "server_start_time": [],
            "server_stop_time": [],
            "request_processing_time": [],
            "connection_establishment_time": [],
            "memory_operation_time": []
        }
        self.counters: Dict[str, int] = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_connections": 0,
            "active_connections": 0
        }
        
    def record_server_start(self, duration: float):
        """Record server start time."""
        self.metrics["server_start_time"].append(duration)
        
    def record_server_stop(self, duration: float):
        """Record server stop time."""
        self.metrics["server_stop_time"].append(duration)
        
    def record_request(self, duration: float, success: bool = True):
        """Record request processing time."""
        self.metrics["request_processing_time"].append(duration)
        self.counters["total_requests"] += 1
        if success:
            self.counters["successful_requests"] += 1
        else:
            self.counters["failed_requests"] += 1
            
    def record_connection(self, duration: float):
        """Record connection establishment time."""
        self.metrics["connection_establishment_time"].append(duration)
        self.counters["total_connections"] += 1
        self.counters["active_connections"] += 1
        
    def record_disconnection(self):
        """Record a disconnection."""
        self.counters["active_connections"] = max(0, self.counters["active_connections"] - 1)
        
    def record_memory_operation(self, operation: str, duration: float):
        """Record memory operation time."""
        self.metrics["memory_operation_time"].append(duration)
        
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of all metrics."""
        summary = {
            "counters": self.counters.copy(),
            "timings": {}
        }
        
        for metric_name, values in self.metrics.items():
            if values:
                summary["timings"][metric_name] = {
                    "count": len(values),
                    "min": min(values),
                    "max": max(values),
                    "avg": sum(values) / len(values)
                }
            else:
                summary["timings"][metric_name] = {
                    "count": 0,
                    "min": 0,
                    "max": 0,
                    "avg": 0
                }
                
        return summary
        
    def reset(self):
        """Reset all metrics."""
        for key in self.metrics:
            self.metrics[key].clear()
        for key in self.counters:
            self.counters[key] = 0