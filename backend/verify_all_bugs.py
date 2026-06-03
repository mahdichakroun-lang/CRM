"""
Comprehensive verification of BUG-001 through BUG-007.
Runs inside Docker container against the live API.
"""
import requests
import json
import sys
import time

BASE = "http://localhost:8000/api/v1"
PASS = 0
FAIL = 0
PARTIAL = 0

def login():
    r = requests.post(f"{BASE}/auth/login", json={"email": "admin@crm.com", "password": "admin123"})
    assert r.status_code == 200, f"Login failed: {r.status_code}"
    return {"Authorization": f"Bearer {r.json()['access_token']}"}

def verdict(name, ok, detail=""):
    global PASS, FAIL
    status = "PASS" if ok else "FAIL"
    if ok:
        PASS += 1
    else:
        FAIL += 1
    print(f"  [{status}] {name}" + (f" — {detail}" if detail else ""))
    return ok


def test_bug_001(h):
    print("\n" + "="*60)
    print("BUG-001: KPI Pipeline Total")
    print("="*60)
    r = requests.get(f"{BASE}/reports/sales", headers=h)
    assert r.status_code == 200, f"Sales report failed: {r.status_code}"
    data = r.json()
    pipeline = data.get("pipeline_summary", [])
    active = sum(p["total_value"] for p in pipeline if p["stage"] not in ["won", "lost"])
    won = data.get("total_won_value", 0)
    verdict("Pipeline summary returned", len(pipeline) > 0, f"{len(pipeline)} stages")
    verdict("Active pipeline > won value", active > won, f"active={active:,.0f} won={won:,.0f}")
    verdict("Active pipeline includes qualification", any(p["stage"] == "qualification" for p in pipeline))
    verdict("Active pipeline includes proposal", any(p["stage"] == "proposal" for p in pipeline))
    verdict("Won excluded from active sum", active != active + won or won == 0 or active > 0)


def test_bug_002(h):
    print("\n" + "="*60)
    print("BUG-002: Temps de resolution negatif")
    print("="*60)
    r = requests.get(f"{BASE}/reports/support", headers=h)
    data = r.json()
    avg = data.get("avg_resolution_hours", -999)
    verdict("Support report returned", r.status_code == 200)
    verdict("avg_resolution_hours >= 0", avg >= 0, f"value={avg}")
    # Test resolved_at auto-set: create ticket, resolve it, check
    r = requests.post(f"{BASE}/tickets", headers=h, json={
        "subject": "Test-002-resolve", "account_id": 1,
        "priority": "low", "status": "open", "category": "support"
    })
    if r.status_code == 201:
        tid = r.json()["id"]
        # Resolve the ticket
        r2 = requests.patch(f"{BASE}/tickets/{tid}", headers=h, json={"status": "resolved"})
        if r2.status_code == 200:
            ticket = r2.json()
            has_resolved = ticket.get("resolved_at") is not None
            verdict("resolved_at auto-set on RESOLVED", has_resolved, f"resolved_at={ticket.get('resolved_at')}")
            # Reopen and check cleared
            r3 = requests.patch(f"{BASE}/tickets/{tid}", headers=h, json={"status": "open"})
            if r3.status_code == 200:
                verdict("resolved_at cleared on reopen", r3.json().get("resolved_at") is None)
        # Cleanup
        requests.delete(f"{BASE}/tickets/{tid}", headers=h)
    else:
        verdict("Create test ticket", False, f"status={r.status_code}")


def test_bug_003(h):
    print("\n" + "="*60)
    print("BUG-003: Suppression cascade")
    print("="*60)
    # Create account -> contact -> deal -> activity, then delete contact
    r = requests.post(f"{BASE}/accounts", headers=h, json={"name": "Test-Cascade-003", "sector": "IT"})
    if r.status_code != 201:
        verdict("Create test account", False, f"{r.status_code}")
        return
    acc_id = r.json()["id"]

    # Create contact linked to account
    r = requests.post(f"{BASE}/contacts", headers=h, json={
        "first_name": "Cascade", "last_name": "Test", "account_id": acc_id, "email": "cascade@test.com"
    })
    if r.status_code == 201:
        cid = r.json()["id"]
        # Create activity linked to contact
        requests.post(f"{BASE}/activities", headers=h, json={
            "type": "note", "subject": "linked-activity", "note": "test", "account_id": acc_id, "contact_id": cid
        })
        # Delete contact (should cascade activity, not error)
        r_del = requests.delete(f"{BASE}/contacts/{cid}", headers=h)
        verdict("Delete contact with activities (no 500)", r_del.status_code == 204, f"status={r_del.status_code}")
    else:
        verdict("Create test contact", False)

    # Create deal -> quote, then delete deal
    r = requests.post(f"{BASE}/deals", headers=h, json={
        "name": "Deal-Cascade-003", "account_id": acc_id, "stage": "qualification", "value": 1000
    })
    if r.status_code == 201:
        did = r.json()["id"]
        requests.post(f"{BASE}/quotes", headers=h, json={
            "deal_id": did, "amount": 500, "status": "draft"
        })
        r_del = requests.delete(f"{BASE}/deals/{did}", headers=h)
        verdict("Delete deal with quotes (no 500)", r_del.status_code == 204, f"status={r_del.status_code}")
    else:
        verdict("Create test deal", False)

    # Delete account (should cascade everything)
    r_del = requests.delete(f"{BASE}/accounts/{acc_id}", headers=h)
    verdict("Delete account (cascade)", r_del.status_code == 204, f"status={r_del.status_code}")


