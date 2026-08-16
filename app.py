from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import logging
import traceback
import urllib.parse
import cloudinary
import cloudinary.uploader

app = Flask(__name__)
app.secret_key = "sandras_palace_secret_key_2024"

log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///store.db")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

if DATABASE_URL.startswith("postgresql"):
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True, "pool_recycle": 300, "pool_timeout": 10,
        "pool_size": 5, "connect_args": {"sslmode": "require", "connect_timeout": 10}
    }
else:
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_pre_ping": True, "pool_recycle": 300}

db = SQLAlchemy(app)

UPLOAD_FOLDER = os.path.join("static", "uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

CLOUD_NAME = os.environ.get("CLOUDINARY_CLOUD_NAME", "").strip()
CLOUD_KEY  = os.environ.get("CLOUDINARY_API_KEY",    "").strip()
CLOUD_SEC  = os.environ.get("CLOUDINARY_API_SECRET", "").strip()
cloudinary.config(cloud_name=CLOUD_NAME, api_key=CLOUD_KEY, api_secret=CLOUD_SEC)

# ==============================
# MODELS
# ==============================

class User(db.Model):
    __tablename__ = "users"
    id         = db.Column(db.Integer,     primary_key=True)
    fullname   = db.Column(db.String(100), nullable=False)
    email      = db.Column(db.String(120), unique=True, nullable=False)
    phone      = db.Column(db.String(20),  nullable=False)
    address    = db.Column(db.String(300), nullable=False)
    password   = db.Column(db.String(200), nullable=False)
    is_active  = db.Column(db.Boolean,     default=True)
    created_at = db.Column(db.DateTime,    default=datetime.utcnow)
    orders     = db.relationship("Order",  backref="user", lazy=True)

class Item(db.Model):
    __tablename__ = "items"
    id              = db.Column(db.Integer,     primary_key=True)
    name            = db.Column(db.String(100), nullable=False)
    description     = db.Column(db.String(500))
    price           = db.Column(db.Float,       nullable=False)
    category        = db.Column(db.String(50))
    in_stock        = db.Column(db.Boolean,     default=True)
    stock_quantity  = db.Column(db.Integer,     default=0)
    low_stock_alert = db.Column(db.Integer,     default=5)
    image_url       = db.Column(db.String(500), default="/static/noimg.png")
    date_added      = db.Column(db.DateTime,    default=datetime.utcnow)

class Order(db.Model):
    __tablename__ = "orders"
    id               = db.Column(db.Integer,     primary_key=True)
    user_id          = db.Column(db.Integer,     db.ForeignKey("users.id"), nullable=False)
    customer_name    = db.Column(db.String(100), nullable=False)
    customer_phone   = db.Column(db.String(20),  nullable=False)
    customer_address = db.Column(db.String(300), nullable=False)
    items            = db.Column(db.Text,        nullable=False)
    total_price      = db.Column(db.Float,       nullable=False)
    status           = db.Column(db.String(50),  default="Pending")
    payment_status   = db.Column(db.String(50),  default="Paid")
    transaction_id   = db.Column(db.String(100), default="")
    momo_number      = db.Column(db.String(100), default="")
    delivered_at     = db.Column(db.DateTime,    nullable=True)
    is_archived      = db.Column(db.Boolean,     default=False)
    date_ordered     = db.Column(db.DateTime,    default=datetime.utcnow)

class Notification(db.Model):
    __tablename__ = "notifications"
    id         = db.Column(db.Integer,     primary_key=True)
    user_id    = db.Column(db.Integer,     default=0)
    for_admin  = db.Column(db.Boolean,     default=False)
    title      = db.Column(db.String(200), nullable=False)
    message    = db.Column(db.String(500), nullable=False)
    is_read    = db.Column(db.Boolean,     default=False)
    order_id   = db.Column(db.Integer,     default=0)
    created_at = db.Column(db.DateTime,    default=datetime.utcnow)

class Review(db.Model):
    __tablename__ = "reviews"
    id         = db.Column(db.Integer,     primary_key=True)
    user_id    = db.Column(db.Integer,     nullable=False)
    item_id    = db.Column(db.Integer,     nullable=False)
    rating     = db.Column(db.Integer,     nullable=False)
    comment    = db.Column(db.String(500))
    user_name  = db.Column(db.String(100))
    created_at = db.Column(db.DateTime,    default=datetime.utcnow)

class Coupon(db.Model):
    __tablename__ = "coupons"
    id             = db.Column(db.Integer,    primary_key=True)
    code           = db.Column(db.String(50), unique=True, nullable=False)
    discount_type  = db.Column(db.String(20), default="percentage")
    discount_value = db.Column(db.Float,      nullable=False)
    min_order      = db.Column(db.Float,      default=0)
    max_uses       = db.Column(db.Integer,    default=0)
    used_count     = db.Column(db.Integer,    default=0)
    is_active      = db.Column(db.Boolean,    default=True)
    expires_at     = db.Column(db.DateTime,   nullable=True)
    created_at     = db.Column(db.DateTime,   default=datetime.utcnow)

class Wishlist(db.Model):
    __tablename__ = "wishlists"
    id         = db.Column(db.Integer,  primary_key=True)
    user_id    = db.Column(db.Integer,  nullable=False)
    item_id    = db.Column(db.Integer,  nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ==============================
# ADMIN
# ==============================
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "sandra")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "SandrasPalace2024")

# ==============================
# HELPERS
# ==============================

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in {"png", "jpg", "jpeg", "gif", "webp"}

def upload_image(image):
    default = "/static/noimg.png"
    if not image or image.filename == "" or not allowed_file(image.filename):
        return default
    if CLOUD_NAME and CLOUD_KEY and CLOUD_SEC:
        try:
            image.stream.seek(0)
            result = cloudinary.uploader.upload(image.stream, folder="esirifuahs_palace", resource_type="image")
            if result and result.get("secure_url"):
                return result["secure_url"]
        except Exception as e:
            print("Cloudinary error:", e)
    try:
        image.stream.seek(0)
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d%H%M%S")
        fn = ts + "_" + secure_filename(image.filename)
        fp = os.path.join(UPLOAD_FOLDER, fn)
        image.save(fp)
        if os.path.exists(fp) and os.path.getsize(fp) > 0:
            return "static/uploads/" + fn
    except Exception as e:
        print("Local save error:", e)
    return default

