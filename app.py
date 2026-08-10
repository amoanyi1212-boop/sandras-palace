from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
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

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

if DATABASE_URL.startswith("postgresql"):
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "pool_timeout": 10,
        "pool_size": 5,
        "connect_args": {
            "sslmode": "require",
            "connect_timeout": 10
        }
    }
else:
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
        "pool_recycle": 300
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
CLOUD_NAME = os.environ.get("CLOUDINARY_CLOUD_NAME", "").strip()
CLOUD_KEY  = os.environ.get("CLOUDINARY_API_KEY",    "").strip()
CLOUD_SEC  = os.environ.get("CLOUDINARY_API_SECRET", "").strip()

cloudinary.config(
    cloud_name = CLOUD_NAME,
    api_key    = CLOUD_KEY,
    api_secret = CLOUD_SEC
)

# ==============================
# MODELS
# ==============================

class User(db.Model):
    __tablename__ = "users"
    id         = db.Column(db.Integer, primary_key=True)
    fullname   = db.Column(db.String(100), nullable=False)
    email      = db.Column(db.String(120), unique=True, nullable=False)
    phone      = db.Column(db.String(20),  nullable=False)
    address    = db.Column(db.String(300), nullable=False)
    password   = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    orders     = db.relationship("Order", backref="user", lazy=True)

class Item(db.Model):
    __tablename__ = "items"
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    price       = db.Column(db.Float, nullable=False)
    category    = db.Column(db.String(50))
    in_stock    = db.Column(db.Boolean, default=True)
    image_url   = db.Column(db.String(500),
                  default="https://via.placeholder.com/400x400?text=No+Image")
    date_added  = db.Column(db.DateTime, default=datetime.utcnow)

class Order(db.Model):
    __tablename__ = "orders"
    id               = db.Column(db.Integer, primary_key=True)
    user_id          = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    customer_name    = db.Column(db.String(100), nullable=False)
    customer_phone   = db.Column(db.String(20),  nullable=False)
    customer_address = db.Column(db.String(300), nullable=False)
    items            = db.Column(db.Text, nullable=False)
    total_price      = db.Column(db.Float, nullable=False)
    status           = db.Column(db.String(50), default="Pending")
    payment_status   = db.Column(db.String(50), default="Paid")
    transaction_id   = db.Column(db.String(100), default="")
    momo_number      = db.Column(db.String(100), default="")
    delivered_at     = db.Column(db.DateTime, nullable=True)
    date_ordered     = db.Column(db.DateTime, default=datetime.utcnow)

class Notification(db.Model):
    __tablename__ = "notifications"
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, default=0)
    for_admin  = db.Column(db.Boolean, default=False)
    title      = db.Column(db.String(200), nullable=False)
    message    = db.Column(db.String(500), nullable=False)
    is_read    = db.Column(db.Boolean, default=False)
    order_id   = db.Column(db.Integer, default=0)
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
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in \
           {"png", "jpg", "jpeg", "gif", "webp"}

def upload_image(image):
    default = "https://via.placeholder.com/400x400?text=No+Image"
    if not image or image.filename == "" or not allowed_file(image.filename):
        return default
    if CLOUD_NAME and CLOUD_KEY and CLOUD_SEC:
        try:
            image.stream.seek(0)
            result = cloudinary.uploader.upload(
                image.stream,
                folder="esirifuahs_palace",
                resource_type="image"
            )
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
        notif = Notification(
            user_id=user_id, for_admin=for_admin,
            title=title, message=message, order_id=order_id
        )
        db.session.add(notif)
        db.session.commit()
        return True
    except Exception as e:
        print("Notification error:", e)
        db.session.rollback()
        return False

