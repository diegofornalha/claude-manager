"""Proper Terminal UI using Textual."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable

from rich.markup import escape
from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, VerticalScroll
from textual.screen import Screen
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    Static,
    TextArea,
)

if TYPE_CHECKING:
    from claude_manager.config import ClaudeConfigManager
    from claude_manager.models import Agent, Project

from claude_manager.terminal_utils import immediate_terminal_reset


class ProjectListScreen(Screen[None]):
    """Main screen showing project list."""

    BINDINGS = [
        Binding("q", "quit", "Sair"),
        Binding("escape", "quit", "Sair"),
        Binding("a", "analyze", "Analisar Projetos"),
        Binding("d", "delete", "Excluir Projeto"),
        Binding("h", "clear_history", "Limpar Histórico"),
        Binding("m", "manage_mcp", "Servidores MCP"),
        Binding("g", "manage_agents", "Agentes"),
        Binding("b", "manage_backups", "Backups"),
        Binding("r", "refresh", "Atualizar"),
        Binding("enter", "view_details", "Ver Detalhes", show=False),
    ]

    def __init__(self, config_manager: ClaudeConfigManager) -> None:
        super().__init__()
        self.config_manager = config_manager
        self.projects: dict[str, Project] = {}

    def compose(self) -> ComposeResult:
        """Create the UI."""
        yield Header()
        yield Container(DataTable(id="projects_table"), id="main_container")
        yield Footer()

    def on_mount(self) -> None:
        """Set up the table when screen mounts."""
        table = self.query_one("#projects_table", DataTable)
        table.add_columns("Caminho", "Histórico", "MCP", "Existe", "Tamanho")
        table.zebra_stripes = True
        table.cursor_type = "row"
        self.refresh_projects()

    @on(DataTable.RowSelected)
    def on_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection with Enter."""
        self.action_view_details()

    def refresh_projects(self) -> None:
        """Refresh the project list."""
        self.projects = self.config_manager.get_projects()
        table = self.query_one("#projects_table", DataTable)
        table.clear()

        for path, project in sorted(self.projects.items()):
            exists = "✓" if project.directory_exists else "✗"
            size = f"{project.get_size_estimate() / 1024:.1f}KB"

            # Shorten long paths
            display_path = path
            if len(path) > 80:
                display_path = "..." + path[-77:]

            table.add_row(
                display_path,
                str(project.history_count),
                str(len(project.mcp_servers)),
                exists,
                size,
                key=path,
            )

    def action_quit(self) -> None:
        """Quit the app."""
        self.app.exit()

    def action_refresh(self) -> None:
        """Refresh the project list."""
        self.refresh_projects()

    def action_view_details(self) -> None:
        """View details of selected project."""
        table = self.query_one("#projects_table", DataTable)
        if table.cursor_row is not None:
            rows = list(table.rows)
            if 0 <= table.cursor_row < len(rows):
                row_key = rows[table.cursor_row]
                project_path = row_key.value  # Get the actual string value
                if project_path in self.projects:
                    detail_screen = ProjectDetailScreen(self.projects[project_path], project_path)
                    detail_screen.config_manager = self.config_manager
                    self.app.push_screen(detail_screen)

    def action_delete(self) -> None:
        """Delete selected project."""
        table = self.query_one("#projects_table", DataTable)
        if table.cursor_row is not None:
            rows = list(table.rows)
            if 0 <= table.cursor_row < len(rows):
                row_key = rows[table.cursor_row]
                project_path = row_key.value  # Get the actual string value
                if project_path in self.projects:
                    self.app.push_screen(
                        ConfirmScreen(
                            f"Excluir projeto?\n\n{project_path}",
                            lambda: self._do_delete(project_path),
                        )
                    )

    def _do_delete(self, project_path: str) -> None:
        """Actually delete the project."""
        self.config_manager.create_backup()
        if self.config_manager.remove_project(project_path):
            if self.config_manager.save_config(create_backup=False):
                self.notify("Projeto excluído", severity="information")
                self.refresh_projects()
            else:
                self.notify("Falha ao salvar alterações", severity="error")
        else:
            self.notify("Falha ao excluir projeto", severity="error")

    def action_clear_history(self) -> None:
        """Clear history of selected project."""
        table = self.query_one("#projects_table", DataTable)
        if table.cursor_row is not None:
            rows = list(table.rows)
            if 0 <= table.cursor_row < len(rows):
                row_key = rows[table.cursor_row]
                project_path = row_key.value  # Get the actual string value
                if project_path in self.projects:
                    project = self.projects[project_path]
                    if project.history_count > 0:
                        self.app.push_screen(
                            HistoryManagementScreen(self.config_manager, project, project_path)
                        )
                    else:
                        self.notify("Sem histórico para limpar", severity="warning")

    def _do_clear_history(self, project_path: str) -> None:
        """Actually clear the history."""
        project = self.projects[project_path]
        self.config_manager.create_backup()
        project.history.clear()
        self.config_manager.update_project(project)

        if self.config_manager.save_config(create_backup=False):
            self.notify("Histórico limpo", severity="information")
            self.refresh_projects()
        else:
            self.notify("Falha ao salvar alterações", severity="error")

    def action_manage_mcp(self) -> None:
        """Manage MCP servers for selected project."""
        table = self.query_one("#projects_table", DataTable)
        if table.cursor_row is not None:
            rows = list(table.rows)
            if 0 <= table.cursor_row < len(rows):
                row_key = rows[table.cursor_row]
                project_path = row_key.value
                if project_path in self.projects:
                    self.app.push_screen(
                        MCPServerScreen(
                            self.config_manager, self.projects[project_path], project_path
                        )
                    )

    def action_analyze(self) -> None:
        """Analyze projects and show issues."""
        self.app.push_screen(AnalyzeProjectsScreen(self.config_manager))

    def action_manage_backups(self) -> None:
        """Manage configuration backups."""
        self.app.push_screen(BackupManagementScreen(self.config_manager))
    
    def action_manage_agents(self) -> None:
        """Manage agents."""
        self.app.push_screen(AgentListScreen(self.config_manager))


