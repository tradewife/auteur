#!/bin/bash
# =============================================================================
# Hermes-Auteur Bootstrap Setup
# Run this from inside your local auteur repository clone
# =============================================================================

set -e

echo "=== Hermes-Auteur Direct Integration Bootstrap ==="
echo ""

# 1. Move into repo (adjust if needed)
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "Using repo at: $REPO_ROOT"
cd "$REPO_ROOT"

# 2. Install in editable mode with dev extras
echo ""
echo ">>> Installing auteur in editable mode..."
pip install -e ".[dev]"

# 3. Copy soul and assignment into repo root (or update paths in bootstrap.py)
echo ""
echo ">>> IMPORTANT: Copy these two files into this repo root if not already here:"
echo "    - hermes-auteur-soul.md"
echo "    - assignment-01-the-hollow-ritual.md"
echo ""
echo "You can copy them from wherever you have them (e.g. your artifacts folder)."
echo "Press Enter once copied, or Ctrl+C to abort and copy manually."
read -r

# 4. Grok Imagine browser authentication (uses your SuperGrok Heavy session)
echo ""
echo ">>> Setting up Grok Imagine browser auth for SuperGrok Heavy..."
echo "This will open a browser flow or prompt for cookies/session."
echo "Use the same browser/profile logged into your SuperGrok Heavy account."
auteur browser-auth grok_imagine || echo "If command not found, ensure auteur CLI is in PATH after install."

echo ""
echo "=== Setup complete ==="
echo ""
echo "Next steps:"
echo "1. Run: python bootstrap.py"
echo "2. It will create hermes_context/hermes_initial_context.md"
echo "3. Feed the content of that file (or the two .md files + instructions) into Hermes as starting context."
echo "4. Hermes will then follow the soul + assignment using direct auteur imports (no MCP server needed)."
echo ""
echo "Good luck, maverick."