def check_expired_deliveries():
    """Auto confirm deliveries after 14 days"""
    try:
        two_weeks_ago = datetime.utcnow() - timedelta(days=14)
        with db.engine.connect() as conn:
            try:
                rows = conn.execute(db.text(
                    "SELECT id, user_id, customer_name FROM orders "
                    "WHERE status = 'Awaiting Delivery' "
                    "AND delivered_at IS NOT NULL "
                    "AND delivered_at <= :d"
                ), {"d": two_weeks_ago}).fetchall()
                for row in rows:
                    conn.execute(db.text(
                        "UPDATE orders SET status = 'Delivered' WHERE id = :id"
                    ), {"id": row[0]})
                    conn.commit()
                    send_notification(row[1], False,
                        "Order #" + str(row[0]) + " Auto-Confirmed",
                        "Your order was auto-confirmed after 14 days.", row[0])
                    send_notification(0, True,
                        "Auto-Confirmed Order #" + str(row[0]),
                        str(row[2]) + " order auto-confirmed.", row[0])
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
                    for col, defn in [
                        ("payment_status", "VARCHAR(50)  DEFAULT 'Paid'"),
                        ("transaction_id", "VARCHAR(100) DEFAULT ''"),
                        ("momo_number",    "VARCHAR(100) DEFAULT ''"),
                        ("delivered_at",   "TIMESTAMP"),
                    ]:
                        try:
                            conn.execute(db.text(
                                "ALTER TABLE orders ADD COLUMN "
                                + col + " " + defn
                            ))
                            conn.commit()
                        except Exception:
                            pass
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
            except Exception as e:
                print("Column setup:", e)
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
    try:
        check_expired_deliveries()
    except Exception:
        pass
    return render_template("index.html")

@app.route("/admin")
def admin():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))
    try:
        check_expired_deliveries()
    except Exception:
        pass
    return render_template("admin.html")

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "Invalid"}), 400
        if (data.get("username") == ADMIN_USERNAME and
                data.get("password") == ADMIN_PASSWORD):
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
        fn   = data.get("fullname", "").strip()
        em   = data.get("email",    "").strip().lower()
        ph   = data.get("phone",    "").strip()
        addr = data.get("address",  "").strip()
        pw   = data.get("password", "")
        if not all([fn, em, ph, addr, pw]):
            return jsonify({"success": False, "message": "All fields required!"})
        if len(pw) < 6:
            return jsonify({"success": False, "message": "Password min 6 chars!"})
        if User.query.filter_by(email=em).first():
            return jsonify({"success": False, "message": "Email already registered!"})
        user = User(
            fullname=fn, email=em, phone=ph,
            address=addr, password=generate_password_hash(pw)
        )
        db.session.add(user)
        db.session.commit()
        session["user_id"]    = user.id
        session["user_name"]  = user.fullname
        session["user_email"] = user.email
        send_notification(0, True, "New User",
            fn + " just registered!", 0)
        return jsonify({"success": True, "message": "Welcome!",
            "user": {"id": user.id, "fullname": user.fullname,
                     "email": user.email, "phone": user.phone,
                     "address": user.address}})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/auth/login", methods=["POST"])
def user_login():
    try:
        data = request.get_json()
        em   = data.get("email",    "").strip().lower()
        pw   = data.get("password", "")
        user = User.query.filter_by(email=em).first()
        if not user or not check_password_hash(user.password, pw):
            return jsonify({"success": False, "message": "Invalid credentials!"})
        session["user_id"]    = user.id
        session["user_name"]  = user.fullname
        session["user_email"] = user.email
        return jsonify({"success": True, "message": "Welcome back!",
            "user": {"id": user.id, "fullname": user.fullname,
                     "email": user.email, "phone": user.phone,
                     "address": user.address}})
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
            return jsonify({"logged_in": True,
                "user": {"id": user.id, "fullname": user.fullname,
                         "email": user.email, "phone": user.phone,
                         "address": user.address}})
    return jsonify({"logged_in": False})