class ProjectDetailScreen(Screen[None]):
    """Screen showing project details."""

    BINDINGS = [
        Binding("escape", "go_back", "Voltar"),
        Binding("q", "go_back", "Voltar"),
    ]

    def __init__(self, project: Project, project_path: str) -> None:
        super().__init__()
        self.project = project
        self.project_path = project_path
        self.config_manager: ClaudeConfigManager | None = None

    def compose(self) -> ComposeResult:
        """Create the detail view."""
        yield Header()
        yield VerticalScroll(
            Static(f"[bold]Projeto: {self.project_path}[/bold]", id="project_title"),
            Static(id="project_info"),
            Static("[bold]Agentes do Projeto:[/bold]", id="agents_title_detail"),
            Static(id="agents_list"),
            Static("[bold]Histórico Recente:[/bold]", id="history_title"),
            Static(id="history_list"),
            id="detail_container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Populate the details."""
        info = self.query_one("#project_info", Static)
        info.update(
            f"Diretório existe: {'✓' if self.project.directory_exists else '✗'}\n"
            f"Entradas do histórico: {self.project.history_count}\n"
            f"Servidores MCP: {len(self.project.mcp_servers)}\n"
            f"Confiança aceita: {'✓' if self.project.has_trust_dialog_accepted else '✗'}\n"
            f"Tamanho: {self.project.get_size_estimate() / 1024:.1f}KB"
        )
        
        # Show project agents
        agents_list = self.query_one("#agents_list", Static)
        if self.config_manager:
            agents = self.config_manager.get_agents(self.project_path)
            # Filter only project-specific agents
            project_agents = {name: agent for name, agent in agents.items() if agent.agent_type == "project"}
            
            if project_agents:
                agents_text = ""
                for name, agent in sorted(project_agents.items()):
                    tools_preview = agent.tools_display
                    agents_text += f"• {name} - {tools_preview}\n"
                agents_list.update(agents_text.rstrip())
            else:
                agents_list.update("[dim]Nenhum agente específico do projeto[/dim]")
        else:
            agents_list.update("[dim]Informação de agentes não disponível[/dim]")

        history = self.query_one("#history_list", Static)
        if self.project.history:
            history_text = ""
            for entry in self.project.history[-10:]:
                display = entry.get("display", "")
                if len(display) > 100:
                    display = display[:97] + "..."
                # Escape special characters to prevent markup errors
                display = escape(display)
                history_text += f"• {display}\n"
            history.update(history_text)
        else:
            history.update("[dim]Sem histórico[/dim]")

    def action_go_back(self) -> None:
        """Go back to project list."""
        self.app.pop_screen()


class ConfirmScreen(Screen[None]):
    """Confirmation dialog screen."""

    def __init__(self, message: str, callback: Callable[[], None]) -> None:
        super().__init__()
        self.message = message
        self.callback = callback

    def compose(self) -> ComposeResult:
        """Create the confirmation dialog."""
        yield Container(
            Static(self.message, id="confirm_message"),
            Horizontal(
                Button("Sim", variant="error", id="yes"),
                Button("Não", variant="primary", id="no"),
                id="button_container",
            ),
            id="confirm_container",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "yes":
            self.callback()
        self.app.pop_screen()


class MCPServerScreen(Screen[None]):
    """Screen for managing MCP servers for a project."""

    BINDINGS = [
        Binding("escape", "go_back", "Voltar"),
        Binding("a", "add_server", "Adicionar Servidor"),
        Binding("d", "delete_server", "Excluir Servidor"),
        Binding("e", "edit_server", "Editar Servidor"),
        Binding("t", "toggle_all", "Alternar Todos"),
    ]

    def __init__(
        self, config_manager: ClaudeConfigManager, project: Project, project_path: str
    ) -> None:
        super().__init__()
        self.config_manager = config_manager
        self.project = project
        self.project_path = project_path

    def compose(self) -> ComposeResult:
        """Create the MCP server management UI."""
        yield Header()
        yield Container(
            Static(f"[bold]Servidores MCP para: {self.project_path}[/bold]", id="mcp_title"),
            Static(
                f"Habilitar todos os servidores: {'✓' if self.project.enable_all_project_mcp_servers else '✗'}",
                id="enable_all_status",
            ),
            DataTable(id="mcp_table"),
            id="mcp_container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Set up the MCP servers table."""
        table = self.query_one("#mcp_table", DataTable)
        table.add_columns("Nome do Servidor", "Configuração")
        table.zebra_stripes = True
        table.cursor_type = "row"
        self.refresh_servers()

    def refresh_servers(self) -> None:
        """Refresh the server list."""
        table = self.query_one("#mcp_table", DataTable)
        table.clear()

        for name, config in self.project.mcp_servers.items():
            # Truncate long configs for display
            config_str = str(config)
            if len(config_str) > 80:
                config_str = config_str[:77] + "..."
            table.add_row(name, config_str, key=name)

        # Update enable all status
        status = self.query_one("#enable_all_status", Static)
        status.update(
            f"Enable all servers: {'✓' if self.project.enable_all_project_mcp_servers else '✗'}"
        )

    def action_go_back(self) -> None:
        """Go back to project list."""
        self.app.pop_screen()

    def action_toggle_all(self) -> None:
        """Toggle enable all servers setting."""
        self.project.enable_all_project_mcp_servers = (
            not self.project.enable_all_project_mcp_servers
        )
        self.config_manager.update_project(self.project)

        if self.config_manager.save_config():
            self.notify("Configuração de todos os servidores atualizada", severity="information")
            self.refresh_servers()
        else:
            self.notify("Falha ao salvar alterações", severity="error")

    def action_add_server(self) -> None:
        """Add a new MCP server."""
        self.app.push_screen(MCPServerEditScreen(self, None, None))

    def action_edit_server(self) -> None:
        """Edit selected MCP server."""
        table = self.query_one("#mcp_table", DataTable)
        if table.cursor_row is not None:
            rows = list(table.rows)
            if 0 <= table.cursor_row < len(rows):
                server_name = str(rows[table.cursor_row].value)
                server_config = self.project.mcp_servers.get(server_name, {})
                self.app.push_screen(MCPServerEditScreen(self, server_name, server_config))

    def action_delete_server(self) -> None:
        """Delete selected MCP server."""
        table = self.query_one("#mcp_table", DataTable)
        if table.cursor_row is not None:
            rows = list(table.rows)
            if 0 <= table.cursor_row < len(rows):
                server_name = str(rows[table.cursor_row].value)
                self.app.push_screen(
                    ConfirmScreen(
                        f"Delete MCP server '{server_name}'?",
                        lambda: self._do_delete_server(server_name),
                    )
                )

    def _do_delete_server(self, server_name: str) -> None:
        """Actually delete the server."""
        if server_name in self.project.mcp_servers:
            del self.project.mcp_servers[server_name]
            self.config_manager.update_project(self.project)

            if self.config_manager.save_config():
                self.notify(f"Deleted server '{server_name}'", severity="information")
                self.refresh_servers()
            else:
                self.notify("Falha ao salvar alterações", severity="error")

    def save_server(self, original_name: str | None, new_name: str, config: dict[str, Any]) -> None:
        """Save a server configuration."""
        # If renaming, remove old entry
        if (
            original_name
            and original_name != new_name
            and original_name in self.project.mcp_servers
        ):
            del self.project.mcp_servers[original_name]

        self.project.mcp_servers[new_name] = config
        self.config_manager.update_project(self.project)

        if self.config_manager.save_config():
            self.notify(f"Saved server '{new_name}'", severity="information")
            self.refresh_servers()
        else:
            self.notify("Falha ao salvar alterações", severity="error")


class MCPServerEditScreen(Screen[None]):
    """Screen for editing MCP server configuration."""

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("ctrl+s", "save", "Save (Ctrl+S)"),
    ]

    def __init__(
        self,
        parent_screen: MCPServerScreen,
        server_name: str | None,
        server_config: dict[str, Any] | None,
    ) -> None:
        super().__init__()
        self.parent_screen = parent_screen
        self.original_name = server_name
        self.server_config = server_config or {}

    def compose(self) -> ComposeResult:
        """Create the edit form."""
        yield Header()
        yield Container(
            Static(
                (
                    "[bold]Editar Servidor MCP[/bold]"
                    if self.original_name
                    else "[bold]Adicionar Servidor MCP[/bold]"
                ),
                id="edit_title",
            ),
            Label("Nome do Servidor:"),
            Input(
                value=self.original_name or "", placeholder="Digite o nome do servidor", id="server_name"
            ),
            Label("Configuração (JSON):"),
            TextArea(
                json.dumps(self.server_config, indent=2) if self.server_config else "{}",
                id="server_config",
                language="json",
            ),
            Static("[dim]Pressione Ctrl+S para salvar, Escape para cancelar[/dim]", id="edit_help"),
            id="edit_container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Focus the name input on mount."""
        self.query_one("#server_name", Input).focus()

    def action_save(self) -> None:
        """Save the server configuration."""
        name_input = self.query_one("#server_name", Input)
        config_area = self.query_one("#server_config", TextArea)

        server_name = name_input.value.strip()
        if not server_name:
            self.notify("Nome do servidor não pode estar vazio", severity="error")
            return

        try:
            # Parse the JSON to validate it
            server_config = json.loads(config_area.text)
            # Store it as a compact single-line JSON in the config
            self.parent_screen.save_server(self.original_name, server_name, server_config)
            self.app.pop_screen()
        except json.JSONDecodeError as e:
            self.notify(f"Invalid JSON: {e}", severity="error")
            return

    def action_cancel(self) -> None:
        """Cancel editing."""
        self.app.pop_screen()


class AnalyzeProjectsScreen(Screen[None]):
    """Screen for analyzing projects and showing issues."""

    BINDINGS = [
        Binding("escape", "go_back", "Voltar"),
        Binding("q", "go_back", "Voltar"),
    ]

    def __init__(self, config_manager: ClaudeConfigManager) -> None:
        super().__init__()
        self.config_manager = config_manager

    def compose(self) -> ComposeResult:
        """Create the analysis view."""
        yield Header()
        yield VerticalScroll(
            Static("[bold]Análise de Projetos[/bold]", id="analysis_title"),
            Static(id="analysis_content"),
            id="analysis_container",
        )
        yield Footer()

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

        # Build analysis report
        report = []

        if non_existent:
            report.append(f"[bold red]Diretórios inexistentes ({len(non_existent)}):[/bold red]")
            for path in non_existent[:10]:
                report.append(f"  • {path}")
            if len(non_existent) > 10:
                report.append(f"  ... e mais {len(non_existent) - 10}")
            report.append("")

        if unused:
            report.append(
                f"[bold yellow]Projetos não utilizados (sem histórico) ({len(unused)}):[/bold yellow]"
            )
            for path in unused[:10]:
                report.append(f"  • {path}")
            if len(unused) > 10:
                report.append(f"  ... e mais {len(unused) - 10}")
            report.append("")

        if large_history:
            report.append(f"[bold blue]Projetos com histórico grande ({len(large_history)}):[/bold blue]")
            for path, count in sorted(large_history, key=lambda x: x[1], reverse=True)[:10]:
                report.append(f"  • {path} ({count} entradas)")
            if len(large_history) > 10:
                report.append(f"  ... e mais {len(large_history) - 10}")
            report.append("")

        if no_trust:
            report.append(
                f"[bold orange]Projetos sem aceitação de confiança ({len(no_trust)}):[/bold orange]"
            )
            for path in no_trust[:10]:
                report.append(f"  • {path}")
            if len(no_trust) > 10:
                report.append(f"  ... e mais {len(no_trust) - 10}")
            report.append("")

        if not report:
            report.append("[green]Nenhum problema encontrado! Todos os projetos parecem saudáveis.[/green]")

        # Summary
        total_projects = len(projects)
        total_history = sum(p.history_count for p in projects.values())
        total_size = sum(p.get_size_estimate() for p in projects.values()) / 1024 / 1024

        summary = [
            "",
            "[bold]Resumo:[/bold]",
            f"Total de projetos: {total_projects}",
            f"Total de entradas no histórico: {total_history}",
            f"Tamanho total estimado: {total_size:.1f} MB",
        ]

        content = self.query_one("#analysis_content", Static)
        content.update("\n".join(report + summary))

    def action_go_back(self) -> None:
        """Go back to project list."""
        self.app.pop_screen()


class HistoryManagementScreen(Screen[None]):
    """Screen for managing project history with retention options."""

    BINDINGS = [
        Binding("escape", "go_back", "Voltar"),
        Binding("q", "go_back", "Voltar"),
        Binding("c", "clear_all", "Limpar Tudo"),
        Binding("k", "keep_recent", "Manter Recentes"),
    ]

    def __init__(
        self, config_manager: ClaudeConfigManager, project: Project, project_path: str
    ) -> None:
        super().__init__()
        self.config_manager = config_manager
        self.project = project
        self.project_path = project_path

    def compose(self) -> ComposeResult:
        """Create the history management UI."""
        yield Header()
        yield Container(
            Static(f"[bold]Gerenciamento de Histórico: {self.project_path}[/bold]", id="history_title"),
            Static(id="history_stats"),
            Static("[bold]Histórico Recente:[/bold]", id="recent_title"),
            Static(id="history_list"),
            Static(
                "\n[dim]Pressione 'c' para limpar tudo, 'k' para manter apenas entradas recentes[/dim]",
                id="history_help",
            ),
            id="history_container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Display history information."""
        # Show statistics
        stats = self.query_one("#history_stats", Static)
        stats.update(
            f"Total de entradas: {self.project.history_count}\n"
            f"Tamanho estimado: {self.project.get_size_estimate() / 1024:.1f} KB"
        )

        # Show recent history
        history_list = self.query_one("#history_list", Static)
        if self.project.history:
            history_text = ""
            for i, entry in enumerate(self.project.history[-10:], 1):
                display = entry.get("display", "")
                if len(display) > 80:
                    display = display[:77] + "..."
                # Escape special characters
                display = escape(display)
                history_text += f"{i}. {display}\n"
            history_list.update(history_text)
        else:
            history_list.update("[dim]Sem entradas de histórico[/dim]")

    def action_go_back(self) -> None:
        """Go back to project list."""
        self.app.pop_screen()

    def action_clear_all(self) -> None:
        """Clear all history."""
        self.app.push_screen(
            ConfirmScreen(
                f"Limpar TODAS as {self.project.history_count} entradas do histórico?\n\nIsso não pode ser desfeito!",
                self._do_clear_all,
            )
        )

    def _do_clear_all(self) -> None:
        """Actually clear all history."""
        self.config_manager.create_backup()
        self.project.history.clear()
        self.config_manager.update_project(self.project)

        if self.config_manager.save_config(create_backup=False):
            self.notify("Todo o histórico foi limpo", severity="information")
            self.app.pop_screen()
        else:
            self.notify("Falha ao salvar alterações", severity="error")

    def action_keep_recent(self) -> None:
        """Show dialog to keep only recent entries."""
        self.app.push_screen(KeepRecentDialog(self._do_keep_recent))

    def _do_keep_recent(self, keep_count: int) -> None:
        """Keep only the specified number of recent entries."""
        if keep_count >= self.project.history_count:
            self.notify("Sem entradas para remover", severity="warning")
            return

        self.config_manager.create_backup()
        # Keep only the last N entries
        self.project.history = self.project.history[-keep_count:]
        self.config_manager.update_project(self.project)

        if self.config_manager.save_config(create_backup=False):
            self.notify(f"Kept {keep_count} most recent entries", severity="information")
            self.app.pop_screen()
        else:
            self.notify("Falha ao salvar alterações", severity="error")


class KeepRecentDialog(Screen[None]):
    """Dialog for specifying how many recent entries to keep."""

    def __init__(self, callback: Callable[[int], None]) -> None:
        super().__init__()
        self.callback = callback

    def compose(self) -> ComposeResult:
        """Create the dialog."""
        yield Container(
            Static("Manter quantas entradas recentes?", id="keep_message"),
            Input(placeholder="Digite um número (ex: 10, 50, 100)", id="keep_input"),
            Horizontal(
                Button("OK", variant="primary", id="ok"),
                Button("Cancelar", variant="default", id="cancel"),
                id="keep_buttons",
            ),
            id="keep_container",
        )

    def on_mount(self) -> None:
        """Focus the input when mounted."""
        self.query_one("#keep_input", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "ok":
            input_widget = self.query_one("#keep_input", Input)
            try:
                count = int(input_widget.value)
                if count > 0:
                    self.callback(count)
                    self.app.pop_screen()
                else:
                    self.notify("Por favor, insira um número positivo", severity="error")
            except ValueError:
                self.notify("Por favor, insira um número válido", severity="error")
        else:
            self.app.pop_screen()

    @on(Input.Submitted)
    def on_input_submitted(self) -> None:
        """Handle Enter key in input."""
        # Trigger OK button
        ok_button = self.query_one("#ok", Button)
        ok_button.press()


class BackupManagementScreen(Screen[None]):
    """Screen for managing configuration backups."""

    BINDINGS = [
        Binding("escape", "go_back", "Voltar"),
        Binding("q", "go_back", "Voltar"),
        Binding("c", "create_backup", "Criar Backup"),
        Binding("r", "restore_backup", "Restaurar Backup"),
        Binding("d", "delete_backup", "Excluir Backup"),
    ]

    def __init__(self, config_manager: ClaudeConfigManager) -> None:
        super().__init__()
        self.config_manager = config_manager
        self.backups: list[Path] = []

    def compose(self) -> ComposeResult:
        """Create the backup management UI."""
        yield Header()
        yield Container(
            Static("[bold]Gerenciamento de Backups[/bold]", id="backup_title"),
            DataTable(id="backup_table"),
            id="backup_container",
        )
        yield Footer()

    def on_mount(self) -> None:
        """Set up the backup table."""
        table = self.query_one("#backup_table", DataTable)
        table.add_columns("Arquivo de Backup", "Data/Hora", "Tamanho")
        table.zebra_stripes = True
        table.cursor_type = "row"
        self.refresh_backups()

    def refresh_backups(self) -> None:
        """Refresh the backup list."""
        table = self.query_one("#backup_table", DataTable)
        table.clear()

        self.backups = list(self.config_manager.get_backups())

        for backup in self.backups:
            # Parse timestamp from filename
            timestamp_str = backup.stem.split("_", 1)[1]
            try:
                from datetime import datetime

                # Try new format with microseconds first
                try:
                    timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S_%f")  # noqa: DTZ007
                except ValueError:
                    # Fall back to old format for existing backups
                    timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")  # noqa: DTZ007
                date_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                date_str = timestamp_str

            size = f"{backup.stat().st_size / 1024:.1f} KB"
            table.add_row(backup.name, date_str, size, key=str(backup))

    def action_go_back(self) -> None:
        """Go back to project list."""
        self.app.pop_screen()

    def action_create_backup(self) -> None:
        """Create a new backup."""
        backup_path = self.config_manager.create_backup()
        if backup_path:
            self.notify(f"Created backup: {backup_path.name}", severity="information")
            self.refresh_backups()
        else:
            self.notify("Falha ao criar backup", severity="error")

    def action_restore_backup(self) -> None:
        """Restore from selected backup."""
        table = self.query_one("#backup_table", DataTable)
        if table.cursor_row is not None:
            rows = list(table.rows)
            if 0 <= table.cursor_row < len(rows):
                backup_path = Path(str(rows[table.cursor_row].value))
                self.app.push_screen(
                    ConfirmScreen(
                        f"Restore from backup?\n\n{backup_path.name}\n\nThis will overwrite your current configuration!",
                        lambda: self._do_restore(backup_path),
                    )
                )

    def _do_restore(self, backup_path: Path) -> None:
        """Actually restore the backup."""
        if self.config_manager.restore_from_backup(backup_path):
            self.notify(f"Restored from {backup_path.name}", severity="information")
            # Refresh the main project list
            self.app.pop_screen()
        else:
            self.notify("Falha ao restaurar backup", severity="error")

    def action_delete_backup(self) -> None:
        """Delete selected backup."""
        table = self.query_one("#backup_table", DataTable)
        if table.cursor_row is not None:
            rows = list(table.rows)
            if 0 <= table.cursor_row < len(rows):
                backup_path = Path(str(rows[table.cursor_row].value))
                self.app.push_screen(
                    ConfirmScreen(
                        f"Delete backup?\n\n{backup_path.name}",
                        lambda: self._do_delete(backup_path),
                    )
                )

    def _do_delete(self, backup_path: Path) -> None:
        """Actually delete the backup."""
        try:
            backup_path.unlink()
            self.notify(f"Deleted {backup_path.name}", severity="information")
            self.refresh_backups()
        except Exception as e:
            self.notify(f"Failed to delete: {e}", severity="error")


class AgentListScreen(Screen[None]):
    """Screen for listing available agents."""
    
    BINDINGS = [
        Binding("escape", "go_back", "Voltar"),
        Binding("q", "go_back", "Voltar"),
        Binding("enter", "view_details", "Ver Detalhes", show=False),
        Binding("r", "refresh", "Atualizar"),
    ]
    
    def __init__(self, config_manager: ClaudeConfigManager) -> None:
        super().__init__()
        self.config_manager = config_manager
        self.agents: dict[str, Agent] = {}
    
    def compose(self) -> ComposeResult:
        """Create the agents list UI."""
        yield Header()
        yield Container(
            Static("[bold]Agentes Disponíveis[/bold]", id="agents_title"),
            DataTable(id="agents_table"),
            id="agents_container",
        )
        yield Footer()
    
    def on_mount(self) -> None:
        """Set up the agents table."""
        table = self.query_one("#agents_table", DataTable)
        table.add_columns("Nome", "Tipo", "Ferramentas", "Prioridade", "Descrição")
        table.zebra_stripes = True
        table.cursor_type = "row"
        self.refresh_agents()
    
    @on(DataTable.RowSelected)
    def on_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection with Enter."""
        self.action_view_details()
    
    def refresh_agents(self) -> None:
        """Refresh the agents list."""
        # Get all agents (global)
        self.agents = self.config_manager.get_agents()
        
        table = self.query_one("#agents_table", DataTable)
        table.clear()
        
        for name, agent in sorted(self.agents.items()):
            # Shorten description
            description = agent.description
            if len(description) > 60:
                description = description[:57] + "..."
            
            # Type indicator
            type_indicator = "🌍 Global" if agent.agent_type == "global" else "📁 Projeto"
            
            # Priority indicator
            priority_display = ""
            if agent.priority:
                if agent.priority == "high":
                    priority_display = "🔴 Alta"
                elif agent.priority == "medium":
                    priority_display = "🟡 Média"
                elif agent.priority == "low":
                    priority_display = "🟢 Baixa"
            
            table.add_row(
                name,
                type_indicator,
                agent.tools_display,
                priority_display,
                description,
                key=name,
            )
    
    def action_go_back(self) -> None:
        """Go back to project list."""
        self.app.pop_screen()
    
    def action_refresh(self) -> None:
        """Refresh the agents list."""
        self.refresh_agents()
    
    def action_view_details(self) -> None:
        """View details of selected agent."""
        table = self.query_one("#agents_table", DataTable)
        if table.cursor_row is not None:
            rows = list(table.rows)
            if 0 <= table.cursor_row < len(rows):
                agent_name = str(rows[table.cursor_row].value)
                if agent_name in self.agents:
                    self.app.push_screen(
                        AgentDetailScreen(self.agents[agent_name])
                    )


class AgentDetailScreen(Screen[None]):
    """Screen showing agent details."""
    
    BINDINGS = [
        Binding("escape", "go_back", "Voltar"),
        Binding("q", "go_back", "Voltar"),
    ]
    
    def __init__(self, agent: Agent) -> None:
        super().__init__()
        self.agent = agent
    
    def compose(self) -> ComposeResult:
        """Create the agent detail view."""
        yield Header()
        yield VerticalScroll(
            Static(f"[bold]Agente: {self.agent.name}[/bold]", id="agent_title"),
            Static(id="agent_info"),
            Static("[bold]Ferramentas:[/bold]", id="tools_title"),
            Static(id="tools_list"),
            Static("[bold]Descrição:[/bold]", id="description_title"),
            Static(id="description_text"),
            id="agent_detail_container",
        )
        yield Footer()
    
    def on_mount(self) -> None:
        """Populate the agent details."""
        # Basic info
        info = self.query_one("#agent_info", Static)
        info_text = []
        info_text.append(f"Tipo: {'Global' if self.agent.agent_type == 'global' else 'Projeto'}")
        if self.agent.color:
            info_text.append(f"Cor: {self.agent.color}")
        if self.agent.priority:
            info_text.append(f"Prioridade: {self.agent.priority}")
        if self.agent.file_path:
            info_text.append(f"Arquivo: {self.agent.file_path}")
        
        # Advanced features
        if self.agent.is_advanced:
            info_text.append("")
            info_text.append("[bold]Recursos Avançados:[/bold]")
            if self.agent.neural_patterns:
                info_text.append(f"Padrões Neurais: {', '.join(self.agent.neural_patterns)}")
            if self.agent.learning_enabled:
                info_text.append("Aprendizado: ✓ Habilitado")
            if self.agent.collective_memory:
                info_text.append("Memória Coletiva: ✓ Habilitada")
            if self.agent.hive_mind_role:
                info_text.append(f"Papel Hive Mind: {self.agent.hive_mind_role}")
            if self.agent.concurrent_execution:
                info_text.append("Execução Concorrente: ✓ Habilitada")
            if self.agent.sparc_integration:
                info_text.append("Integração SPARC: ✓ Habilitada")
        
        info.update("\n".join(info_text))
        
        # Tools list
        tools = self.query_one("#tools_list", Static)
        if self.agent.tools:
            tools_text = "\n".join(f"• {tool}" for tool in self.agent.tools)
        else:
            tools_text = "[dim]Nenhuma ferramenta especificada[/dim]"
        tools.update(tools_text)
        
        # Description
        description = self.query_one("#description_text", Static)
        if self.agent.description:
            # Escape description to prevent markup errors
            desc_text = escape(self.agent.description)
        else:
            desc_text = "[dim]Sem descrição disponível[/dim]"
        description.update(desc_text)
    
    def action_go_back(self) -> None:
        """Go back to agents list."""
        self.app.pop_screen()


class ClaudeManagerApp(App[None]):
    """The main TUI application with robust terminal cleanup."""

    CSS = """
    #main_container {
        height: 100%;
        overflow: auto;
    }

    #projects_table {
        height: 100%;
    }

    #confirm_container {
        align: center middle;
        height: auto;
        width: 60;
        border: thick $background 80%;
        background: $surface;
        padding: 1 2;
        margin: 1 2;
    }

    #confirm_message {
        height: auto;
        margin: 1 0;
        text-align: center;
    }

    #button_container {
        height: auto;
        align: center middle;
        margin-top: 1;
    }

    Button {
        margin: 0 1;
    }

    #detail_container {
        padding: 1 2;
    }

    #project_title {
        margin-bottom: 1;
    }

    #history_title {
        margin-top: 2;
        margin-bottom: 1;
    }

    #mcp_container {
        height: 100%;
        padding: 1 2;
    }

    #mcp_title {
        margin-bottom: 1;
    }

    #enable_all_status {
        margin-bottom: 1;
        color: $text-muted;
    }

    #mcp_table {
        height: 1fr;
    }

    #edit_container {
        align: center middle;
        height: auto;
        width: 80;
        max-width: 100;
        border: thick $background 80%;
        background: $surface;
        padding: 2;
    }

    #edit_title {
        margin-bottom: 1;
        text-align: center;
    }

    #server_name {
        margin-bottom: 1;
    }

    #server_config {
        height: 15;
        margin-bottom: 1;
    }

    #edit_help {
        text-align: center;
        margin-top: 1;
    }

    #analysis_container {
        padding: 1 2;
    }

    #analysis_title {
        margin-bottom: 1;
        text-align: center;
    }

    #backup_container {
        height: 100%;
        padding: 1 2;
    }

    #backup_title {
        margin-bottom: 1;
        text-align: center;
    }

    #backup_table {
        height: 1fr;
    }

    #history_container {
        padding: 1 2;
    }

    #history_title {
        margin-bottom: 1;
    }

    #recent_title {
        margin-top: 2;
        margin-bottom: 1;
    }

    #history_help {
        margin-top: 2;
        color: $text-muted;
    }

    #keep_container {
        align: center middle;
        height: auto;
        width: 50;
        border: thick $background 80%;
        background: $surface;
        padding: 2;
        margin: 1 2;
    }

    #keep_message {
        margin-bottom: 1;
        text-align: center;
    }

    #keep_input {
        margin-bottom: 1;
    }

    #keep_buttons {
        align: center middle;
        margin-top: 1;
    }
    
    #agents_container {
        height: 100%;
        padding: 1 2;
    }
    
    #agents_title {
        margin-bottom: 1;
        text-align: center;
    }
    
    #agents_table {
        height: 1fr;
    }
    
    #agent_detail_container {
        padding: 1 2;
    }
    
    #agent_title {
        margin-bottom: 1;
    }
    
    #tools_title {
        margin-top: 2;
        margin-bottom: 1;
    }
    
    #description_title {
        margin-top: 2;
        margin-bottom: 1;
    }
    
    #agents_title_detail {
        margin-top: 2;
        margin-bottom: 1;
    }
    """

    def __init__(self, config_manager: ClaudeConfigManager) -> None:
        super().__init__()
        self.config_manager = config_manager

    def on_mount(self) -> None:
        """Set up the app."""
        self.title = "Claude Manager"
        self.sub_title = "Manage your Claude Code projects"
        self.push_screen(ProjectListScreen(self.config_manager))
        
    def on_unmount(self) -> None:
        """Clean up when app unmounts."""
        immediate_terminal_reset()
        
    def exit(self, return_code: int = 0) -> None:
        """Override exit to ensure terminal cleanup."""
        immediate_terminal_reset()
        super().exit(return_code)


def run_tui(config_manager: ClaudeConfigManager) -> None:
    """Run the Textual UI with guaranteed cleanup."""
    app = ClaudeManagerApp(config_manager)
    try:
        app.run()
    except Exception:
        # Ensure terminal is reset even if app crashes
        immediate_terminal_reset()
        raise
    finally:
        # Double-check terminal reset on exit
        immediate_terminal_reset()
