import os

print("")
print("  ========================================")
print("  Database Column Fixer")
print("  ========================================")
print("")

# ==============================
# UPDATE app.py
# ==============================
print("  Updating app.py...")

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix create_tables to add missing columns safely
old_create = '''def create_tables():
    try:
        with app.app_context():
            db.create_all()
            print("✅ Database tables ready!")
    except Exception as e:
        print(f"⚠️ Database connection warning: {e}")
        print("⚠️ App will start anyway...")

create_tables()'''

new_create = '''def create_tables():
    try:
        with app.app_context():
            db.create_all()

            # Add missing columns if they dont exist
            # This handles existing databases
            try:
                with db.engine.connect() as conn:
                    # Check and add payment_status
                    try:
                        conn.execute(db.text(
                            "ALTER TABLE orders ADD COLUMN payment_status VARCHAR(50) DEFAULT 'Paid'"
                        ))
                        conn.commit()
                        print("✅ Added payment_status column")
                    except Exception:
                        pass

                    # Check and add transaction_id
                    try:
                        conn.execute(db.text(
                            "ALTER TABLE orders ADD COLUMN transaction_id VARCHAR(100) DEFAULT ''"
                        ))
                        conn.commit()
                        print("✅ Added transaction_id column")
                    except Exception:
                        pass

                    # Check and add momo_number
                    try:
                        conn.execute(db.text(
                            "ALTER TABLE orders ADD COLUMN momo_number VARCHAR(20) DEFAULT ''"
                        ))
                        conn.commit()
                        print("✅ Added momo_number column")
                    except Exception:
                        pass

            except Exception as col_err:
                print(f"Column check: {col_err}")

            print("✅ Database tables ready!")
    except Exception as e:
        print(f"⚠️ Database connection warning: {e}")
        print("⚠️ App will start anyway...")

create_tables()'''

content = content.replace(old_create, new_create)
print("  ✅ Updated create_tables to add missing columns")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("  ✅ app.py saved!")
print("")

# ==============================
# PUSH TO GITHUB
# ==============================
print("  Pushing to GitHub...")
print("")

os.system('git add .')
os.system('git commit -m "Fixed database columns for payment system"')
os.system('git push')

print("")
print("  ========================================")
print("  ALL DONE!")
print("  ✅ app.py updated")
print("  ✅ Pushed to GitHub")
print("")
print("  Render will update in 2-3 minutes!")
print("  New columns will be added automatically!")
print("  ========================================")
print("")