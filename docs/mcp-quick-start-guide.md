# Guia Rápido: Começando com Testes MCP

## 🚀 Início Rápido (Primeiras 2 Horas)

Este guia mostra como começar a implementar testes MCP no Claude Manager de forma prática e incremental.

## Passo 1: Criar Estrutura Base (15 min)

```bash
# Na raiz do projeto Claude Manager
cd claude_manager/tests
mkdir -p mcp/{mocks,unit,integration,workflows,performance,security}
touch mcp/__init__.py
touch mcp/conftest.py
```

## Passo 2: Adicionar Dependências (10 min)

Atualizar `pyproject.toml`:

```toml
[project.optional-dependencies]
mcp = [
    "pytest-asyncio>=0.21.0",
    "pytest-mock>=3.11.0", 
    "pytest-timeout>=2.1.0",
    "aiohttp>=3.8.0",
    "jsonrpc>=1.0.0",
]

# Para instalar:
# uv sync --extra mcp
```

## Passo 3: Criar Mock Base (30 min)

```python
# claude_manager/tests/mcp/mocks/base_mock.py
import asyncio
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class MCPRequest:
    """Representa uma requisição MCP."""
    method: str
    params: Dict[str, Any]
    id: Optional[int] = None

@dataclass 
class MCPResponse:
    """Representa uma resposta MCP."""
    result: Any = None
    error: Optional[Dict[str, Any]] = None
    id: Optional[int] = None

class BaseMockMCPServer:
    """Classe base para mock de servidores MCP."""
    
    def __init__(self, name: str, port: int = 0):
        self.name = name
        self.port = port
        self.running = False
        self._handlers = {}
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Registra handlers para métodos MCP."""
        self._handlers["initialize"] = self._handle_initialize
        self._handlers["ping"] = self._handle_ping
    
    async def _handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handler para inicialização."""
        return {
            "name": self.name,
            "version": "1.0.0",
            "capabilities": self.get_capabilities()
        }
    
    async def _handle_ping(self, params: Dict[str, Any]) -> str:
        """Handler para ping."""
        return "pong"
    
    def get_capabilities(self) -> list[str]:
        """Retorna capacidades do servidor."""
        return ["base"]
    
    async def start(self):
        """Inicia o servidor mock."""
        self.running = True
        # Implementação específica por servidor
    
    async def stop(self):
        """Para o servidor mock."""
        self.running = False
```

## Passo 4: Implementar Mock Memory MCP (30 min)

```python
# claude_manager/tests/mcp/mocks/mock_memory.py
from typing import Dict, List, Any
from .base_mock import BaseMockMCPServer

class MockMemoryMCP(BaseMockMCPServer):
    """Mock do Memory MCP para testes."""
    
    def __init__(self):
        super().__init__("memory", port=8001)
        self.entities: Dict[str, Any] = {}
        self.relations: List[Dict[str, Any]] = []
        self._entity_counter = 0
    
    def _setup_handlers(self):
        super()._setup_handlers()
        self._handlers["create_entities"] = self._handle_create_entities
        self._handlers["read_graph"] = self._handle_read_graph
        self._handlers["search_nodes"] = self._handle_search_nodes
        self._handlers["delete_entities"] = self._handle_delete_entities
    
    def get_capabilities(self) -> list[str]:
        return ["entities", "relations", "search", "graph"]
    
    async def _handle_create_entities(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Cria entidades no grafo."""
        created = []
        
        for entity_data in params.get("entities", []):
            self._entity_counter += 1
            entity_id = f"entity_{self._entity_counter}"
            
            entity = {
                "id": entity_id,
                "name": entity_data["name"],
                "type": entity_data["entityType"],
                "observations": entity_data.get("observations", [])
            }
            
            self.entities[entity_id] = entity
            created.append(entity)
        
        return {"entities": created}
    
    async def _handle_read_graph(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Retorna o grafo completo."""
        return {
            "entities": list(self.entities.values()),
            "relations": self.relations
        }
    
    async def _handle_search_nodes(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Busca nós no grafo."""
        query = params.get("query", "").lower()
        results = []
        
        for entity in self.entities.values():
            if query in entity["name"].lower():
                results.append(entity)
            elif any(query in obs.lower() for obs in entity["observations"]):
                results.append(entity)
        
        return {"results": results}
    
    async def _handle_delete_entities(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Remove entidades do grafo."""
        entity_names = params.get("entityNames", [])
        deleted = []
        
        # Encontrar IDs por nome
        for name in entity_names:
            for entity_id, entity in list(self.entities.items()):
                if entity["name"] == name:
                    del self.entities[entity_id]
                    deleted.append(name)
                    break
        
        return {"deleted": deleted}
```

## Passo 5: Criar Fixtures de Teste (20 min)

```python
# claude_manager/tests/mcp/conftest.py
import pytest
import asyncio
from typing import AsyncGenerator
from .mocks.mock_memory import MockMemoryMCP
from .mocks.mock_desktop import MockDesktopMCP
from .mocks.mock_terminal import MockTerminalMCP

@pytest.fixture
async def mock_memory_server() -> AsyncGenerator[MockMemoryMCP, None]:
    """Fornece um servidor Memory MCP mock."""
    server = MockMemoryMCP()
    await server.start()
    
    yield server
    
    await server.stop()

@pytest.fixture
async def mcp_client(mock_memory_server):
    """Cliente MCP conectado ao mock server."""
    # Simular cliente MCP
    class SimpleMCPClient:
        def __init__(self, server):
            self.server = server
        
        async def request(self, method: str, params: dict = None):
            """Faz uma requisição ao servidor."""
            handler = self.server._handlers.get(method)
            if handler:
                return await handler(params or {})
            raise ValueError(f"Método {method} não suportado")
    
    return SimpleMCPClient(mock_memory_server)

@pytest.fixture
def sample_project_data():
    """Dados de exemplo para testes."""
    return {
        "name": "TestProject",
        "path": "/test/project",
        "observations": [
            "Projeto de teste para Claude Manager",
            "Inclui integração com MCPs"
        ]
    }
```

