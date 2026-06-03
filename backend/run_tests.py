import requests, json, time, sys

BASE = "http://localhost:8000/api/v1"
results = []

def log(msg):
    results.append(msg)

def v(name, ok, detail=""):
    s = "PASS" if ok else "FAIL"
    log(f"  [{s}] {name}" + (f" | {detail}" if detail else ""))
    return ok

# LOGIN
r = requests.post(f"{BASE}/auth/login", json={"email":"admin@crm.com","password":"admin123"})
assert r.status_code == 200
h = {"Authorization": f"Bearer {r.json()['access_token']}"}

# ===== BUG-001 =====
log("\n=== BUG-001: KPI Pipeline Total ===")
r = requests.get(f"{BASE}/reports/sales", headers=h)
s = r.json()
ps = s.get("pipeline_summary", [])
active = sum(p["total_value"] for p in ps if p["stage"] not in ["won","lost"])
won = s.get("total_won_value", 0)
v("API returns pipeline_summary", len(ps) > 0, f"{len(ps)} stages")
v("Active pipeline calculated", active > 0, f"{active}")
v("Active != total_won_value", active != won, f"active={active} won={won}")

# ===== BUG-002 =====
log("\n=== BUG-002: Resolution Time ===")
r = requests.get(f"{BASE}/reports/support", headers=h)
sup = r.json()
avg = sup.get("avg_resolution_hours", -999)
v("avg_resolution_hours >= 0", avg >= 0, f"{avg}")

r = requests.post(f"{BASE}/tickets", headers=h, json={
    "subject":"T002","account_id":1,"priority":"low","status":"open","category":"support"
})
if r.status_code == 201:
    tid = r.json()["id"]
    r2 = requests.patch(f"{BASE}/tickets/{tid}", headers=h, json={"status":"resolved"})
    if r2.status_code == 200:
        v("resolved_at auto-set", r2.json().get("resolved_at") is not None)
        r3 = requests.patch(f"{BASE}/tickets/{tid}", headers=h, json={"status":"open"})
        if r3.status_code == 200:
            v("resolved_at cleared on reopen", r3.json().get("resolved_at") is None)
    requests.delete(f"{BASE}/tickets/{tid}", headers=h)

# ===== BUG-003 =====
log("\n=== BUG-003: Cascade Delete ===")
r = requests.post(f"{BASE}/accounts", headers=h, json={"name":"CascadeTest003","sector":"IT"})
if r.status_code == 201:
    aid = r.json()["id"]
    r = requests.post(f"{BASE}/contacts", headers=h, json={
        "first_name":"Del","last_name":"Test","account_id":aid,"email":"del@test.com"
    })
    if r.status_code == 201:
        cid = r.json()["id"]
        requests.post(f"{BASE}/activities", headers=h, json={
            "type":"note","subject":"act","note":"x","account_id":aid,"contact_id":cid
        })
        rd = requests.delete(f"{BASE}/contacts/{cid}", headers=h)
        v("Delete contact+activities no 500", rd.status_code == 204, f"status={rd.status_code}")

    r = requests.post(f"{BASE}/deals", headers=h, json={
        "name":"DealCascade","account_id":aid,"stage":"qualification","value":100
    })
    if r.status_code == 201:
        did = r.json()["id"]
        requests.post(f"{BASE}/quotes", headers=h, json={"deal_id":did,"amount":50,"status":"draft"})
        rd = requests.delete(f"{BASE}/deals/{did}", headers=h)
        v("Delete deal+quotes no 500", rd.status_code == 204, f"status={rd.status_code}")

    rd = requests.delete(f"{BASE}/accounts/{aid}", headers=h)
    v("Delete account no 500", rd.status_code == 204, f"status={rd.status_code}")

# ===== BUG-004 =====
log("\n=== BUG-004: Dashboard Trends ===")
r = requests.get(f"{BASE}/reports/sales", headers=h)
sales = r.json()
r2 = requests.get(f"{BASE}/reports/support", headers=h)
support = r2.json()
v("pipeline_trend in API", "pipeline_trend" in sales, f"val={sales.get('pipeline_trend')}")
v("conversion_trend in API", "conversion_trend" in sales, f"val={sales.get('conversion_trend')}")
v("open_tickets_trend in API", "open_tickets_trend" in support, f"val={support.get('open_tickets_trend')}")
v("resolution_trend in API", "resolution_trend" in support, f"val={support.get('resolution_trend')}")

