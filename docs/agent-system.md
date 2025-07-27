# Sistema de Agentes

## 📋 Visão Geral

O **Sistema de Agentes** do Claude Manager permite gerenciar agentes Claude Code tanto globais quanto específicos de projeto. Os agentes são definidos em arquivos Markdown com frontmatter YAML e podem ter configurações avançadas como padrões neurais, aprendizado e integração com sistemas externos.

## 🏗️ Arquitetura

### Arquivos Principais
- **`config.py`** - Parsing e gerenciamento de agentes (parte)
- **`models.py`** - Modelo de dados Agent

### Dependências
```python
import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any, List, Optional
```

## 🤖 Modelo de Dados Agent

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

### Propriedades Computadas

```python
@property
def tools_display(self) -> str:
    """Get a display string of tools."""
    if not self.tools:
        return "Nenhuma ferramenta"
    elif len(self.tools) <= 3:
        return ", ".join(self.tools)
    else:
        return f"{', '.join(self.tools[:3])}... (+{len(self.tools) - 3})"

@property
def is_advanced(self) -> bool:
    """Check if this is an advanced agent with neural patterns."""
    return bool(self.neural_patterns or self.learning_enabled or self.hive_mind_role)
```

## 📁 Estrutura de Diretórios

### Agentes Globais
```
~/.claude/agents/
├── assistant.md
├── code-reviewer.md
├── documentation-writer.md
└── security-auditor.md
```

### Agentes de Projeto
```
project/.claude/agents/
├── project-specific.md
├── domain-expert.md
└── testing-specialist.md
```

## 📄 Formato de Arquivo de Agente

### Exemplo de Agente Básico

```markdown
---
name: "Assistant"
description: "A helpful assistant for general tasks"
tools: "Read, Write, Edit, Search"
color: "blue"
priority: "normal"
---

# Assistant

This is a basic assistant agent that can help with general tasks.

## Capabilities

- Reading and writing files
- Editing code
- Searching for information
- Basic problem solving
```

### Exemplo de Agente Avançado

```markdown
---
name: "Neural Architect"
description: "Advanced agent with neural patterns and learning capabilities"
tools: "Read, Write, Edit, Bash, TodoWrite, NeuralPattern, Learning"
color: "purple"
priority: "high"
neural_patterns: ["systems", "critical", "adaptive", "creative"]
learning_enabled: true
collective_memory: true
hive_mind_role: "coordinator"
concurrent_execution: true
sparc_integration: true
agent_type: "global"
---

# Neural Architect

An advanced agent with neural patterns and learning capabilities.

## Neural Patterns

- **Systems**: Thinks in terms of interconnected systems
- **Critical**: Applies critical thinking and analysis
- **Adaptive**: Adapts to changing requirements
- **Creative**: Generates innovative solutions

## Learning Capabilities

- Learns from interactions
- Builds collective memory
- Coordinates with other agents
- Integrates with SPARC systems
```

## 🔧 Parsing de Agentes

### _parse_agent_file()

```python
def _parse_agent_file(self, file_path: Path, agent_type: str) -> Agent | None:
    """Parse an agent markdown file and extract frontmatter.
    
    Args:
        file_path: Path to the agent .md file
        agent_type: "global" or "project"
        
    Returns:
        Agent object if successful, None otherwise
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Extract frontmatter
        if content.startswith("---"):
            # Find the closing ---
            end_idx = content.find("---", 3)
            if end_idx != -1:
                frontmatter_str = content[3:end_idx].strip()
                try:
                    frontmatter = yaml.safe_load(frontmatter_str)
                    if frontmatter and isinstance(frontmatter, dict):
                        # Extract fields from frontmatter
                        name = frontmatter.get("name", file_path.stem)
                        description = frontmatter.get("description", "")
                        tools_str = frontmatter.get("tools", "")
                        
                        # Parse tools list
                        tools = []
                        if tools_str:
                            tools = [t.strip() for t in tools_str.split(",") if t.strip()]
                        
                        # Create Agent object
                        agent = Agent(
                            name=name,
                            description=description,
                            tools=tools,
                            file_path=str(file_path),
                            color=frontmatter.get("color"),
                            priority=frontmatter.get("priority"),
                            neural_patterns=frontmatter.get("neural_patterns", []),
                            learning_enabled=frontmatter.get("learning_enabled", False),
                            collective_memory=frontmatter.get("collective_memory", False),
                            hive_mind_role=frontmatter.get("hive_mind_role"),
                            concurrent_execution=frontmatter.get("concurrent_execution", False),
                            sparc_integration=frontmatter.get("sparc_integration", False),
                            agent_type=agent_type,
                        )
                        
                        return agent
                except yaml.YAMLError as e:
                    logger.warning(f"Error parsing YAML frontmatter in {file_path}: {e}")
        
    except Exception as e:
        logger.error(f"Error reading agent file {file_path}: {e}")
    
    return None
```

