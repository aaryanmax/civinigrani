# ═══════════════════════════════════════════════════════════
#  🛡️ CiviNigrani Installation Script (Windows)
# ═══════════════════════════════════════════════════════════
# Run with: Set-ExecutionPolicy Bypass -Scope Process -Force; .\install.ps1

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  🛡️ CiviNigrani Installation Script (Windows)" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python (\d+\.\d+)") {
        $version = $matches[1]
        Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
        
        # Check version is 3.8 or higher
        $versionParts = $version.Split('.')
        $major = [int]$versionParts[0]
        $minor = [int]$versionParts[1]
        
        if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 8)) {
            Write-Host "⚠️  Python 3.8+ required, found $version" -ForegroundColor Yellow
            Write-Host "   Please upgrade Python from https://www.python.org/downloads/" -ForegroundColor Yellow
            exit 1
        }
    }
} catch {
    Write-Host "❌ Python is not installed or not in PATH." -ForegroundColor Red
    Write-Host "   Please install Python 3.8+ from:" -ForegroundColor Yellow
    Write-Host "   https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   During installation, make sure to check:" -ForegroundColor Yellow
    Write-Host "   ☑ Add Python to PATH" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Create virtual environment
Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
python -m venv venv

if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "❌ Failed to create virtual environment." -ForegroundColor Red
    Write-Host "   Try running: python -m ensurepip --upgrade" -ForegroundColor Yellow
    exit 1
}

# Activate virtual environment
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host "⬆️  Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet

# Install dependencies
Write-Host "📚 Installing dependencies..." -ForegroundColor Yellow
Write-Host "   This may take a few minutes..." -ForegroundColor Gray
pip install -r requirements.txt --quiet

if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Some packages may have failed to install." -ForegroundColor Yellow
    Write-Host "   Try running: pip install -r requirements.txt" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🔄 Initializing Data Pipeline..." -ForegroundColor Yellow
Write-Host "   1. Fetching raw data & PDFs..." -ForegroundColor Gray
python scripts/scrape_data.py
Write-Host "   2. Extracting grievance intelligence..." -ForegroundColor Gray
python scripts/extract_cpgrams.py

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "  ✅ Installation Complete!" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 To run CiviNigrani:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  1. Activate the virtual environment:" -ForegroundColor White
Write-Host "     .\venv\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host "  2. Start the dashboard:" -ForegroundColor White
Write-Host "     streamlit run Home.py" -ForegroundColor Gray
Write-Host ""
Write-Host "📱 The app will open in your browser at:" -ForegroundColor Cyan
Write-Host "   http://localhost:8501" -ForegroundColor White
Write-Host ""
Write-Host "📖 Pages available:" -ForegroundColor Cyan
Write-Host "   • Overview: Dashboard, Risk Map, Alerts, Grievances" -ForegroundColor White
Write-Host "   • AI Intelligence: ML Forecasts, PGSM Validation" -ForegroundColor White
Write-Host "   • About: Methodology and documentation" -ForegroundColor White
Write-Host ""
Write-Host "🔑 Optional: For live news analysis, create .env file with:" -ForegroundColor Cyan
Write-Host "   NEWS_API_KEY=your_key_from_newsapi.org" -ForegroundColor Gray
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""