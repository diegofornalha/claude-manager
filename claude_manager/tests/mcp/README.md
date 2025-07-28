# MCP Test Suite

This directory contains the comprehensive test suite for Model Context Protocol (MCP) functionality in Claude Manager.

## 📁 Directory Structure

```
mcp/
├── mocks/              # Mock implementations for testing
│   ├── mock_mcp_server.py      # Mock MCP server and connection
│   └── mock_mcp_events.py      # Mock event bus and notifications
├── unit/               # Unit tests
│   ├── test_mcp_models.py      # Tests for MCP data models
│   ├── test_mcp_config.py      # Tests for MCP configuration
│   ├── test_mock_server.py     # Tests for mock implementations
│   └── test_mcp_events.py      # Tests for event handling
├── integration/        # Integration tests
│   └── test_mcp_integration.py # Tests for MCP component integration
├── workflows/          # Workflow tests
│   └── test_mcp_workflows.py   # Tests for complex MCP workflows
├── performance/        # Performance tests (Phase 2)
├── security/           # Security tests (Phase 3)
├── conftest.py        # Shared fixtures and configuration
├── test_runner.py     # Quick test runner script
└── README.md          # This file
```

## 🚀 Quick Start

### Run All MCP Tests

```bash
# From project root
pytest claude_manager/tests/mcp -v

# Or use the test runner
python claude_manager/tests/mcp/test_runner.py
```

### Run Specific Test Categories

```bash
# Unit tests only
pytest claude_manager/tests/mcp/unit -v

# Integration tests only
pytest claude_manager/tests/mcp/integration -v

# Workflow tests only
pytest claude_manager/tests/mcp/workflows -v
```

### Run with Coverage

```bash
pytest claude_manager/tests/mcp --cov=claude_manager --cov-report=html
```

## 🧪 Test Categories

### Unit Tests
- **test_mcp_models.py**: Tests for Project model MCP fields
- **test_mcp_config.py**: Tests for MCP configuration management
- **test_mock_server.py**: Tests for mock MCP server implementation
- **test_mcp_events.py**: Tests for event bus and notifications

### Integration Tests
- **test_mcp_integration.py**: Tests for MCP component interactions
  - Full workflow from config to operation
  - Multiple server management
  - Connection failure and recovery
  - Configuration updates and reloads

### Workflow Tests
- **test_mcp_workflows.py**: Complex multi-step scenarios
  - Project lifecycle with MCP
  - Collaborative server workflows
  - Failover and redundancy
  - Data pipeline processing
  - Monitoring and alerting

## 🔧 Mock Implementations

### MockMemoryMCPServer
A mock implementation of a Memory MCP server that supports:
- Store/retrieve/delete operations
- List keys with prefix filtering
- Clear all data
- Server statistics
- Request/response logging

### MockMCPConnection
Mock connection that simulates MCP protocol:
- Connect/disconnect lifecycle
- Request/response handling
- Error simulation
- Connection state management

### MockMCPEventBus
Event system for testing:
- Event emission and subscription
- Event filtering by type
- Async event handlers
- Event history tracking

### MockMCPNotificationService
Notification service for testing:
- Server lifecycle notifications
- Connection status notifications
- Error notifications
- Notification filtering

### MockMCPMetricsCollector
Performance metrics collection:
- Operation timing
- Success/failure counters
- Connection tracking
- Metrics aggregation

## 📝 Writing New Tests

### Adding a Unit Test

```python
class TestMCPFeature:
    def test_feature_behavior(self):
        """Test specific MCP feature."""
        # Setup
        server = MockMemoryMCPServer()
        
        # Test
        result = server.some_operation()
        
        # Assert
        assert result.expected_value
```

### Adding an Integration Test

```python
@pytest.mark.asyncio
async def test_mcp_integration(mcp_server_manager):
    """Test MCP components working together."""
    # Setup components
    await mcp_server_manager.start_all()
    
    # Perform integrated operations
    result = await perform_workflow()
    
    # Verify results
    assert result.success
```

### Using Fixtures

```python
def test_with_fixtures(sample_project_with_mcp, mock_mcp_servers):
    """Test using provided fixtures."""
    # Fixtures provide pre-configured objects
    assert sample_project_with_mcp.mcp_servers is not None
    assert "memory" in mock_mcp_servers
```

## 🎯 Test Coverage Goals

- **Phase 1**: ✅ Foundation (Unit tests, mocks, basic integration)
- **Phase 2**: 🔄 Advanced Testing (Performance, stress tests)
- **Phase 3**: 🔄 Security & Edge Cases
- **Phase 4**: 🔄 Documentation & Maintenance

Target: 90%+ code coverage for MCP-related code

## 🐛 Debugging Tests

### Run with Detailed Output

```bash
pytest claude_manager/tests/mcp -vv -s
```

### Run Specific Test

```bash
pytest claude_manager/tests/mcp/unit/test_mcp_models.py::TestMCPModels::test_project_with_mcp_servers -v
```

### Debug with PDB

```bash
pytest claude_manager/tests/mcp --pdb
```

## 📊 Current Test Status

Run the test runner to see current status:

```bash
python claude_manager/tests/mcp/test_runner.py
```

This will show:
- Test results by category
- Pass/fail counts
- Summary statistics

## 🤝 Contributing

When adding MCP features:
1. Write tests first (TDD approach)
2. Ensure all tests pass
3. Maintain >90% coverage
4. Update this README if needed

## 📚 Related Documentation

- [MCP Test Implementation Plan](../../../docs/mcp-test-implementation-plan.md)
- [MCP Quick Start Guide](../../../docs/mcp-quick-start-guide.md)
- [MCP Test Visual Summary](../../../docs/mcp-test-visual-summary.md)