## Passo 6: Primeiro Teste Funcional (25 min)

```python
# claude_manager/tests/mcp/integration/test_memory_basic.py
import pytest

@pytest.mark.asyncio
async def test_memory_entity_creation(mcp_client, sample_project_data):
    """Testa criação básica de entidade no Memory MCP."""
    # Arrange
    entities = [{
        "name": sample_project_data["name"],
        "entityType": "Project",
        "observations": sample_project_data["observations"]
    }]
    
    # Act
    result = await mcp_client.request("create_entities", {"entities": entities})
    
    # Assert
    assert "entities" in result
    assert len(result["entities"]) == 1
    
    created = result["entities"][0]
    assert created["name"] == "TestProject"
    assert created["type"] == "Project"
    assert len(created["observations"]) == 2

@pytest.mark.asyncio
async def test_memory_search(mcp_client, sample_project_data):
    """Testa busca de entidades."""
    # Primeiro criar uma entidade
    await mcp_client.request("create_entities", {
        "entities": [{
            "name": "Claude Manager",
            "entityType": "Project",
            "observations": ["Sistema de gerenciamento"]
        }]
    })
    
    # Buscar
    result = await mcp_client.request("search_nodes", {"query": "Claude"})
    
    # Verificar
    assert "results" in result
    assert len(result["results"]) == 1
    assert result["results"][0]["name"] == "Claude Manager"

@pytest.mark.asyncio 
async def test_memory_full_workflow(mcp_client):
    """Testa workflow completo: criar, buscar, atualizar, deletar."""
    # 1. Criar múltiplas entidades
    entities = [
        {"name": "Frontend", "entityType": "Component", "observations": ["React app"]},
        {"name": "Backend", "entityType": "Component", "observations": ["Node.js API"]},
        {"name": "Database", "entityType": "Component", "observations": ["PostgreSQL"]}
    ]
    
    await mcp_client.request("create_entities", {"entities": entities})
    
    # 2. Ler grafo completo
    graph = await mcp_client.request("read_graph", {})
    assert len(graph["entities"]) == 3
    
    # 3. Buscar específico
    results = await mcp_client.request("search_nodes", {"query": "API"})
    assert len(results["results"]) == 1
    assert results["results"][0]["name"] == "Backend"
    
    # 4. Deletar um componente
    await mcp_client.request("delete_entities", {"entityNames": ["Database"]})
    
    # 5. Verificar deleção
    graph = await mcp_client.request("read_graph", {})
    assert len(graph["entities"]) == 2
    assert not any(e["name"] == "Database" for e in graph["entities"])
```

## Passo 7: Executar os Testes (5 min)

```bash
# Executar apenas testes MCP
uv run pytest claude_manager/tests/mcp -v

# Com cobertura
uv run pytest claude_manager/tests/mcp --cov=claude_manager --cov-report=html

# Específico
uv run pytest claude_manager/tests/mcp/integration/test_memory_basic.py::test_memory_entity_creation -v
```

## 🎯 Próximos Passos Imediatos

Após completar este guia rápido, você terá:

✅ Estrutura de testes MCP criada  
✅ Mock server Memory MCP funcional  
✅ Primeiros testes integrados rodando  
✅ Base para expandir para outros MCPs  

### Tarefas para Hoje
1. ✅ Implementar mock Desktop Commander (30 min)
2. ✅ Adicionar testes de erro/timeout (20 min)
3. ✅ Configurar CI para rodar testes MCP (15 min)
4. ✅ Documentar processo para time (15 min)

### Tarefas para Amanhã
1. Mock Terminal MCP
2. Testes de reconexão
3. Integração com Claude Manager
4. Primeiros benchmarks

## 💡 Dicas Importantes

### Performance
```python
# Use fixtures com scope apropriado
@pytest.fixture(scope="session")
async def shared_mcp_server():
    """Servidor compartilhado entre testes."""
    # ...

# Parallelize quando possível
@pytest.mark.asyncio
@pytest.mark.parametrize("entity_count", [1, 10, 100])
async def test_bulk_creation(entity_count):
    # ...
```

### Debugging
```python
# Adicione logs estruturados
import structlog
logger = structlog.get_logger()

async def test_complex_workflow():
    logger.info("starting_workflow", test="complex")
    # ...
    logger.info("workflow_complete", duration=elapsed)
```

### Isolamento
```python
# Sempre limpe estado entre testes
@pytest.fixture(autouse=True)
async def cleanup_mcp_state(mock_memory_server):
    yield
    # Limpar após cada teste
    mock_memory_server.entities.clear()
    mock_memory_server.relations.clear()
```

## 📞 Suporte

Dúvidas sobre implementação? 
- Consulte o [Plano Completo](./mcp-test-implementation-plan.md)
- Revise a [Documentação MCP](https://github.com/anthropics/mcp)
- Pergunte no canal #claude-manager

---

**Tempo estimado**: 2 horas para configuração inicial  
**Resultado**: Framework de testes MCP funcional e extensível