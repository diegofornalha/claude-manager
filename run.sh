#!/bin/bash

# Claude Manager Runner Script
# This script runs the Claude Manager TUI application

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BLUE}Claude Manager Runner${NC}"
echo "======================================"

# Check if we're in the right directory
if [[ ! -f "$SCRIPT_DIR/pyproject.toml" ]]; then
    echo -e "${RED}Error: pyproject.toml not found. Make sure you're running this from the claude-manager directory.${NC}"
    exit 1
fi

# Change to the project directory
cd "$SCRIPT_DIR"

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo -e "${RED}Error: uv is not installed. Please install uv first:${NC}"
    echo "curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo -e "${YELLOW}Installing dependencies...${NC}"
uv sync

echo -e "${YELLOW}Starting Claude Manager...${NC}"
echo -e "${BLUE}Press Ctrl+C to exit the application${NC}"
echo "======================================"

# Run the application
uv run claude-manager "$@"

echo -e "${GREEN}Claude Manager exited.${NC}"