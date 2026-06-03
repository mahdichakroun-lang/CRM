"""Create dummy ticket using API calls instead of SQL."""
import urllib.request
import urllib.parse
import json

# 1. Login to get token
data = urllib.parse.urlencode({
    'username': 'omar@crm.com',
    'password': 'omar1234'
}).encode('utf-8')
req = urllib.request.Request('http://localhost:8000/api/v1/auth/token', data=data)
response = urllib.request.urlopen(req)
token_data = json.loads(response.read())
access_token = token_data['access_token']

# 2. Create ticket
ticket_payload = {
    'subject': 'Problème de connexion au portail',
    'description': 'Bonjour, je n\'arrive pas à me connecter, le site m\'affiche une erreur 500.',
    'status': 'open',
    'priority': 'high',
    'category': 'incident',
    'account_id': 1
}
req2 = urllib.request.Request(
    'http://localhost:8000/api/v1/tickets',
    data=json.dumps(ticket_payload).encode('utf-8'),
    headers={
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
)
response2 = urllib.request.urlopen(req2)
print('Ticket créé:', json.loads(response2.read()))
