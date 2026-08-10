
import os
import sys

# Add the app directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db

print("Running database migration...")

with app.app_context():
    try:
        with db.engine.connect() as conn:

            # Add delivered_at column
            try:
                conn.execute(db.text(
                    "ALTER TABLE orders ADD COLUMN delivered_at TIMESTAMP NULL"
                ))
                conn.commit()
                print("Added delivered_at column!")
            except Exception as e:
                if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                    print("delivered_at already exists - OK")
                else:
                    print("delivered_at error:", e)

            # Add all other missing columns just in case
            other_cols = [
                ("payment_status", "VARCHAR(50) DEFAULT 'Paid'"),
                ("transaction_id", "VARCHAR(100) DEFAULT ''"),
                ("momo_number",    "VARCHAR(100) DEFAULT ''"),
            ]

            for col, defn in other_cols:
                try:
                    conn.execute(db.text(
                        f"ALTER TABLE orders ADD COLUMN {col} {defn}"
                    ))
                    conn.commit()
                    print(f"Added {col}")
                except Exception:
                    pass

            # Create notifications table
            try:
                conn.execute(db.text("""
                    CREATE TABLE IF NOT EXISTS notifications (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER DEFAULT 0,
                        for_admin BOOLEAN DEFAULT FALSE,
                        title VARCHAR(200) NOT NULL,
                        message VARCHAR(500) NOT NULL,
                        is_read BOOLEAN DEFAULT FALSE,
                        order_id INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                conn.commit()
                print("Notifications table ready!")
            except Exception as e:
                print("Notifications table:", e)

        print("")
        print("Migration complete!")

    except Exception as e:
        print("Migration error:", e)