def send_notification(user_id, for_admin, title, message, order_id=0):
    try:
        notif = Notification(user_id=user_id, for_admin=for_admin, title=title, message=message, order_id=order_id)
        db.session.add(notif)
        db.session.commit()
        return True
    except Exception as e:
        print("Notification error:", e)
        db.session.rollback()
        return False

def check_expired_deliveries():
    try:
        two_weeks_ago = datetime.utcnow() - timedelta(days=14)
        with db.engine.connect() as conn:
            try:
                rows = conn.execute(db.text(
                    "SELECT id, user_id, customer_name FROM orders "
                    "WHERE status = \'Awaiting Delivery\' "
                    "AND delivered_at IS NOT NULL AND delivered_at <= :d"
                ), {"d": two_weeks_ago}).fetchall()
                for row in rows:
                    conn.execute(db.text("UPDATE orders SET status = \'Delivered\' WHERE id = :id"), {"id": row[0]})
                    conn.commit()
                    send_notification(row[1], False, "Order #" + str(row[0]) + " Auto-Confirmed", "Your order was auto-confirmed after 14 days.", row[0])
                    send_notification(0, True, "Auto-Confirmed Order #" + str(row[0]), str(row[2]) + " order auto-confirmed.", row[0])
            except Exception:
                pass
    except Exception:
        pass

# ==============================
# CREATE TABLES
# ==============================
def create_tables():
    try:
        with app.app_context():
            db.create_all()
            try:
                with db.engine.connect() as conn:
                    # Orders columns
                    for col, defn in [
                        ("payment_status", "VARCHAR(50) DEFAULT \'Paid\'"),
                        ("transaction_id",  "VARCHAR(100) DEFAULT \'\'"),
                        ("momo_number",     "VARCHAR(100) DEFAULT \'\'"),
                        ("delivered_at",    "TIMESTAMP NULL"),
                        ("is_archived",     "BOOLEAN DEFAULT FALSE"),
                    ]:
                        try:
                            conn.execute(db.text("ALTER TABLE orders ADD COLUMN IF NOT EXISTS " + col + " " + defn))
                            conn.commit()
                        except Exception:
                            try:
                                conn.execute(db.text("ALTER TABLE orders ADD COLUMN " + col + " " + defn))
                                conn.commit()
                            except Exception:
                                pass
                    # Items columns
                    for col, defn in [
                        ("stock_quantity",  "INTEGER DEFAULT 0"),
                        ("low_stock_alert", "INTEGER DEFAULT 5"),
                    ]:
                        try:
                            conn.execute(db.text("ALTER TABLE items ADD COLUMN IF NOT EXISTS " + col + " " + defn))
                            conn.commit()
                        except Exception:
                            try:
                                conn.execute(db.text("ALTER TABLE items ADD COLUMN " + col + " " + defn))
                                conn.commit()
                            except Exception:
                                pass
                    # Users column
                    try:
                        conn.execute(db.text("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE"))
                        conn.commit()
                    except Exception:
                        try:
                            conn.execute(db.text("ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT TRUE"))
                            conn.commit()
                        except Exception:
                            pass
                    # Create extra tables
                    for sql in [
                        """CREATE TABLE IF NOT EXISTS notifications (id SERIAL PRIMARY KEY, user_id INTEGER DEFAULT 0, for_admin BOOLEAN DEFAULT FALSE, title VARCHAR(200) NOT NULL, message VARCHAR(500) NOT NULL, is_read BOOLEAN DEFAULT FALSE, order_id INTEGER DEFAULT 0, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""",
                        """CREATE TABLE IF NOT EXISTS reviews (id SERIAL PRIMARY KEY, user_id INTEGER NOT NULL, item_id INTEGER NOT NULL, rating INTEGER NOT NULL, comment VARCHAR(500), user_name VARCHAR(100), created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""",
                        """CREATE TABLE IF NOT EXISTS coupons (id SERIAL PRIMARY KEY, code VARCHAR(50) UNIQUE NOT NULL, discount_type VARCHAR(20) DEFAULT \'percentage\', discount_value FLOAT NOT NULL, min_order FLOAT DEFAULT 0, max_uses INTEGER DEFAULT 0, used_count INTEGER DEFAULT 0, is_active BOOLEAN DEFAULT TRUE, expires_at TIMESTAMP, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""",
                        """CREATE TABLE IF NOT EXISTS wishlists (id SERIAL PRIMARY KEY, user_id INTEGER NOT NULL, item_id INTEGER NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""",
                    ]:
                        try:
                            conn.execute(db.text(sql))
                            conn.commit()
                        except Exception:
                            pass
            except Exception as e:
                print("Column setup:", e)
            print("Database ready!")
    except Exception as e:
        print("DB warning:", e)
        print("App will start anyway...")

create_tables()

# ==============================
# PAGE ROUTES
# ==============================

@app.route("/")
def index():
    try: check_expired_deliveries()
    except Exception: pass
    return render_template("index.html")

@app.route("/admin")
def admin():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))
    try: check_expired_deliveries()
    except Exception: pass
    return render_template("admin.html")

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        data = request.get_json()
        if not data: return jsonify({"success": False, "message": "Invalid"}), 400
        if data.get("username") == ADMIN_USERNAME and data.get("password") == ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            return jsonify({"success": True})
        return jsonify({"success": False, "message": "Wrong credentials"})
    return render_template("admin_login.html")

@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("admin_login"))

# ==============================
# USER AUTH
# ==============================

@app.route("/api/auth/register", methods=["POST"])
def register():
    try:
        data = request.get_json()
        fn = data.get("fullname","").strip(); em = data.get("email","").strip().lower()
        ph = data.get("phone","").strip(); addr = data.get("address","").strip(); pw = data.get("password","")
        if not all([fn, em, ph, addr, pw]): return jsonify({"success": False, "message": "All fields required!"})
        if len(pw) < 6: return jsonify({"success": False, "message": "Password min 6 chars!"})
        if User.query.filter_by(email=em).first(): return jsonify({"success": False, "message": "Email already registered!"})
        user = User(fullname=fn, email=em, phone=ph, address=addr, password=generate_password_hash(pw))
        db.session.add(user); db.session.commit()
        session["user_id"] = user.id; session["user_name"] = user.fullname; session["user_email"] = user.email
        send_notification(0, True, "New User", fn + " registered!", 0)
        return jsonify({"success": True, "message": "Welcome!", "user": {"id": user.id, "fullname": user.fullname, "email": user.email, "phone": user.phone, "address": user.address}})
    except Exception as e:
        db.session.rollback(); return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/auth/login", methods=["POST"])