## 🔍 Gerenciamento de Agentes

### get_agents()

```python
def get_agents(self, project_path: str | None = None) -> dict[str, Agent]:
    """Get available agents, both global and project-specific.
    
    Args:
        project_path: Optional project path to get project-specific agents
        
    Returns:
        Dictionary mapping agent names to Agent objects
    """
    agents = {}
    
    # Global agents
    global_agents_dir = Path.home() / ".claude" / "agents"
    if global_agents_dir.exists():
        for agent_file in global_agents_dir.glob("*.md"):
            agent = self._parse_agent_file(agent_file, "global")
            if agent:
                agents[agent.name] = agent
    
    # Project-specific agents
    if project_path:
        project_agents_dir = Path(project_path) / ".claude" / "agents"
        if project_agents_dir.exists():
            for agent_file in project_agents_dir.glob("*.md"):
                agent = self._parse_agent_file(agent_file, "project")
                if agent:
                    # Project agents override global ones with same name
                    agents[agent.name] = agent
    
    return agents
```

## 🎯 Tipos de Agentes

### Agentes Globais
- **Localização**: `~/.claude/agents/`
- **Escopo**: Disponível para todos os projetos
- **Uso**: Funcionalidades gerais e utilitários

### Agentes de Projeto
- **Localização**: `project/.claude/agents/`
- **Escopo**: Específicos do projeto
- **Uso**: Funcionalidades específicas do domínio

## 🧠 Padrões Neurais

### Padrões Disponíveis

| Padrão | Descrição |
|--------|-----------|
| `systems` | Pensamento em sistemas interconectados |
| `critical` | Pensamento crítico e análise |
| `adaptive` | Adaptação a mudanças |
| `creative` | Geração de soluções inovadoras |
| `logical` | Raciocínio lógico estruturado |
| `intuitive` | Intuição e insights |
| `collaborative` | Trabalho em equipe |
| `strategic` | Planejamento estratégico |

### Exemplo de Configuração

```yaml
neural_patterns: ["systems", "critical", "adaptive"]
```

## 🔧 Ferramentas de Agente

### Ferramentas Básicas

| Ferramenta | Descrição |
|------------|-----------|
| `Read` | Leitura de arquivos |
| `Write` | Escrita de arquivos |
| `Edit` | Edição de código |
| `Search` | Busca de informações |
| `Bash` | Execução de comandos |
| `TodoWrite` | Gerenciamento de tarefas |

### Ferramentas Avançadas

| Ferramenta | Descrição |
|------------|-----------|
| `NeuralPattern` | Aplicação de padrões neurais |
| `Learning` | Aprendizado e adaptação |
| `CollectiveMemory` | Memória coletiva |
| `HiveMind` | Coordenação com outros agentes |
| `SPARC` | Integração com sistemas SPARC |

## 🎨 Configuração Visual

### Cores Disponíveis

```python
# Cores suportadas
COLORS = [
    "blue", "green", "red", "yellow", "magenta", "cyan",
    "white", "black", "gray", "purple", "orange", "pink"
]
```

### Prioridades

```python
# Níveis de prioridade
PRIORITIES = ["low", "normal", "high", "critical"]
```

## 🔄 Integração com Interface

### Exibição na TUI