@app.route("/api/auth/update", methods=["POST"])
def update_profile():
    if not session.get("user_id"):
        return jsonify({"success": False}), 401
    try:
        data = request.get_json()
        user = User.query.get(session["user_id"])
        if not user:
            return jsonify({"success": False}), 404
        user.fullname = data.get("fullname", user.fullname)
        user.phone    = data.get("phone",    user.phone)
        user.address  = data.get("address",  user.address)
        db.session.commit()
        session["user_name"] = user.fullname
        return jsonify({"success": True, "message": "Updated!",
            "user": {"id": user.id, "fullname": user.fullname,
                     "email": user.email, "phone": user.phone,
                     "address": user.address}})
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
            "id": i.id, "name": i.name,
            "description": i.description,
            "price": i.price, "category": i.category,
            "in_stock": i.in_stock, "image_url": i.image_url,
            "date_added": i.date_added.strftime("%Y-%m-%d")
        } for i in items])
    except Exception:
        return jsonify([])

@app.route("/api/items/add", methods=["POST"])
def add_item():
    if not session.get("admin_logged_in"):
        return jsonify({"success": False}), 401
    try:
        data  = request.form
        image = request.files.get("image")
        url   = "https://via.placeholder.com/400x400?text=No+Image"
        if image and image.filename != "":
            url = upload_image(image)
        new = Item(
            name=data.get("name"),
            description=data.get("description", ""),
            price=float(data.get("price")),
            category=data.get("category", "General"),
            in_stock=data.get("in_stock", "true") == "true",
            image_url=url
        )
        db.session.add(new)
        db.session.commit()
        return jsonify({"success": True, "message": "Item added!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/items/update/<int:item_id>", methods=["POST"])
def update_item(item_id):
    if not session.get("admin_logged_in"):
        return jsonify({"success": False}), 401
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
        return jsonify({"success": True, "message": "Updated!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/items/delete/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    if not session.get("admin_logged_in"):
        return jsonify({"success": False}), 401
    try:
        item = Item.query.get_or_404(item_id)
        if item.image_url and item.image_url.startswith("static/uploads/"):
            if os.path.exists(item.image_url):
                os.remove(item.image_url)
        db.session.delete(item)
        db.session.commit()
        return jsonify({"success": True, "message": "Deleted!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/items/toggle/<int:item_id>", methods=["POST"])
def toggle_stock(item_id):
    if not session.get("admin_logged_in"):
        return jsonify({"success": False}), 401
    try:
        item = Item.query.get(item_id)
        if not item:
            return jsonify({"success": False, "message": "Not found!"}), 404
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
        return jsonify({"success": False,
            "message": "Login first!", "need_login": True}), 401
    try:
        data = request.get_json()
        if not data or not data.get("items"):
            return jsonify({"success": False, "message": "No items!"}), 400
        user = User.query.get(session["user_id"])
        if not user:
            return jsonify({"success": False, "message": "User not found!"}), 404
        order = Order(
            user_id=user.id,
            customer_name=data.get("customer_name",    user.fullname),
            customer_phone=data.get("customer_phone",  user.phone),
            customer_address=data.get("customer_address", user.address),
            items=str(data.get("items")),
            total_price=float(data.get("total_price")),
            status="Pending", payment_status="Paid",
            transaction_id=data.get("transaction_id", ""),
            momo_number=data.get("momo_number", "")
        )
        db.session.add(order)
        db.session.commit()
        send_notification(0, True,
            "New Order #" + str(order.id),
            user.fullname + " placed order GH" + chr(8373) +
            " " + str(order.total_price) +
            ". Trans: " + data.get("transaction_id", "N/A"),
            order.id)
        send_notification(user.id, False,
            "Order #" + str(order.id) + " Received",
            "Your order has been received! We will confirm shortly.",
            order.id)
        return jsonify({"success": True, "message": "Order placed!",
            "order_id": order.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/orders/my", methods=["GET"])
def my_orders():
    if not session.get("user_id"):
        return jsonify([])
    try:
        orders = Order.query.filter_by(
            user_id=session["user_id"]
        ).order_by(Order.date_ordered.desc()).all()
        return jsonify([{
            "id": o.id, "items": o.items,
            "total_price": o.total_price, "status": o.status,
            "payment_status": o.payment_status or "Paid",
            "transaction_id": o.transaction_id or "",
            "date_ordered": o.date_ordered.strftime("%Y-%m-%d %H:%M"),
            "delivered_at": o.delivered_at.strftime("%Y-%m-%d %H:%M")
                            if o.delivered_at else ""
        } for o in orders])
    except Exception:
        return jsonify([])

@app.route("/api/orders", methods=["GET"])
def get_orders():
    if not session.get("admin_logged_in"):
        return jsonify([])
    try:
        orders = Order.query.order_by(Order.date_ordered.desc()).all()
        return jsonify([{
            "id": o.id,
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
            "delivered_at":     o.delivered_at.strftime("%Y-%m-%d %H:%M")
                                if o.delivered_at else "",
            "user_id": o.user_id
        } for o in orders])
    except Exception:
        return jsonify([])

@app.route("/api/orders/status/<int:order_id>", methods=["POST"])
def update_order_status(order_id):
    if not session.get("admin_logged_in"):
        return jsonify({"success": False}), 401
    try:
        order   = Order.query.get_or_404(order_id)
        data    = request.get_json()
        status  = data.get("status", order.status)
        current = order.status

        if current in ["Delivered", "Cancelled"]:
            return jsonify({"success": False,
                "message": "Cannot change " + current + " orders!"}), 400
        if current == "Disputed":
            return jsonify({"success": False,
                "message": "This order is disputed!"}), 400
        if current == "Awaiting Delivery":
            return jsonify({"success": False,
                "message": "Waiting for customer to confirm!"}), 400
        if current == "Pending" and status not in ["Confirmed", "Cancelled"]:
            return jsonify({"success": False,
                "message": "Can only Confirm or Cancel!"}), 400
        if current == "Confirmed" and status != "Delivered":
            return jsonify({"success": False,
                "message": "Can only mark as Delivered!"}), 400

        if status == "Delivered":
            order.status       = "Awaiting Delivery"
            order.delivered_at = datetime.utcnow()
            send_notification(order.user_id, False,
                "Order #" + str(order.id) + " On The Way!",
                "Your order is on its way! Please confirm when received. "
                "Auto-confirms in 14 days.", order.id)
        elif status == "Confirmed":
            order.status = "Confirmed"
            send_notification(order.user_id, False,
                "Order #" + str(order.id) + " Confirmed!",
                "Your order is confirmed and being prepared!", order.id)
        elif status == "Cancelled":
            order.status = "Cancelled"
            send_notification(order.user_id, False,
                "Order #" + str(order.id) + " Cancelled",
                "Your order was cancelled. Contact us for info.", order.id)

        db.session.commit()
        return jsonify({"success": True, "message": "Status updated!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/orders/confirm-delivery/<int:order_id>", methods=["POST"])
def confirm_delivery(order_id):
    if not session.get("user_id"):
        return jsonify({"success": False}), 401
    try:
        order = Order.query.get_or_404(order_id)
        if order.user_id != session["user_id"]:
            return jsonify({"success": False, "message": "Not your order!"}), 403
        if order.status != "Awaiting Delivery":
            return jsonify({"success": False,
                "message": "Order not awaiting delivery!"}), 400
        order.status = "Delivered"
        db.session.commit()
        send_notification(0, True,
            "Delivery Confirmed - #" + str(order.id),
            order.customer_name + " confirmed order #" + str(order.id),
            order.id)
        send_notification(order.user_id, False,
            "Order #" + str(order.id) + " Complete!",
            "Thank you for confirming! Enjoy your purchase!", order.id)
        return jsonify({"success": True, "message": "Confirmed! Thank you!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/orders/dispute/<int:order_id>", methods=["POST"])
def dispute_order(order_id):
    if not session.get("user_id"):
        return jsonify({"success": False}), 401
    try:
        order = Order.query.get_or_404(order_id)
        if order.user_id != session["user_id"]:
            return jsonify({"success": False, "message": "Not your order!"}), 403
        if order.status != "Awaiting Delivery":
            return jsonify({"success": False,
                "message": "Cannot dispute this order!"}), 400
        data   = request.get_json()
        reason = data.get("reason", "No reason given")
        order.status = "Disputed"
        db.session.commit()
        send_notification(0, True,
            "DISPUTE - Order #" + str(order.id),
            order.customer_name + " disputed order. Reason: " + reason,
            order.id)
        send_notification(order.user_id, False,
            "Dispute Filed - #" + str(order.id),
            "Dispute filed! We will contact you in 24 hours.", order.id)
        return jsonify({"success": True,
            "message": "Dispute filed! We will contact you."})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

# ==============================
# NOTIFICATIONS
# ==============================

@app.route("/api/notifications/admin", methods=["GET"])
def admin_notifications():
    if not session.get("admin_logged_in"):
        return jsonify({"notifications": [], "unread_count": 0})
    try:
        notifs = Notification.query.filter_by(
            for_admin=True
        ).order_by(Notification.created_at.desc()).limit(50).all()
        unread = Notification.query.filter_by(
            for_admin=True, is_read=False).count()
        return jsonify({
            "notifications": [{
                "id": n.id, "title": n.title, "message": n.message,
                "is_read": n.is_read, "order_id": n.order_id,
                "created_at": n.created_at.strftime("%Y-%m-%d %H:%M")
            } for n in notifs],
            "unread_count": unread
        })
    except Exception:
        return jsonify({"notifications": [], "unread_count": 0})

@app.route("/api/notifications/user", methods=["GET"])
def user_notifications():
    if not session.get("user_id"):
        return jsonify({"notifications": [], "unread_count": 0})
    try:
        notifs = Notification.query.filter_by(
            user_id=session["user_id"], for_admin=False
        ).order_by(Notification.created_at.desc()).limit(50).all()
        unread = Notification.query.filter_by(
            user_id=session["user_id"], for_admin=False, is_read=False
        ).count()
        return jsonify({
            "notifications": [{
                "id": n.id, "title": n.title, "message": n.message,
                "is_read": n.is_read, "order_id": n.order_id,
                "created_at": n.created_at.strftime("%Y-%m-%d %H:%M")
            } for n in notifs],
            "unread_count": unread
        })
    except Exception:
        return jsonify({"notifications": [], "unread_count": 0})

@app.route("/api/notifications/read/<int:notif_id>", methods=["POST"])
def mark_read(notif_id):
    try:
        n = Notification.query.get(notif_id)
        if n:
            n.is_read = True
            db.session.commit()
        return jsonify({"success": True})
    except Exception:
        return jsonify({"success": False})

@app.route("/api/notifications/read-all", methods=["POST"])
def mark_all_read():
    try:
        if session.get("admin_logged_in"):
            Notification.query.filter_by(
                for_admin=True, is_read=False
            ).update({"is_read": True})
        elif session.get("user_id"):
            Notification.query.filter_by(
                user_id=session["user_id"], is_read=False
            ).update({"is_read": True})
        db.session.commit()
        return jsonify({"success": True})
    except Exception:
        return jsonify({"success": False})

@app.route("/api/users", methods=["GET"])
def get_users():
    if not session.get("admin_logged_in"):
        return jsonify([])
    try:
        users = User.query.all()
        return jsonify([{
            "id": u.id, "fullname": u.fullname,
            "email": u.email, "phone": u.phone,
            "address": u.address,
            "created_at": u.created_at.strftime("%Y-%m-%d %H:%M"),
            "order_count": len(u.orders)
        } for u in users])
    except Exception:
        return jsonify([])

# ==============================
# RUN
# ==============================
if __name__ == "__main__":
    print("")
    print("  Esirifuahs Palace LIVE!")
    print("  Store → http://localhost:5000")
    print("  Admin → http://localhost:5000/admin")
    print("")
    app.run(debug=False, host="0.0.0.0", port=5000)