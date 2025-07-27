# CLI e Utilitários

## 📋 Visão Geral

O cluster de **CLI e Utilitários** do Claude Manager fornece a interface de linha de comando principal, gerenciamento de sinais, utilitários de terminal e funcionalidades de limpeza e reset, garantindo uma experiência robusta e confiável.

## 🏗️ Arquitetura

### Arquivos Principais
- **`cli.py`** - Interface de linha de comando principal
- **`utils.py`** - Utilitários gerais e gerenciamento de sinais
- **`terminal_utils.py`** - Utilitários específicos de terminal

### Dependências
```python
# CLI
import click
import logging
import sys
from rich.console import Console
from rich.logging import RichHandler

# Utils
import signal
import atexit
from contextlib import contextmanager
from typing import Any, Generator

# Terminal Utils
import os
import shutil
from pathlib import Path
```

## ⚡ Interface de Linha de Comando (CLI)

### Função Principal

```python
@click.command()
@click.option(
    "-c",
    "--config",
    "config_path",
    type=click.Path(exists=False),
    help="Path to claude.json configuration file (default: ~/.claude.json)",
)
@click.option(
    "--no-backup",
    is_flag=True,
    help="Disable automatic backups when making changes",
)
@click.option(
    "--debug",
    is_flag=True,
    help="Enable debug logging",
)
@click.option(
    "--reset-terminal",
    is_flag=True,
    help="Emergency terminal reset (fixes stuck ANSI codes)",
)
@click.version_option(version=__version__, prog_name="claude-manager")
def main(config_path: str | None, no_backup: bool, debug: bool, reset_terminal: bool) -> None:
    """Claude Manager - Manage your Claude Code projects and configurations.
    
    This tool provides a terminal UI for managing Claude Code projects stored
    in the .claude.json configuration file. It supports:
    
    \b
    • Listing and analyzing projects
    • Removing unused or old projects
    • Managing MCP server configurations
    • Clearing project history
    • Creating and restoring backups
    
    Examples:
    
    \b
        # Run with default config location (~/.claude.json)
        claude-manager
        
    \b
        # Use custom config file
        claude-manager -c /path/to/config.json
        
    \b
        # Enable debug logging
        claude-manager --debug
    """
```

### Configuração de Logging

```python
def setup_logging(debug: bool = False) -> None:
    """Set up logging configuration.
    
    Args:
        debug: Whether to enable debug logging
    """
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(message)s",
        handlers=[RichHandler(rich_tracebacks=True)],
    )
```

### Fluxo Principal

```python
def main(config_path: str | None, no_backup: bool, debug: bool, reset_terminal: bool) -> None:
    setup_logging(debug)
    logging.getLogger(__name__)
    
    # Emergency terminal reset option
    if reset_terminal:
        console.print("[yellow]Performing emergency terminal reset...[/yellow]")
        immediate_terminal_reset()
        console.print("[green]Terminal reset completed![/green]")
        console.print("[dim]Mouse tracking and ANSI codes should now be disabled.[/dim]")
        return
    
    # Check terminal compatibility first
    if not check_terminal_compatibility():
        console.print("[yellow]Warning: Terminal may not support full TUI features[/yellow]")
        console.print("[dim]Continuing anyway... Use Ctrl+C to exit if problems occur[/dim]")
    
    # Set up signal handlers and terminal management for clean exit
    with SignalHandler(), safe_terminal() as terminal_manager:
        try:
            # Initialize config manager
            config_manager = ClaudeConfigManager(config_path)
            
            # Load configuration
            if not config_manager.load_config():
                console.print("[red]Failed to load configuration. Exiting.[/red]")
                sys.exit(1)
            
            # Run TUI with terminal management
            run_tui(config_manager)
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Interrupted by user[/yellow]")
            sys.exit(0)
        except Exception as e:
            console.print(f"\n[red]Error: {e}[/red]")
            if debug:
                console.print_exception()
            sys.exit(1)
```

