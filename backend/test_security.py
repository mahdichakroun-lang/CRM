"""
Security validation for FAILLE-0 and FAILLE-1.
Tests that /auth/register is admin-only and DELETE endpoints are admin/manager-only.
"""
import requests, time

BASE = "http://localhost:8000/api/v1"
results = []

def v(name, ok, detail=""):
    s = "PASS" if ok else "FAIL"
    results.append(f"  [{s}] {name}" + (f" | {detail}" if detail else ""))
    return ok

# Wait for backend to be ready
for i in range(10):
    try:
        requests.get(f"{BASE}/auth/me", timeout=2)
        break
    except:
        time.sleep(1)

# ===== Get tokens for different roles =====
admin = requests.post(f"{BASE}/auth/login", json={"email":"admin@crm.com","password":"admin123"})
assert admin.status_code == 200, f"Admin login failed: {admin.status_code}"
admin_h = {"Authorization": f"Bearer {admin.json()['access_token']}"}
admin_role = admin.json()["user"]["role"]

# Get a commercial user token
commercial = requests.post(f"{BASE}/auth/login", json={"email":"commercial@crm.com","password":"admin123"})
if commercial.status_code == 200:
    comm_h = {"Authorization": f"Bearer {commercial.json()['access_token']}"}
    comm_role = commercial.json()["user"]["role"]
else:
    # Create a commercial user for testing
    requests.post(f"{BASE}/users", headers=admin_h, json={
        "name":"TestCommercial","email":"test_comm_sec@crm.com","password":"admin123","role":"commercial"
    })
    commercial = requests.post(f"{BASE}/auth/login", json={"email":"test_comm_sec@crm.com","password":"admin123"})
    comm_h = {"Authorization": f"Bearer {commercial.json()['access_token']}"}
    comm_role = commercial.json()["user"]["role"]

# Get a support user token  
support = requests.post(f"{BASE}/auth/login", json={"email":"support@crm.com","password":"admin123"})
if support.status_code == 200:
    sup_h = {"Authorization": f"Bearer {support.json()['access_token']}"}
    sup_role = support.json()["user"]["role"]
else:
    requests.post(f"{BASE}/users", headers=admin_h, json={
        "name":"TestSupport","email":"test_sup_sec@crm.com","password":"admin123","role":"support"
    })
    support = requests.post(f"{BASE}/auth/login", json={"email":"test_sup_sec@crm.com","password":"admin123"})
    sup_h = {"Authorization": f"Bearer {support.json()['access_token']}"}
    sup_role = support.json()["user"]["role"]

results.append(f"\nRoles: admin={admin_role}, commercial={comm_role}, support={sup_role}")

# ===== FAILLE-0: /auth/register must be admin-only =====
results.append("\n=== FAILLE-0: /auth/register protection ===")

# Test 1: Anonymous register should fail (401)
r = requests.post(f"{BASE}/auth/register", json={
    "name":"Hacker","email":"hacker@evil.com","password":"hack123"
})
v("Anonymous register blocked", r.status_code == 401, f"status={r.status_code}")

# Test 2: Commercial trying to register should fail (403)
r = requests.post(f"{BASE}/auth/register", headers=comm_h, json={
    "name":"CommUser","email":"comm_user@crm.com","password":"test123"
})
v("Commercial register blocked", r.status_code == 403, f"status={r.status_code}")

# Test 3: Support trying to register should fail (403)
r = requests.post(f"{BASE}/auth/register", headers=sup_h, json={
    "name":"SupUser","email":"sup_user@crm.com","password":"test123"
})
v("Support register blocked", r.status_code == 403, f"status={r.status_code}")

# Test 4: Admin CAN register (201)
r = requests.post(f"{BASE}/auth/register", headers=admin_h, json={
    "name":"AdminCreated","email":"admin_created_sec@crm.com","password":"test123"
})
v("Admin register allowed", r.status_code == 201, f"status={r.status_code}")
if r.status_code == 201:
    v("Registered user role is commercial", r.json()["role"] == "commercial", f"role={r.json()['role']}")

# ===== FAILLE-1: DELETE endpoints must be admin/manager-only =====
results.append("\n=== FAILLE-1: DELETE endpoints protection ===")

# Create test data
acc = requests.post(f"{BASE}/accounts", headers=admin_h, json={"name":"SecTest","sector":"IT"})
acc_id = acc.json()["id"] if acc.status_code == 201 else None

