import os
import re

print("")
print("  ========================================")
print("  Complete Fix - All Files")
print("  ========================================")
print("")

# ==============================
# WRITE COMPLETE app.py
# ==============================
print("  Writing clean app.py...")

app_content = '''from flask import Flask, render_template, request, jsonify, session, redirect, url_for
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

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///store.db")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

if DATABASE_URL.startswith("postgresql"):
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "connect_args": {"sslmode": "require", "connect_timeout": 10}
    }
else:
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
        "pool_recycle": 300
    }

db = SQLAlchemy(app)

UPLOAD_FOLDER = os.path.join("static", "uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

CLOUDINARY_CLOUD_NAME = os.environ.get("CLOUDINARY_CLOUD_NAME", "").strip()
CLOUDINARY_API_KEY    = os.environ.get("CLOUDINARY_API_KEY",    "").strip()
CLOUDINARY_API_SECRET = os.environ.get("CLOUDINARY_API_SECRET", "").strip()

cloudinary.config(
    cloud_name = CLOUDINARY_CLOUD_NAME,
    api_key    = CLOUDINARY_API_KEY,
    api_secret = CLOUDINARY_API_SECRET
)

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

ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "sandra")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "SandrasPalace2024")

def allowed_file(filename):
    ALLOWED = {"png", "jpg", "jpeg", "gif", "webp"}
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED

def upload_image(image):
    default_image = "https://via.placeholder.com/400x400?text=No+Image"
    if not image or image.filename == "":
        return default_image
    if not allowed_file(image.filename):
        return default_image

    if CLOUDINARY_CLOUD_NAME and CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET:
        try:
            image.stream.seek(0)
            result = cloudinary.uploader.upload(
                image.stream,
                folder="esirifuahs_palace",
                resource_type="image"
            )
            if result and result.get("secure_url"):
                print("Cloudinary OK:", result["secure_url"])
                return result["secure_url"]
        except Exception as e:
            print(f"Cloudinary error: {e}")
    else:
        print("Cloudinary credentials missing!")

    try:
        image.stream.seek(0)
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        fname = f"{datetime.now().strftime(\\'%Y%m%d%H%M%S\\')}_{secure_filename(image.filename)}"
        fpath = os.path.join(UPLOAD_FOLDER, fname)
        image.save(fpath)
        if os.path.exists(fpath) and os.path.getsize(fpath) > 0:
            print("Local save OK:", fpath)
            return f"static/uploads/{fname}"
    except Exception as e:
        print(f"Local save error: {e}")

    return default_image

def create_tables():
    try:
        with app.app_context():
            db.create_all()
            try:
                with db.engine.connect() as conn:
                    for col, defn in [
                        ("payment_status", "VARCHAR(50) DEFAULT \\'Paid\\'"),
                        ("transaction_id", "VARCHAR(100) DEFAULT \\'\\'"),
                        ("momo_number",    "VARCHAR(100) DEFAULT \\'\\'"  ),
                    ]:
                        try:
                            conn.execute(db.text(f"ALTER TABLE orders ADD COLUMN {col} {defn}"))
                            conn.commit()
                            print(f"Added column: {col}")
                        except Exception:
                            pass
            except Exception as e:
                print(f"Column check: {e}")
            print("Database ready!")
    except Exception as e:
        print(f"DB warning: {e}")
        print("App will start anyway...")

create_tables()

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
            return jsonify({"success": False, "message": "All fields are required!"})
        if len(password) < 6:
            return jsonify({"success": False, "message": "Password must be at least 6 characters!"})
        if User.query.filter_by(email=email).first():
            return jsonify({"success": False, "message": "Email already registered!"})

        user = User(
            fullname = fullname, email    = email,
            phone    = phone,    address  = address,
            password = generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()

        session["user_id"]    = user.id
        session["user_name"]  = user.fullname
        session["user_email"] = user.email

        return jsonify({"success": True, "message": "Account created! Welcome!",
            "user": {"id": user.id, "fullname": user.fullname,
                     "email": user.email, "phone": user.phone, "address": user.address}})
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

        return jsonify({"success": True, "message": f"Welcome back, {user.fullname}!",
            "user": {"id": user.id, "fullname": user.fullname,
                     "email": user.email, "phone": user.phone, "address": user.address}})
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
                         "email": user.email, "phone": user.phone, "address": user.address}})
    return jsonify({"logged_in": False})

@app.route("/api/items", methods=["GET"])
def get_items():
    try:
        items = Item.query.all()
        return jsonify([{
            "id": i.id, "name": i.name, "description": i.description,
            "price": i.price, "category": i.category, "in_stock": i.in_stock,
            "image_url": i.image_url, "date_added": i.date_added.strftime("%Y-%m-%d")
        } for i in items])
    except Exception as e:
        print(f"Get items error: {e}")
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
        return jsonify({"success": True, "in_stock": item.in_stock,
            "message": f"Item marked as {\\'In Stock\\' if item.in_stock else \\'Out of Stock\\'}"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/orders/place", methods=["POST"])
def place_order():
    if not session.get("user_id"):
        return jsonify({"success": False, "message": "Please login first!", "need_login": True}), 401
    try:
        data = request.get_json()
        if not data or not data.get("items"):
            return jsonify({"success": False, "message": "No items in order!"}), 400

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
        return jsonify({"success": True, "message": "Order placed!", "order_id": new_order.id})
    except Exception as e:
        db.session.rollback()
        print(f"Order error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/orders/my", methods=["GET"])
def my_orders():
    if not session.get("user_id"):
        return jsonify({"success": False, "message": "Not logged in"}), 401
    try:
        orders = Order.query.filter_by(user_id=session["user_id"]).order_by(Order.date_ordered.desc()).all()
        return jsonify([{
            "id": o.id, "items": o.items, "total_price": o.total_price,
            "status": o.status,
            "payment_status": o.payment_status or "Paid",
            "transaction_id": o.transaction_id or "",
            "date_ordered":   o.date_ordered.strftime("%Y-%m-%d %H:%M")
        } for o in orders])
    except Exception as e:
        print(f"My orders error: {e}")
        return jsonify([])

@app.route("/api/orders", methods=["GET"])
def get_orders():
    if not session.get("admin_logged_in"):
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    try:
        orders = Order.query.order_by(Order.date_ordered.desc()).all()
        return jsonify([{
            "id": o.id, "customer_name": o.customer_name,
            "customer_phone": o.customer_phone, "customer_address": o.customer_address,
            "items": o.items, "total_price": o.total_price, "status": o.status,
            "payment_status": o.payment_status or "Paid",
            "transaction_id": o.transaction_id or "",
            "momo_number":    o.momo_number    or "",
            "date_ordered":   o.date_ordered.strftime("%Y-%m-%d %H:%M"),
            "user_id": o.user_id
        } for o in orders])
    except Exception as e:
        print(f"Get orders error: {e}")
        return jsonify([])

@app.route("/api/orders/status/<int:order_id>", methods=["POST"])
def update_order_status(order_id):
    if not session.get("admin_logged_in"):
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    try:
        order  = Order.query.get_or_404(order_id)
        data   = request.get_json()
        status = data.get("status", order.status)
        if status not in ["Pending", "Confirmed", "Delivered", "Cancelled"]:
            return jsonify({"success": False, "message": "Invalid status!"}), 400
        order.status = status
        db.session.commit()
        return jsonify({"success": True, "message": f"Status updated to {status}!"})
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
            "id": u.id, "fullname": u.fullname, "email": u.email,
            "phone": u.phone, "address": u.address,
            "created_at":  u.created_at.strftime("%Y-%m-%d %H:%M"),
            "order_count": len(u.orders)
        } for u in users])
    except Exception as e:
        return jsonify([])

if __name__ == "__main__":
    print("")
    print("  Esirifuah\\'s Palace is LIVE!")
    print("  Store → http://localhost:5000")
    print("  Admin → http://localhost:5000/admin")
    print("  User  → sandra")
    print("  Pass  → SandrasPalace2024")
    print("")
    app.run(debug=False, host="0.0.0.0", port=5000)
'''

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(app_content)
print("  ✅ app.py written!")

