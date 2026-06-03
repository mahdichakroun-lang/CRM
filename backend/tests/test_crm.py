"""
Test — Accounts & Leads CRUD + Lead Conversion.
"""


def test_account_crud(client, auth_headers):
    # Create
    resp = client.post("/api/v1/accounts", json={
        "name": "Test Company",
        "sector": "IT",
        "city": "Alger",
    }, headers=auth_headers)
    assert resp.status_code == 201
    account_id = resp.json()["id"]

    # Read
    resp = client.get(f"/api/v1/accounts/{account_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["name"] == "Test Company"

    # Update
    resp = client.patch(f"/api/v1/accounts/{account_id}", json={
        "name": "Updated Company",
    }, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["name"] == "Updated Company"

    # List
    resp = client.get("/api/v1/accounts", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["total"] >= 1

    # Delete
    resp = client.delete(f"/api/v1/accounts/{account_id}", headers=auth_headers)
    assert resp.status_code == 204


def test_lead_crud_and_conversion(client, auth_headers):
    # Create lead
    resp = client.post("/api/v1/leads", json={
        "contact_name": "Prospect Test",
        "company_name": "Prospect Corp",
        "email": "prospect@test.dz",
        "source": "website",
        "estimated_value": 500000,
    }, headers=auth_headers)
    assert resp.status_code == 201
    lead_id = resp.json()["id"]

    # Update to qualified
    resp = client.patch(f"/api/v1/leads/{lead_id}", json={
        "status": "qualified",
    }, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "qualified"

    # Convert
    resp = client.post(f"/api/v1/leads/{lead_id}/convert", json={
        "deal_name": "Deal from Lead",
        "deal_value": 500000,
    }, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["account_id"] > 0
    assert data["contact_id"] > 0
    assert data["deal_id"] > 0

    # Verify lead is converted
    resp = client.get(f"/api/v1/leads/{lead_id}", headers=auth_headers)
    assert resp.json()["status"] == "converted"