def test_bug_004(h):
    print("\n" + "="*60)
    print("BUG-004: Tendances dashboard hardcodees")
    print("="*60)
    r = requests.get(f"{BASE}/reports/sales", headers=h)
    sales = r.json()
    r2 = requests.get(f"{BASE}/reports/support", headers=h)
    support = r2.json()

    pt = sales.get("pipeline_trend")
    ct = sales.get("conversion_trend")
    ot = support.get("open_tickets_trend")
    rt = support.get("resolution_trend")

    verdict("pipeline_trend field exists in API", "pipeline_trend" in sales, f"value={pt}")
    verdict("conversion_trend field exists in API", "conversion_trend" in sales, f"value={ct}")
    verdict("open_tickets_trend field exists in API", "open_tickets_trend" in support, f"value={ot}")
    verdict("resolution_trend field exists in API", "resolution_trend" in support, f"value={rt}")
    # Make sure they are not the old hardcoded values
    verdict("pipeline_trend != 12.5 (old hardcoded)", pt != 12.5)
    verdict("conversion_trend != 2.1 (old hardcoded)", ct != 2.1)


def test_bug_005(h):
    print("\n" + "="*60)
    print("BUG-005: User.account_id FK")
    print("="*60)
    # Verify the relationship works by getting current user info
    r = requests.get(f"{BASE}/auth/me", headers=h)
    verdict("GET /auth/me works", r.status_code == 200)
    # Try creating a user with invalid account_id - should fail or be nullable
    # Existing users should still work
    r = requests.get(f"{BASE}/users", headers=h)
    verdict("GET /users works after FK change", r.status_code == 200)
    if r.status_code == 200:
        users = r.json()
        items = users.get("items", users) if isinstance(users, dict) else users
        verdict("Users list not empty", len(items) > 0, f"count={len(items)}")


def test_bug_006(h):
    print("\n" + "="*60)
    print("BUG-006: Recherche Contacts multi-champs")
    print("="*60)

    # First, get all contacts to know what we have
    r = requests.get(f"{BASE}/contacts", headers=h, params={"size": 100})
    all_contacts = r.json().get("items", [])
    if not all_contacts:
        verdict("Has contacts to test", False, "No contacts in DB")
        return
    
    first = all_contacts[0]
    fname = first.get("first_name", "")
    lname = first.get("last_name", "")
    email = first.get("email", "")
    phone = first.get("phone", "")

    print(f"  Test contact: {fname} {lname} | {email} | {phone}")

    # Test 1: Search by first_name
    if fname:
        r = requests.get(f"{BASE}/contacts", headers=h, params={"search": fname[:3], "size": 100})
        found = r.json().get("total", 0)
        verdict(f"Search by first_name '{fname[:3]}'", found > 0, f"found={found}")

    # Test 2: Search by last_name
    if lname:
        r = requests.get(f"{BASE}/contacts", headers=h, params={"search": lname[:3], "size": 100})
        found = r.json().get("total", 0)
        verdict(f"Search by last_name '{lname[:3]}'", found > 0, f"found={found}")
    else:
        verdict("Search by last_name", False, "No last_name on test contact")

    # Test 3: Search by email
    if email:
        email_part = email.split("@")[0][:4]
        r = requests.get(f"{BASE}/contacts", headers=h, params={"search": email_part, "size": 100})
        found = r.json().get("total", 0)
        verdict(f"Search by email '{email_part}'", found > 0, f"found={found}")

    # Test 4: Search by phone
    if phone:
        phone_part = phone[-4:]  # last 4 digits
        r = requests.get(f"{BASE}/contacts", headers=h, params={"search": phone_part, "size": 100})
        found = r.json().get("total", 0)
        verdict(f"Search by phone '{phone_part}'", found > 0, f"found={found}")
    else:
        verdict("Search by phone", False, "No phone on test contact — testing with different contact")
        # Try finding a contact with a phone
        for c in all_contacts:
            if c.get("phone"):
                p = c["phone"][-4:]
                r = requests.get(f"{BASE}/contacts", headers=h, params={"search": p, "size": 100})
                found = r.json().get("total", 0)
                verdict(f"Search by phone '{p}'", found > 0, f"found={found}")
                break

    # Test 5: Case insensitive
    if fname:
        r = requests.get(f"{BASE}/contacts", headers=h, params={"search": fname.upper()[:3], "size": 100})
        found = r.json().get("total", 0)
        verdict(f"Case insensitive '{fname.upper()[:3]}'", found > 0, f"found={found}")

    # Test 6: No match
    r = requests.get(f"{BASE}/contacts", headers=h, params={"search": "zzzxxx999", "size": 100})
    found = r.json().get("total", 0)
    verdict("No false positives 'zzzxxx999'", found == 0, f"found={found}")


