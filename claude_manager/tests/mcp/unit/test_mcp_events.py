"""Unit tests for MCP events and notifications."""
import pytest
import asyncio
from datetime import datetime
from claude_manager.tests.mcp.mocks import (
    MCPEventType,
    MCPEvent,
    MockMCPEventBus,
    MockMCPNotificationService,
    MockMCPMetricsCollector
)


class TestMCPEvent:
    """Test MCP event structure."""
    
    def test_event_creation(self):
        """Test creating MCP events."""
        event = MCPEvent(
            type=MCPEventType.SERVER_STARTED,
            timestamp=datetime.utcnow(),
            server_name="test-server",
            data={"config": {"command": "test-mcp"}}
        )
        
        assert event.type == MCPEventType.SERVER_STARTED
        assert event.server_name == "test-server"
        assert "config" in event.data
        
    def test_event_to_dict(self):
        """Test converting event to dictionary."""
        timestamp = datetime.utcnow()
        event = MCPEvent(
            type=MCPEventType.CONNECTION_ESTABLISHED,
            timestamp=timestamp,
            server_name="test",
            data={"connection_id": "conn123"}
        )
        
        event_dict = event.to_dict()
        assert event_dict["type"] == "connection_established"
        assert event_dict["timestamp"] == timestamp.isoformat()
        assert event_dict["server_name"] == "test"
        assert event_dict["data"]["connection_id"] == "conn123"


class TestMockMCPEventBus:
    """Test the mock MCP event bus."""
    
    @pytest.mark.asyncio
    async def test_event_bus_lifecycle(self):
        """Test starting and stopping event bus."""
        bus = MockMCPEventBus()
        await bus.start()
        assert bus._running
        
        await bus.stop()
        assert not bus._running
        
    @pytest.mark.asyncio
    async def test_emit_and_store_events(self):
        """Test emitting and storing events."""
        bus = MockMCPEventBus()
        await bus.start()
        
        # Emit events
        event1 = MCPEvent(
            type=MCPEventType.SERVER_STARTED,
            timestamp=datetime.utcnow(),
            server_name="server1"
        )
        event2 = MCPEvent(
            type=MCPEventType.SERVER_STOPPED,
            timestamp=datetime.utcnow(),
            server_name="server1"
        )
        
        await bus.emit(event1)
        await bus.emit(event2)
        
        # Give time for processing
        await asyncio.sleep(0.2)
        
        # Check stored events
        events = bus.get_events()
        assert len(events) == 2
        assert events[0].type == MCPEventType.SERVER_STARTED
        assert events[1].type == MCPEventType.SERVER_STOPPED
        
        await bus.stop()
        
    @pytest.mark.asyncio
    async def test_event_subscription(self):
        """Test subscribing to events."""
        bus = MockMCPEventBus()
        await bus.start()
        
        # Track received events
        received_events = []
        
        def handler(event):
            received_events.append(event)
            
        # Subscribe to server started events
        bus.subscribe(MCPEventType.SERVER_STARTED, handler)
        
        # Emit various events
        await bus.emit(MCPEvent(
            type=MCPEventType.SERVER_STARTED,
            timestamp=datetime.utcnow(),
            server_name="test1"
        ))
        await bus.emit(MCPEvent(
            type=MCPEventType.SERVER_STOPPED,
            timestamp=datetime.utcnow(),
            server_name="test1"
        ))
        await bus.emit(MCPEvent(
            type=MCPEventType.SERVER_STARTED,
            timestamp=datetime.utcnow(),
            server_name="test2"
        ))
        
        # Give time for processing
        await asyncio.sleep(0.2)
        
        # Should have received only SERVER_STARTED events
        assert len(received_events) == 2
        assert all(e.type == MCPEventType.SERVER_STARTED for e in received_events)
        
        await bus.stop()
        
    @pytest.mark.asyncio
    async def test_async_event_handler(self):
        """Test async event handlers."""
        bus = MockMCPEventBus()
        await bus.start()
        
        processed = []
        
        async def async_handler(event):
            await asyncio.sleep(0.1)  # Simulate async work
            processed.append(event.server_name)
            
        bus.subscribe(MCPEventType.CONNECTION_ESTABLISHED, async_handler)
        
        await bus.emit(MCPEvent(
            type=MCPEventType.CONNECTION_ESTABLISHED,
            timestamp=datetime.utcnow(),
            server_name="async-test"
        ))
        
        # Wait for async processing
        await asyncio.sleep(0.3)
        
        assert "async-test" in processed
        
        await bus.stop()
        
    @pytest.mark.asyncio
    async def test_event_filtering(self):
        """Test filtering events by type."""
        bus = MockMCPEventBus()
        await bus.start()
        
        # Emit various events
        for i in range(3):
            await bus.emit(MCPEvent(
                type=MCPEventType.REQUEST_RECEIVED,
                timestamp=datetime.utcnow(),
                server_name=f"server{i}"
            ))
        for i in range(2):
            await bus.emit(MCPEvent(
                type=MCPEventType.RESPONSE_SENT,
                timestamp=datetime.utcnow(),
                server_name=f"server{i}"
            ))
            
        await asyncio.sleep(0.1)
        
        # Filter by type
        request_events = bus.get_events(MCPEventType.REQUEST_RECEIVED)
        response_events = bus.get_events(MCPEventType.RESPONSE_SENT)
        
        assert len(request_events) == 3
        assert len(response_events) == 2
        
        await bus.stop()
        
    @pytest.mark.asyncio
    async def test_event_counts(self):
        """Test getting event counts."""
        bus = MockMCPEventBus()
        await bus.start()
        
        # Emit various events
        await bus.emit(MCPEvent(MCPEventType.SERVER_STARTED, datetime.utcnow(), "s1"))
        await bus.emit(MCPEvent(MCPEventType.SERVER_STARTED, datetime.utcnow(), "s2"))
        await bus.emit(MCPEvent(MCPEventType.SERVER_STOPPED, datetime.utcnow(), "s1"))
        await bus.emit(MCPEvent(MCPEventType.SERVER_ERROR, datetime.utcnow(), "s2"))
        
        await asyncio.sleep(0.1)
        
        counts = bus.get_event_counts()
        assert counts["server_started"] == 2
        assert counts["server_stopped"] == 1
        assert counts["server_error"] == 1
        
        await bus.stop()


