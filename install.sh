#!/usr/bin/env bash
set -e

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  🛡️ CiviNigrani Installation Script (Linux/macOS)"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed."
    echo "   Please install Python 3.8+ and try again."
    echo "   Download from: https://www.python.org/downloads/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✅ Python found: $PYTHON_VERSION"

# Check Python version is 3.8 or higher
PYTHON_MAJOR=$(python3 -c 'import sys; print(sys.version_info[0])')
PYTHON_MINOR=$(python3 -c 'import sys; print(sys.version_info[1])')

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    echo "⚠️  Python 3.8+ required, found $PYTHON_VERSION"
    echo "   Please upgrade Python and try again."
    exit 1
fi

echo ""
echo "📦 Creating virtual environment..."
python3 -m venv venv

echo "🔧 Activating virtual environment..."
source venv/bin/activate

echo "⬆️  Upgrading pip..."
pip install --upgrade pip --quiet

echo "📚 Installing dependencies..."
echo "   This may take a few minutes..."
pip install -r requirements.txt --quiet

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  ✅ Installation Complete!"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "🚀 To run CiviNigrani:"
echo ""
echo "  1. Activate the virtual environment:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Start the dashboard:"
echo "     streamlit run Home.py"
echo ""
echo "📱 The app will open in your browser at:"
echo "   http://localhost:8501"
echo ""
echo "📖 Pages available:"
echo "   • Overview: Dashboard, Risk Map, Alerts, Grievances"
echo "   • AI Intelligence: ML Forecasts, PGSM Validation"
echo "   • About: Methodology and documentation"
echo ""
echo "🔑 Optional: For live news analysis, create .env file with:"
echo "   NEWS_API_KEY=your_key_from_newsapi.org"
echo ""
echo "═══════════════════════════════════════════════════════════"