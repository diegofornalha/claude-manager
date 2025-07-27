"""Terminal utilities for robust cleanup and reset operations."""

from __future__ import annotations

import atexit
import os
import signal
import sys
from contextlib import contextmanager
from typing import Any, Generator

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
            # Save environment variables that might affect terminal behavior
            self._original_state = {
                'TERM': os.environ.get('TERM', ''),
                'COLUMNS': os.environ.get('COLUMNS', ''),
                'LINES': os.environ.get('LINES', ''),
            }
        except Exception:
            # If we can't save state, we'll still do our best to reset
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
                # Some signals might not be available on all platforms
                pass
                
        self._cleanup_registered = True
        
    def _signal_handler(self, signum: int, frame: Any) -> None:
        """Handle signals by performing cleanup and re-raising."""
        self.force_reset_terminal()
        # Re-raise the signal with default handler
        signal.signal(signum, signal.SIG_DFL)
        os.kill(os.getpid(), signum)
        
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


@contextmanager
def safe_terminal() -> Generator[TerminalManager, None, None]:
    """Context manager for safe terminal operations."""
    manager = TerminalManager()
    try:
        yield manager.__enter__()
    finally:
        manager.__exit__(None, None, None)


def immediate_terminal_reset() -> None:
    """Immediately reset terminal without context manager."""
    manager = TerminalManager()
    manager.force_reset_terminal()


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


# Auto-register emergency cleanup on module import
atexit.register(emergency_terminal_cleanup)