## 🔧 Gerenciamento de Sinais

### SignalHandler Class

```python
class SignalHandler:
    """Context manager for handling system signals gracefully."""
    
    def __init__(self) -> None:
        self._original_handlers: dict[int, Any] = {}
    
    def __enter__(self) -> SignalHandler:
        """Set up signal handlers."""
        # Save original handlers
        self._original_handlers[signal.SIGINT] = signal.signal(signal.SIGINT, self._handle_sigint)
        self._original_handlers[signal.SIGTERM] = signal.signal(signal.SIGTERM, self._handle_sigterm)
        return self
    
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Restore original signal handlers."""
        for sig, handler in self._original_handlers.items():
            signal.signal(sig, handler)
    
    def _handle_sigint(self, signum: int, frame: Any) -> None:
        """Handle SIGINT (Ctrl+C)."""
        print("\n[yellow]Interrupted by user[/yellow]")
        sys.exit(0)
    
    def _handle_sigterm(self, signum: int, frame: Any) -> None:
        """Handle SIGTERM."""
        print("\n[yellow]Received termination signal[/yellow]")
        sys.exit(0)
```

## 🖥️ Utilitários de Terminal

### TerminalManager Class

```python
class TerminalManager:
    """Context manager for safe terminal operations with guaranteed cleanup."""
    
    def __init__(self) -> None:
        self._original_state: dict[str, Any] = {}
        self._cleanup_registered = False
        self._in_context = False
        
    def __enter__(self) -> TerminalManager:
        """Enter the terminal management context."""
        self._in_context = True
        self._save_terminal_state()
        self._register_cleanup()
        return self
        
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context and perform guaranteed cleanup."""
        self._in_context = False
        self.force_reset_terminal()
        
    def _save_terminal_state(self) -> None:
        """Save current terminal state for restoration."""
        try:
            self._original_state = {
                'TERM': os.environ.get('TERM', ''),
                'COLUMNS': os.environ.get('COLUMNS', ''),
                'LINES': os.environ.get('LINES', ''),
            }
        except Exception:
            self._original_state = {}
            
    def _register_cleanup(self) -> None:
        """Register cleanup handlers for various exit scenarios."""
        if self._cleanup_registered:
            return
            
        # Register atexit handler
        atexit.register(self.force_reset_terminal)
        
        # Register signal handlers for clean exit
        for sig in [signal.SIGINT, signal.SIGTERM]:
            try:
                signal.signal(sig, self._signal_handler)
            except (ValueError, OSError):
                pass
                
        self._cleanup_registered = True
```

### Sequências de Reset de Terminal

```python
# Comprehensive terminal reset sequences
TERMINAL_RESET_SEQUENCES = [
    # Mouse tracking disable - CRITICAL for stopping mouse movement codes
    "\033[?1000l",    # Disable normal mouse tracking
    "\033[?1001l",    # Disable mouse highlight tracking
    "\033[?1002l",    # Disable button event tracking
    "\033[?1003l",    # Disable any motion tracking - THIS STOPS MOUSE MOVEMENT CODES!
    "\033[?1004l",    # Disable focus in/out reporting
    "\033[?1005l",    # Disable UTF-8 mouse mode
    "\033[?1006l",    # Disable SGR extended reporting
    "\033[?1015l",    # Disable urxvt extended reporting
    "\033[?1016l",    # Disable pixel position reporting
    "\033[?9l",       # Disable X10 mouse reporting
    "\033[?1000;1002;1003;1004;1005;1006;1015;1016l",  # Bulk disable all mouse modes
    
    # Screen and cursor management
    "\033[?1049l",    # Exit alternate screen buffer
    "\033[?1047l",    # Use normal screen buffer (fallback)
    "\033[?47l",      # Use normal screen buffer (old format)
    "\033[?25h",      # Show cursor
    "\033[?12l",      # Disable cursor blinking
    
    # Query responses disable (fixes [O?2048;0$y)
    "\033[?2048l",    # Disable specific query mode
    "\033[?1l",       # Disable application cursor keys
    "\033[?7h",       # Enable auto-wrap mode
    "\033[>0c",       # Request primary device attributes (clear pending)
    
    # Color and style reset
    "\033[0m",        # Reset all attributes
    "\033[39m",       # Default foreground color
    "\033[49m",       # Default background color
    "\033[22m",       # Normal intensity
    "\033[24m",       # No underline
    "\033[25m",       # No blink
    "\033[27m",       # No reverse
    
    # Clear screen and position
    "\033[2J",        # Clear entire screen
    "\033[H",         # Move cursor to top-left
    "\033[1;1H",      # Move cursor to home position
    
    # Final reset
    "\033c",          # Full terminal reset (RIS - Reset to Initial State)
]
```

