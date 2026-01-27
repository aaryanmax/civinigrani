# CiviNigrani Installation Script for Windows
# Run with: Set-ExecutionPolicy Bypass -Scope Process -Force; .\install.ps1

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  CiviNigrani Installation (Windows)" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python is not installed or not in PATH." -ForegroundColor Red
    Write-Host "   Please install Python 3.8+ from https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Create virtual environment
Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
python -m venv venv

# Activate virtual environment
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host "⬆️  Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install dependencies
Write-Host "📚 Installing dependencies from requirements.txt..." -ForegroundColor Yellow
pip install -r requirements.txt

Write-Host ""
Write-Host "======================================" -ForegroundColor Green
Write-Host "  ✅ Installation Complete!" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green
Write-Host ""
Write-Host "To run CiviNigrani:" -ForegroundColor Cyan
Write-Host "  1. Activate the virtual environment:" -ForegroundColor White
Write-Host "     .\venv\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host "  2. Start the Streamlit app:" -ForegroundColor White
Write-Host "     streamlit run Home.py" -ForegroundColor Gray
Write-Host ""
Write-Host "The dashboard will open in your browser at http://localhost:8501" -ForegroundColor Cyan
Write-Host ""