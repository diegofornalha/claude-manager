#!/usr/bin/env python3
"""Test script for agent functionality."""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from claude_manager.config import ClaudeConfigManager
from claude_manager.models import Agent

def test_agent_parsing():
    """Test agent parsing functionality."""
    print("Testing agent parsing...")
    
    config_manager = ClaudeConfigManager()
    
    # Test global agents
    print("\n📍 Testing global agents from ~/.claude/agents/")
    global_agents = config_manager.get_agents()
    
    if global_agents:
        print(f"Found {len(global_agents)} global agents:")
        for name, agent in global_agents.items():
            print(f"\n  🤖 {name}")
            print(f"     Type: {agent.agent_type}")
            print(f"     Tools: {agent.tools_display}")
            print(f"     Priority: {agent.priority or 'None'}")
            print(f"     Advanced: {'Yes' if agent.is_advanced else 'No'}")
            if len(agent.description) > 80:
                print(f"     Description: {agent.description[:77]}...")
            else:
                print(f"     Description: {agent.description}")
    else:
        print("No global agents found.")
    
    # Test project agents (using current directory as example)
    test_project = str(Path.cwd())
    print(f"\n📁 Testing project agents from {test_project}/.claude/agents/")
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
    else:
        print("No project-specific agents found.")
    
    print("\n✅ Agent parsing test completed!")

def test_agent_model():
    """Test Agent model functionality."""
    print("\n\nTesting Agent model...")
    
    # Create a basic agent
    basic_agent = Agent(
        name="test-agent",
        description="A test agent for validation",
        tools=["Read", "Write", "Edit"],
        agent_type="global"
    )
    
    print(f"\n📋 Basic Agent:")
    print(f"   Name: {basic_agent.name}")
    print(f"   Tools Display: {basic_agent.tools_display}")
    print(f"   Is Advanced: {basic_agent.is_advanced}")
    
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
    
    print(f"\n🧠 Advanced Agent:")
    print(f"   Name: {advanced_agent.name}")
    print(f"   Tools Display: {advanced_agent.tools_display}")
    print(f"   Is Advanced: {advanced_agent.is_advanced}")
    print(f"   Neural Patterns: {', '.join(advanced_agent.neural_patterns)}")
    
    print("\n✅ Agent model test completed!")

if __name__ == "__main__":
    test_agent_parsing()
    test_agent_model()
    print("\n🎉 All tests completed!")