class TestMockMCPNotificationService:
    """Test the mock MCP notification service."""
    
    @pytest.mark.asyncio
    async def test_server_notifications(self):
        """Test server-related notifications."""
        bus = MockMCPEventBus()
        await bus.start()
        
        service = MockMCPNotificationService(bus)
        
        # Notify server start
        await service.notify_server_start("test-server", {"command": "test-mcp"})
        
        # Notify server stop
        await service.notify_server_stop("test-server", "shutdown")
        
        # Notify server error
        await service.notify_server_error("test-server", "Connection failed")
        
        await asyncio.sleep(0.1)
        
        # Check events were emitted
        events = bus.get_events()
        assert len(events) == 3
        
        # Check notifications were stored
        notifications = service.get_notifications()
        assert len(notifications) == 3
        assert notifications[0]["type"] == "server_start"
        assert notifications[1]["type"] == "server_stop"
        assert notifications[2]["type"] == "server_error"
        
        await bus.stop()
        
    @pytest.mark.asyncio
    async def test_connection_notifications(self):
        """Test connection-related notifications."""
        bus = MockMCPEventBus()
        await bus.start()
        
        service = MockMCPNotificationService(bus)
        
        # Notify connection established
        await service.notify_connection_established("server1", "conn123")
        
        # Notify connection lost
        await service.notify_connection_lost("server1", "conn123", "timeout")
        
        await asyncio.sleep(0.1)
        
        # Check notifications
        notifications = service.get_notifications()
        assert len(notifications) == 2
        assert notifications[0]["data"]["connection_id"] == "conn123"
        assert notifications[1]["data"]["reason"] == "timeout"
        
        await bus.stop()
        
    @pytest.mark.asyncio
    async def test_notification_filtering(self):
        """Test filtering notifications by type."""
        bus = MockMCPEventBus()
        await bus.start()
        
        service = MockMCPNotificationService(bus)
        
        # Create various notifications
        await service.notify_server_start("s1", {})
        await service.notify_server_start("s2", {})
        await service.notify_server_error("s1", "error")
        
        # Filter by type
        start_notifications = service.get_notifications("server_start")
        error_notifications = service.get_notifications("server_error")
        
        assert len(start_notifications) == 2
        assert len(error_notifications) == 1
        
        await bus.stop()


