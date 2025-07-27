"""Configuration management for Claude Manager."""

from __future__ import annotations

import json
import logging
import shutil
import yaml
from datetime import datetime
from pathlib import Path
from typing import Any

from claude_manager.models import Agent, Project

logger = logging.getLogger(__name__)


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

    def create_backup(self) -> Path | None:
        """Create a timestamped backup of the current configuration.

        Returns:
            Path to the backup file if successful, None otherwise
        """
        try:
            if not self.config_path.exists():
                return None

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")  # noqa: DTZ005
            backup_path = self.backup_dir / f"claude_{timestamp}.json"

            shutil.copy2(self.config_path, backup_path)
            logger.info(f"Created backup at {backup_path}")

            # Clean old backups (keep last 10)
            self._clean_old_backups()

            return backup_path

        except Exception as e:
            logger.exception(f"Error creating backup: {e}")
            return None

    def _clean_old_backups(self, keep_count: int = 10) -> None:
        """Keep only the most recent backups.

        Args:
            keep_count: Number of backups to keep
        """
        backups = sorted(self.backup_dir.glob("claude_*.json"))
        if len(backups) > keep_count:
            for backup in backups[:-keep_count]:
                backup.unlink()
                logger.debug(f"Removed old backup: {backup}")

    def get_projects(self) -> dict[str, Project]:
        """Get all projects as Project objects.

        Returns:
            Dictionary mapping project paths to Project objects
        """
        projects = {}
        for path, data in self.config_data.get("projects", {}).items():
            projects[path] = Project.from_dict(path, data)
        return projects

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

    def get_config_size(self) -> int:
        """Get the size of the configuration file in bytes.

        Returns:
            Size in bytes, or 0 if file doesn't exist
        """
        if self.config_path.exists():
            return self.config_path.stat().st_size
        return 0

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

    def restore_from_backup(self, backup_path: Path) -> bool:
        """Restore configuration from a backup file.

        Args:
            backup_path: Path to the backup file

        Returns:
            True if successful, False otherwise
        """
        try:
            if not backup_path.exists():
                logger.error(f"Backup file not found: {backup_path}")
                return False

            # Don't create a backup when restoring - it doesn't make sense to
            # backup a corrupted/empty state that we're trying to fix

            # Copy backup to config location
            # Use str() to ensure Windows compatibility
            shutil.copy2(str(backup_path), str(self.config_path))

            # Verify the copy worked
            if not self.config_path.exists():
                logger.error("Failed to copy backup to config location")
                return False

            # Reload the configuration
            return self.load_config()

        except Exception as e:
            logger.exception(f"Error restoring from backup: {e}")
            return False

    def get_backups(self) -> list[Path]:
        """Get list of available backup files.

        Returns:
            List of backup file paths sorted by modification time (most recent first)
        """
        return sorted(self.backup_dir.glob("claude_*.json"), reverse=True)

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
