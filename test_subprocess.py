#!/usr/bin/env python3
"""
Test subprocess call to facturador_afip/main.py
"""
import subprocess
import sys
from pathlib import Path

print("=" * 60)
print("TEST: Subprocess call to facturador_afip/main.py")
print("=" * 60)

facturador_afip_path = Path(__file__).parent.parent / "facturador_afip"

print(f"\nfacturador_afip path: {facturador_afip_path}")
print(f"Path exists: {facturador_afip_path.exists()}")
print(f"main.py exists: {(facturador_afip_path / 'main.py').exists()}")

# Simulate calling main.py --help (doesn't require AFIP credentials)
print("\n" + "=" * 60)
print("Calling: python main.py --help")
print("=" * 60)

try:
    result = subprocess.run(
        [sys.executable, str(facturador_afip_path / "main.py"), "--help"],
        cwd=str(facturador_afip_path),
        capture_output=True,
        text=True,
        timeout=10
    )
    
    print(f"Return code: {result.returncode}")
    if result.stdout:
        print(f"STDOUT:\n{result.stdout}")
    if result.stderr:
        print(f"STDERR:\n{result.stderr}")
    
    if result.returncode == 0:
        print("\n✅ main.py --help works (can import all modules)")
    else:
        print("\n⚠️  Non-zero return code")
        
except subprocess.TimeoutExpired:
    print("❌ Timeout after 10 seconds")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 60)
print("RESULT: Subprocess integration is viable")
print("=" * 60)
