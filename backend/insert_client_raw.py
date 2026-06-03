import sys
from sqlalchemy import text
from app.database import engine
from app.shared.security import hash_password

def insert_client():
    pwd = hash_password("client123")
    query = text("""
        INSERT INTO users (name, email, hashed_password, role, phone, account_id, is_active) 
        VALUES ('Karim Boumediene', 'karim@sonatrach.dz', :pwd, 'client', '+216 50 000 000', 1, 1)
    """)
    with engine.begin() as conn:
        # Check if exists first
        res = conn.execute(text("SELECT id FROM users WHERE email='karim@sonatrach.dz'")).fetchone()
        if res:
            print("Client already exists in DB.")
        else:
            conn.execute(query, {"pwd": pwd})
            print("Client Karim Boumediene inserted successfully!")

if __name__ == "__main__":
    insert_client()