def user_login():
    try:
        data = request.get_json(); em = data.get("email","").strip().lower(); pw = data.get("password","")
        user = User.query.filter_by(email=em).first()
        if not user or not check_password_hash(user.password, pw):
            return jsonify({"success": False, "message": "Invalid email or password!"})
        if hasattr(user, "is_active") and not user.is_active:
            user.is_active = True; db.session.commit()
        session["user_id"] = user.id; session["user_name"] = user.fullname; session["user_email"] = user.email
        return jsonify({"success": True, "message": "Welcome back!", "user": {"id": user.id, "fullname": user.fullname, "email": user.email, "phone": user.phone, "address": user.address}})
    except Exception as e: return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/auth/logout", methods=["POST"])
def user_logout():
    session.pop("user_id", None); session.pop("user_name", None); session.pop("user_email", None)
    return jsonify({"success": True})

@app.route("/api/auth/check", methods=["GET"])
def check_auth():
    if session.get("user_id"):
        user = User.query.get(session["user_id"])
        if user:
            return jsonify({"logged_in": True, "user": {"id": user.id, "fullname": user.fullname, "email": user.email, "phone": user.phone, "address": user.address}})
    return jsonify({"logged_in": False})

@app.route("/api/auth/update", methods=["POST"])
def update_profile():
    if not session.get("user_id"): return jsonify({"success": False}), 401
    try:
        data = request.get_json(); user = User.query.get(session["user_id"])
        if not user: return jsonify({"success": False}), 404
        user.fullname = data.get("fullname", user.fullname); user.phone = data.get("phone", user.phone); user.address = data.get("address", user.address)
        db.session.commit(); session["user_name"] = user.fullname
        return jsonify({"success": True, "message": "Updated!", "user": {"id": user.id, "fullname": user.fullname, "email": user.email, "phone": user.phone, "address": user.address}})
    except Exception as e: db.session.rollback(); return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/auth/deactivate", methods=["POST"])
def deactivate_account():
    if not session.get("user_id"): return jsonify({"success": False}), 401
    try:
        data = request.get_json(); pw = data.get("password",""); reason = data.get("reason","")
        user = User.query.get(session["user_id"])
        if not user: return jsonify({"success": False, "message": "User not found!"}), 404
        if not check_password_hash(user.password, pw): return jsonify({"success": False, "message": "Wrong password!"})
        user.is_active = False; db.session.commit()
        send_notification(0, True, "Account Deactivated", user.fullname + " deactivated. Reason: " + reason, 0)
        session.pop("user_id", None); session.pop("user_name", None); session.pop("user_email", None)
        return jsonify({"success": True, "message": "Account deactivated."})
    except Exception as e: db.session.rollback(); return jsonify({"success": False, "message": str(e)}), 500

# ==============================
# ITEMS
# ==============================

@app.route("/api/items", methods=["GET"])
def get_items():
    try:
        items = Item.query.all()
        return jsonify([{"id": i.id, "name": i.name, "description": i.description or "", "price": i.price, "category": i.category or "General", "in_stock": i.in_stock, "stock_quantity": i.stock_quantity if hasattr(i,"stock_quantity") and i.stock_quantity else 0, "low_stock_alert": i.low_stock_alert if hasattr(i,"low_stock_alert") and i.low_stock_alert else 5, "image_url": i.image_url or "/static/noimg.png", "date_added": i.date_added.strftime("%Y-%m-%d") if i.date_added else ""} for i in items])
    except Exception as e: print("Get items error:", e); return jsonify([])

@app.route("/api/items/add", methods=["POST"])
def add_item():
    if not session.get("admin_logged_in"): return jsonify({"success": False}), 401
    try:
        data = request.form; image = request.files.get("image"); url = "/static/noimg.png"
        if image and image.filename != "": url = upload_image(image)
        if not data.get("name") or not data.get("price"): return jsonify({"success": False, "message": "Name and price required!"}), 400
        qty = 0; low = 5
        try: qty = int(data.get("stock_quantity", 0))
        except: pass
        try: low = int(data.get("low_stock_alert", 5))
        except: pass
        new = Item(name=data.get("name"), description=data.get("description",""), price=float(data.get("price")), category=data.get("category","General"), in_stock=qty > 0 if qty > 0 else data.get("in_stock","true") == "true", stock_quantity=qty, low_stock_alert=low, image_url=url)
        db.session.add(new); db.session.commit()
        return jsonify({"success": True, "message": "Item added!"})
    except Exception as e: db.session.rollback(); print("Add item error:", e); return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/items/update/<int:item_id>", methods=["POST"])
def update_item(item_id):
    if not session.get("admin_logged_in"): return jsonify({"success": False}), 401
    try:
        item = Item.query.get_or_404(item_id); data = request.form; image = request.files.get("image")
        if image and image.filename != "": item.image_url = upload_image(image)
        item.name = data.get("name", item.name); item.description = data.get("description", item.description)
        item.price = float(data.get("price", item.price)); item.category = data.get("category", item.category)
        # Update stock quantity
        qty_str = data.get("stock_quantity", "")
        if qty_str != "" and qty_str is not None:
            try:
                item.stock_quantity = int(qty_str)
            except (ValueError, TypeError):
                item.stock_quantity = 0

        # Update in_stock - always respect the dropdown value
        in_stock_str = data.get("in_stock", "true")
        item.in_stock = (in_stock_str == "true")

        # Update low stock alert
        low_str = data.get("low_stock_alert", "")
        if low_str != "" and low_str is not None:
            try:
                item.low_stock_alert = int(low_str)
            except (ValueError, TypeError):
                item.low_stock_alert = 5
        db.session.commit()
        return jsonify({"success": True, "message": "Item updated!"})
    except Exception as e: db.session.rollback(); print("Update error:", e); return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/items/delete/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    if not session.get("admin_logged_in"): return jsonify({"success": False}), 401
    try:
        item = Item.query.get_or_404(item_id)
        if item.image_url and item.image_url.startswith("static/uploads/"):
            if os.path.exists(item.image_url): os.remove(item.image_url)
        db.session.delete(item); db.session.commit()
        return jsonify({"success": True, "message": "Deleted!"})
    except Exception as e: db.session.rollback(); return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/items/toggle/<int:item_id>", methods=["POST"])
