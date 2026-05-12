#!/usr/bin/env python3
"""
Test script for send-to-afip endpoint
Tests the new failed bills handling functionality
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5050"

def test_basic_connectivity():
    """Test that the server is responding"""
    print("\n" + "="*60)
    print("TEST 1: Basic Server Connectivity")
    print("="*60)
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            print("✅ Server is responding on port 5050")
            return True
        else:
            print(f"❌ Server returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Server connection failed: {e}")
        return False

def test_get_month():
    """Test getting month data"""
    print("\n" + "="*60)
    print("TEST 2: GET Month Data (2026-04)")
    print("="*60)
    try:
        response = requests.get(f"{BASE_URL}/api/month/2026/4", timeout=5)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Month data retrieved")
            print(f"   - Preview items: {len(data.get('preview', []))}")
            print(f"   - Results items: {len(data.get('results', []))}")
            return True, data
        else:
            print(f"❌ Failed to get month data: {response.text}")
            return False, None
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, None

def test_send_to_afip_with_test_data():
    """Test send-to-afip endpoint with test data"""
    print("\n" + "="*60)
    print("TEST 3: POST send-to-afip with TEST DATA")
    print("="*60)
    
    # Create test invoices
    test_invoices = {
        "preview": [
            {
                "date": "2026-05-01",
                "billType": "055",
                "amount": 1500
            },
            {
                "date": "2026-05-02",
                "billType": "055",
                "amount": 2500
            }
        ],
        "results": []
    }
    
    print(f"Sending {len(test_invoices['preview'])} test invoices:")
    for inv in test_invoices['preview']:
        print(f"  - {inv['date']}: ${inv['amount']}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/month/2026/5/send-to-afip",
            json=test_invoices,
            timeout=60
        )
        
        print(f"\nResponse Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Request successful!")
            print(f"   - Message: {result.get('message', 'N/A')}")
            print(f"   - Processed: {result.get('processed', 0)}")
            print(f"   - Pending: {result.get('pending', 0)}")
            
            # Check response structure
            if 'data' in result:
                data = result['data']
                print(f"\n  Response Data:")
                print(f"   - Preview items (for retry): {len(data.get('preview', []))}")
                print(f"   - Results items (success): {len(data.get('results', []))}")
                
                if data.get('preview'):
                    print(f"\n  ⚠️  PENDING BILLS (failed):")
                    for bill in data.get('preview', []):
                        print(f"      - {bill.get('date')}: ${bill.get('amount')} [STATUS: {bill.get('status', 'unknown')}]")
                
                if data.get('results'):
                    print(f"\n  ✅ PROCESSED BILLS (success):")
                    for bill in data.get('results', []):
                        cae = bill.get('cae', 'N/A')
                        print(f"      - {bill.get('date')}: ${bill.get('amount')} [CAE: {cae[:10] if cae else 'N/A'}...]")
                
                return True, result
            else:
                print("⚠️  No data in response")
                return True, result
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ Error during request: {e}")
        return False, None

def test_verify_data_persistence():
    """Verify that data was saved correctly"""
    print("\n" + "="*60)
    print("TEST 4: Verify Data Persistence (Check saved JSON)")
    print("="*60)
    
    try:
        from pathlib import Path
        month_file = Path("c:\\joelsla apps\\invoice llc\\facturador_calculador\\data\\months\\2026-05.json")
        
        if month_file.exists():
            print(f"✅ Month file exists: {month_file}")
            
            with open(month_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"\n  File Contents:")
            print(f"   - Preview items: {len(data.get('preview', []))}")
            print(f"   - Results items: {len(data.get('results', []))}")
            
            if data.get('preview'):
                print(f"\n  Still PENDING (will retry):")
                for item in data.get('preview', []):
                    print(f"    - {item.get('date')}: ${item.get('amount')}")
            
            if data.get('results'):
                print(f"\n  Successfully PROCESSED:")
                for item in data.get('results', []):
                    print(f"    - {item.get('date')}: ${item.get('amount')} [CAE: {item.get('cae', 'N/A')[:10]}...]")
            
            return True
        else:
            print(f"❌ Month file not found: {month_file}")
            print("   This is expected if facturador_afip didn't process any bills")
            return False
            
    except Exception as e:
        print(f"⚠️  Could not verify file: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "█"*60)
    print("  FACTURADOR CALCULADOR - SEND-TO-AFIP TEST SUITE")
    print("█"*60)
    print(f"  Timestamp: {datetime.now().isoformat()}")
    
    results = {
        "connectivity": test_basic_connectivity(),
        "get_month": test_get_month()[0],
        "send_to_afip": test_send_to_afip_with_test_data()[0],
        "persistence": test_verify_data_persistence()
    }
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, passed_flag in results.items():
        status = "✅ PASS" if passed_flag else "❌ FAIL"
        print(f"{status}: {test_name.replace('_', ' ').title()}")
    
    print(f"\nResult: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ ALL TESTS PASSED - READY FOR LIVE!")
    else:
        print("⚠️  Some tests failed - review output above")

if __name__ == "__main__":
    main()
