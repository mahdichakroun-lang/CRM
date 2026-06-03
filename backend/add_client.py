"""Add client Karim Boumediene inside Docker - minimal script."""
from app.database import SessionLocal
from app.domain.auth.models import User, UserRole
from app.domain.accounts.models import Account
from app.shared.security import hash_password

db = SessionLocal()
try:
    existing = db.query(User).filter(User.email == "karim@sonatrach.dz").first()
    if existing:
        print(f"Client already exists: {existing.name} (id={existing.id})")
        if not existing.account_id:
            acc = db.query(Account).first()
            if acc:
                existing.account_id = acc.id
                db.commit()
                print(f"Linked to: {acc.name}")
    else:
        acc = db.query(Account).first()
        if not acc:
            print("No accounts found!")
        else:
            u = User(
                name="Karim Boumediene",
                email="karim@sonatrach.dz",
                hashed_password=hash_password("client123"),
                role=UserRole.CLIENT,
                phone="+216 50 000 000",
                account_id=acc.id,
            )
            db.add(u)
            db.commit()
            print(f"Created: {u.name} ({u.email}) -> {acc.name}")
finally:
    db.close()
