#!/usr/bin/env python
"""
Quick smoke test for SkillBridge API endpoints.
Run this to verify the app is responding correctly.
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_health():
    """Test /api/health endpoint"""
    try:
        resp = requests.get(f"{BASE_URL}/api/health", timeout=5)
        print(f"✓ Health: {resp.status_code}")
        print(f"  Response: {resp.json()}\n")
        return resp.status_code == 200
    except Exception as e:
        print(f"✗ Health failed: {str(e)}\n")
        return False


def test_status():
    """Test /api/status endpoint"""
    try:
        resp = requests.get(f"{BASE_URL}/api/status", timeout=5)
        print(f"✓ Status: {resp.status_code}")
        print(f"  Response: {resp.json()}\n")
        return resp.status_code == 200
    except Exception as e:
        print(f"✗ Status failed: {str(e)}\n")
        return False


def test_register():
    """Test /api/auth/register endpoint"""
    try:
        payload = {
            "email": f"test_{int(time.time())}@example.com",
            "password": "test_password_123",
            "name": "Test User"
        }
        resp = requests.post(
            f"{BASE_URL}/api/auth/register",
            json=payload,
            timeout=5
        )
        print(f"✓ Register: {resp.status_code}")
        print(f"  Response: {resp.json()}\n")
        return resp.status_code in [200, 201]
    except Exception as e:
        print(f"✗ Register failed: {str(e)}\n")
        return False


def test_login():
    """Test /api/auth/login endpoint"""
    try:
        # First register
        reg_payload = {
            "email": "smoketest@example.com",
            "password": "smoketest123",
            "name": "Smoke Test"
        }
        requests.post(
            f"{BASE_URL}/api/auth/register",
            json=reg_payload,
            timeout=5
        )
        
        # Then login
        login_payload = {
            "email": "smoketest@example.com",
            "password": "smoketest123"
        }
        resp = requests.post(
            f"{BASE_URL}/api/auth/login",
            json=login_payload,
            timeout=5
        )
        print(f"✓ Login: {resp.status_code}")
        print(f"  Response: {resp.json()}\n")
        return resp.status_code == 200
    except Exception as e:
        print(f"✗ Login failed: {str(e)}\n")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("SkillBridge API Smoke Tests")
    print("=" * 60 + "\n")
    
    results = []
    results.append(("Health", test_health()))
    results.append(("Status", test_status()))
    results.append(("Register", test_register()))
    results.append(("Login", test_login()))
    
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {name}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    print(f"\nTotal: {passed}/{total} tests passed")
    print("=" * 60)
