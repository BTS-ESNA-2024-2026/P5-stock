"""
Script de test rapide pour vérifier les fonctionnalités de l'API
"""

import requests
import json

BASE_URL = "http://localhost:5000/api/v1"

def test_health():
    """Test l'endpoint de santé"""
    print("\n=== Test Health Endpoint ===")
    response = requests.get("http://localhost:5000/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_login():
    """Test la connexion"""
    print("\n=== Test Login ===")
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"username": "admin", "password": "Admin123!@#SecurePassword"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

    if response.status_code == 200:
        return response.json().get('access_token')
    return None

def test_list_asset_types(token):
    """Test la liste des types d'assets"""
    print("\n=== Test List Asset Types ===")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/assets/types", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)[:500]}...")
    return response.status_code == 200

def test_list_missions(token):
    """Test la liste des missions"""
    print("\n=== Test List Missions ===")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/missions", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)[:500]}...")
    return response.status_code == 200

def test_dashboard(token):
    """Test le dashboard"""
    print("\n=== Test Dashboard ===")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/reports/dashboard", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)[:500]}...")
    return response.status_code == 200

def test_list_users(token):
    """Test la liste des utilisateurs"""
    print("\n=== Test List Users ===")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/users", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)[:500]}...")
    return response.status_code == 200

def test_list_weapons(token):
    """Test la liste des armes"""
    print("\n=== Test List Weapons ===")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/assets/weapon", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)[:500]}...")
    return response.status_code == 200

if __name__ == "__main__":
    print("=" * 60)
    print("TEST DE L'API SGLM")
    print("=" * 60)

    results = []

    # Test 1: Health
    results.append(("Health Endpoint", test_health()))

    # Test 2: Login
    token = test_login()
    results.append(("Login", token is not None))

    if token:
        # Test 3-7: Endpoints protégés
        results.append(("List Asset Types", test_list_asset_types(token)))
        results.append(("List Missions", test_list_missions(token)))
        results.append(("Dashboard", test_dashboard(token)))
        results.append(("List Users", test_list_users(token)))
        results.append(("List Weapons", test_list_weapons(token)))

    # Résumé
    print("\n" + "=" * 60)
    print("RÉSUMÉ DES TESTS")
    print("=" * 60)
    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {test_name}")

    print(f"\nRésultat: {passed}/{total} tests réussis")
    print("=" * 60)
