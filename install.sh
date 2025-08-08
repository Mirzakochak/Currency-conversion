#!/bin/bash

set -e
echo "=== Currency Bot Auto Installer ==="

# ===== SETTINGS =====
GITHUB_USER="Mirzakochak"       # <-- اینجا یوزرنیم گیت هاب خودت
GITHUB_REPO="Currency-conversion"      # <-- اینجا اسم ریپوی پروژه
API_KEY="cur_live_u2XtAoOZazmnILhI8CL5Mo5tK86raq51CLUj1nnO"
INSTALL_DIR="$HOME/currency-bot"

# ===== DOWNLOAD PROJECT =====
echo "[...] Downloading project from GitHub..."
rm -rf "$INSTALL_DIR"
git clone https://github.com/$GITHUB_USER/$GITHUB_REPO.git "$INSTALL_DIR"

cd "$INSTALL_DIR"

# ===== GET BOT TOKEN =====
read -p "Enter your Telegram Bot Token: " BOT_TOKEN

# ===== CREATE CONFIG.PY =====
cat > config.py <<EOL
BOT_TOKEN = "$BOT_TOKEN"
CURRENCY_API_KEY = "$API_KEY"
EOL
echo "[OK] config.py created."

# ===== INSTALL DEPENDENCIES =====
echo "[...] Installing dependencies..."
sudo apt update
sudo apt install -y python3 python3-pip git
pip3 install --upgrade pip
pip3 install -r requirements.txt
echo "[OK] Dependencies installed."

# ===== START BOT =====
echo "[...] Starting bot..."
python3 -m handlers &

echo "✅ Installation complete! Bot is running."
