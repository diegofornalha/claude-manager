# Interfaces de Usuário

## 📋 Visão Geral

O cluster de **Interfaces de Usuário** do Claude Manager oferece múltiplas formas de interação com o sistema, desde uma interface de terminal rica (TUI) até interfaces simples e alternativas, garantindo flexibilidade e usabilidade em diferentes cenários.

## 🏗️ Arquitetura

### Arquivos Principais
- **`tui.py`** - Interface de terminal rica (TUI) com Textual
- **`simple_ui.py`** - Interface simples com questionary
- **`ui.py`** - Interface alternativa com Rich

### Dependências
```python
# TUI (Textual)
from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import DataTable, Static, Button, Input
from textual.binding import Binding

# Simple UI (Questionary)
import questionary
from rich.console import Console
from rich.table import Table

# Alternative UI (Rich)
from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich.tree import Tree
```

## 🖥️ Interface de Terminal (TUI)

### ClaudeManagerApp

```python
class ClaudeManagerApp(App[None]):
    """The main TUI application with robust terminal cleanup."""
    
    CSS = """
    DataTable {
        height: 1fr;
    }
    
    #project_info {
        height: auto;
        min-height: 10;
    }
    
    #history_list {
        height: auto;
        min-height: 10;
    }
    """
    
    def __init__(self, config_manager: ClaudeConfigManager) -> None:
        super().__init__()
        self.config_manager = config_manager
```

### Telas Principais

#### 1. ProjectListScreen

```python
class ProjectListScreen(Screen[None]):
    """Main screen showing project list."""
    
    BINDINGS = [
        Binding("q", "quit", "Sair"),
        Binding("r", "refresh", "Atualizar"),
        Binding("d", "delete", "Excluir"),
        Binding("c", "clear_history", "Limpar Histórico"),
        Binding("m", "manage_mcp", "Gerenciar MCP"),
        Binding("a", "analyze", "Analisar"),
        Binding("b", "manage_backups", "Backups"),
        Binding("g", "manage_agents", "Agentes"),
    ]
    
    def compose(self) -> ComposeResult:
        """Create the main project list view."""
        yield Header()
        yield DataTable(id="projects_table")
        yield Footer()
```

#### 2. ProjectDetailScreen

```python
class ProjectDetailScreen(Screen[None]):
    """Screen showing project details."""
    
    BINDINGS = [
        Binding("escape", "go_back", "Voltar"),
        Binding("q", "go_back", "Voltar"),
    ]
    
    def compose(self) -> ComposeResult:
        """Create the project detail view."""
        yield Header()
        yield Container(
            Static(f"[bold]Projeto: {self.project_path}[/bold]", id="project_title"),
            Static(id="project_info"),
            Static("[bold]Agentes do Projeto:[/bold]", id="agents_title"),
            Static(id="agents_list"),
            Static("[bold]Histórico Recente:[/bold]", id="history_title"),
            Static(id="history_list"),
            id="detail_container",
        )
        yield Footer()
```

#### 3. AnalyzeProjectsScreen

```python
class AnalyzeProjectsScreen(Screen[None]):
    """Screen for analyzing projects and showing issues."""
    
    BINDINGS = [
        Binding("escape", "go_back", "Voltar"),
        Binding("q", "go_back", "Voltar"),
    ]
    
    def on_mount(self) -> None:
        """Analyze projects when screen mounts."""
        projects = self.config_manager.get_projects()
        
        # Analyze issues
        non_existent = []
        unused = []  # No history
        large_history = []  # > 50 entries
        no_trust = []
        
        for path, project in projects.items():
            if not project.directory_exists:
                non_existent.append(path)
            if project.history_count == 0:
                unused.append(path)
            elif project.history_count > 50:
                large_history.append((path, project.history_count))
            if not project.has_trust_dialog_accepted:
                no_trust.append(path)
```

## 📱 Interface Simples (SimpleUI)

### SimpleUI Class