```python
def show_project_agents(self, project_path: str) -> None:
    """Show agents for a specific project."""
    agents = self.config_manager.get_agents(project_path)
    
    if not agents:
        console.print("[dim]No agents found for this project.[/dim]")
        return
    
    table = Table(title=f"Agents ({len(agents)})")
    table.add_column("Name", style="cyan")
    table.add_column("Type", style="blue")
    table.add_column("Tools", style="green")
    table.add_column("Advanced", style="yellow")
    
    for name, agent in sorted(agents.items()):
        advanced = "✓" if agent.is_advanced else "✗"
        table.add_row(
            name,
            agent.agent_type,
            agent.tools_display,
            advanced
        )
    
    console.print(table)
```

### Exibição de Detalhes

```python
def show_agent_details(self, agent: Agent) -> None:
    """Show detailed information about an agent."""
    console.print(f"\n[bold cyan]{agent.name}[/bold cyan]")
    console.print(f"Type: {agent.agent_type}")
    console.print(f"Description: {agent.description}")
    console.print(f"Tools: {agent.tools_display}")
    
    if agent.color:
        console.print(f"Color: {agent.color}")
    
    if agent.priority:
        console.print(f"Priority: {agent.priority}")
    
    if agent.neural_patterns:
        console.print(f"Neural Patterns: {', '.join(agent.neural_patterns)}")
    
    if agent.learning_enabled:
        console.print("Learning: Enabled")
    
    if agent.collective_memory:
        console.print("Collective Memory: Enabled")
    
    if agent.hive_mind_role:
        console.print(f"Hive Mind Role: {agent.hive_mind_role}")
    
    if agent.concurrent_execution:
        console.print("Concurrent Execution: Enabled")
    
    if agent.sparc_integration:
        console.print("SPARC Integration: Enabled")
```

## 🧪 Testes

### Testes de Parsing

```python
def test_agent_parsing():
    """Test agent parsing functionality."""
    config_manager = ClaudeConfigManager()
    
    # Test global agents
    global_agents = config_manager.get_agents()
    
    if global_agents:
        print(f"Found {len(global_agents)} global agents:")
        for name, agent in global_agents.items():
            print(f"\n  🤖 {name}")
            print(f"     Type: {agent.agent_type}")
            print(f"     Tools: {agent.tools_display}")
            print(f"     Priority: {agent.priority or 'None'}")
            print(f"     Advanced: {'Yes' if agent.is_advanced else 'No'}")
    
    # Test project agents
    test_project = str(Path.cwd())
    project_agents = config_manager.get_agents(test_project)
    
    # Filter only project-specific agents
    project_only = {name: agent for name, agent in project_agents.items() 
                    if agent.agent_type == "project"}
    
    if project_only:
        print(f"Found {len(project_only)} project-specific agents:")
        for name, agent in project_only.items():
            print(f"\n  🤖 {name}")
            print(f"     Tools: {agent.tools_display}")
            print(f"     File: {agent.file_path}")
```

### Testes de Modelo

```python
def test_agent_model():
    """Test Agent model functionality."""
    # Create a basic agent
    basic_agent = Agent(
        name="test-agent",
        description="A test agent for validation",
        tools=["Read", "Write", "Edit"],
        agent_type="global"
    )
    
    assert basic_agent.name == "test-agent"
    assert basic_agent.tools_display == "Read, Write, Edit"
    assert basic_agent.is_advanced is False
    
    # Create an advanced agent
    advanced_agent = Agent(
        name="neural-agent",
        description="An advanced agent with neural patterns",
        tools=["Read", "Write", "Edit", "Bash", "TodoWrite"],
        neural_patterns=["systems", "critical", "adaptive"],
        learning_enabled=True,
        collective_memory=True,
        hive_mind_role="coordinator",
        agent_type="project"
    )
    
    assert advanced_agent.is_advanced is True
    assert len(advanced_agent.neural_patterns) == 3
```

## 🔮 Melhorias Futuras

### Funcionalidades Planejadas
- [ ] Editor visual de agentes
- [ ] Templates de agentes
- [ ] Validação de configuração
- [ ] Versionamento de agentes
- [ ] Compartilhamento de agentes
- [ ] Marketplace de agentes
- [ ] Métricas de performance
- [ ] Aprendizado automático

### Integrações
- [ ] Integração com sistemas de IA
- [ ] APIs de terceiros
- [ ] Plugins customizados
- [ ] Workflows automatizados
- [ ] Orquestração de agentes

---

**Sistema de Agentes** - Agentes inteligentes para Claude Code! 🤖🧠 