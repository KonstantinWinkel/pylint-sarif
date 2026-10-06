#!/bin/bash

# Project Utility Script
# Usage: ./project_utils.sh [setup|clean]

set -e  # Exit immediately if a command exits with a non-zero status

# Determine the project root (directory where this script resides)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

cmd_clean() {
    log_info "Starting cleanup of __pycache__ folders in: $PROJECT_ROOT"

    # Find and delete __pycache__ directories
    count=$(find "$PROJECT_ROOT" -type d -name "__pycache__" | wc -l)

    if [ "$count" -eq 0 ]; then
        log_info "No __pycache__ folders found."
    else
        log_info "Found $count __pycache__ folder(s). Deleting..."
        find "$PROJECT_ROOT" -type d -name "__pycache__" -exec rm -rf {} +
        log_info "Cleanup of __pycache__ complete."
    fi
}

cmd_setup() {
    log_info "Running setup in: $PROJECT_ROOT"

    # Change to project root
    cd "$PROJECT_ROOT" || { log_error "Failed to change directory to $PROJECT_ROOT"; exit 1; }

    # 1. Git Pull
    if [ -d ".git" ]; then
        log_info "Updating repository via git pull..."
        git pull --rebase
        log_info "Git update successful."
    else
        log_warn "Not a git repository. Skipping 'git pull'."
    fi

    # 2. Pip Install
    log_info "Installing dependencies (importlib)..."
    # Check if pip is available
    if command -v pip &> /dev/null; then
        pip install importlib
    elif command -v pip3 &> /dev/null; then
        pip3 install importlib
    else
        log_error "Neither 'pip' nor 'pip3' found. Cannot install python dependencies."
        exit 1
    fi

    log_info "Setup complete."
}

# Main Logic
case "${1:-}" in
    setup)
        cmd_setup
        ;;
    clean)
        cmd_clean
        ;;
    *)
        echo "Usage: $0 {setup|clean}"
        echo ""
        echo "Commands:"
        echo "  setup   - Runs 'git pull' and installs python dependencies"
        echo "  clean   - Removes all '__pycache__' folders recursively"
        exit 1
        ;;
esac