```python
class SimpleUI:
    """A simple UI that actually works."""
    
    def __init__(self, config_manager: ClaudeConfigManager) -> None:
        self.config_manager = config_manager
    
    def run(self) -> None:
        """Main loop."""
        while True:
            console.clear()
            console.print("[bold cyan]Claude Manager[/bold cyan]\n")
            
            action = questionary.select(
                "What do you want to do?",
                choices=[
                    "List all projects",
                    "Remove unused projects",
                    "Clear project history",
                    "View project details",
                    "Exit",
                ],
            ).ask()
            
            if not action or action == "Exit":
                break
```

### Funcionalidades Principais

#### 1. Listagem de Projetos

```python
def list_projects(self) -> None:
    """Just list the damn projects."""
    console.clear()
    projects = self.config_manager.get_projects()
    
    if not projects:
        console.print("[yellow]No projects found.[/yellow]")
        console.print("\n[dim]Press Enter to continue...[/dim]")
        console.input()
        return
    
    table = Table(title=f"Projects ({len(projects)})", box=box.SIMPLE)
    table.add_column("Path", style="cyan")
    table.add_column("History", justify="right")
    table.add_column("Exists", justify="center")
    
    for path, project in sorted(projects.items()):
        exists = "✓" if project.directory_exists else "✗"
        table.add_row(
            path if len(path) < 80 else "..." + path[-77:],
            str(project.history_count),
            exists
        )
    
    console.print(table)
    console.print("\n[dim]Press Enter to continue...[/dim]")
    console.input()
```

#### 2. Visualização de Detalhes

```python
def view_project_details(self) -> None:
    """View details of a specific project."""
    console.clear()
    projects = self.config_manager.get_projects()
    
    if not projects:
        console.print("[yellow]No projects found.[/yellow]")
        console.print("\n[dim]Press Enter to continue...[/dim]")
        console.input()
        return
    
    # Simple list to choose from
    project_list = sorted(projects.keys())
    selected = questionary.select(
        "Select a project:",
        choices=[*project_list, "← Back"]
    ).ask()
    
    if not selected or selected == "← Back":
        return
    
    project = projects[selected]
    console.clear()
    console.print(f"[bold cyan]Project: {selected}[/bold cyan]\n")
    console.print(f"Directory exists: {'✓' if project.directory_exists else '✗'}")
    console.print(f"History entries: {project.history_count}")
    console.print(f"MCP servers: {len(project.mcp_servers)}")
    console.print(f"Trust accepted: {'✓' if project.has_trust_dialog_accepted else '✗'}")
```

## 🎨 Interface Alternativa (Rich UI)

### ClaudeProjectManagerUI

```python
class ClaudeProjectManagerUI:
    """Rich-based UI for Claude Project Manager."""
    
    def __init__(self, config_manager: ClaudeConfigManager) -> None:
        self.config_manager = config_manager
        self.console = Console()
    
    def run(self) -> None:
        """Main UI loop."""
        while True:
            self.show_welcome()
            action = self.show_main_menu()
            
            if not action:
                break
            
            if action == "list":
                self.list_projects()
            elif action == "analyze":
                self.analyze_projects()
            elif action == "edit":
                self.edit_project()
            elif action == "remove":
                self.remove_projects()
            elif action == "mcp":
                self.manage_mcp_servers()
            elif action == "clear":
                self.clear_history()
            elif action == "backup":
                self.backup_management()
            elif action == "info":
                self.show_config_info()
```

### Funcionalidades Principais

#### 1. Menu Principal

```python
def show_main_menu(self) -> str | None:
    """Show the main menu and get user choice."""
    choices = [
        Choice(title="📋 List Projects", value="list"),
        Choice(title="🔍 Analyze Projects", value="analyze"),
        Choice(title="✏️ Edit Project", value="edit"),
        Choice(title="🗑️ Remove Projects", value="remove"),
        Choice(title="🔌 Manage MCP Servers", value="mcp"),
        Choice(title="🧹 Clear History", value="clear"),
        Choice(title="💾 Backup Management", value="backup"),
        Choice(title="ℹ️ Config Info", value="info"),
        Choice(title="❌ Exit", value="exit"),
    ]
    
    return safe_select("What would you like to do?", choices=choices)
```

#### 2. Análise de Projetos

