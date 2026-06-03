"""
Seed script — Populates the database with demo data.
Run: python -m seed
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from datetime import datetime, timedelta, timezone, date
from app.database import SessionLocal, engine, Base
from app.domain.auth.models import User, UserRole
from app.domain.accounts.models import Account
from app.domain.contacts.models import Contact
from app.domain.leads.models import Lead, LeadSource, LeadStatus
from app.domain.deals.models import Deal, DealStage
from app.domain.activities.models import Activity, ActivityType
from app.domain.quotes.models import Quote, QuoteStatus
from app.domain.tickets.models import Ticket, TicketMessage, TicketPriority, TicketStatus, TicketCategory
from app.domain.audit.models import AuditLog
from app.shared.security import hash_password

now = datetime.now(timezone.utc)


def seed():
    # Create all tables
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Check if already seeded
        if db.query(User).first():
            print("⚠️  Database already contains data. Skipping seed.")
            return

        print("🌱 Seeding database...")

        # ═══════════════════════════════════════════════════
        # 1) USERS
        # ═══════════════════════════════════════════════════
        users = [
            User(name="Admin CRM", email="admin@crm.com", hashed_password=hash_password("admin123"), role=UserRole.ADMIN, phone="+216 555 000 001"),
            User(name="Ahmed Benali", email="ahmed@crm.com", hashed_password=hash_password("ahmed123"), role=UserRole.COMMERCIAL, phone="+216 555 000 002"),
            User(name="Sara Kaddour", email="sara@crm.com", hashed_password=hash_password("sara1234"), role=UserRole.COMMERCIAL, phone="+216 555 000 003"),
            User(name="Omar Tounsi", email="omar@crm.com", hashed_password=hash_password("omar1234"), role=UserRole.SUPPORT, phone="+216 555 000 004"),
            User(name="Fatima Zahra", email="fatima@crm.com", hashed_password=hash_password("fatima123"), role=UserRole.MANAGER, phone="+216 555 000 005"),
        ]
        db.add_all(users)
        db.flush()
        print(f"   ✅ {len(users)} users created")

        # ═══════════════════════════════════════════════════
        # 2) ACCOUNTS (Entreprises)
        # ═══════════════════════════════════════════════════
        accounts = [
            Account(name="Sonatrach", sector="Énergie", industry="Oil & Gas", phone="+216 21 00 00 00", email="contact@sonatrach.dz", city="Alger", country="Algérie", owner_user_id=users[1].id),
            Account(name="Djezzy", sector="Télécommunications", industry="Telecom", phone="+216 21 11 11 11", email="business@djezzy.dz", city="Alger", country="Algérie", owner_user_id=users[1].id),
            Account(name="Groupe Cevital", sector="Agroalimentaire", industry="Food Industry", phone="+216 34 22 22 22", email="info@cevital.dz", city="Béjaïa", country="Algérie", owner_user_id=users[2].id),
            Account(name="ANEM", sector="Public", industry="Government", phone="+216 21 33 33 33", email="contact@anem.dz", city="Alger", country="Algérie", owner_user_id=users[2].id),
            Account(name="Algérie Télécom", sector="Télécommunications", industry="Telecom", phone="+216 21 44 44 44", email="pro@algerietelecom.dz", city="Alger", country="Algérie", owner_user_id=users[1].id),
            Account(name="Cosider Groupe", sector="BTP", industry="Construction", phone="+216 21 55 55 55", email="contact@cosider.dz", city="Alger", country="Algérie", owner_user_id=users[2].id),
        ]
        db.add_all(accounts)
        db.flush()
        print(f"   ✅ {len(accounts)} accounts created")

        # ═══════════════════════════════════════════════════
        # 2b) CLIENT USER (linked to account)
        # ═══════════════════════════════════════════════════
        client_user = User(
            name="Karim Boumediene",
            email="karim@sonatrach.dz",
            hashed_password=hash_password("client123"),
            role=UserRole.CLIENT,
            phone="+216 50 000 000",
            account_id=accounts[0].id,  # Linked to Sonatrach
        )
        db.add(client_user)
        db.flush()
        print(f"   ✅ Client user created: {client_user.name} ({client_user.email}) → {accounts[0].name}")

        # ═══════════════════════════════════════════════════
        # 3) CONTACTS
        # ═══════════════════════════════════════════════════
        contacts = [
            Contact(account_id=accounts[0].id, first_name="Karim", last_name="Boumediene", email="karim.b@sonatrach.dz", phone="+216 660 111 111", position="DSI"),
            Contact(account_id=accounts[0].id, first_name="Nadia", last_name="Mansouri", email="nadia.m@sonatrach.dz", phone="+216 660 111 222", position="Chef de projet"),
            Contact(account_id=accounts[1].id, first_name="Yacine", last_name="Haddad", email="yacine.h@djezzy.dz", phone="+216 770 222 111", position="Directeur IT"),
            Contact(account_id=accounts[2].id, first_name="Lina", last_name="Rebai", email="lina.r@cevital.dz", phone="+216 660 333 111", position="Responsable SI"),
            Contact(account_id=accounts[3].id, first_name="Mourad", last_name="Ait Ahmed", email="mourad.a@anem.dz", phone="+216 550 444 111", position="Directeur"),
            Contact(account_id=accounts[4].id, first_name="Amina", last_name="Cherif", email="amina.c@at.dz", phone="+216 660 555 111", position="Responsable Commercial"),
            Contact(account_id=accounts[5].id, first_name="Mehdi", last_name="Larbi", email="mehdi.l@cosider.dz", phone="+216 770 666 111", position="DG Adjoint"),
        ]
        db.add_all(contacts)
        db.flush()
        print(f"   ✅ {len(contacts)} contacts created")

        # ═══════════════════════════════════════════════════
        # 4) LEADS
        # ═══════════════════════════════════════════════════
        leads = [
            Lead(company_name="Mobilis", contact_name="Ali Bensalem", email="ali@mobilis.dz", phone="+216 770 001 001", source=LeadSource.PHONE, status=LeadStatus.NEW, owner_user_id=users[1].id, estimated_value=500000),
            Lead(company_name="Ooredoo", contact_name="Samira Ouali", email="samira@ooredoo.dz", phone="+216 770 002 002", source=LeadSource.WEBSITE, status=LeadStatus.CONTACTED, owner_user_id=users[2].id, estimated_value=800000),
            Lead(company_name="Condor Electronics", contact_name="Rachid Meziane", email="rachid@condor.dz", source=LeadSource.TRADE_SHOW, status=LeadStatus.QUALIFIED, owner_user_id=users[1].id, estimated_value=1200000),
            Lead(company_name="Brandt Algérie", contact_name="Karima Ferhat", email="karima@brandt.dz", source=LeadSource.REFERRAL, status=LeadStatus.NEW, owner_user_id=users[2].id, estimated_value=350000),
            Lead(company_name="Geant Electronics", contact_name="Hakim Djebbar", source=LeadSource.SOCIAL_MEDIA, status=LeadStatus.UNQUALIFIED, owner_user_id=users[1].id, estimated_value=200000),
            Lead(company_name="ENIE", contact_name="Fatiha Slimani", email="fatiha@enie.dz", source=LeadSource.EMAIL, status=LeadStatus.CONTACTED, owner_user_id=users[2].id, estimated_value=600000),
        ]
        db.add_all(leads)
        db.flush()
        print(f"   ✅ {len(leads)} leads created")

        # ═══════════════════════════════════════════════════
        # 5) DEALS
        # ═══════════════════════════════════════════════════
        deals = [
            Deal(account_id=accounts[0].id, name="ERP Sonatrach - Module Finance", stage=DealStage.NEGOTIATION, value=2500000, probability=70, expected_close_date=date(2026, 4, 15), owner_user_id=users[1].id),
            Deal(account_id=accounts[1].id, name="Infogérance Djezzy - Helpdesk", stage=DealStage.PROPOSAL, value=1800000, probability=50, expected_close_date=date(2026, 5, 1), owner_user_id=users[1].id),
            Deal(account_id=accounts[2].id, name="Intégration SI Cevital", stage=DealStage.QUALIFICATION, value=3000000, probability=30, expected_close_date=date(2026, 6, 30), owner_user_id=users[2].id),
            Deal(account_id=accounts[4].id, name="Migration Cloud AT", stage=DealStage.WON, value=950000, probability=100, expected_close_date=date(2026, 2, 1), owner_user_id=users[2].id),
            Deal(account_id=accounts[3].id, name="Portail RH ANEM", stage=DealStage.LOST, value=700000, probability=0, expected_close_date=date(2026, 1, 15), owner_user_id=users[1].id, lost_reason="Budget insuffisant"),
            Deal(account_id=accounts[5].id, name="TMA Cosider - Maintenance applicative", stage=DealStage.PROPOSAL, value=1200000, probability=60, expected_close_date=date(2026, 4, 30), owner_user_id=users[2].id),
        ]
        db.add_all(deals)
        db.flush()
        print(f"   ✅ {len(deals)} deals created")

        # ═══════════════════════════════════════════════════
        # 6) ACTIVITIES
        # ═══════════════════════════════════════════════════
        activities = [
            Activity(type=ActivityType.CALL, subject="Appel découverte Sonatrach", note="Karim intéressé par le module finance ERP", account_id=accounts[0].id, contact_id=contacts[0].id, deal_id=deals[0].id, created_by=users[1].id, due_date=now + timedelta(days=3)),
            Activity(type=ActivityType.MEETING, subject="RDV démo Djezzy", note="Démonstration du helpdesk, retour positif", account_id=accounts[1].id, contact_id=contacts[2].id, deal_id=deals[1].id, created_by=users[1].id),
            Activity(type=ActivityType.EMAIL, subject="Envoi proposition Cevital", note="Proposition technique envoyée à Lina", account_id=accounts[2].id, contact_id=contacts[3].id, deal_id=deals[2].id, created_by=users[2].id, due_date=now + timedelta(days=7)),
            Activity(type=ActivityType.NOTE, subject="Note interne AT", note="Migration cloud terminée avec succès", account_id=accounts[4].id, deal_id=deals[3].id, created_by=users[2].id),
            Activity(type=ActivityType.CALL, subject="Relance Cosider", note="Mehdi demande un délai pour la décision", account_id=accounts[5].id, contact_id=contacts[6].id, deal_id=deals[5].id, created_by=users[2].id, due_date=now + timedelta(days=5)),
        ]
        db.add_all(activities)
        db.flush()
        print(f"   ✅ {len(activities)} activities created")

        # ═══════════════════════════════════════════════════
        # 7) QUOTES
        # ═══════════════════════════════════════════════════
        quotes = [
            Quote(deal_id=deals[0].id, reference="DEV-2026-001", amount=2500000, status=QuoteStatus.SENT),
            Quote(deal_id=deals[1].id, reference="DEV-2026-002", amount=1800000, status=QuoteStatus.DRAFT),
            Quote(deal_id=deals[3].id, reference="DEV-2026-003", amount=950000, status=QuoteStatus.ACCEPTED),
            Quote(deal_id=deals[5].id, reference="DEV-2026-004", amount=1200000, status=QuoteStatus.SENT),
        ]
        db.add_all(quotes)
        db.flush()
        print(f"   ✅ {len(quotes)} quotes created")

        # ═══════════════════════════════════════════════════
        # 8) TICKETS
        # ═══════════════════════════════════════════════════
        tickets = [
            Ticket(account_id=accounts[0].id, contact_id=contacts[0].id, subject="Erreur module comptabilité", description="Le module compta affiche une erreur 500 lors de la saisie", category=TicketCategory.BUG, priority=TicketPriority.URGENT, status=TicketStatus.IN_PROGRESS, assigned_to=users[3].id, created_by=users[3].id, due_date=now + timedelta(hours=24)),
            Ticket(account_id=accounts[1].id, contact_id=contacts[2].id, subject="Demande formation utilisateurs", description="Formation sur le nouveau dashboard", category=TicketCategory.SUPPORT, priority=TicketPriority.MEDIUM, status=TicketStatus.OPEN, assigned_to=users[3].id, created_by=users[3].id, due_date=now + timedelta(days=5)),
            Ticket(account_id=accounts[4].id, contact_id=contacts[5].id, subject="Lenteur application cloud", description="Performance dégradée depuis la migration", category=TicketCategory.INCIDENT, priority=TicketPriority.HIGH, status=TicketStatus.WAITING_CUSTOMER, assigned_to=users[3].id, created_by=users[3].id, due_date=now + timedelta(days=2)),
            Ticket(account_id=accounts[2].id, contact_id=contacts[3].id, subject="Demande d'ajout de champ", description="Ajouter un champ 'N° bon de commande' dans la fiche fournisseur", category=TicketCategory.FEATURE_REQUEST, priority=TicketPriority.LOW, status=TicketStatus.RESOLVED, assigned_to=users[3].id, created_by=users[0].id, due_date=now - timedelta(days=1), resolved_at=now - timedelta(hours=6)),
            Ticket(account_id=accounts[5].id, subject="Problème impression rapports", description="Les rapports PDF ne s'impriment plus correctement", category=TicketCategory.BUG, priority=TicketPriority.MEDIUM, status=TicketStatus.OPEN, created_by=users[3].id, due_date=now + timedelta(days=3)),
        ]
        db.add_all(tickets)
        db.flush()
        print(f"   ✅ {len(tickets)} tickets created")

        # ═══════════════════════════════════════════════════
        # 9) TICKET MESSAGES
        # ═══════════════════════════════════════════════════
        messages = [
            TicketMessage(ticket_id=tickets[0].id, author_user_id=users[3].id, message="J'ai reproduit le problème. C'est lié à la mise à jour de la semaine dernière."),
            TicketMessage(ticket_id=tickets[0].id, author_user_id=users[0].id, message="Priorité maximale, merci de corriger avant demain.", is_internal=1),
            TicketMessage(ticket_id=tickets[2].id, author_user_id=users[3].id, message="En attente de la réponse du client pour les logs serveur."),
            TicketMessage(ticket_id=tickets[3].id, author_user_id=users[3].id, message="Champ ajouté et déployé en production. Ticket résolu."),
        ]
        db.add_all(messages)
        db.flush()
        print(f"   ✅ {len(messages)} ticket messages created")

        db.commit()
        print("\n🎉 Seed completed successfully!")
        print("\n📋 Demo login credentials:")
        print("   ┌─────────────────────────────────────────────────┐")
        print("   │  Role        │ Email              │ Password    │")
        print("   ├─────────────────────────────────────────────────┤")
        print("   │  Admin       │ admin@crm.com    │ admin123    │")
        print("   │  Commercial  │ ahmed@crm.com    │ ahmed123    │")
        print("   │  Commercial  │ sara@crm.com     │ sara1234    │")
        print("   │  Support     │ omar@crm.com     │ omar1234    │")
        print("   │  Manager     │ fatima@crm.com   │ fatima123   │")
        print("   │  Client      │ karim@sonatrach.dz │ client123   │")
        print("   └─────────────────────────────────────────────────┘")

    except Exception as e:
        db.rollback()
        print(f"❌ Seed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