# ==============================
# WRITE COMPLETE index.html
# ==============================
print("  Writing clean index.html...")

index_content = open('templates/index.html', 'r', encoding='utf-8').read()

# Remove ALL old checkout/order related JS functions
patterns_to_remove = [
    r'function openCheckout\(\).*?(?=function \w|\Z)',
    r'function closeOrderModal\(\).*?(?=function \w|\Z)',
    r'function goToPayment\(\).*?(?=function \w|\Z)',
    r'function backToDelivery\(\).*?(?=function \w|\Z)',
    r'function submitOrder\(\).*?(?=function \w|\Z)',
    r'document\.getElementById\(\'orderForm\'\)\.addEventListener.*?(?=function \w|document\.getElementById\(\'auth|\Z)',
]

for pattern in patterns_to_remove:
    index_content = re.sub(pattern, '', index_content, flags=re.DOTALL)

# Remove old order modal
index_content = re.sub(
    r'<!-- ORDER MODAL -->.*?<!-- SUCCESS MODAL -->',
    '<!-- SUCCESS MODAL -->',
    index_content,
    flags=re.DOTALL
)

# Add clean order modal
clean_modal = '''    <!-- ORDER MODAL -->
    <div class="modal-overlay" id="orderModal">
        <div class="modal">
            <div class="modal-header">
                <h2 id="order-modal-title">📋 Delivery Details</h2>
                <button class="modal-close" onclick="closeOrderModal()">✕</button>
            </div>
            <div class="modal-body">

                <div class="order-summary">
                    <h3>🛒 Your Order</h3>
                    <div id="order-summary-items"></div>
                    <div class="order-summary-total">
                        <span>Total</span>
                        <span id="order-summary-total">GH&#8373; 0.00</span>
                    </div>
                </div>

                <!-- STEP 1 DELIVERY -->
                <div id="step-delivery">
                    <div class="form-group">
                        <label>👤 Full Name</label>
                        <input type="text" id="cust-name" placeholder="Your full name" />
                    </div>
                    <div class="form-group">
                        <label>📱 Phone Number</label>
                        <input type="tel" id="cust-phone" placeholder="Your phone" />
                    </div>
                    <div class="form-group">
                        <label>📍 Delivery Address</label>
                        <textarea id="cust-address" placeholder="Your address"></textarea>
                    </div>
                    <button class="modal-btn" onclick="goToPayment()">
                        💳 Next: Make Payment
                    </button>
                </div>

                <!-- STEP 2 PAYMENT -->
                <div id="step-payment" style="display:none">
                    <div style="background:linear-gradient(135deg,#fff8e1,#fff3cd);border:3px solid #f9a825;border-radius:18px;padding:20px;margin-bottom:20px;text-align:center;">
                        <div style="font-size:35px;margin-bottom:8px;">📱</div>
                        <h3 style="font-family:'Fredoka One',cursive;color:#f57f17;font-size:17px;margin-bottom:15px;">Send MTN Mobile Money To:</h3>
                        <div style="background:white;border-radius:12px;padding:12px;margin-bottom:10px;border:2px solid #fce4ec;">
                            <div style="font-size:22px;font-weight:800;color:#e91e63;font-family:'Fredoka One',cursive;">0550618807</div>
                            <div style="color:#888;font-size:13px;font-weight:700;">👤 Sandra Nkrumah</div>
                        </div>
                        <div style="background:white;border-radius:12px;padding:12px;margin-bottom:15px;border:2px solid #fce4ec;">
                            <div style="font-size:22px;font-weight:800;color:#e91e63;font-family:'Fredoka One',cursive;">0540882629</div>
                            <div style="color:#888;font-size:13px;font-weight:700;">👤 Milicent Nkrumah</div>
                        </div>
                        <div id="amount-display" style="background:linear-gradient(135deg,#e91e63,#ff6f00);color:white;border-radius:12px;padding:12px 20px;font-family:'Fredoka One',cursive;font-size:20px;">
                            Amount: GH&#8373; 0.00
                        </div>
                    </div>

                    <div class="form-group">
                        <label>📱 Which number did you pay to? *</label>
                        <select id="momo-number" style="width:100%;padding:14px 16px;border:3px solid #fce4ec;border-radius:14px;font-size:14px;font-weight:600;outline:none;font-family:'Nunito',sans-serif;background:#fffbfc;cursor:pointer;">
                            <option value="">-- Select number --</option>
                            <option value="0550618807 - Sandra Nkrumah">0550618807 - Sandra Nkrumah</option>
                            <option value="0540882629 - Milicent Nkrumah">0540882629 - Milicent Nkrumah</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label>🔢 Transaction ID *</label>
                        <input type="text" id="transaction-id" placeholder="e.g. 1234567890" />
                        <small style="color:#aaa;font-size:12px;font-weight:700;display:block;margin-top:5px;">
                            Find this in your MoMo SMS after payment
                        </small>
                    </div>

                    <button class="modal-btn green" id="place-order-btn" onclick="submitOrder()">
                        ✅ I Have Paid - Place Order
                    </button>

                    <button onclick="backToDelivery()" style="width:100%;padding:13px;background:none;border:3px solid #fce4ec;border-radius:16px;font-size:15px;font-weight:800;cursor:pointer;color:#aaa;margin-top:10px;font-family:'Nunito';">
                        ← Back
                    </button>
                </div>

            </div>
        </div>
    </div>

    <!-- SUCCESS MODAL -->'''