```python
def analyze_projects(self) -> None:
    """Analyze projects for issues and usage patterns."""
    projects = self.config_manager.get_projects()
    
    if not projects:
        console.print("\n[yellow]No projects found in configuration.[/yellow]\n")
        return
    
    console.print("\n[bold]Analyzing projects...[/bold]\n")
    
    # Find issues
    non_existent: list[str] = []
    empty_history: list[str] = []
    large_history: list[tuple[str, int]] = []
    no_trust: list[str] = []
    
    total_size = 0
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Analyzing...", total=len(projects))
        
        for path, project in projects.items():
            if not project.directory_exists:
                non_existent.append(path)
            
            if project.history_count == 0:
                empty_history.append(path)
            elif project.history_count > 100:
                large_history.append((path, project.history_count))
            
            if not project.has_trust_dialog_accepted:
                no_trust.append(path)
            
            total_size += project.get_size_estimate()
            progress.update(task, advance=1)
```

## 🎯 Componentes Visuais

### DataTable (TUI)

```python
def refresh_projects(self) -> None:
    """Refresh the projects table."""
    table = self.query_one("#projects_table", DataTable)
    table.clear(columns=True)
    
    # Add columns
    table.add_columns(
        "Path",
        "History",
        "MCP",
        "Trust",
        "Exists",
        "Size"
    )
    
    # Add rows
    projects = self.config_manager.get_projects()
    for path, project in sorted(projects.items()):
        exists = "✓" if project.directory_exists else "✗"
        trust = "✓" if project.has_trust_dialog_accepted else "✗"
        size = f"{project.get_size_estimate() / 1024:.1f}KB"
        
        table.add_row(
            path,
            str(project.history_count),
            str(len(project.mcp_servers)),
            trust,
            exists,
            size
        )
```

### Rich Tables (Simple UI)

```python
def create_project_table(self, projects: dict[str, Project]) -> Table:
    """Create a rich table for projects."""
    table = Table(title=f"Projects ({len(projects)})", box=box.SIMPLE)
    table.add_column("Path", style="cyan")
    table.add_column("History", justify="right")
    table.add_column("MCP", justify="right")
    table.add_column("Trust", justify="center")
    table.add_column("Exists", justify="center")
    
    for path, project in sorted(projects.items()):
        exists = "✓" if project.directory_exists else "✗"
        trust = "✓" if project.has_trust_dialog_accepted else "✗"
        
        table.add_row(
            path if len(path) < 60 else "..." + path[-57:],
            str(project.history_count),
            str(len(project.mcp_servers)),
            trust,
            exists
        )
    
    return table
```

### Trees (Rich UI)

```python
def show_project_details(self, project: Project) -> None:
    """Show detailed information about a project."""
    console.print()
    
    # Create a tree view
    tree = Tree(f"[bold cyan]{project.path}[/bold cyan]")
    
    # Basic info
    info_branch = tree.add("[bold]Basic Information[/bold]")
    info_branch.add(f"Directory exists: {'✓' if project.directory_exists else '[red]✗[/red]'}")
    info_branch.add(f"History entries: {project.history_count}")
    info_branch.add(f"Trust dialog accepted: {'✓' if project.has_trust_dialog_accepted else '✗'}")
    info_branch.add(f"Onboarding seen: {project.project_onboarding_seen_count} times")
    
    # MCP Servers
    if project.mcp_servers:
        mcp_branch = tree.add(f"[bold]MCP Servers ({len(project.mcp_servers)})[/bold]")
        for server_name, server_config in project.mcp_servers.items():
            mcp_branch.add(f"{server_name}: {server_config}")
    
    # Recent history
    if project.history:
        history_branch = tree.add("[bold]Recent History (last 5)[/bold]")
        for entry in project.history[-5:]:
            display = entry.get("display", "N/A")
            if len(display) > 60:
                display = display[:57] + "..."
            history_branch.add(display)
    
    console.print(tree)
    console.print()
```

## 🔧 Navegação e Interação

### Bindings (TUI)

```python
# ProjectListScreen bindings
BINDINGS = [
    Binding("q", "quit", "Sair"),
    Binding("r", "refresh", "Atualizar"),
    Binding("d", "delete", "Excluir"),
    Binding("c", "clear_history", "Limpar Histórico"),
    Binding("m", "manage_mcp", "Gerenciar MCP"),
    Binding("a", "analyze", "Analisar"),
    Binding("b", "manage_backups", "Backups"),
    Binding("g", "manage_agents", "Agentes"),
]

# ProjectDetailScreen bindings
BINDINGS = [
    Binding("escape", "go_back", "Voltar"),
    Binding("q", "go_back", "Voltar"),
]
```

