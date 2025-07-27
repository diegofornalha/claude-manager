# Configuração e Gerenciamento de Dados

## 📋 Visão Geral

O cluster de **Configuração e Gerenciamento de Dados** é o coração do Claude Manager, responsável por gerenciar o arquivo de configuração JSON, definir modelos de dados e garantir a integridade das informações dos projetos Claude Code.

## 🏗️ Arquitetura

### Arquivos Principais
- **`config.py`** - Gerenciamento de configuração
- **`models.py`** - Modelos de dados

### Dependências
```python
# Dependências principais
import json
import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any, Dict, List
```

## 📊 Modelos de Dados

### Classe Project

```python
@dataclass
class Project:
    """Represents a Claude Code project."""
    
    path: str
    allowed_tools: list[str] = field(default_factory=list)
    history: list[dict[str, Any]] = field(default_factory=list)
    mcp_servers: dict[str, Any] = field(default_factory=dict)
    enabled_mcpjson_servers: list[str] = field(default_factory=list)
    disabled_mcpjson_servers: list[str] = field(default_factory=list)
    enable_all_project_mcp_servers: bool = False
    has_trust_dialog_accepted: bool = False
    ignore_patterns: list[str] = field(default_factory=list)
    project_onboarding_seen_count: int = 0
    has_claude_md_external_includes_approved: bool = False
    has_claude_md_external_includes_warning_shown: bool = False
    dont_crawl_directory: bool = False
    mcp_context_uris: list[str] = field(default_factory=list)
```

#### Propriedades Computadas

```python
@property
def history_count(self) -> int:
    """Get the number of history entries."""
    return len(self.history)

@property
def last_accessed(self) -> str | None:
    """Returns the last accessed command/display from history."""
    if self.history:
        return str(self.history[-1].get("display", "N/A"))
    return None

@property
def directory_exists(self) -> bool:
    """Check if the project directory still exists."""
    return Path(self.path).exists()

def get_size_estimate(self) -> int:
    """Estimate the size of project data in bytes."""
    return len(json.dumps(self.to_dict()))
```

### Classe Agent

```python
@dataclass
class Agent:
    """Represents a Claude Code agent."""
    
    name: str
    description: str
    tools: list[str] = field(default_factory=list)
    file_path: str = ""
    color: str | None = None
    priority: str | None = None
    neural_patterns: list[str] = field(default_factory=list)
    learning_enabled: bool = False
    collective_memory: bool = False
    hive_mind_role: str | None = None
    concurrent_execution: bool = False
    sparc_integration: bool = False
    agent_type: str = "project"  # "global" or "project"
```

## 🔧 ClaudeConfigManager

### Inicialização

```python
class ClaudeConfigManager:
    """Manages Claude Code configuration file operations."""
    
    def __init__(self, config_path: str | None = None) -> None:
        """Initialize the configuration manager.
        
        Args:
            config_path: Path to the configuration file. Defaults to ~/.claude.json
        """
        self.config_path = Path(config_path) if config_path else Path.home() / ".claude.json"
        self.config_data: dict[str, Any] = {}
        self.backup_dir = Path.home() / ".claude_backups"
        self.backup_dir.mkdir(exist_ok=True)
```

### Operações Principais

#### 1. Carregamento de Configuração

```python
def load_config(self) -> bool:
    """Load the Claude configuration file.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        if not self.config_path.exists():
            logger.error(f"Configuration file not found at {self.config_path}")
            return False

        with open(self.config_path, encoding="utf-8") as f:
            self.config_data = json.load(f)

        # Validate that config_data is a dictionary
        if not isinstance(self.config_data, dict):
            logger.error("Configuration file does not contain a JSON object")
            self.config_data = {}
            return False

        logger.info(f"Loaded configuration from {self.config_path}")
        return True

    except json.JSONDecodeError as e:
        logger.exception(f"Error parsing JSON: {e}")
        return False
    except Exception as e:
        logger.exception(f"Error loading config: {e}")
        return False
```

#### 2. Salvamento de Configuração

```python
def save_config(self, create_backup: bool = True) -> bool:
    """Save the configuration with optional backup.
    
    Args:
        create_backup: Whether to create a backup before saving
        
    Returns:
        True if successful, False otherwise
    """
    try:
        if create_backup:
            self.create_backup()

        # Write to temporary file first
        temp_path = self.config_path.with_suffix(".tmp")
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(self.config_data, f, indent=2)

        # Validate the temp file
        with open(temp_path, encoding="utf-8") as f:
            json.load(f)

        # Move temp file to actual location
        shutil.move(str(temp_path), str(self.config_path))

        logger.info(f"Saved configuration to {self.config_path}")
        return True

    except Exception as e:
        logger.exception(f"Error saving config: {e}")
        if temp_path.exists():
            temp_path.unlink()
        return False
```