# ===== BUG-005 =====
log("\n=== BUG-005: User.account_id FK ===")
r = requests.get(f"{BASE}/auth/me", headers=h)
v("GET /auth/me works", r.status_code == 200)
r = requests.get(f"{BASE}/users", headers=h)
v("GET /users works after FK", r.status_code == 200)

# ===== BUG-006 =====
log("\n=== BUG-006: Contact Search Multi-field ===")
r = requests.get(f"{BASE}/contacts", headers=h, params={"size":100})
contacts = r.json().get("items", [])
if contacts:
    c = contacts[0]
    fn = c.get("first_name","")
    ln = c.get("last_name","")
    em = c.get("email","")
    log(f"  Test: {fn} {ln} | {em}")

    if fn:
        r = requests.get(f"{BASE}/contacts", headers=h, params={"search":fn[:3],"size":100})
        v(f"Search first_name '{fn[:3]}'", r.json().get("total",0) > 0, f"found={r.json().get('total')}")

    if ln:
        r = requests.get(f"{BASE}/contacts", headers=h, params={"search":ln[:3],"size":100})
        v(f"Search last_name '{ln[:3]}'", r.json().get("total",0) > 0, f"found={r.json().get('total')}")

    if em:
        ep = em.split("@")[0][:4]
        r = requests.get(f"{BASE}/contacts", headers=h, params={"search":ep,"size":100})
        v(f"Search email '{ep}'", r.json().get("total",0) > 0, f"found={r.json().get('total')}")

    if fn:
        r = requests.get(f"{BASE}/contacts", headers=h, params={"search":fn.upper()[:3],"size":100})
        v(f"Case insensitive '{fn.upper()[:3]}'", r.json().get("total",0) > 0, f"found={r.json().get('total')}")

    r = requests.get(f"{BASE}/contacts", headers=h, params={"search":"zzzxxx999","size":100})
    v("No false positives", r.json().get("total",0) == 0)

# ===== BUG-007 =====
log("\n=== BUG-007: Activities Audit ===")
r = requests.post(f"{BASE}/activities", headers=h, json={
    "type":"note","subject":"AuditTest007","note":"verify","account_id":1
})
v("Create activity", r.status_code == 201, f"status={r.status_code}")
if r.status_code == 201:
    act_id = r.json()["id"]
    time.sleep(0.3)

    r2 = requests.get(f"{BASE}/reports/audit-logs", headers=h, params={"size":200})
    logs = r2.json() if isinstance(r2.json(), list) else r2.json().get("items",[])
    create_found = any(l.get("entity")=="activity" and l.get("action")=="create" for l in logs)
    v("Audit CREATE logged", create_found)

    r3 = requests.patch(f"{BASE}/activities/{act_id}", headers=h, json={"subject":"AuditTest007-Up"})
    v("Update activity", r3.status_code == 200)
    time.sleep(0.3)

    r4 = requests.get(f"{BASE}/reports/audit-logs", headers=h, params={"size":200})
    logs2 = r4.json() if isinstance(r4.json(), list) else r4.json().get("items",[])
    update_found = any(l.get("entity")=="activity" and l.get("action")=="update" for l in logs2)
    v("Audit UPDATE logged", update_found)

    r5 = requests.delete(f"{BASE}/activities/{act_id}", headers=h)
    v("Delete activity", r5.status_code == 204)
    time.sleep(0.3)

    r6 = requests.get(f"{BASE}/reports/audit-logs", headers=h, params={"size":200})
    logs3 = r6.json() if isinstance(r6.json(), list) else r6.json().get("items",[])
    delete_found = any(l.get("entity")=="activity" and l.get("action")=="delete" for l in logs3)
    v("Audit DELETE logged", delete_found)

# SUMMARY
passes = sum(1 for r in results if "[PASS]" in r)
fails = sum(1 for r in results if "[FAIL]" in r)
log(f"\n{'='*50}")
log(f"TOTAL: {passes} PASS | {fails} FAIL / {passes+fails}")
log(f"{'='*50}")

with open("/tmp/bug_results.txt", "w") as f:
    f.write("\n".join(results))

print("\n".join(results))