### Event Handlers (TUI)

```python
@on(DataTable.RowSelected)
def on_row_selected(self, event: DataTable.RowSelected) -> None:
    """Handle row selection in the projects table."""
    if event.row_key is not None:
        project_path = str(event.row_key.value)
        projects = self.config_manager.get_projects()
        
        if project_path in projects:
            project = projects[project_path]
            self.app.push_screen(ProjectDetailScreen(project, project_path))

def action_quit(self) -> None:
    """Quit the application."""
    self.app.exit()

def action_refresh(self) -> None:
    """Refresh the projects list."""
    self.refresh_projects()
```

### Questionary (Simple UI)

```python
def get_user_choice(self, message: str, choices: list[str]) -> str | None:
    """Get user choice using questionary."""
    return questionary.select(message, choices=choices).ask()

def get_user_confirmation(self, message: str) -> bool:
    """Get user confirmation using questionary."""
    return questionary.confirm(message).ask()

def get_user_input(self, message: str) -> str | None:
    """Get user input using questionary."""
    return questionary.text(message).ask()
```

## 🎨 Estilização e Temas

### CSS (TUI)

```python
CSS = """
DataTable {
    height: 1fr;
}

#project_info {
    height: auto;
    min-height: 10;
}

#history_list {
    height: auto;
    min-height: 10;
}

Header {
    background: $accent;
    color: $text;
    padding: 1;
}

Footer {
    background: $accent;
    color: $text;
    padding: 1;
}
"""
```

### Rich Styling

```python
# Console styling
console = Console(style="bold cyan")

# Table styling
table = Table(
    title="Projects",
    box=box.SIMPLE,
    title_style="bold magenta",
    header_style="bold blue"
)

# Tree styling
tree = Tree(
    "[bold cyan]Project Structure[/bold cyan]",
    guide_style="blue",
    style="green"
)
```

## 🔧 Helpers de Interface

### safe_select()

```python
def safe_select(message: str, choices: list[Any], **kwargs: Any) -> Any | None:
    """Run a select prompt, letting CTRL+C propagate for app exit.
    
    Args:
        message: The prompt message
        choices: List of choices
        **kwargs: Additional arguments for questionary.select
        
    Returns:
        Selected choice or None if cancelled with ESC
    """
    return questionary.select(message, choices=choices, **kwargs).ask()
```

### wait_for_enter()

```python
def wait_for_enter(console: Any, message: str = "Press Enter to continue...") -> None:
    """Wait for user to press Enter.
    
    Args:
        console: Rich console instance
        message: Message to display
    """
    console.print(f"\n[dim]{message}[/dim]")
    console.input()
```

## 🧪 Testes de Interface

### Testes TUI

```python
def test_project_list_screen():
    """Test the project list screen."""
    app = ClaudeManagerApp(config_manager)
    screen = ProjectListScreen(config_manager)
    
    # Test screen composition
    assert screen is not None
    
    # Test refresh functionality
    screen.refresh_projects()
    
    # Test navigation
    screen.action_quit()
```

### Testes Simple UI

```python
def test_simple_ui_list_projects():
    """Test simple UI project listing."""
    ui = SimpleUI(config_manager)
    
    # Mock console output
    with patch('rich.console.Console.print') as mock_print:
        ui.list_projects()
        mock_print.assert_called()
```

## 🔮 Melhorias Futuras

### Funcionalidades Planejadas
- [ ] Temas personalizáveis
- [ ] Atalhos de teclado configuráveis
- [ ] Modo escuro/claro
- [ ] Interface web opcional
- [ ] Gráficos e visualizações
- [ ] Drag and drop (TUI)
- [ ] Autocompletar inteligente

### Otimizações
- [ ] Lazy loading de componentes
- [ ] Cache de renderização
- [ ] Virtualização de listas grandes
- [ ] Compressão de dados visuais

---

**Interfaces de Usuário** - Flexibilidade e usabilidade em múltiplas formas! 🖥️🎨 