cont = requests.post(f"{BASE}/contacts", headers=admin_h, json={
    "first_name":"Sec","last_name":"Test","account_id":1,"email":"sec@test.com"
})
cont_id = cont.json()["id"] if cont.status_code == 201 else None

deal = requests.post(f"{BASE}/deals", headers=admin_h, json={
    "name":"SecDeal","account_id":1,"stage":"qualification","value":100
})
deal_id = deal.json()["id"] if deal.status_code == 201 else None

quote = requests.post(f"{BASE}/quotes", headers=admin_h, json={
    "deal_id":deal_id or 1,"amount":50,"status":"draft"
})
quote_id = quote.json()["id"] if quote.status_code == 201 else None

act = requests.post(f"{BASE}/activities", headers=admin_h, json={
    "type":"note","subject":"SecTest","note":"x","account_id":1
})
act_id = act.json()["id"] if act.status_code == 201 else None

# Test: Commercial CANNOT delete any resource
if act_id:
    r = requests.delete(f"{BASE}/activities/{act_id}", headers=comm_h)
    v("Commercial DELETE activity blocked", r.status_code == 403, f"status={r.status_code}")

if quote_id:
    r = requests.delete(f"{BASE}/quotes/{quote_id}", headers=comm_h)
    v("Commercial DELETE quote blocked", r.status_code == 403, f"status={r.status_code}")

if deal_id:
    r = requests.delete(f"{BASE}/deals/{deal_id}", headers=comm_h)
    v("Commercial DELETE deal blocked", r.status_code == 403, f"status={r.status_code}")

if cont_id:
    r = requests.delete(f"{BASE}/contacts/{cont_id}", headers=comm_h)
    v("Commercial DELETE contact blocked", r.status_code == 403, f"status={r.status_code}")

if acc_id:
    r = requests.delete(f"{BASE}/accounts/{acc_id}", headers=comm_h)
    v("Commercial DELETE account blocked", r.status_code == 403, f"status={r.status_code}")

# Test: Support CANNOT delete any resource  
if act_id:
    r = requests.delete(f"{BASE}/activities/{act_id}", headers=sup_h)
    v("Support DELETE activity blocked", r.status_code == 403, f"status={r.status_code}")

if acc_id:
    r = requests.delete(f"{BASE}/accounts/{acc_id}", headers=sup_h)
    v("Support DELETE account blocked", r.status_code == 403, f"status={r.status_code}")

# Test: Admin CAN delete (cleanup)
if act_id:
    r = requests.delete(f"{BASE}/activities/{act_id}", headers=admin_h)
    v("Admin DELETE activity allowed", r.status_code == 204, f"status={r.status_code}")

if quote_id:
    r = requests.delete(f"{BASE}/quotes/{quote_id}", headers=admin_h)
    v("Admin DELETE quote allowed", r.status_code == 204, f"status={r.status_code}")

if deal_id:
    r = requests.delete(f"{BASE}/deals/{deal_id}", headers=admin_h)
    v("Admin DELETE deal allowed", r.status_code == 204, f"status={r.status_code}")

if cont_id:
    r = requests.delete(f"{BASE}/contacts/{cont_id}", headers=admin_h)
    v("Admin DELETE contact allowed", r.status_code == 204, f"status={r.status_code}")

if acc_id:
    r = requests.delete(f"{BASE}/accounts/{acc_id}", headers=admin_h)
    v("Admin DELETE account allowed", r.status_code == 204, f"status={r.status_code}")

# ===== Verify prior BUG fixes still work (non-regression) =====
results.append("\n=== NON-REGRESSION ===")
r = requests.get(f"{BASE}/reports/sales", headers=admin_h)
v("Sales report still works", r.status_code == 200)

r = requests.get(f"{BASE}/contacts", headers=admin_h, params={"search":"Ben","size":100})
v("Contact search still works", r.json().get("total",0) > 0)

r = requests.get(f"{BASE}/reports/support", headers=admin_h)
v("Support report still works", r.status_code == 200)

# SUMMARY
passes = sum(1 for r in results if "[PASS]" in r)
fails = sum(1 for r in results if "[FAIL]" in r)
results.append(f"\n{'='*50}")
results.append(f"TOTAL: {passes} PASS | {fails} FAIL / {passes+fails}")
results.append(f"{'='*50}")

with open("/tmp/security_results.txt", "w") as f:
    f.write("\n".join(results))

print("\n".join(results))
