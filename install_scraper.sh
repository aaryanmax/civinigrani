#!/usr/bin/env bash
# install_scraper.sh
# One-time setup for Ubuntu 25.10
# Creates venv and installs Python deps needed for scraping + PDF parsing.

set -euo pipefail

echo "==> Updating package lists"
sudo apt-get update -y

echo "==> Installing system packages (if not present)"
# curl, unzip are often present, installing to be safe
sudo apt-get install -y curl unzip

echo "==> Activating venv and upgrading pip"
source ~/Projects/venv/bin/activate
cd ~/Projects/civinigrani
# shellcheck disable=SC1091
pip install --upgrade pip setuptools wheel

echo "==> Installing Python requirements"
# Minimal requirements file created on-the-fly if not present
if [ ! -f requirements.txt ]; then
  cat > requirements.txt <<'REQ'
requests
beautifulsoup4
lxml
pandas
tqdm
pdfplumber
python-dateutil
urllib3
REQ
fi

pip install -r requirements.txt

echo "==> Setup complete."
echo "To start scraping run: source ~/Projects/venv/bin/activate && cd ~/Projects/civinigrani && python scripts/scrape_data.py"
