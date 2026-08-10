from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import logging
import cloudinary
import cloudinary.uploader

app = Flask(__name__)
app.secret_key = "sandras_palace_secret_key_2024"

log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)

# ==============================
# DATABASE
# ==============================
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///store.db")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"]      = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

if DATABASE_URL.startswith("postgresql"):
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
        "pool_recycle":  300,
        "connect_args":  {
            "sslmode":         "require",
            "connect_timeout": 10
        }
    }
else:
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
        "pool_recycle":  300
    }

db = SQLAlchemy(app)

# ==============================
# UPLOADS
# ==============================
UPLOAD_FOLDER = os.path.join("static", "uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ==============================
# CLOUDINARY
# ==============================
CLOUDINARY_CLOUD_NAME = os.environ.get("CLOUDINARY_CLOUD_NAME", "").strip()
CLOUDINARY_API_KEY    = os.environ.get("CLOUDINARY_API_KEY",    "").strip()
CLOUDINARY_API_SECRET = os.environ.get("CLOUDINARY_API_SECRET", "").strip()

cloudinary.config(
    cloud_name = CLOUDINARY_CLOUD_NAME,
    api_key    = CLOUDINARY_API_KEY,
    api_secret = CLOUDINARY_API_SECRET
)

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
    created_at = db.Column(db.DateTime,    default=datetime.utcnow)
    orders     = db.relationship("Order",  backref="user", lazy=True)

class Item(db.Model):
    __tablename__ = "items"
    id          = db.Column(db.Integer,     primary_key=True)
    name        = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    price       = db.Column(db.Float,       nullable=False)
    category    = db.Column(db.String(50))
    in_stock    = db.Column(db.Boolean,     default=True)
    image_url   = db.Column(db.String(500), default="https://via.placeholder.com/400x400?text=No+Image")
    date_added  = db.Column(db.DateTime,    default=datetime.utcnow)

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
    date_ordered     = db.Column(db.DateTime,    default=datetime.utcnow)

# ==============================
# ADMIN
# ==============================
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

ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "sandra")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "SandrasPalace2024")

# ==============================
# HELPERS
# ==============================
def allowed_file(filename):
    ALLOWED = {"png", "jpg", "jpeg", "gif", "webp"}
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED

def upload_image(image):
    default = "https://via.placeholder.com/400x400?text=No+Image"

    if not image or image.filename == "":
        return default

    if not allowed_file(image.filename):
        return default

    # Try Cloudinary
    if CLOUDINARY_CLOUD_NAME and CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET:
        try:
            image.stream.seek(0)
            result = cloudinary.uploader.upload(
                image.stream,
                folder        = "esirifuahs_palace",
                resource_type = "image"
            )
            if result and result.get("secure_url"):
                print("Cloudinary OK:", result["secure_url"])
                return result["secure_url"]
        except Exception as e:
            print("Cloudinary error:", e)
    else:
        print("Cloudinary credentials missing")

    # Fallback local
    try:
        image.stream.seek(0)
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        safe_name = secure_filename(image.filename)
        fname     = timestamp + "_" + safe_name
        fpath     = os.path.join(UPLOAD_FOLDER, fname)
        image.save(fpath)
        if os.path.exists(fpath) and os.path.getsize(fpath) > 0:
            print("Local save OK:", fpath)
            return "static/uploads/" + fname
    except Exception as e:
        print("Local save error:", e)

    return default

# ==============================
# CREATE TABLES
# ==============================
def create_tables():
    try:
        with app.app_context():
            db.create_all()

            try:
                with db.engine.connect() as conn:
                    columns = [
                        ("payment_status", "VARCHAR(50)  DEFAULT 'Paid'"),
                        ("transaction_id", "VARCHAR(100) DEFAULT ''"),
                        ("momo_number",    "VARCHAR(100) DEFAULT ''"),
                    ]

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
                    except Exception:
                        pass
                    for col, defn in columns:
                        try:
                            conn.execute(db.text(
                                "ALTER TABLE orders ADD COLUMN " + col + " " + defn
                            ))
                            conn.commit()
                            print("Added column:", col)
                        except Exception:
                            pass
            except Exception as e:
                print("Column check:", e)

            print("Database ready!")

    except Exception as e:
        print("DB warning:", e)
        print("App will start anyway...")