def toggle_stock(item_id):
    if not session.get("admin_logged_in"): return jsonify({"success": False}), 401
    try:
        item = Item.query.get(item_id)
        if not item: return jsonify({"success": False, "message": "Not found!"}), 404
        item.in_stock = not item.in_stock; db.session.commit()
        return jsonify({"success": True, "in_stock": item.in_stock, "message": "In Stock" if item.in_stock else "Out of Stock"})
    except Exception as e: db.session.rollback(); return jsonify({"success": False, "message": str(e)}), 500

# ==============================
# ORDERS
# ==============================

@app.route("/api/orders/place", methods=["POST"])
def place_order():
    if not session.get("user_id"): return jsonify({"success": False, "message": "Login first!", "need_login": True}), 401
    try:
        data = request.get_json()
        if not data or not data.get("items"): return jsonify({"success": False, "message": "No items!"}), 400
        user = User.query.get(session["user_id"])
        if not user: return jsonify({"success": False, "message": "User not found!"}), 404
        with db.engine.connect() as conn:
            result = conn.execute(db.text("""INSERT INTO orders (user_id, customer_name, customer_phone, customer_address, items, total_price, status, payment_status, transaction_id, momo_number, date_ordered) VALUES (:uid, :cn, :cp, :ca, :it, :tp, :st, :ps, :tid, :mn, :do) RETURNING id"""),
                {"uid": user.id, "cn": data.get("customer_name", user.fullname), "cp": data.get("customer_phone", user.phone), "ca": data.get("customer_address", user.address), "it": str(data.get("items")), "tp": float(data.get("total_price")), "st": "Pending", "ps": "Paid", "tid": data.get("transaction_id",""), "mn": data.get("momo_number",""), "do": datetime.utcnow()})
            conn.commit(); order_id = result.fetchone()[0]
        # Reduce stock
        try:
            for oi in data.get("items",[]):
                oi_id = oi.get("id"); oi_qty = oi.get("quantity",1)
                if oi_id:
                    with db.engine.connect() as sc:
                        sc.execute(db.text("UPDATE items SET stock_quantity = GREATEST(COALESCE(stock_quantity,0) - :q, 0) WHERE id = :id"), {"q": oi_qty, "id": oi_id})
                        sc.execute(db.text("UPDATE items SET in_stock = FALSE WHERE id = :id AND stock_quantity <= 0"), {"id": oi_id})
                        sc.commit()
                        row = sc.execute(db.text("SELECT name, stock_quantity, low_stock_alert FROM items WHERE id = :id"), {"id": oi_id}).fetchone()
                        if row and row[1] is not None and row[2] is not None:
                            if row[1] <= row[2] and row[1] > 0: send_notification(0, True, "Low Stock: " + str(row[0]), str(row[0]) + " has only " + str(row[1]) + " left!", 0)
                            elif row[1] <= 0: send_notification(0, True, "OUT OF STOCK: " + str(row[0]), str(row[0]) + " is now out of stock!", 0)
        except Exception as se: print("Stock error:", se)
        # WhatsApp
        wa_url = ""
        try:
            momo_raw = data.get("momo_number",""); wa_phone = ""
            if "0550618807" in momo_raw: wa_phone = "233550618807"
            elif "0540882629" in momo_raw: wa_phone = "233540882629"
            if wa_phone:
                items_txt = "".join([str(oi.get("name","")) + " x" + str(oi.get("quantity",1)) + "\n" for oi in data.get("items",[])])
                wa_msg = "*NEW ORDER #" + str(order_id) + "*\n\nCustomer: " + str(data.get("customer_name","")) + "\nPhone: " + str(data.get("customer_phone","")) + "\n\n*Items:*\n" + items_txt + "\n*Total: GH" + chr(8373) + " " + str(data.get("total_price","")) + "*\nTrans: " + str(data.get("transaction_id","")) + "\nAddress: " + str(data.get("customer_address",""))
                wa_url = "https://wa.me/" + wa_phone + "?text=" + urllib.parse.quote(wa_msg)
        except Exception as we: print("WhatsApp error:", we)
        send_notification(0, True, "New Order #" + str(order_id), user.fullname + " ordered GH" + chr(8373) + " " + str(data.get("total_price","")) + ". Trans: " + data.get("transaction_id","N/A"), order_id)
        send_notification(user.id, False, "Order #" + str(order_id) + " Received", "Your order has been received! We will confirm shortly.", order_id)
        result_data = {"success": True, "message": "Order placed!", "order_id": order_id}
        if wa_url: result_data["whatsapp_url"] = wa_url
        return jsonify(result_data)
    except Exception as e: print("Place order error:", e); traceback.print_exc(); return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/orders/my", methods=["GET"])
def my_orders():
    if not session.get("user_id"): return jsonify([])
    try:
        with db.engine.connect() as conn:
            rows = conn.execute(db.text("SELECT id, items, total_price, status, payment_status, transaction_id, date_ordered, delivered_at FROM orders WHERE user_id = :uid ORDER BY date_ordered DESC"), {"uid": session["user_id"]}).fetchall()
        return jsonify([{"id": o[0], "items": o[1], "total_price": float(o[2]), "status": o[3] or "Pending", "payment_status": o[4] or "Paid", "transaction_id": o[5] or "", "date_ordered": str(o[6])[:16] if o[6] else "", "delivered_at": str(o[7])[:16] if o[7] else ""} for o in rows])
    except Exception as e: print("My orders error:", e); return jsonify([])

@app.route("/api/orders", methods=["GET"])
def get_orders():
    if not session.get("admin_logged_in"): return jsonify([])
    try:
        show = request.args.get("show","active")
        if show == "archived": where = "WHERE COALESCE(is_archived, FALSE) = TRUE"
        elif show == "all": where = ""
        else: where = "WHERE COALESCE(is_archived, FALSE) = FALSE"
        query = "SELECT id, customer_name, customer_phone, customer_address, items, total_price, status, payment_status, transaction_id, momo_number, date_ordered, delivered_at, user_id FROM orders " + where + " ORDER BY date_ordered DESC"
        with db.engine.connect() as conn:
            rows = conn.execute(db.text(query)).fetchall()
        result = []
        for o in rows:
            try:
                result.append({"id": o[0], "customer_name": o[1] or "", "customer_phone": o[2] or "", "customer_address": o[3] or "", "items": o[4] or "", "total_price": float(o[5]) if o[5] else 0, "status": o[6] or "Pending", "payment_status": o[7] or "Paid", "transaction_id": o[8] or "", "momo_number": o[9] or "", "date_ordered": str(o[10])[:16] if o[10] else "", "delivered_at": str(o[11])[:16] if o[11] else "", "user_id": o[12] or 0})
            except Exception: continue
        return jsonify(result)
    except Exception as e: print("Get orders error:", e); return jsonify([])

