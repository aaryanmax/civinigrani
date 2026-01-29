"""
PDS Data Diagnostic Script
Run this on Windows to debug path and loading issues
"""

import sys
from pathlib import Path

print("=" * 70)
print("🔍 CiviNigrani PDS Data Diagnostic")
print("=" * 70)

# 1. Python & OS Info
print("\n1️⃣  System Information:")
print(f"   Python version: {sys.version}")
print(f"   Platform: {sys.platform}")
print(f"   Working directory: {Path.cwd()}")

# 2. Check src module
print("\n2️⃣  Module Check:")
try:
    # Add project root to sys.path
    root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(root))
    
    from src.config import PDS_RAW_PATH, PROJECT_ROOT, RAW_DIR
    print(f"   ✅ src.config imported successfully")
    print(f"   PROJECT_ROOT: {PROJECT_ROOT}")
    print(f"   RAW_DIR: {RAW_DIR}")
    print(f"   PDS_RAW_PATH: {PDS_RAW_PATH}")
except Exception as e:
    print(f"   ❌ Failed to import src.config: {e}")
    sys.exit(1)

# 3. Path Resolution
print("\n3️⃣  Path Resolution:")
pds_path_resolved = PDS_RAW_PATH.resolve()
print(f"   Original path: {PDS_RAW_PATH}")
print(f"   Resolved path: {pds_path_resolved}")
print(f"   Path exists: {pds_path_resolved.exists()}")

if pds_path_resolved.exists():
    print(f"   Is file: {pds_path_resolved.is_file()}")
    print(f"   File size: {pds_path_resolved.stat().st_size / 1024 / 1024:.2f} MB")
    print(f"   Readable: {pds_path_resolved.stat().st_mode}")
else:
    print(f"   ❌ File does not exist!")
    print(f"\n   Checking parent directory:")
    parent = pds_path_resolved.parent
    print(f"   Parent path: {parent}")
    print(f"   Parent exists: {parent.exists()}")
    if parent.exists():
        print(f"   Contents of {parent.name}:")
        for item in parent.iterdir():
            print(f"     - {item.name} ({'dir' if item.is_dir() else f'{item.stat().st_size/1024:.1f}KB'})")

# 4. Try Loading with pandas
print("\n4️⃣  Pandas Loading Test:")
if pds_path_resolved.exists():
    try:
        import pandas as pd
        print(f"   Attempting to read CSV...")
        df = pd.read_csv(pds_path_resolved, encoding='utf-8', low_memory=False)
        print(f"   ✅ Successfully loaded {len(df)} rows")
        print(f"   Columns: {list(df.columns)[:5]}...")
    except UnicodeDecodeError:
        print(f"   ⚠️  UTF-8 failed, trying latin-1...")
        try:
            df = pd.read_csv(pds_path_resolved, encoding='latin-1', low_memory=False)
            print(f"   ✅ Successfully loaded {len(df)} rows with latin-1")
        except Exception as e:
            print(f"   ❌ Failed with latin-1: {e}")
    except Exception as e:
        print(f"   ❌ Failed to load: {e}")
        import traceback
        traceback.print_exc()
else:
    print(f"   ⚠️  Skipped (file not found)")

# 5. Try the actual loader
print("\n5️⃣  Testing src.loaders.load_pds_data():")
try:
    from src.loaders import load_pds_data
    print(f"   Calling load_pds_data()...")
    df = load_pds_data()
    print(f"   Result: {len(df)} rows")
    if len(df) == 0:
        print(f"   ⚠️  Empty DataFrame returned - check logs above")
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("✅ Diagnostic complete!")
print("=" * 70)
print("\n💡 If you see errors, please share this output for troubleshooting.")