create_tables()

# ==============================
# ROUTES
# ==============================

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/admin")
def admin():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))
    return render_template("admin.html")

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "Invalid request"}), 400
        if data.get("username") == ADMIN_USERNAME and data.get("password") == ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            return jsonify({"success": True})
        return jsonify({"success": False, "message": "Wrong username or password"})
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
        data     = request.get_json()
        fullname = data.get("fullname", "").strip()
        email    = data.get("email",    "").strip().lower()
        phone    = data.get("phone",    "").strip()
        address  = data.get("address",  "").strip()
        password = data.get("password", "")

        if not all([fullname, email, phone, address, password]):
            return jsonify({"success": False, "message": "All fields required!"})

        if len(password) < 6:
            return jsonify({"success": False, "message": "Password min 6 characters!"})

        if User.query.filter_by(email=email).first():
            return jsonify({"success": False, "message": "Email already registered!"})

        user = User(
            fullname = fullname,
            email    = email,
            phone    = phone,
            address  = address,
            password = generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()

        session["user_id"]    = user.id
        session["user_name"]  = user.fullname
        session["user_email"] = user.email

        return jsonify({
            "success": True,
            "message": "Account created! Welcome!",
            "user": {
                "id":       user.id,
                "fullname": user.fullname,
                "email":    user.email,
                "phone":    user.phone,
                "address":  user.address
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/auth/login", methods=["POST"])
def user_login():
    try:
        data     = request.get_json()
        email    = data.get("email",    "").strip().lower()
        password = data.get("password", "")

        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            return jsonify({"success": False, "message": "Invalid email or password!"})

        session["user_id"]    = user.id
        session["user_name"]  = user.fullname
        session["user_email"] = user.email

        return jsonify({
            "success": True,
            "message": "Welcome back " + user.fullname + "!",
            "user": {
                "id":       user.id,
                "fullname": user.fullname,
                "email":    user.email,
                "phone":    user.phone,
                "address":  user.address
            }
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/auth/logout", methods=["POST"])
def user_logout():
    session.pop("user_id",    None)
    session.pop("user_name",  None)
    session.pop("user_email", None)
    return jsonify({"success": True})

@app.route("/api/auth/check", methods=["GET"])
def check_auth():
    if session.get("user_id"):
        user = User.query.get(session["user_id"])
        if user:
            return jsonify({
                "logged_in": True,
                "user": {
                    "id":       user.id,
                    "fullname": user.fullname,
                    "email":    user.email,
                    "phone":    user.phone,
                    "address":  user.address
                }
            })
    return jsonify({"logged_in": False})

@app.route("/api/auth/update", methods=["POST"])
def update_profile():
    if not session.get("user_id"):
        return jsonify({"success": False, "message": "Not logged in"}), 401
    try:
        data = request.get_json()
        user = User.query.get(session["user_id"])
        if not user:
            return jsonify({"success": False, "message": "User not found"}), 404

        user.fullname = data.get("fullname", user.fullname)
        user.phone    = data.get("phone",    user.phone)
        user.address  = data.get("address",  user.address)
        db.session.commit()
        session["user_name"] = user.fullname

        return jsonify({
            "success": True,
            "message": "Profile updated!",
            "user": {
                "id":       user.id,
                "fullname": user.fullname,
                "email":    user.email,
                "phone":    user.phone,
                "address":  user.address
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

# ==============================
# ITEMS
# ==============================

@app.route("/api/items", methods=["GET"])
def get_items():
    try:
        items = Item.query.all()
        return jsonify([{
            "id":          i.id,
            "name":        i.name,
            "description": i.description,
            "price":       i.price,
            "category":    i.category,
            "in_stock":    i.in_stock,
            "image_url":   i.image_url,
            "date_added":  i.date_added.strftime("%Y-%m-%d")
        } for i in items])
    except Exception as e:
        print("Get items error:", e)
        return jsonify([])

@app.route("/api/items/add", methods=["POST"])
def add_item():
    if not session.get("admin_logged_in"):
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    try:
        data      = request.form
        image     = request.files.get("image")
        image_url = "https://via.placeholder.com/400x400?text=No+Image"

        if image and image.filename != "":
            image_url = upload_image(image)
            print("Image URL saved:", image_url)

        if not data.get("name") or not data.get("price"):
            return jsonify({"success": False, "message": "Name and price required!"}), 400

        new_item = Item(
            name        = data.get("name"),
            description = data.get("description", ""),
            price       = float(data.get("price")),
            category    = data.get("category", "General"),
            in_stock    = data.get("in_stock", "true") == "true",
            image_url   = image_url
        )
        db.session.add(new_item)
        db.session.commit()
        return jsonify({"success": True, "message": "Item added!"})

    except Exception as e:
        db.session.rollback()
        print("Add item error:", e)
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/items/update/<int:item_id>", methods=["POST"])
def update_item(item_id):
    if not session.get("admin_logged_in"):
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    try:
        item  = Item.query.get_or_404(item_id)
        data  = request.form
        image = request.files.get("image")

        if image and image.filename != "":
            item.image_url = upload_image(image)

        item.name        = data.get("name",        item.name)
        item.description = data.get("description", item.description)
        item.price       = float(data.get("price", item.price))
        item.category    = data.get("category",    item.category)
        item.in_stock    = data.get("in_stock", "true") == "true"

        db.session.commit()
        return jsonify({"success": True, "message": "Item updated!"})

    except Exception as e:
        db.session.rollback()
        print("Update error:", e)
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/items/delete/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    if not session.get("admin_logged_in"):
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    try:
        item = Item.query.get_or_404(item_id)
        if item.image_url and item.image_url.startswith("static/uploads/"):
            if os.path.exists(item.image_url):
                os.remove(item.image_url)
        db.session.delete(item)
        db.session.commit()
        return jsonify({"success": True, "message": "Item deleted!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/items/toggle/<int:item_id>", methods=["POST"])
def toggle_stock(item_id):
    if not session.get("admin_logged_in"):
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    try:
        item = Item.query.get(item_id)
        if not item:
            return jsonify({"success": False, "message": "Item not found!"}), 404
        item.in_stock = not item.in_stock
        db.session.commit()
        msg = "In Stock" if item.in_stock else "Out of Stock"
        return jsonify({"success": True, "in_stock": item.in_stock, "message": msg})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

# ==============================
# ORDERS
# ==============================

@app.route("/api/orders/place", methods=["POST"])
def place_order():
    if not session.get("user_id"):
        return jsonify({
            "success":    False,
            "message":    "Please login first!",
            "need_login": True
        }), 401

    try:
        data = request.get_json()
        if not data or not data.get("items"):
            return jsonify({"success": False, "message": "No items!"}), 400

        user = User.query.get(session["user_id"])
        if not user:
            return jsonify({"success": False, "message": "User not found!"}), 404

        new_order = Order(
            user_id          = user.id,
            customer_name    = data.get("customer_name",    user.fullname),
            customer_phone   = data.get("customer_phone",   user.phone),
            customer_address = data.get("customer_address", user.address),
            items            = str(data.get("items")),
            total_price      = float(data.get("total_price")),
            status           = "Pending",
            payment_status   = "Paid",
            transaction_id   = data.get("transaction_id", ""),
            momo_number      = data.get("momo_number",    "")
        )
        db.session.add(new_order)
        db.session.commit()

        # Create notification for admin
        try:
            admin_notif = Notification(
                user_id   = 0,
                for_admin = True,
                title     = "New Order #" + str(new_order.id),
                message   = user.fullname + " placed an order for GH" + chr(8373) + " " + str(new_order.total_price) + ". Transaction ID: " + data.get("transaction_id", "N/A"),
                order_id  = new_order.id
            )
            db.session.add(admin_notif)
            db.session.commit()
        except Exception as e:
            print("Notification error:", e)

        return jsonify({
            "success":  True,
            "message":  "Order placed!",
            "order_id": new_order.id
        })

    except Exception as e:
        db.session.rollback()
        print("Place order error:", e)
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/orders/my", methods=["GET"])
def my_orders():
    if not session.get("user_id"):
        return jsonify({"success": False, "message": "Not logged in"}), 401
    try:
        orders = Order.query.filter_by(
            user_id=session["user_id"]
        ).order_by(Order.date_ordered.desc()).all()

        return jsonify([{
            "id":             o.id,
            "items":          o.items,
            "total_price":    o.total_price,
            "status":         o.status,
            "payment_status": o.payment_status or "Paid",
            "transaction_id": o.transaction_id or "",
            "date_ordered":   o.date_ordered.strftime("%Y-%m-%d %H:%M")
        } for o in orders])

    except Exception as e:
        print("My orders error:", e)
        return jsonify([])

@app.route("/api/orders", methods=["GET"])
def get_orders():
    if not session.get("admin_logged_in"):
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    try:
        orders = Order.query.order_by(Order.date_ordered.desc()).all()
        return jsonify([{
            "id":               o.id,
            "customer_name":    o.customer_name,
            "customer_phone":   o.customer_phone,
            "customer_address": o.customer_address,
            "items":            o.items,
            "total_price":      o.total_price,
            "status":           o.status,
            "payment_status":   o.payment_status or "Paid",
            "transaction_id":   o.transaction_id or "",
            "momo_number":      o.momo_number    or "",
            "date_ordered":     o.date_ordered.strftime("%Y-%m-%d %H:%M"),
            "user_id":          o.user_id
        } for o in orders])
    except Exception as e:
        print("Get orders error:", e)
        return jsonify([])

@app.route("/api/orders/status/<int:order_id>", methods=["POST"])
def update_order_status(order_id):
    if not session.get("admin_logged_in"):
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    try:
        order  = Order.query.get_or_404(order_id)
        data   = request.get_json()
        status = data.get("status", order.status)

        if status not in ["Pending", "Confirmed", "Delivered", "Cancelled", "Awaiting Delivery"]:
            return jsonify({"success": False, "message": "Invalid status!"}), 400

        # Enforce order flow
        current = order.status

        # Cannot change from Delivered or Cancelled
        if current in ["Delivered", "Cancelled"]:
            return jsonify({"success": False, "message": "Cannot change " + current + " orders!"}), 400

        # Pending can only go to Confirmed or Cancelled
        if current == "Pending" and status not in ["Confirmed", "Cancelled"]:
            return jsonify({"success": False, "message": "Pending orders can only be Confirmed or Cancelled!"}), 400

        # Confirmed can only go to Delivered
        if current == "Confirmed" and status != "Delivered":
            return jsonify({"success": False, "message": "Confirmed orders can only be marked as Delivered!"}), 400

        # If marking as Delivered, set to Awaiting Confirmation
        if status == "Delivered":
            order.status = "Awaiting Delivery"
        else:
            order.status = status

        db.session.commit()

        # Create notification for customer
        try:
            status_messages = {
                "Confirmed": "Your order #" + str(order.id) + " has been confirmed! We are preparing it now.",
                "Awaiting Delivery": "Your order #" + str(order.id) + " is on its way! Please confirm when you receive it.",
                "Cancelled": "Your order #" + str(order.id) + " has been cancelled. Contact us for more info."
            }
            
            actual_status = "Awaiting Delivery" if status == "Delivered" else status
            
            if actual_status in status_messages:
                user_notif = Notification(
                    user_id   = order.user_id,
                    for_admin = False,
                    title     = "Order #" + str(order.id) + " - " + actual_status,
                    message   = status_messages[actual_status],
                    order_id  = order.id
                )
                db.session.add(user_notif)
                db.session.commit()
        except Exception as e:
            print("Notification error:", e)

        return jsonify({"success": True, "message": "Status updated!"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/users", methods=["GET"])
def get_users():
    if not session.get("admin_logged_in"):
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    try:
        users = User.query.all()
        return jsonify([{
            "id":          u.id,
            "fullname":    u.fullname,
            "email":       u.email,
            "phone":       u.phone,
            "address":     u.address,
            "created_at":  u.created_at.strftime("%Y-%m-%d %H:%M"),
            "order_count": len(u.orders)
        } for u in users])
    except Exception as e:
        return jsonify([])

# ==============================
# NOTIFICATION ROUTES
# ==============================

@app.route("/api/notifications/admin", methods=["GET"])
def admin_notifications():
    if not session.get("admin_logged_in"):
        return jsonify({"success": False}), 401
    try:
        notifs = Notification.query.filter_by(for_admin=True).order_by(Notification.created_at.desc()).limit(50).all()
        unread = Notification.query.filter_by(for_admin=True, is_read=False).count()
        return jsonify({
            "notifications": [{
                "id":         n.id,
                "title":      n.title,
                "message":    n.message,
                "is_read":    n.is_read,
                "order_id":   n.order_id,
                "created_at": n.created_at.strftime("%Y-%m-%d %H:%M")
            } for n in notifs],
            "unread_count": unread
        })
    except Exception as e:
        print("Admin notif error:", e)
        return jsonify({"notifications": [], "unread_count": 0})

@app.route("/api/notifications/user", methods=["GET"])
def user_notifications():
    if not session.get("user_id"):
        return jsonify({"success": False}), 401
    try:
        notifs = Notification.query.filter_by(
            user_id=session["user_id"], for_admin=False
        ).order_by(Notification.created_at.desc()).limit(50).all()
        unread = Notification.query.filter_by(
            user_id=session["user_id"], for_admin=False, is_read=False
        ).count()
        return jsonify({
            "notifications": [{
                "id":         n.id,
                "title":      n.title,
                "message":    n.message,
                "is_read":    n.is_read,
                "order_id":   n.order_id,
                "created_at": n.created_at.strftime("%Y-%m-%d %H:%M")
            } for n in notifs],
            "unread_count": unread
        })
    except Exception as e:
        print("User notif error:", e)
        return jsonify({"notifications": [], "unread_count": 0})

@app.route("/api/notifications/read/<int:notif_id>", methods=["POST"])
def mark_read(notif_id):
    try:
        notif = Notification.query.get(notif_id)
        if notif:
            notif.is_read = True
            db.session.commit()
        return jsonify({"success": True})
    except Exception:
        return jsonify({"success": False})

@app.route("/api/notifications/read-all", methods=["POST"])
def mark_all_read():
    try:
        if session.get("admin_logged_in"):
            Notification.query.filter_by(for_admin=True, is_read=False).update({"is_read": True})
        elif session.get("user_id"):
            Notification.query.filter_by(user_id=session["user_id"], is_read=False).update({"is_read": True})
        db.session.commit()
        return jsonify({"success": True})
    except Exception:
        return jsonify({"success": False})

@app.route("/api/orders/confirm-delivery/<int:order_id>", methods=["POST"])
def confirm_delivery(order_id):
    if not session.get("user_id"):
        return jsonify({"success": False, "message": "Not logged in"}), 401
    try:
        order = Order.query.get_or_404(order_id)
        if order.user_id != session["user_id"]:
            return jsonify({"success": False, "message": "Not your order!"}), 403
        if order.status != "Awaiting Delivery":
            return jsonify({"success": False, "message": "Order not awaiting delivery!"}), 400

        order.status = "Delivered"
        db.session.commit()

        # Notify admin
        try:
            admin_notif = Notification(
                user_id   = 0,
                for_admin = True,
                title     = "Delivery Confirmed - Order #" + str(order.id),
                message   = order.customer_name + " confirmed receiving order #" + str(order.id),
                order_id  = order.id
            )
            db.session.add(admin_notif)
            db.session.commit()
        except Exception:
            pass

        return jsonify({"success": True, "message": "Delivery confirmed! Thank you!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

# ==============================
# RUN
# ==============================
if __name__ == "__main__":
    print("")
    print("  Esirifuahs Palace is LIVE!")
    print("  Store → http://localhost:5000")
    print("  Admin → http://localhost:5000/admin")
    print("  User  → sandra")
    print("  Pass  → SandrasPalace2024")
    print("")
    app.run(debug=False, host="0.0.0.0", port=5000)