@app.route("/api/orders/status/<int:order_id>", methods=["POST"])
def update_order_status(order_id):
    if not session.get("admin_logged_in"): return jsonify({"success": False}), 401
    try:
        order = Order.query.get_or_404(order_id); data = request.get_json(); status = data.get("status", order.status); current = order.status
        if current in ["Delivered","Cancelled","Refunded","Dispute Rejected"]: return jsonify({"success": False, "message": "Cannot change " + current + " orders!"}), 400
        if current == "Disputed": return jsonify({"success": False, "message": "Use Resolve button!"}), 400
        if current == "Awaiting Delivery": return jsonify({"success": False, "message": "Waiting for customer!"}), 400
        if current == "Pending" and status not in ["Confirmed","Cancelled"]: return jsonify({"success": False, "message": "Can only Confirm or Cancel!"}), 400
        if current == "Confirmed" and status != "Delivered": return jsonify({"success": False, "message": "Can only mark as Delivered!"}), 400
        if status == "Delivered":
            with db.engine.connect() as conn:
                conn.execute(db.text("UPDATE orders SET status = \'Awaiting Delivery\', delivered_at = :dt WHERE id = :id"), {"dt": datetime.utcnow(), "id": order_id})
                conn.commit()
            send_notification(order.user_id, False, "Order #" + str(order_id) + " On The Way!", "Your order is on its way! Please confirm when received. Auto-confirms in 14 days.", order_id)
        elif status == "Confirmed":
            order.status = "Confirmed"; db.session.commit()
            send_notification(order.user_id, False, "Order #" + str(order_id) + " Confirmed!", "Your order is confirmed and being prepared!", order_id)
        elif status == "Cancelled":
            order.status = "Cancelled"; db.session.commit()
            send_notification(order.user_id, False, "Order #" + str(order_id) + " Cancelled", "Your order was cancelled. Contact us for info.", order_id)
        return jsonify({"success": True, "message": "Status updated!"})
    except Exception as e: db.session.rollback(); return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/orders/confirm-delivery/<int:order_id>", methods=["POST"])
def confirm_delivery(order_id):
    if not session.get("user_id"): return jsonify({"success": False}), 401
    try:
        order = Order.query.get_or_404(order_id)
        if order.user_id != session["user_id"]: return jsonify({"success": False, "message": "Not your order!"}), 403
        if order.status != "Awaiting Delivery": return jsonify({"success": False, "message": "Order not awaiting delivery!"}), 400
        order.status = "Delivered"; db.session.commit()
        send_notification(0, True, "Delivery Confirmed #" + str(order_id), order.customer_name + " confirmed order #" + str(order_id), order_id)
        send_notification(order.user_id, False, "Order #" + str(order_id) + " Complete!", "Thank you for confirming! Enjoy your purchase!", order_id)
        return jsonify({"success": True, "message": "Confirmed! Thank you!"})
    except Exception as e: db.session.rollback(); return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/orders/dispute/<int:order_id>", methods=["POST"])
def dispute_order(order_id):
    if not session.get("user_id"): return jsonify({"success": False}), 401
    try:
        order = Order.query.get_or_404(order_id)
        if order.user_id != session["user_id"]: return jsonify({"success": False, "message": "Not your order!"}), 403
        if order.status != "Awaiting Delivery": return jsonify({"success": False, "message": "Cannot dispute!"}), 400
        data = request.get_json(); reason = data.get("reason","No reason")
        order.status = "Disputed"; db.session.commit()
        send_notification(0, True, "DISPUTE - Order #" + str(order_id), order.customer_name + " disputed. Reason: " + reason, order_id)
        send_notification(order.user_id, False, "Dispute Filed #" + str(order_id), "Dispute filed! We will contact you in 24 hours.", order_id)
        return jsonify({"success": True, "message": "Dispute filed!"})
    except Exception as e: db.session.rollback(); return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/orders/resolve-dispute/<int:order_id>", methods=["POST"])
def resolve_dispute(order_id):
    if not session.get("admin_logged_in"): return jsonify({"success": False}), 401
    try:
        order = Order.query.get_or_404(order_id)
        if order.status != "Disputed": return jsonify({"success": False, "message": "Not disputed!"}), 400
        data = request.get_json(); action = data.get("action",""); comment = data.get("comment","")
        if not action: return jsonify({"success": False, "message": "Select action!"}), 400
        if not comment: return jsonify({"success": False, "message": "Add comment!"}), 400
        if action == "refund":
            order.status = "Refunded"
            send_notification(order.user_id, False, "Refund Approved #" + str(order.id), "Refund approved! Admin: " + comment, order.id)
        elif action == "no_refund":
            order.status = "Dispute Rejected"
            send_notification(order.user_id, False, "Dispute Rejected #" + str(order.id), "After investigation not approved. Reason: " + comment, order.id)
        elif action == "redeliver":
            order.status = "Confirmed"
            send_notification(order.user_id, False, "Redelivery #" + str(order.id), "We will redeliver your order. Admin: " + comment, order.id)
        db.session.commit()
        return jsonify({"success": True, "message": "Dispute resolved!"})
    except Exception as e: db.session.rollback(); return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/orders/track/<int:order_id>", methods=["GET"])