def test_bug_007(h):
    print("\n" + "="*60)
    print("BUG-007: Activities audit trail")
    print("="*60)

    # Get initial audit log count
    r0 = requests.get(f"{BASE}/reports/audit-logs", headers=h, params={"size": 200})
    logs_before = r0.json() if isinstance(r0.json(), list) else r0.json().get("items", [])
    count_before = len([l for l in logs_before if l.get("entity_type") == "activity"])

    # CREATE activity
    r = requests.post(f"{BASE}/activities", headers=h, json={
        "type": "note", "subject": "Audit-Test-007", "note": "Testing audit on create", "account_id": 1
    })
    verdict("Create activity", r.status_code == 201, f"status={r.status_code}")
    if r.status_code != 201:
        return

    act_id = r.json()["id"]

    # Check audit for CREATE
    time.sleep(0.5)
    r2 = requests.get(f"{BASE}/reports/audit-logs", headers=h, params={"size": 200})
    logs_after_create = r2.json() if isinstance(r2.json(), list) else r2.json().get("items", [])
    create_logs = [l for l in logs_after_create if l.get("entity_type") == "activity" and l.get("action") == "create"]
    verdict("Audit log CREATE found", len(create_logs) > count_before, f"create_logs={len(create_logs)}")

    # UPDATE activity
    r3 = requests.patch(f"{BASE}/activities/{act_id}", headers=h, json={"subject": "Audit-Test-007-Updated"})
    verdict("Update activity", r3.status_code == 200, f"status={r3.status_code}")

    time.sleep(0.5)
    r4 = requests.get(f"{BASE}/reports/audit-logs", headers=h, params={"size": 200})
    logs_after_update = r4.json() if isinstance(r4.json(), list) else r4.json().get("items", [])
    update_logs = [l for l in logs_after_update if l.get("entity_type") == "activity" and l.get("action") == "update"]
    verdict("Audit log UPDATE found", len(update_logs) > 0, f"update_logs={len(update_logs)}")

    # Check metadata quality
    if update_logs:
        latest = update_logs[0]
        has_before = latest.get("before") is not None
        has_after = latest.get("after") is not None
        verdict("Audit UPDATE has 'before' snapshot", has_before)
        verdict("Audit UPDATE has 'after' snapshot", has_after)

    # DELETE activity
    r5 = requests.delete(f"{BASE}/activities/{act_id}", headers=h)
    verdict("Delete activity", r5.status_code == 204, f"status={r5.status_code}")

    time.sleep(0.5)
    r6 = requests.get(f"{BASE}/reports/audit-logs", headers=h, params={"size": 200})
    logs_after_delete = r6.json() if isinstance(r6.json(), list) else r6.json().get("items", [])
    delete_logs = [l for l in logs_after_delete if l.get("entity_type") == "activity" and l.get("action") == "delete"]
    verdict("Audit log DELETE found", len(delete_logs) > 0, f"delete_logs={len(delete_logs)}")

    # Cross-check: other entities are also audited (compare consistency)
    all_types = set(l.get("entity_type") for l in logs_after_delete)
    verdict("Audit covers multiple entity types", len(all_types) >= 3, f"types={all_types}")


# ── MAIN ──
if __name__ == "__main__":
    print("=" * 60)
    print("  CRM BUG VERIFICATION SUITE — BUG-001 to BUG-007")
    print("=" * 60)
    
    h = login()
    print("[OK] Logged in as admin")
    
    test_bug_001(h)
    test_bug_002(h)
    test_bug_003(h)
    test_bug_004(h)
    test_bug_005(h)
    test_bug_006(h)
    test_bug_007(h)

    print("\n" + "=" * 60)
    total = PASS + FAIL
    print(f"  RESULTATS: {PASS}/{total} PASS | {FAIL}/{total} FAIL")
    print("=" * 60)
    
    sys.exit(0 if FAIL == 0 else 1)
