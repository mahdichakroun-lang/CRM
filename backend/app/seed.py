"""
Database seeder — creates demo accounts on first startup.
Only inserts if the users table is empty (idempotent).
"""
import logging
from sqlalchemy.orm import Session
from app.domain.auth.models import User
from app.shared.security import hash_password

logger = logging.getLogger("crm")

DEMO_USERS = [
    {"name": "Admin CRM",         "email": "admin@crm.com",         "password": "admin123",   "role": "admin",      "phone": "+216 70 000 001"},
    {"name": "Fatima Benali",      "email": "fatima@crm.com",        "password": "fatima123",  "role": "manager",    "phone": "+216 70 000 002"},
    {"name": "Ahmed Khaled",       "email": "ahmed@crm.com",         "password": "ahmed123",   "role": "commercial", "phone": "+216 70 000 003"},
    {"name": "Omar Mansouri",      "email": "omar@crm.com",          "password": "omar1234",   "role": "support",    "phone": "+216 70 000 004"},
    {"name": "Karim Sonatrach",    "email": "karim@sonatrach.dz",    "password": "client123",  "role": "client",     "phone": "+216 70 000 005"},
]


def seed_demo_users(db: Session) -> None:
    """Insert demo users if the table is empty."""
    user_count = db.query(User).count()
    if user_count > 0:
        logger.info(f"✅ Seed skipped — {user_count} user(s) already exist")
        return

    logger.info("🌱 Seeding demo users...")
    for u in DEMO_USERS:
        user = User(
            name=u["name"],
            email=u["email"],
            hashed_password=hash_password(u["password"]),
            role=u["role"],
            phone=u.get("phone"),
            is_active=True,
        )
        db.add(user)

    db.commit()
    logger.info(f"✅ {len(DEMO_USERS)} demo users created")