def track_order(order_id):
    if not session.get("user_id"): return jsonify({"success": False}), 401
    try:
        order = Order.query.get(order_id)
        if not order or order.user_id != session["user_id"]: return jsonify({"success": False, "message": "Not found!"}), 404
        steps = [{"step":"Order Placed","icon":"📋","done":True,"date":order.date_ordered.strftime("%Y-%m-%d %H:%M")},{"step":"Payment Confirmed","icon":"💳","done":order.status != "Pending","date":""},{"step":"Order Confirmed","icon":"✅","done":order.status in ["Confirmed","Awaiting Delivery","Delivered"],"date":""},{"step":"Being Prepared","icon":"📦","done":order.status in ["Confirmed","Awaiting Delivery","Delivered"],"date":""},{"step":"Out for Delivery","icon":"🚚","done":order.status in ["Awaiting Delivery","Delivered"],"date":order.delivered_at.strftime("%Y-%m-%d %H:%M") if order.delivered_at else ""},{"step":"Delivered","icon":"🎉","done":order.status == "Delivered","date":""}]
        if order.status == "Cancelled": steps = [{"step":"Order Placed","icon":"📋","done":True,"date":order.date_ordered.strftime("%Y-%m-%d %H:%M")},{"step":"Cancelled","icon":"❌","done":True,"date":""}]
        return jsonify({"success":True,"order_id":order.id,"status":order.status,"total":order.total_price,"items":order.items,"steps":steps})
    except Exception as e: return jsonify({"success": False, "message": str(e)}), 500

# ==============================
# ARCHIVE
# ==============================

@app.route("/api/orders/archive/<int:order_id>", methods=["POST"])
def archive_order(order_id):
    if not session.get("admin_logged_in"): return jsonify({"success": False}), 401
    try:
        with db.engine.connect() as conn:
            order = conn.execute(db.text("SELECT status FROM orders WHERE id = :id"), {"id": order_id}).fetchone()
            if not order: return jsonify({"success": False, "message": "Order not found!"}), 404
            if order[0] not in ["Delivered","Cancelled","Refunded","Dispute Rejected"]:
                return jsonify({"success": False, "message": "Can only archive completed orders!"}), 400
            conn.execute(db.text("UPDATE orders SET is_archived = TRUE WHERE id = :id"), {"id": order_id})
            conn.commit()
        return jsonify({"success": True, "message": "Order archived!"})
    except Exception as e: return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/orders/unarchive/<int:order_id>", methods=["POST"])
def unarchive_order(order_id):
    if not session.get("admin_logged_in"): return jsonify({"success": False}), 401
    try:
        with db.engine.connect() as conn:
            conn.execute(db.text("UPDATE orders SET is_archived = FALSE WHERE id = :id"), {"id": order_id})
            conn.commit()
        return jsonify({"success": True, "message": "Order restored!"})
    except Exception as e: return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/orders/archive-completed", methods=["POST"])
def archive_all_completed():
    if not session.get("admin_logged_in"): return jsonify({"success": False}), 401
    try:
        with db.engine.connect() as conn:
            result = conn.execute(db.text("UPDATE orders SET is_archived = TRUE WHERE status IN (\'Delivered\', \'Cancelled\', \'Refunded\', \'Dispute Rejected\') AND COALESCE(is_archived, FALSE) = FALSE"))
            conn.commit(); count = result.rowcount
        return jsonify({"success": True, "message": str(count) + " orders archived!"})
    except Exception as e: return jsonify({"success": False, "message": str(e)}), 500

# ==============================
# NOTIFICATIONS
# ==============================

@app.route("/api/notifications/admin", methods=["GET"])
def admin_notifications():
    if not session.get("admin_logged_in"): return jsonify({"notifications":[],"unread_count":0})
    try:
        notifs = Notification.query.filter_by(for_admin=True).order_by(Notification.created_at.desc()).limit(50).all()
        unread = Notification.query.filter_by(for_admin=True, is_read=False).count()
        return jsonify({"notifications":[{"id":n.id,"title":n.title,"message":n.message,"is_read":n.is_read,"order_id":n.order_id,"created_at":n.created_at.strftime("%Y-%m-%d %H:%M")} for n in notifs],"unread_count":unread})
    except Exception: return jsonify({"notifications":[],"unread_count":0})

@app.route("/api/notifications/user", methods=["GET"])
def user_notifications():
    if not session.get("user_id"): return jsonify({"notifications":[],"unread_count":0})
    try:
        notifs = Notification.query.filter_by(user_id=session["user_id"], for_admin=False).order_by(Notification.created_at.desc()).limit(50).all()
        unread = Notification.query.filter_by(user_id=session["user_id"], for_admin=False, is_read=False).count()
        return jsonify({"notifications":[{"id":n.id,"title":n.title,"message":n.message,"is_read":n.is_read,"order_id":n.order_id,"created_at":n.created_at.strftime("%Y-%m-%d %H:%M")} for n in notifs],"unread_count":unread})
    except Exception: return jsonify({"notifications":[],"unread_count":0})

@app.route("/api/notifications/read/<int:notif_id>", methods=["POST"])
def mark_read(notif_id):
    try:
        with db.engine.connect() as conn:
            conn.execute(db.text("UPDATE notifications SET is_read = TRUE WHERE id = :id"), {"id": notif_id})
            conn.commit()
        return jsonify({"success": True})
    except Exception: return jsonify({"success": False})

@app.route("/api/notifications/read-all", methods=["POST"])
def mark_all_read():
    try:
        if session.get("admin_logged_in"):
            with db.engine.connect() as conn:
                conn.execute(db.text("UPDATE notifications SET is_read = TRUE WHERE for_admin = TRUE AND is_read = FALSE"))
                conn.commit()
        elif session.get("user_id"):
            with db.engine.connect() as conn:
                conn.execute(db.text("UPDATE notifications SET is_read = TRUE WHERE user_id = :uid AND for_admin = FALSE AND is_read = FALSE"), {"uid": session["user_id"]})
                conn.commit()
        return jsonify({"success": True})
    except Exception: return jsonify({"success": False})

# ==============================
# REVIEWS
# ==============================

@app.route("/api/reviews/<int:item_id>", methods=["GET"])
def get_reviews(item_id):
    try:
        with db.engine.connect() as conn:
            rows = conn.execute(db.text("SELECT id, user_id, rating, comment, user_name, created_at FROM reviews WHERE item_id = :iid ORDER BY created_at DESC"), {"iid": item_id}).fetchall()
        reviews = [{"id":r[0],"user_id":r[1],"rating":r[2],"comment":r[3] or "","user_name":r[4] or "Anonymous","created_at":str(r[5])[:16] if r[5] else ""} for r in rows]
        avg = round(sum(r["rating"] for r in reviews) / len(reviews), 1) if reviews else 0
        return jsonify({"reviews":reviews,"count":len(reviews),"avg_rating":avg})
    except Exception as e: return jsonify({"reviews":[],"count":0,"avg_rating":0})

