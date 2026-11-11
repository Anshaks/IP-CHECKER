#!/data/data/com.termux/files/usr/bin/bash
# IP CHECKER - Install Script
# Developer: KSURitam

set -e

echo "================================================"
echo "  IP CHECKER - Termux Installation"
echo "  Developer: KSURitam"
echo "================================================"
echo

echo "[*] Updating package list..."
pkg update -y || true

echo "[*] Installing required packages..."
pkg install python iproute2 -y

echo "[*] Optional: Termux:API for clipboard support"
read -p "Install termux-api? [y/N]: " yn
if [[ "$yn" =~ ^[Yy]$ ]]; then
    pkg install termux-api -y || \
        echo "  ! termux-api not installed (install the Termux:API app from F-Droid)"
fi

echo
echo "[*] Setting up directories..."
mkdir -p "$HOME/.ip_checker"

echo "[*] Making scripts executable..."
chmod +x ip_checker.py run.sh 2>/dev/null || true

echo
echo "================================================"
echo "  ✔ Installation Complete"
echo "================================================"
echo
echo "Run the app with:"
echo "  python ip_checker.py"
echo "  OR"
echo "  ./run.sh"
echo