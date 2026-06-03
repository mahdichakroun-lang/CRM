import urllib.request, json

# Test via Nginx (port 3000) - same as browser
login_data = json.dumps({"email": "omar@crm.com", "password": "omar1234"}).encode()
req = urllib.request.Request(
    'http://localhost:3000/api/v1/auth/login',
    data=login_data,
    headers={'Content-Type': 'application/json'}
)
try:
    r = urllib.request.urlopen(req)
    result = json.loads(r.read())
    token = result.get('access_token', '')
    print(f"NGINX LOGIN: OK")
except urllib.error.HTTPError as e:
    print(f"NGINX LOGIN FAIL: {e.code} -> {e.read().decode()[:200]}")
    exit(1)

# Get accounts via nginx
try:
    req3 = urllib.request.Request('http://localhost:3000/api/v1/accounts?size=5', headers={'Authorization': f'Bearer {token}'})
    r3 = urllib.request.urlopen(req3)
    d = json.loads(r3.read())
    print(f"NGINX ACCOUNTS: total={d.get('total', 0)}")
except urllib.error.HTTPError as e:
    print(f"NGINX ACCOUNTS FAIL: {e.code} -> {e.read().decode()[:100]}")

# Get tickets via nginx
try:
    req4 = urllib.request.Request('http://localhost:3000/api/v1/tickets?size=5', headers={'Authorization': f'Bearer {token}'})
    r4 = urllib.request.urlopen(req4)
    d = json.loads(r4.read())
    print(f"NGINX TICKETS: total={d.get('total', 0)}")
except urllib.error.HTTPError as e:
    print(f"NGINX TICKETS FAIL: {e.code} -> {e.read().decode()[:100]}")