@app.route("/api/reviews/add", methods=["POST"])
def add_review():
    if not session.get("user_id"): return jsonify({"success": False, "message": "Login first!"}), 401
    try:
        data = request.get_json(); item_id = data.get("item_id"); rating = data.get("rating",5); comment = data.get("comment","")
        if not item_id or not rating: return jsonify({"success": False, "message": "Rating required!"})
        if rating < 1 or rating > 5: return jsonify({"success": False, "message": "Rating 1-5!"})
        user = User.query.get(session["user_id"])
        if not user: return jsonify({"success": False, "message": "User not found!"}), 404
        with db.engine.connect() as conn:
            existing = conn.execute(db.text("SELECT id FROM reviews WHERE user_id = :uid AND item_id = :iid"), {"uid": user.id, "iid": item_id}).fetchone()
            if existing:
                conn.execute(db.text("UPDATE reviews SET rating = :r, comment = :c WHERE user_id = :uid AND item_id = :iid"), {"r":rating,"c":comment,"uid":user.id,"iid":item_id})
                conn.commit()
                return jsonify({"success": True, "message": "Review updated!"})
            conn.execute(db.text("INSERT INTO reviews (user_id, item_id, rating, comment, user_name) VALUES (:uid, :iid, :r, :c, :un)"), {"uid":user.id,"iid":item_id,"r":rating,"c":comment,"un":user.fullname})
            conn.commit()
        return jsonify({"success": True, "message": "Review added!"})
    except Exception as e: return jsonify({"success": False, "message": str(e)}), 500

# ==============================
# COUPONS
# ==============================

@app.route("/api/coupons/validate", methods=["POST"])
def validate_coupon():
    try:
        data = request.get_json(); code = data.get("code","").strip().upper(); total = float(data.get("total",0))
        if not code: return jsonify({"success": False, "message": "Enter a coupon code!"})
        coupon = Coupon.query.filter_by(code=code, is_active=True).first()
        if not coupon: return jsonify({"success": False, "message": "Invalid coupon code!"})
        if coupon.expires_at and coupon.expires_at < datetime.utcnow(): return jsonify({"success": False, "message": "Coupon expired!"})
        if coupon.max_uses > 0 and coupon.used_count >= coupon.max_uses: return jsonify({"success": False, "message": "Coupon fully used!"})
        if total < coupon.min_order: return jsonify({"success": False, "message": "Minimum order GH" + chr(8373) + " " + str(coupon.min_order) + " required!"})
        if coupon.discount_type == "percentage":
            discount = total * (coupon.discount_value / 100); msg = str(int(coupon.discount_value)) + "% off!"
        else:
            discount = coupon.discount_value; msg = "GH" + chr(8373) + " " + str(discount) + " off!"
        return jsonify({"success":True,"message":msg,"discount":round(discount,2),"new_total":round(max(total-discount,0),2),"coupon_id":coupon.id})
    except Exception as e: return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/coupons/use/<int:coupon_id>", methods=["POST"])
def use_coupon(coupon_id):
    try:
        with db.engine.connect() as conn:
            conn.execute(db.text("UPDATE coupons SET used_count = used_count + 1 WHERE id = :id"), {"id": coupon_id})
            conn.commit()
        return jsonify({"success": True})
    except Exception: return jsonify({"success": False})

@app.route("/api/coupons/create", methods=["POST"])
def create_coupon():
    if not session.get("admin_logged_in"): return jsonify({"success": False}), 401
    try:
        data = request.get_json(); code = data.get("code","").strip().upper()
        if not code or not data.get("discount_value"): return jsonify({"success": False, "message": "Code and value required!"})
        if Coupon.query.filter_by(code=code).first(): return jsonify({"success": False, "message": "Code already exists!"})
        expires = None
        if data.get("expires_at"):
            try: expires = datetime.strptime(data["expires_at"], "%Y-%m-%d")
            except: pass
        try:
            dv = float(data.get("discount_value", 0))
        except (ValueError, TypeError):
            return jsonify({"success": False, "message": "Invalid discount value!"})

        try:
            mo = float(data.get("min_order", 0))
        except (ValueError, TypeError):
            mo = 0

        try:
            mu = int(data.get("max_uses", 0))
        except (ValueError, TypeError):
            mu = 0

        coupon = Coupon(
            code           = code,
            discount_type  = data.get("discount_type", "percentage"),
            discount_value = dv,
            min_order      = mo,
            max_uses       = mu,
            is_active      = True,
            expires_at     = expires
        )
        db.session.add(coupon); db.session.commit()
        return jsonify({"success": True, "message": "Coupon created!"})
    except Exception as e: db.session.rollback(); return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/coupons", methods=["GET"])
def get_coupons():
    if not session.get("admin_logged_in"): return jsonify([])
    try:
        coupons = Coupon.query.order_by(Coupon.created_at.desc()).all()
        return jsonify([{"id":c.id,"code":c.code,"discount_type":c.discount_type,"discount_value":c.discount_value,"min_order":c.min_order,"max_uses":c.max_uses,"used_count":c.used_count,"is_active":c.is_active,"expires_at":c.expires_at.strftime("%Y-%m-%d") if c.expires_at else "","created_at":c.created_at.strftime("%Y-%m-%d")} for c in coupons])
    except Exception: return jsonify([])

@app.route("/api/coupons/delete/<int:coupon_id>", methods=["DELETE"])
def delete_coupon(coupon_id):
    if not session.get("admin_logged_in"): return jsonify({"success": False}), 401
    try:
        c = Coupon.query.get(coupon_id)
        if c: db.session.delete(c); db.session.commit()
        return jsonify({"success": True, "message": "Deleted!"})
    except Exception as e: db.session.rollback(); return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/coupons/toggle/<int:coupon_id>", methods=["POST"])
def toggle_coupon(coupon_id):
    if not session.get("admin_logged_in"): return jsonify({"success": False}), 401
    try:
        c = Coupon.query.get(coupon_id)
        if c: c.is_active = not c.is_active; db.session.commit()
        return jsonify({"success": True})
    except Exception: return jsonify({"success": False})

# ==============================
# WISHLIST
# ==============================

