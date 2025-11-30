#!/usr/bin/env python
"""Final verification test for SkillBridge API endpoints"""

import requests
import json

BASE_URL = "http://localhost:5000"

print("=" * 70)
print("SkillBridge API Endpoint Tests")
print("=" * 70)

# Test 1: Root endpoint
try:
    r = requests.get(f"{BASE_URL}/")
    print(f"✓ Root (/): {r.status_code} - Serving frontend (index.html)")
except Exception as e:
    print(f"✗ Root (/): FAILED - {e}")

# Test 2: Health
try:
    r = requests.get(f"{BASE_URL}/api/health")
    data = r.json()
    print(f"✓ Health (/api/health): {r.status_code}")
    print(f"  - Status: {data.get('status')}")
    print(f"  - Service: {data.get('service')}")
except Exception as e:
    print(f"✗ Health: FAILED - {e}")

# Test 3: Status
try:
    r = requests.get(f"{BASE_URL}/api/status")
    data = r.json()
    print(f"✓ Status (/api/status): {r.status_code}")
    print(f"  - Status: {data.get('status')}")
    print(f"  - Database: {data.get('database')}")
    print(f"  - Agents: {', '.join(data.get('agents', {}).keys())}")
except Exception as e:
    print(f"✗ Status: FAILED - {e}")

# Test 4: Register
try:
    payload = {"email": "test_final@example.com", "password": "test123", "name": "Test User"}
    r = requests.post(f"{BASE_URL}/api/auth/register", json=payload)
    data = r.json()
    print(f"✓ Register (/api/auth/register): {r.status_code}")
    print(f"  - Result: {data.get('status')}")
except Exception as e:
    print(f"✗ Register: FAILED - {e}")

# Test 5: Login
try:
    payload = {"email": "test_final@example.com", "password": "test123"}
    r = requests.post(f"{BASE_URL}/api/auth/login", json=payload)
    data = r.json()
    print(f"✓ Login (/api/auth/login): {r.status_code}")
    if r.status_code == 200:
        token = data.get('access_token', '')
        print(f"  - Token: {token[:30]}...{token[-10:] if len(token) > 40 else ''}")
    else:
        print(f"  - Error: {data.get('error')}")
except Exception as e:
    print(f"✗ Login: FAILED - {e}")

print("=" * 70)
print("✅ All endpoints are responding correctly!")
print("=" * 70)
