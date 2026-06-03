import os
from sqlalchemy import create_engine, inspect, text
from app.config import get_settings

settings = get_settings()
engine = create_engine(settings.DATABASE_URL)

def alter_fks():
    inspector = inspect(engine)
    with engine.begin() as conn:
        # 1. Ticket.created_by : RESTRICT
        # 2. ticket_messages.ticket_id : CASCADE
        # 3. ticket_messages.author_user_id: SET NULL
        # 4. activities account_id, contact_id, deal_id, created_by: SET NULL
        # 5. audit_logs.actor_user_id: SET NULL
        # 6. users.account_id: SET NULL
        
        updates = [
            ("tickets", "created_by", "users", "id", "RESTRICT"),
            ("ticket_messages", "ticket_id", "tickets", "id", "CASCADE"),
            ("ticket_messages", "author_user_id", "users", "id", "SET NULL"),
            ("activities", "account_id", "accounts", "id", "SET NULL"),
            ("activities", "contact_id", "contacts", "id", "SET NULL"),
            ("activities", "deal_id", "deals", "id", "SET NULL"),
            ("activities", "created_by", "users", "id", "SET NULL"),
            ("audit_logs", "actor_user_id", "users", "id", "SET NULL"),
            ("users", "account_id", "accounts", "id", "SET NULL"),
        ]
        
        for table, col, ref_table, ref_col, on_delete in updates:
            print(f"🔧 Synchronisation de la FK {table}.{col} -> ON DELETE {on_delete}...")
            # Find the existing constraint name
            fks = inspector.get_foreign_keys(table)
            constraint_name = None
            for fk in fks:
                if col in fk['constrained_columns'] and fk['referred_table'] == ref_table:
                    constraint_name = fk['name']
                    break
            
            if constraint_name:
                conn.execute(text(f"ALTER TABLE {table} DROP FOREIGN KEY {constraint_name}"))
            
            # Since author_user_id, etc. might need nullable=True now:
            if on_delete == "SET NULL" and col != "created_by": # tickets.created_by is RESTRICT
                 conn.execute(text(f"ALTER TABLE {table} MODIFY {col} INT NULL"))
            
            # Add the new constraint
            conn.execute(text(f"""
                ALTER TABLE {table} 
                ADD CONSTRAINT fk_{table}_{col} 
                FOREIGN KEY ({col}) REFERENCES {ref_table}({ref_col}) 
                ON DELETE {on_delete}
            """))
            print(f"✅ FK mise à jour avec succès sur {table}.{col}")

        print("🔧 Conversion de Deals.value et Quotes.amount en NUMERIC(15,2)...")
        conn.execute(text("ALTER TABLE deals MODIFY value DECIMAL(15,2)"))
        conn.execute(text("ALTER TABLE quotes MODIFY amount DECIMAL(15,2)"))
        print("✅ Types des montants mis à jour")

if __name__ == "__main__":
    try:
        alter_fks()
        print("🎉 Synchronisation de la Base de Données terminée avec succès !")
    except Exception as e:
        print(f"❌ Erreur lors de la synchronisation : {e}")
