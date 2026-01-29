#!/usr/bin/env python3
"""
Deployment Readiness Checker for Streamlit Cloud
Validates environment, dependencies, and data before deployment
"""

import sys
import subprocess
from pathlib import Path

def check_files():
    """Check if required files exist"""
    print("\n📁 Checking Required Files...")
    # Root is parent of diagnostics/
    root = Path(__file__).resolve().parent.parent
    
    required_files = [
        "Home.py",
        "requirements.txt",
        ".streamlit/config.toml",
        ".streamlit/secrets.toml.example",
        "packages.txt",
        "data/raw/pds_district_monthly_wheat_rice.csv"
    ]
    
    missing = []
    for file in required_files:
        path = root / file
        if path.exists():
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file} - MISSING")
            missing.append(file)
    
    return len(missing) == 0

def check_imports():
    """Test critical imports"""
    print("\n📦 Testing Critical Imports...")
    # Add root to sys.path
    root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(root))
    
    critical_modules = [
        "streamlit",
        "pandas",
        "numpy",
        "plotly",
        "geopandas",
        "folium",
        "prophet",
        "sklearn"
    ]
    
    failed = []
    for module in critical_modules:
        try:
            __import__(module)
            print(f"  ✓ {module}")
        except ImportError:
            try:
                # Try pip installing if missing (simulated check)
                pass 
            except:
                pass
            print(f"  ✗ {module} - FAILED")
            failed.append(module)
    
    return len(failed) == 0

def check_data_size():
    """Check if data directory is too large"""
    print("\n💾 Checking Data Sizes...")
    root = Path(__file__).resolve().parent.parent
    data_path = root / "data"
    
    # Get size of data directory
    try:
        result = subprocess.run(
            ["du", "-sh", "data/raw"],
            capture_output=True,
            text=True
        )
        size = result.stdout.split()[0]
        print(f"  data/raw: {size}")
        
        # Warn if > 100MB
        if "G" in size or (size.replace("M", "").replace(".", "").isdigit() and float(size.replace("M", "")) > 100):
            print(f"  ⚠️  Large data directory may slow deployment")
            print(f"  💡 Consider using Git LFS for files > 100MB")
    except Exception as e:
        print(f"  ⚠️  Could not check size: {e}")
    
    return True

def check_secrets():
    """Check secrets configuration"""
    print("\n🔐 Checking Secrets Configuration...")
    
    secrets_example = Path(".streamlit/secrets.toml.example")
    secrets_real = Path(".streamlit/secrets.toml")
    
    if secrets_example.exists():
        print("  ✓ secrets.toml.example exists")
    else:
        print("  ✗ secrets.toml.example missing")
        return False
    
    if secrets_real.exists():
        print("  ⚠️  secrets.toml exists locally (good for dev)")
        print("  ⚠️  Make sure it's in .gitignore!")
    else:
        print("  ℹ️  No local secrets.toml (will use env vars on cloud)")
    
    # Check gitignore
    gitignore = Path(".gitignore")
    if gitignore.exists():
        content = gitignore.read_text()
        if "secrets.toml" in content:
            print("  ✓ secrets.toml in .gitignore")
            return True
        else:
            print("  ✗ secrets.toml NOT in .gitignore!")
            return False
    
    return True

def check_pages():
    """Check page files exist"""
    print("\n📄 Checking Page Files...")
    pages = [
        "pages/1_Overview.py",
        "pages/2_AI_Intelligence.py",
        "pages/3_About.py"
    ]
    
    missing = []
    for page in pages:
        path = Path(page)
        if path.exists():
            print(f"  ✓ {page}")
        else:
            print(f"  ✗ {page} - MISSING")
            missing.append(page)
    
    return len(missing) == 0

def main():
    """Run all checks"""
    print("═" * 60)
    print("   🚀 Streamlit Cloud Deployment Readiness Check")
    print("═" * 60)
    
    checks = [
        ("Files", check_files),
        ("Imports", check_imports),
        ("Data Size", check_data_size),
        ("Secrets", check_secrets),
        ("Pages", check_pages)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name} check failed with error: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "═" * 60)
    print("   📊 Summary")
    print("═" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} - {name}")
        if not passed:
            all_passed = False
    
    print("\n" + "═" * 60)
    
    if all_passed:
        print("✅ All checks passed! Ready for deployment.")
        print("\n📝 Next Steps:")
        print("  1. Commit all changes to git")
        print("  2. Push to GitHub")
        print("  3. Go to https://share.streamlit.io")
        print("  4. Connect your repository")
        print("  5. Set main file: Home.py")
        print("  6. Add secrets in Streamlit Cloud dashboard")
        print("  7. Deploy!")
        return 0
    else:
        print("❌ Some checks failed. Fix issues before deploying.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
