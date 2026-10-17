#!/usr/bin/env bash
# VeloC Linux/macOS Installation Script
set -e
INSTALL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo -e "\033[36mInstalling VeloC 1.0.0 GA from: $INSTALL_DIR\033[0m"

BIN_PATH="/usr/local/bin/veloc"
if [ -w "/usr/local/bin" ]; then
    ln -sf "$INSTALL_DIR/veloc.py" "$BIN_PATH"
    chmod +x "$INSTALL_DIR/veloc.py"
    echo -e "\033[32m[SUCCESS] Linked VeloC to $BIN_PATH\033[0m"
else
    echo "Run with sudo to install globally: sudo ln -sf $INSTALL_DIR/veloc.py /usr/local/bin/veloc"
fi
