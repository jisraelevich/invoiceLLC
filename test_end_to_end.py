#!/usr/bin/env python3
"""
End-to-end test: Simulate user workflow
1. Parse & Preview (grid populated)
2. Click Facturate (calls send-to-afip API)
3. Verify results saved back to facturador_calculador JSON
"""
import json
import sys
from pathlib import Path
from datetime import datetime

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from app import app

print("=" * 70)
print("END-TO-END TEST: Facturator Integration")
print("=" * 70)

# Test 1: Setup test data (simulate Parse & Preview)
print("\n[TEST 1] Setup: Create test month data with preview items")
print("-" * 70)

test_year = 2026
test_month = 5
preview_items = [
    {"date": "5/1/2026", "billType": "055", "amount": 11111, "status": "01"},
    {"date": "5/1/2026", "billType": "055", "amount": 2222, "status": "01"},
    {"date": "5/3/2026", "billType": "055", "amount": 3333, "status": "01"},
    {"date": "5/4/2026", "billType": "055", "amount": 44444, "status": "01"},
]

month_data = {
    "year": test_year,
    "month": test_month,
    "estimated": 700000,
    "defaultContent": "",
    "preview": preview_items,
    "results": []
}

# Create JSON file
month_dir = Path(__file__).parent / "data" / "months"
month_dir.mkdir(parents=True, exist_ok=True)
month_file = month_dir / f"{test_year}-{test_month:02d}.json"

with open(month_file, "w", encoding="utf-8") as f:
    json.dump(month_data, f, ensure_ascii=False, indent=2)

print(f"✅ Created test month file: {month_file}")
print(f"   - Preview items: {len(preview_items)}")
print(f"   - Results items: 0 (starting empty)")

# Test 2: Verify JSON before API call
print("\n[TEST 2] Verify JSON state BEFORE send-to-afip")
print("-" * 70)

with open(month_file, "r", encoding="utf-8") as f:
    data_before = json.load(f)

print(f"✅ Before state:")
print(f"   - preview.length: {len(data_before['preview'])}")
print(f"   - results.length: {len(data_before['results'])}")
for idx, item in enumerate(data_before['preview'], 1):
    print(f"     Item {idx}: ${item['amount']} ({item['date']})")

# Test 3: Call the API endpoint
print("\n[TEST 3] Call send-to-afip API endpoint")
print("-" * 70)

with app.test_client() as client:
    print(f"POSTing to: /api/month/{test_year}/{test_month}/send-to-afip")
    
    response = client.post(
        f"/api/month/{test_year}/{test_month}/send-to-afip",
        data=json.dumps(month_data),
        content_type="application/json"
    )
    
    print(f"\nResponse status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ API call successful")
        response_data = response.get_json()
        print(f"\nResponse data:")
        print(f"   - success: {response_data.get('success')}")
        print(f"   - message: {response_data.get('message')}")
        print(f"   - processed: {response_data.get('processed', 'N/A')}")
        
        if 'data' in response_data:
            api_data = response_data['data']
            print(f"\n   - Returned preview.length: {len(api_data.get('preview', []))}")
            print(f"   - Returned results.length: {len(api_data.get('results', []))}")
    else:
        print(f"❌ API call failed")
        print(f"Response: {response.get_json()}")
        sys.exit(1)

# Test 4: Verify JSON after API call
print("\n[TEST 4] Verify JSON state AFTER send-to-afip")
print("-" * 70)

with open(month_file, "r", encoding="utf-8") as f:
    data_after = json.load(f)

print(f"✅ After state:")
print(f"   - preview.length: {len(data_after['preview'])} (should be 0)")
print(f"   - results.length: {len(data_after['results'])} (should have results)")

if len(data_after['preview']) == 0:
    print("   ✅ Preview cleared correctly")
else:
    print(f"   ❌ Preview not cleared! Still has {len(data_after['preview'])} items")

if len(data_after['results']) > 0:
    print(f"   ✅ Results populated with {len(data_after['results'])} items")
    for idx, result in enumerate(data_after['results'], 1):
        print(f"     Result {idx}:")
        print(f"       - Date: {result.get('date')}")
        print(f"       - Amount: ${result.get('amount')}")
        print(f"       - CAE: {result.get('cae', 'N/A')}")
        print(f"       - NRO: {result.get('nro_comprobante', 'N/A')}")
else:
    print(f"   ⚠️  No results! This might be OK if AFIP processing didn't complete")

# Test 5: Verify CSV was created in facturador_afip
print("\n[TEST 5] Verify CSV was written to facturador_afip")
print("-" * 70)

facturador_afip_path = Path(__file__).parent.parent / "facturador_afip"
csv_file = facturador_afip_path / "Facturas" / "facturas.csv"

if csv_file.exists():
    print(f"✅ CSV file exists: {csv_file}")
    
    # Read first few lines
    with open(csv_file, "r", encoding="utf-8") as f:
        lines = f.readlines()[:5]
    
    print(f"   - File size: {csv_file.stat().st_size} bytes")
    print(f"   - Total rows: {len(lines)}")
    print(f"   - Header: {lines[0].strip()[:60]}...")
    if len(lines) > 1:
        print(f"   - First data row: {lines[1].strip()[:60]}...")
else:
    print(f"❌ CSV file NOT found: {csv_file}")

# Test 6: Verify facturador_calculador JSON is persistent
print("\n[TEST 6] Verify persistence: Load JSON again")
print("-" * 70)

with open(month_file, "r", encoding="utf-8") as f:
    data_reload = json.load(f)

print(f"✅ Reloaded from disk:")
print(f"   - preview.length: {len(data_reload['preview'])}")
print(f"   - results.length: {len(data_reload['results'])}")

if len(data_reload['preview']) == 0 and len(data_reload['results']) > 0:
    print("\n✅ STATE PERSISTED CORRECTLY!")
else:
    print("\n⚠️  State may not be correct")

# Summary
print("\n" + "=" * 70)
print("TEST SUMMARY")
print("=" * 70)

if (len(data_after['preview']) == 0 and 
    len(data_after['results']) > 0 and 
    csv_file.exists() and
    response.status_code == 200):
    print("✅ ALL TESTS PASSED!")
    print("\nThe integration is ready for real AFIP testing.")
    print("\nNext steps:")
    print("1. Add some invoices in facturador_calculador")
    print("2. Click 'Parse & Preview' to add to grid")
    print("3. Click 'Facturate' to send to AFIP")
    print("4. Wait for AFIP processing to complete")
    print("5. Results should appear in the Results tab with CAE numbers")
else:
    print("❌ SOME TESTS FAILED - See details above")
    if response.status_code != 200:
        print(f"   API returned {response.status_code}")
    if not csv_file.exists():
        print(f"   CSV file was not created")
    if len(data_after['preview']) != 0:
        print(f"   Preview not cleared ({len(data_after['preview'])} items remain)")
    if len(data_after['results']) == 0:
        print(f"   No results were saved")

print("=" * 70)