index_content = index_content.replace('<!-- SUCCESS MODAL -->', clean_modal)

# Add clean JS functions before closing script tag
clean_js = '''
        // ===========================
        // CHECKOUT FUNCTIONS
        // ===========================
        function openCheckout() {
            if (cart.length === 0) {
                showToast('Cart is empty!', 'error');
                return;
            }
            if (!currentUser) {
                showToast('Please login first!', 'error');
                closeCart();
                openAuthModal('login');
                return;
            }
            const tp = cart.reduce((s, i) => s + (i.price * i.quantity), 0);
            document.getElementById('order-summary-items').innerHTML = cart.map(i =>
                '<div class="order-summary-item"><span>' + i.name + ' x' + i.quantity + '</span><span>GH&#8373; ' + (i.price * i.quantity).toFixed(2) + '</span></div>'
            ).join('');
            document.getElementById('order-summary-total').textContent = 'GH\u20b5 ' + tp.toFixed(2);
            document.getElementById('amount-display').textContent      = 'Amount: GH\u20b5 ' + tp.toFixed(2);
            document.getElementById('cust-name').value    = currentUser.fullname || '';
            document.getElementById('cust-phone').value   = currentUser.phone    || '';
            document.getElementById('cust-address').value = currentUser.address  || '';
            document.getElementById('step-delivery').style.display = 'block';
            document.getElementById('step-payment').style.display  = 'none';
            document.getElementById('order-modal-title').textContent = 'Delivery Details';
            closeCart();
            document.getElementById('orderModal').classList.add('show');
        }

        function closeOrderModal() {
            document.getElementById('orderModal').classList.remove('show');
        }

        function goToPayment() {
            var name    = document.getElementById('cust-name').value.trim();
            var phone   = document.getElementById('cust-phone').value.trim();
            var address = document.getElementById('cust-address').value.trim();
            if (!name)    { showToast('Please enter your name!',    'error'); return; }
            if (!phone)   { showToast('Please enter your phone!',   'error'); return; }
            if (!address) { showToast('Please enter your address!', 'error'); return; }
            document.getElementById('step-delivery').style.display = 'none';
            document.getElementById('step-payment').style.display  = 'block';
            document.getElementById('order-modal-title').textContent = 'Make Payment';
        }

        function backToDelivery() {
            document.getElementById('step-delivery').style.display = 'block';
            document.getElementById('step-payment').style.display  = 'none';
            document.getElementById('order-modal-title').textContent = 'Delivery Details';
        }

        async function submitOrder() {
            var momoNumber    = document.getElementById('momo-number').value.trim();
            var transactionId = document.getElementById('transaction-id').value.trim();

            if (!momoNumber)    { showToast('Please select which number you paid to!', 'error'); return; }
            if (!transactionId) { showToast('Please enter your Transaction ID!',       'error'); return; }

            var btn = document.getElementById('place-order-btn');
            btn.textContent = 'Placing Order...';
            btn.disabled    = true;

            var tp = cart.reduce(function(s, i) { return s + (i.price * i.quantity); }, 0);

            var orderData = {
                customer_name:    document.getElementById('cust-name').value.trim(),
                customer_phone:   document.getElementById('cust-phone').value.trim(),
                customer_address: document.getElementById('cust-address').value.trim(),
                items:            cart.map(function(i) {
                    return { id: i.id, name: i.name, price: i.price, quantity: i.quantity };
                }),
                total_price:    tp,
                transaction_id: transactionId,
                momo_number:    momoNumber
            };

            try {
                var response = await fetch('/api/orders/place', {
                    method:  'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body:    JSON.stringify(orderData)
                });
                var data = await response.json();

                if (data.success) {
                    closeOrderModal();
                    document.getElementById('success-order-id').textContent = 'Order #' + data.order_id;
                    document.getElementById('successModal').classList.add('show');
                    cart = [];
                    updateCartUI();
                    document.getElementById('momo-number').value    = '';
                    document.getElementById('transaction-id').value = '';
                } else if (data.need_login) {
                    showToast('Please login first!', 'error');
                    closeOrderModal();
                    openAuthModal('login');
                } else {
                    showToast(data.message || 'Error placing order!', 'error');
                }
            } catch (err) {
                console.error('Order error:', err);
                showToast('Something went wrong! Try again.', 'error');
            }

            btn.textContent = 'I Have Paid - Place Order';
            btn.disabled    = false;
        }

'''

# Insert before closing script tag
index_content = index_content.replace(
    "        document.getElementById('authModal').addEventListener",
    clean_js + "        document.getElementById('authModal').addEventListener"
)

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(index_content)

print("  ✅ index.html written!")

# ==============================
# PUSH TO GITHUB
# ==============================
print("")
print("  Pushing to GitHub...")
os.system('git add .')
os.system('git commit -m "Complete fix - checkout and order flow"')
os.system('git push')

print("")
print("  ========================================")
print("  ALL DONE!")
print("  Render updates in 2-3 minutes!")
print("  ========================================")
print("")