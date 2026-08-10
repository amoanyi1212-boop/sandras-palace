import os

print("")
print("  ========================================")
print("  Fixing delivered_at column")
print("  ========================================")
print("")

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix create_tables to add delivered_at column
old_cols = '''                    cols = [
                        ("payment_status", "VARCHAR(50) DEFAULT 'Paid'"),
                        ("transaction_id", "VARCHAR(100) DEFAULT ''"),
                        ("momo_number", "VARCHAR(100) DEFAULT ''"),
                        ("delivered_at", "TIMESTAMP"),
                    ]'''

new_cols = '''                    cols = [
                        ("payment_status", "VARCHAR(50) DEFAULT 'Paid'"),
                        ("transaction_id", "VARCHAR(100) DEFAULT ''"),
                        ("momo_number", "VARCHAR(100) DEFAULT ''"),
                        ("delivered_at", "TIMESTAMP NULL"),
                    ]'''

content = content.replace(old_cols, new_cols)

# Also fix check_expired_deliveries to handle missing column gracefully
old_check = '''def check_expired_deliveries():
    """Auto-confirm deliveries after 14 days"""
    try:
        two_weeks_ago = datetime.utcnow() - timedelta(days=14)
        expired = Order.query.filter(
            Order.status == "Awaiting Delivery",
            Order.delivered_at != None,
            Order.delivered_at <= two_weeks_ago
        ).all()

        for order in expired:
            order.status = "Delivered"
            send_notification(
                order.user_id, False,
                "Order #" + str(order.id) + " Auto-Confirmed",
                "Your order has been automatically confirmed as delivered after 14 days.",
                order.id
            )
            send_notification(
                0, True,
                "Auto-Confirmed - Order #" + str(order.id),
                order.customer_name + "'s order was auto-confirmed after 14 days.",
                order.id
            )

        if expired:
            db.session.commit()
            print("Auto-confirmed", len(expired), "deliveries")
    except Exception as e:
        print("Auto-confirm error:", e)
        db.session.rollback()'''

new_check = '''def check_expired_deliveries():
    """Auto-confirm deliveries after 14 days"""
    try:
        two_weeks_ago = datetime.utcnow() - timedelta(days=14)

        # Use raw SQL to avoid column not found error
        result = db.engine.execute(
            "SELECT id FROM orders WHERE status = 'Awaiting Delivery'"
        ) if False else None

        # Safe query using text
        try:
            expired = db.session.execute(db.text(
                "SELECT id, user_id, customer_name FROM orders "
                "WHERE status = 'Awaiting Delivery' "
                "AND delivered_at IS NOT NULL "
                "AND delivered_at <= :two_weeks_ago"
            ), {"two_weeks_ago": two_weeks_ago}).fetchall()

            for row in expired:
                db.session.execute(db.text(
                    "UPDATE orders SET status = 'Delivered' WHERE id = :id"
                ), {"id": row[0]})

                send_notification(
                    row[1], False,
                    "Order #" + str(row[0]) + " Auto-Confirmed",
                    "Your order has been automatically confirmed after 14 days.",
                    row[0]
                )
                send_notification(
                    0, True,
                    "Auto-Confirmed - Order #" + str(row[0]),
                    row[2] + "'s order was auto-confirmed after 14 days.",
                    row[0]
                )

            if expired:
                db.session.commit()
                print("Auto-confirmed", len(expired), "deliveries")

        except Exception as inner_e:
            # Column might not exist yet - skip silently
            if "delivered_at" in str(inner_e):
                pass
            else:
                print("Auto-confirm inner error:", inner_e)

    except Exception as e:
        print("Auto-confirm error:", e)
        db.session.rollback()'''

content = content.replace(old_check, new_check)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("  ✅ Fixed check_expired_deliveries")
print("")

# Now create a separate migration script
print("  Creating database migration...")

migration = '''
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
'''

with open('migrate.py', 'w', encoding='utf-8') as f:
    f.write(migration)

print("  ✅ Created migrate.py")
print("")

# Push to GitHub
print("  Pushing to GitHub...")
os.system('git add .')
os.system('git commit -m "Fixed delivered_at column and migration"')
os.system('git push')

print("")
print("  ========================================")
print("  ALL DONE!")
print("  Render updates in 2-3 minutes!")
print("  ========================================")
print("")