### Funções de Reset

```python
def force_reset_terminal(self) -> None:
    """Force terminal reset using comprehensive escape sequences."""
    if not sys.stdout.isatty():
        return
        
    try:
        # Send all reset sequences
        for sequence in TERMINAL_RESET_SEQUENCES:
            sys.stdout.write(sequence)
            sys.stdout.flush()
            
        # Extra flush to ensure all sequences are sent
        sys.stdout.flush()
        
    except (OSError, IOError):
        # If we can't write to stdout, terminal is probably closed
        pass

def immediate_terminal_reset() -> None:
    """Immediately reset terminal without context manager."""
    manager = TerminalManager()
    manager.force_reset_terminal()

def emergency_terminal_cleanup() -> None:
    """Emergency cleanup function that can be called from anywhere."""
    try:
        # This is the nuclear option - reset everything we can think of
        reset_commands = [
            "\033[?1000l\033[?1002l\033[?1003l\033[?1004l\033[?1005l\033[?1006l\033[?1015l\033[?1016l",
            "\033[?1049l\033[?1047l\033[?47l\033[?25h\033[?12l",
            "\033[?2048l\033[?1l\033[?7h\033[>0c",
            "\033[0m\033[39m\033[49m\033[22m\033[24m\033[25m\033[27m",
            "\033[2J\033[H\033[1;1H",
            "\033c"
        ]
        
        for cmd in reset_commands:
            try:
                sys.stdout.write(cmd)
                sys.stdout.flush()
            except Exception:
                continue
                
    except Exception:
        # If all else fails, at least try a simple reset
        try:
            os.system('reset 2>/dev/null || tput reset 2>/dev/null || echo -e "\\033c"')
        except Exception:
            pass
```

## 🔍 Verificação de Compatibilidade

### check_terminal_compatibility()

```python
def check_terminal_compatibility() -> bool:
    """Check if current terminal supports TUI operations."""
    try:
        # Check if we have a TTY
        if not sys.stdout.isatty():
            return False
            
        # Check TERM environment variable
        term = os.environ.get('TERM', '').lower()
        if not term or term in ['dumb', 'unknown']:
            return False
            
        # Check for basic ANSI support
        try:
            sys.stdout.write('\033[0m')
            sys.stdout.flush()
            return True
        except (OSError, IOError):
            return False
            
    except Exception:
        return False
```

## 🔧 Context Managers

### safe_terminal()

```python
@contextmanager
def safe_terminal() -> Generator[TerminalManager, None, None]:
    """Context manager for safe terminal operations."""
    manager = TerminalManager()
    try:
        yield manager.__enter__()
    finally:
        manager.__exit__(None, None, None)
```

## 📊 Opções de Linha de Comando

### Opções Disponíveis

| Opção | Tipo | Padrão | Descrição |
|-------|------|--------|-----------|
| `-c, --config` | `path` | `~/.claude.json` | Caminho para arquivo de configuração |
| `--no-backup` | `flag` | `False` | Desabilitar backups automáticos |
| `--debug` | `flag` | `False` | Habilitar logging de debug |
| `--reset-terminal` | `flag` | `False` | Reset de emergência do terminal |
| `--version` | `flag` | - | Mostrar versão do programa |