#### 3. Gerenciamento de Projetos

```python
def get_projects(self) -> dict[str, Project]:
    """Get all projects as Project objects.
    
    Returns:
        Dictionary mapping project paths to Project objects
    """
    projects = {}
    for path, data in self.config_data.get("projects", {}).items():
        projects[path] = Project.from_dict(path, data)
    return projects

def update_project(self, project: Project) -> bool:
    """Update a project in the configuration.
    
    Args:
        project: Project object to update
        
    Returns:
        True (always successful)
    """
    if "projects" not in self.config_data:
        self.config_data["projects"] = {}

    self.config_data["projects"][project.path] = project.to_dict()
    return True

def remove_project(self, project_path: str) -> bool:
    """Remove a project from the configuration.
    
    Args:
        project_path: Path to the project to remove
        
    Returns:
        True if project was removed, False if not found
    """
    if project_path in self.config_data.get("projects", {}):
        del self.config_data["projects"][project_path]
        return True
    return False
```

## 📁 Estrutura do Arquivo de Configuração

### Formato JSON

```json
{
  "numStartups": 10,
  "firstStartTime": "2024-01-01T00:00:00.000Z",
  "oauthAccount": {
    "emailAddress": "user@example.com",
    "organizationName": "Example Organization"
  },
  "projects": {
    "/path/to/project1": {
      "allowedTools": ["tool1", "tool2"],
      "history": [
        {
          "display": "command executed",
          "pastedContents": {}
        }
      ],
      "mcpServers": {
        "server1": {
          "url": "http://localhost:8080"
        }
      },
      "enabledMcpjsonServers": [],
      "disabledMcpjsonServers": [],
      "enableAllProjectMcpServers": false,
      "hasTrustDialogAccepted": true,
      "ignorePatterns": ["*.pyc", "__pycache__"],
      "projectOnboardingSeenCount": 3,
      "hasClaudeMdExternalIncludesApproved": false,
      "hasClaudeMdExternalIncludesWarningShown": false,
      "dontCrawlDirectory": false,
      "mcpContextUris": []
    }
  }
}
```

### Campos Principais

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `numStartups` | `int` | Número de vezes que o Claude foi iniciado |
| `firstStartTime` | `string` | Timestamp do primeiro uso |
| `oauthAccount` | `object` | Informações da conta do usuário |
| `projects` | `object` | Dicionário de projetos |

## 🔄 Serialização e Deserialização

### Project.to_dict()

```python
def to_dict(self) -> dict[str, Any]:
    """Convert project to dictionary format for JSON serialization."""
    return {
        "allowedTools": self.allowed_tools,
        "history": self.history,
        "mcpServers": self.mcp_servers,
        "enabledMcpjsonServers": self.enabled_mcpjson_servers,
        "disabledMcpjsonServers": self.disabled_mcpjson_servers,
        "enableAllProjectMcpServers": self.enable_all_project_mcp_servers,
        "hasTrustDialogAccepted": self.has_trust_dialog_accepted,
        "ignorePatterns": self.ignore_patterns,
        "projectOnboardingSeenCount": self.project_onboarding_seen_count,
        "hasClaudeMdExternalIncludesApproved": self.has_claude_md_external_includes_approved,
        "hasClaudeMdExternalIncludesWarningShown": self.has_claude_md_external_includes_warning_shown,
        "dontCrawlDirectory": self.dont_crawl_directory,
        "mcpContextUris": self.mcp_context_uris,
    }
```

### Project.from_dict()