@app.route("/api/wishlist", methods=["GET"])
def get_wishlist():
    if not session.get("user_id"): return jsonify([])
    try:
        with db.engine.connect() as conn:
            rows = conn.execute(db.text("SELECT w.id, w.item_id, i.name, i.price, i.image_url, i.in_stock, COALESCE(i.stock_quantity,0) FROM wishlists w JOIN items i ON w.item_id = i.id WHERE w.user_id = :uid ORDER BY w.created_at DESC"), {"uid": session["user_id"]}).fetchall()
        return jsonify([{"id":r[0],"item_id":r[1],"name":r[2],"price":float(r[3]),"image_url":r[4] or "/static/noimg.png","in_stock":r[5],"stock_quantity":r[6]} for r in rows])
    except Exception as e: return jsonify([])

@app.route("/api/wishlist/add/<int:item_id>", methods=["POST"])
def add_to_wishlist(item_id):
    if not session.get("user_id"): return jsonify({"success": False, "message": "Login first!"}), 401
    try:
        uid = session["user_id"]
        with db.engine.connect() as conn:
            existing = conn.execute(db.text("SELECT id FROM wishlists WHERE user_id = :uid AND item_id = :iid"), {"uid":uid,"iid":item_id}).fetchone()
            if existing: return jsonify({"success": False, "message": "Already in wishlist!"})
            conn.execute(db.text("INSERT INTO wishlists (user_id, item_id) VALUES (:uid, :iid)"), {"uid":uid,"iid":item_id})
            conn.commit()
        return jsonify({"success": True, "message": "Added to wishlist!"})
    except Exception as e: return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/wishlist/remove/<int:item_id>", methods=["DELETE"])
def remove_from_wishlist(item_id):
    if not session.get("user_id"): return jsonify({"success": False}), 401
    try:
        with db.engine.connect() as conn:
            conn.execute(db.text("DELETE FROM wishlists WHERE user_id = :uid AND item_id = :iid"), {"uid":session["user_id"],"iid":item_id})
            conn.commit()
        return jsonify({"success": True, "message": "Removed!"})
    except Exception: return jsonify({"success": False})

# ==============================
# REPORTS
# ==============================

@app.route("/api/reports/sales", methods=["GET"])
def sales_report():
    if not session.get("admin_logged_in"): return jsonify({"success": False}), 401
    try:
        with db.engine.connect() as conn:
            def q(sql, params=None):
                try: return conn.execute(db.text(sql), params or {}).scalar() or 0
                except: return 0
            total_rev  = q("SELECT COALESCE(SUM(total_price),0) FROM orders WHERE status NOT IN (\'Cancelled\',\'Disputed\',\'Refunded\')")
            today_rev  = q("SELECT COALESCE(SUM(total_price),0) FROM orders WHERE status NOT IN (\'Cancelled\',\'Disputed\',\'Refunded\') AND date_ordered >= CURRENT_DATE")
            week_rev   = q("SELECT COALESCE(SUM(total_price),0) FROM orders WHERE status NOT IN (\'Cancelled\',\'Disputed\',\'Refunded\') AND date_ordered >= CURRENT_DATE - INTERVAL \'7 days\'")
            month_rev  = q("SELECT COALESCE(SUM(total_price),0) FROM orders WHERE status NOT IN (\'Cancelled\',\'Disputed\',\'Refunded\') AND date_ordered >= CURRENT_DATE - INTERVAL \'30 days\'")
            total_ord  = q("SELECT COUNT(*) FROM orders")
            completed  = q("SELECT COUNT(*) FROM orders WHERE status = \'Delivered\'")
            pending    = q("SELECT COUNT(*) FROM orders WHERE status = \'Pending\'")
            cancelled  = q("SELECT COUNT(*) FROM orders WHERE status = \'Cancelled\'")
            best = []
            try:
                rows = conn.execute(db.text("SELECT i.name, COUNT(o.id) as cnt, COALESCE(SUM(o.total_price),0) as rev FROM orders o, items i WHERE o.items LIKE \'%\' || i.name || \'%\' AND o.status NOT IN (\'Cancelled\',\'Disputed\',\'Refunded\') GROUP BY i.name ORDER BY cnt DESC LIMIT 10")).fetchall()
                best = [{"name":r[0],"orders":r[1],"revenue":float(r[2])} for r in rows]
            except: pass
            daily = []
            try:
                rows = conn.execute(db.text("SELECT DATE(date_ordered) as day, COUNT(*) as cnt, COALESCE(SUM(total_price),0) as rev FROM orders WHERE status NOT IN (\'Cancelled\',\'Disputed\',\'Refunded\') AND date_ordered >= CURRENT_DATE - INTERVAL \'7 days\' GROUP BY DATE(date_ordered) ORDER BY day")).fetchall()
                daily = [{"date":str(r[0]),"orders":r[1],"revenue":float(r[2])} for r in rows]
            except: pass
        return jsonify({"total_revenue":float(total_rev),"today_revenue":float(today_rev),"week_revenue":float(week_rev),"month_revenue":float(month_rev),"total_orders":total_ord,"completed_orders":completed,"pending_orders":pending,"cancelled_orders":cancelled,"best_sellers":best,"daily_sales":daily})
    except Exception as e: print("Reports error:", e); return jsonify({"total_revenue":0,"today_revenue":0,"week_revenue":0,"month_revenue":0,"total_orders":0,"completed_orders":0,"pending_orders":0,"cancelled_orders":0,"best_sellers":[],"daily_sales":[]})

# ==============================
# USERS
# ==============================

@app.route("/api/users", methods=["GET"])
def get_users():
    if not session.get("admin_logged_in"): return jsonify([])
    try:
        with db.engine.connect() as conn:
            rows = conn.execute(db.text("SELECT id, fullname, email, phone, address, created_at FROM users ORDER BY id DESC")).fetchall()
        result = []
        for row in rows:
            try:
                with db.engine.connect() as conn2:
                    oc = conn2.execute(db.text("SELECT COUNT(*) FROM orders WHERE user_id = :uid"), {"uid": row[0]}).scalar()
                result.append({"id":row[0],"fullname":row[1] or "","email":row[2] or "","phone":row[3] or "","address":row[4] or "","created_at":str(row[5])[:16] if row[5] else "","order_count":oc or 0})
            except: continue
        return jsonify(result)
    except Exception as e: print("Get users error:", e); return jsonify([])

# ==============================
# RUN
# ==============================
if __name__ == "__main__":
    print("Esirifuahs Palace is LIVE!")
    app.run(debug=False, host="0.0.0.0", port=5000)