### Exemplos de Uso

```bash
# Uso básico
claude-manager

# Com arquivo de configuração customizado
claude-manager -c /path/to/custom/config.json

# Com debug habilitado
claude-manager --debug

# Reset de emergência do terminal
claude-manager --reset-terminal

# Desabilitar backups automáticos
claude-manager --no-backup

# Mostrar versão
claude-manager --version

# Mostrar ajuda
claude-manager --help
```

## 🛡️ Tratamento de Erros

### Estrutura de Tratamento

```python
try:
    # Initialize config manager
    config_manager = ClaudeConfigManager(config_path)
    
    # Load configuration
    if not config_manager.load_config():
        console.print("[red]Failed to load configuration. Exiting.[/red]")
        sys.exit(1)
    
    # Run TUI with terminal management
    run_tui(config_manager)
    
except KeyboardInterrupt:
    console.print("\n[yellow]Interrupted by user[/yellow]")
    # Terminal cleanup happens automatically via context manager
    sys.exit(0)
except Exception as e:
    console.print(f"\n[red]Error: {e}[/red]")
    if debug:
        console.print_exception()
    # Terminal cleanup happens automatically via context manager
    sys.exit(1)
```

### Códigos de Saída

| Código | Significado |
|--------|-------------|
| `0` | Sucesso |
| `1` | Erro geral |
| `2` | Erro de configuração |

## 🔧 Auto-Registro de Cleanup

```python
# Auto-register emergency cleanup on module import
atexit.register(emergency_terminal_cleanup)
```

## 🧪 Testes

### Testes de CLI

```python
def test_version_option(self, runner: CliRunner) -> None:
    """Test --version option."""
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "claude-manager" in result.output
    assert "1.0.0" in result.output

def test_help_option(self, runner: CliRunner) -> None:
    """Test --help option."""
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "Claude Manager" in result.output
    assert "Manage your Claude Code projects" in result.output
    assert "--config" in result.output
    assert "--debug" in result.output

def test_main_success(self, runner: CliRunner, temp_config_file: Path) -> None:
    """Test successful execution."""
    with patch("claude_manager.cli.ClaudeConfigManager") as mock_config_class:
        with patch("claude_manager.cli.run_tui") as mock_run_tui:
            mock_config = Mock()
            mock_config.load_config.return_value = True
            mock_config_class.return_value = mock_config
            
            result = runner.invoke(main, ["-c", str(temp_config_file)])
            
            assert result.exit_code == 0
            mock_config_class.assert_called_once_with(str(temp_config_file))
            mock_config.load_config.assert_called_once()
            mock_run_tui.assert_called_once_with(mock_config)
```

### Testes de Utilitários

```python
def test_signal_handler(self):
    """Test signal handler functionality."""
    with SignalHandler():
        # Test that signal handlers are set up
        assert signal.getsignal(signal.SIGINT) is not None
        assert signal.getsignal(signal.SIGTERM) is not None

def test_terminal_manager(self):
    """Test terminal manager functionality."""
    with TerminalManager() as manager:
        # Test that cleanup is registered
        assert manager._cleanup_registered is True
        assert manager._in_context is True
    
    # Test that cleanup was performed
    assert manager._in_context is False

def test_terminal_compatibility(self):
    """Test terminal compatibility checking."""
    # Should work in a real terminal
    assert check_terminal_compatibility() is True
```

## 🔮 Melhorias Futuras

### Funcionalidades Planejadas
- [ ] Comandos de linha de comando adicionais
- [ ] Modo batch/não-interativo
- [ ] Exportação de configurações
- [ ] Validação de configuração via CLI
- [ ] Scripts de automação
- [ ] Integração com ferramentas de CI/CD

### Otimizações
- [ ] Lazy loading de módulos
- [ ] Cache de configuração
- [ ] Compressão de dados
- [ ] Logging estruturado

---

**CLI e Utilitários** - Interface robusta e confiável para o Claude Manager! ⚡🔧 