```python
@classmethod
def from_dict(cls, path: str, data: dict[str, Any]) -> Project:
    """Create a Project instance from dictionary data."""
    return cls(
        path=path,
        allowed_tools=data.get("allowedTools", []),
        history=data.get("history", []),
        mcp_servers=data.get("mcpServers", {}),
        enabled_mcpjson_servers=data.get("enabledMcpjsonServers", []),
        disabled_mcpjson_servers=data.get("disabledMcpjsonServers", []),
        enable_all_project_mcp_servers=data.get("enableAllProjectMcpServers", False),
        has_trust_dialog_accepted=data.get("hasTrustDialogAccepted", False),
        ignore_patterns=data.get("ignorePatterns", []),
        project_onboarding_seen_count=data.get("projectOnboardingSeenCount", 0),
        has_claude_md_external_includes_approved=data.get(
            "hasClaudeMdExternalIncludesApproved", False
        ),
        has_claude_md_external_includes_warning_shown=data.get(
            "hasClaudeMdExternalIncludesWarningShown", False
        ),
        dont_crawl_directory=data.get("dontCrawlDirectory", False),
        mcp_context_uris=data.get("mcpContextUris", []),
    )
```

## 📊 Estatísticas e Métricas

### get_stats()

```python
def get_stats(self) -> dict[str, Any]:
    """Get statistics about the configuration.
    
    Returns:
        Dictionary containing various statistics
    """
    projects = self.get_projects()
    total_history = sum(p.history_count for p in projects.values())
    total_mcp_servers = sum(len(p.mcp_servers) for p in projects.values())

    return {
        "total_projects": len(projects),
        "total_history_entries": total_history,
        "total_mcp_servers": total_mcp_servers,
        "config_size": self.get_config_size(),
        "num_startups": self.config_data.get("numStartups", 0),
        "first_start_time": self.config_data.get("firstStartTime", "N/A"),
        "user_email": self.config_data.get("oauthAccount", {}).get("emailAddress", "N/A"),
        "organization": self.config_data.get("oauthAccount", {}).get("organizationName", "N/A"),
    }
```

## 🛡️ Validação e Segurança

### Validação de Dados

```python
# Validação de tipo de dados
if not isinstance(self.config_data, dict):
    logger.error("Configuration file does not contain a JSON object")
    self.config_data = {}
    return False

# Validação de campos obrigatórios
if "projects" not in self.config_data:
    self.config_data["projects"] = {}
```

### Salvamento Seguro

```python
# Salvamento em arquivo temporário primeiro
temp_path = self.config_path.with_suffix(".tmp")
with open(temp_path, "w", encoding="utf-8") as f:
    json.dump(self.config_data, f, indent=2)

# Validação do arquivo temporário
with open(temp_path, encoding="utf-8") as f:
    json.load(f)

# Movimento seguro para localização final
shutil.move(str(temp_path), str(self.config_path))
```

## 🔧 Uso Prático

### Exemplo de Uso

```python
# Inicializar gerenciador
config_manager = ClaudeConfigManager()

# Carregar configuração
if config_manager.load_config():
    # Obter projetos
    projects = config_manager.get_projects()
    
    # Modificar projeto
    for path, project in projects.items():
        if project.history_count > 100:
            project.history = project.history[-50:]  # Manter apenas 50 entradas
            config_manager.update_project(project)
    
    # Salvar mudanças
    config_manager.save_config()
```

### Tratamento de Erros

```python
try:
    config_manager = ClaudeConfigManager()
    if not config_manager.load_config():
        print("Erro ao carregar configuração")
        return
    
    # Operações com configuração...
    
except Exception as e:
    logger.error(f"Erro no gerenciamento de configuração: {e}")
    # Fallback ou recuperação
```

## 🧪 Testes

### Testes Unitários

```python
def test_project_creation(self):
    """Test creating a Project instance."""
    project = Project(
        path="/test/path",
        allowed_tools=["tool1"],
        has_trust_dialog_accepted=True
    )
    
    assert project.path == "/test/path"
    assert project.allowed_tools == ["tool1"]
    assert project.has_trust_dialog_accepted is True

def test_config_manager_operations(self):
    """Test config manager operations."""
    manager = ClaudeConfigManager()
    
    # Test loading
    assert manager.load_config() is True
    
    # Test getting projects
    projects = manager.get_projects()
    assert isinstance(projects, dict)
```

## 🔮 Melhorias Futuras

### Funcionalidades Planejadas
- [ ] Validação de schema com JSON Schema
- [ ] Migração automática de versões de configuração
- [ ] Criptografia de dados sensíveis
- [ ] Sincronização em nuvem
- [ ] Cache de configuração em memória
- [ ] Validação de integridade de dados

### Otimizações
- [ ] Lazy loading de projetos
- [ ] Compressão de histórico
- [ ] Indexação de dados
- [ ] Cache inteligente

---

**Configuração e Gerenciamento de Dados** - O coração do Claude Manager! 🔧📊 