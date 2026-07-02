"""
Test script for the Customer Agent API
Run this after starting the API server
"""

import requests
import json
from time import sleep

BASE_URL = "http://localhost:8000"


def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def test_health():
    """Test health endpoint"""
    print_section("1. Health Check")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_info():
    """Test info endpoint"""
    print_section("2. API Info")
    response = requests.get(f"{BASE_URL}/info")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_add_memory():
    """Test adding a memory"""
    print_section("3. Add Memory")
    payload = {
        "content": "El cliente prefiere brownies warmed up with vanilla ice cream",
        "customer_id": "customer001"
    }
    print(f"Request: {json.dumps(payload, indent=2)}")
    response = requests.post(f"{BASE_URL}/memory/add", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_search_memories():
    """Test searching memories"""
    print_section("4. Search Memories")
    payload = {
        "query": None,
        "customer_id": "customer001"
    }
    print(f"Request: {json.dumps(payload, indent=2)}")
    response = requests.post(f"{BASE_URL}/memory/search", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_list_memories():
    """Test listing all memories"""
    print_section("5. List All Memories")
    customer_id = "customer001"
    response = requests.get(f"{BASE_URL}/memory/list/{customer_id}")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_chat():
    """Test chat endpoint"""
    print_section("6. Chat with Agent")
    payload = {
        "message": "Hola, ¿cuáles son mis preferencias?",
        "customer_id": "customer001"
    }
    print(f"Request: {json.dumps(payload, indent=2)}")
    print("⏳ Waiting for agent response (this may take a few seconds)...")
    response = requests.post(f"{BASE_URL}/chat", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def main():
    print("\n" + "="*60)
    print("  Customer Agent API - Test Suite")
    print("="*60)
    print(f"Base URL: {BASE_URL}")
    
    # Check if API is running
    try:
        requests.get(f"{BASE_URL}/health", timeout=2)
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to API at {BASE_URL}")
        print("   Make sure the API is running:")
        print("   python -m uvicorn api.main:app --reload")
        return

    results = {
        "Health Check": test_health(),
        "API Info": test_info(),
        "Add Memory": test_add_memory(),
        "Search Memories": test_search_memories(),
        "List Memories": test_list_memories(),
        "Chat": test_chat(),
    }

    # Summary
    print_section("Test Summary")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✓ PASS" if passed_test else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")


if __name__ == "__main__":
    main()