class TestMockMCPMetricsCollector:
    """Test the mock MCP metrics collector."""
    
    def test_record_server_metrics(self):
        """Test recording server metrics."""
        collector = MockMCPMetricsCollector()
        
        # Record server operations
        collector.record_server_start(0.5)
        collector.record_server_start(0.3)
        collector.record_server_stop(0.1)
        
        summary = collector.get_metrics_summary()
        
        assert summary["timings"]["server_start_time"]["count"] == 2
        assert summary["timings"]["server_start_time"]["avg"] == 0.4
        assert summary["timings"]["server_stop_time"]["count"] == 1
        
    def test_record_request_metrics(self):
        """Test recording request metrics."""
        collector = MockMCPMetricsCollector()
        
        # Record successful requests
        collector.record_request(0.1, success=True)
        collector.record_request(0.2, success=True)
        
        # Record failed request
        collector.record_request(0.05, success=False)
        
        summary = collector.get_metrics_summary()
        
        assert summary["counters"]["total_requests"] == 3
        assert summary["counters"]["successful_requests"] == 2
        assert summary["counters"]["failed_requests"] == 1
        assert summary["timings"]["request_processing_time"]["avg"] == pytest.approx(0.116, rel=0.01)
        
    def test_connection_metrics(self):
        """Test connection metrics."""
        collector = MockMCPMetricsCollector()
        
        # Record connections
        collector.record_connection(0.2)
        collector.record_connection(0.3)
        
        assert collector.counters["total_connections"] == 2
        assert collector.counters["active_connections"] == 2
        
        # Record disconnection
        collector.record_disconnection()
        
        assert collector.counters["active_connections"] == 1
        
    def test_memory_operation_metrics(self):
        """Test memory operation metrics."""
        collector = MockMCPMetricsCollector()
        
        # Record various memory operations
        collector.record_memory_operation("store", 0.01)
        collector.record_memory_operation("retrieve", 0.005)
        collector.record_memory_operation("delete", 0.008)
        
        summary = collector.get_metrics_summary()
        
        assert summary["timings"]["memory_operation_time"]["count"] == 3
        assert summary["timings"]["memory_operation_time"]["min"] == 0.005
        assert summary["timings"]["memory_operation_time"]["max"] == 0.01
        
    def test_metrics_reset(self):
        """Test resetting metrics."""
        collector = MockMCPMetricsCollector()
        
        # Add some metrics
        collector.record_request(0.1)
        collector.record_connection(0.2)
        collector.counters["total_requests"] = 5
        
        # Reset
        collector.reset()
        
        # Verify all cleared
        summary = collector.get_metrics_summary()
        assert summary["counters"]["total_requests"] == 0
        assert summary["timings"]["request_processing_time"]["count"] == 0
        assert summary["timings"]["connection_establishment_time"]["count"] == 0
        
    def test_empty_metrics_summary(self):
        """Test metrics summary with no data."""
        collector = MockMCPMetricsCollector()
        summary = collector.get_metrics_summary()
        
        # Should have default values
        for timing in summary["timings"].values():
            assert timing["count"] == 0
            assert timing["min"] == 0
            assert timing["max"] == 0
            assert timing["avg"] == 0