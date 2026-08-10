from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import os
import logging
import cloudinary
import cloudinary.uploader

app = Flask(__name__)
app.secret_key = "sandras_palace_secret_key_2024"

# ==============================
# SUPPRESS DEV WARNING
# ==============================
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# ==============================
# DATABASE SETUP
# ==============================
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///store.db')

# Fix for SQLAlchemy compatibility
if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
    'connect_args': {
        'sslmode': 'require',
        'connect_timeout': 10
    } if DATABASE_URL.startswith('postgresql') else {}
}

db = SQLAlchemy(app)

# ==============================
# UPLOAD FOLDER SETUP
# ==============================
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ==============================
# CLOUDINARY SETUP
# ==============================
cloudinary.config(
    cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME', ''),
    api_key    = os.environ.get('CLOUDINARY_API_KEY', ''),
    api_secret = os.environ.get('CLOUDINARY_API_SECRET', '')
)

# ==============================
# DATABASE MODELS
# ==============================

class User(db.Model):
    __tablename__ = 'users'
    id         = db.Column(db.Integer, primary_key=True)
    fullname   = db.Column(db.String(100), nullable=False)
    email      = db.Column(db.String(120), unique=True, nullable=False)
    phone      = db.Column(db.String(20),  nullable=False)
    address    = db.Column(db.String(300), nullable=False)
    password   = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    orders     = db.relationship('Order', backref='user', lazy=True)

class Item(db.Model):
    __tablename__ = 'items'
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    price       = db.Column(db.Float, nullable=False)
    category    = db.Column(db.String(50))
    in_stock    = db.Column(db.Boolean, default=True)
    image_url   = db.Column(db.String(500),
                            default='https://via.placeholder.com/400x400?text=No+Image')
    date_added  = db.Column(db.DateTime, default=datetime.utcnow)

class Order(db.Model):
    __tablename__ = 'orders'
    id               = db.Column(db.Integer, primary_key=True)
    user_id          = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    customer_name    = db.Column(db.String(100), nullable=False)
    customer_phone   = db.Column(db.String(20),  nullable=False)
    customer_address = db.Column(db.String(300), nullable=False)
    items            = db.Column(db.Text,        nullable=False)
    total_price      = db.Column(db.Float,       nullable=False)
    status           = db.Column(db.String(50),  default='Pending')
    date_ordered     = db.Column(db.DateTime,    default=datetime.utcnow)

# ==============================
# ADMIN CREDENTIALS
# ==============================
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'sandra')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'SandrasPalace2024')

# ==============================
# HELPER FUNCTIONS
# ==============================
def allowed_file(filename):
    ALLOWED = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED

def upload_image(image):
    """Upload image to Cloudinary or save locally"""
    try:
        cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME', '')
        if cloud_name:
            result = cloudinary.uploader.upload(
                image,
                folder    = "sandras_palace",
                overwrite = True
            )
            return result['secure_url']
        else:
            filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{image.filename}"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            image.save(filepath)
            return f"static/uploads/{filename}"
    except Exception as e:
        print(f"Image upload error: {e}")
        try:
            filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{image.filename}"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            image.save(filepath)
            return f"static/uploads/{filename}"
        except:
            return 'https://via.placeholder.com/400x400?text=No+Image'

# ==============================
# CREATE TABLES SAFELY
# ==============================
def create_tables():
    try:
        with app.app_context():
            db.create_all()
            print("✅ Database tables ready!")
    except Exception as e:
        print(f"⚠️ Database connection warning: {e}")
        print("⚠️ App will start anyway...")

create_tables()

# ==============================
# PAGE ROUTES
# ==============================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def admin():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    return render_template('admin.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'Invalid request'
            }), 400

        username = data.get('username', '')
        password = data.get('password', '')

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return jsonify({'success': True})

        return jsonify({
            'success': False,
            'message': 'Wrong username or password'
        })

    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

# ==============================
# USER AUTH API
# ==============================

@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Invalid request'}), 400

        fullname = data.get('fullname', '').strip()
        email    = data.get('email', '').strip().lower()
        phone    = data.get('phone', '').strip()
        address  = data.get('address', '').strip()
        password = data.get('password', '')

        if not fullname or not email or not phone or not address or not password:
            return jsonify({
                'success': False,
                'message': 'All fields are required!'
            })

        if len(password) < 6:
            return jsonify({
                'success': False,
                'message': 'Password must be at least 6 characters!'
            })

        existing = User.query.filter_by(email=email).first()
        if existing:
            return jsonify({
                'success': False,
                'message': 'Email already registered! Please login.'
            })

        new_user = User(
            fullname = fullname,
            email    = email,
            phone    = phone,
            address  = address,
            password = generate_password_hash(password)
        )

        db.session.add(new_user)
        db.session.commit()

        session['user_id']    = new_user.id
        session['user_name']  = new_user.fullname
        session['user_email'] = new_user.email

        return jsonify({
            'success': True,
            'message': 'Account created successfully! Welcome! 🎉',
            'user': {
                'id':       new_user.id,
                'fullname': new_user.fullname,
                'email':    new_user.email,
                'phone':    new_user.phone,
                'address':  new_user.address
            }
        })

    except Exception as e:
        db.session.rollback()
        print(f"Register error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def user_login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Invalid request'}), 400

        email    = data.get('email', '').strip().lower()
        password = data.get('password', '')

        if not email or not password:
            return jsonify({
                'success': False,
                'message': 'Email and password required!'
            })

        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password, password):
            return jsonify({
                'success': False,
                'message': 'Invalid email or password!'
            })

        session['user_id']    = user.id
        session['user_name']  = user.fullname
        session['user_email'] = user.email

        return jsonify({
            'success': True,
            'message': f'Welcome back, {user.fullname}! 👑',
            'user': {
                'id':       user.id,
                'fullname': user.fullname,
                'email':    user.email,
                'phone':    user.phone,
                'address':  user.address
            }
        })

    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/auth/logout', methods=['POST'])
def user_logout():
    session.pop('user_id',    None)
    session.pop('user_name',  None)
    session.pop('user_email', None)
    return jsonify({'success': True, 'message': 'Logged out!'})

@app.route('/api/auth/check', methods=['GET'])
def check_auth():
    if session.get('user_id'):
        user = User.query.get(session['user_id'])
        if user:
            return jsonify({
                'logged_in': True,
                'user': {
                    'id':       user.id,
                    'fullname': user.fullname,
                    'email':    user.email,
                    'phone':    user.phone,
                    'address':  user.address
                }
            })
    return jsonify({'logged_in': False})

@app.route('/api/auth/update', methods=['POST'])
def update_profile():
    if not session.get('user_id'):
        return jsonify({'success': False, 'message': 'Not logged in'}), 401

    try:
        data = request.get_json()
        user = User.query.get(session['user_id'])

        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 404

        user.fullname = data.get('fullname', user.fullname)
        user.phone    = data.get('phone',    user.phone)
        user.address  = data.get('address',  user.address)

        db.session.commit()
        session['user_name'] = user.fullname

        return jsonify({
            'success': True,
            'message': 'Profile updated!',
            'user': {
                'id':       user.id,
                'fullname': user.fullname,
                'email':    user.email,
                'phone':    user.phone,
                'address':  user.address
            }
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# ==============================
# ITEMS API
# ==============================

@app.route('/api/items', methods=['GET'])
def get_items():
    try:
        items = Item.query.all()
        return jsonify([{
            'id':          item.id,
            'name':        item.name,
            'description': item.description,
            'price':       item.price,
            'category':    item.category,
            'in_stock':    item.in_stock,
            'image_url':   item.image_url,
            'date_added':  item.date_added.strftime('%Y-%m-%d')
        } for item in items])
    except Exception as e:
        print(f"Get items error: {e}")
        return jsonify([])

@app.route('/api/items/add', methods=['POST'])
def add_item():
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    try:
        data      = request.form
        image     = request.files.get('image')
        image_url = 'https://via.placeholder.com/400x400?text=No+Image'

        if image and image.filename != '' and allowed_file(image.filename):
            image_url = upload_image(image)

        if not data.get('name') or not data.get('price'):
            return jsonify({
                'success': False,
                'message': 'Name and price are required!'
            }), 400

        new_item = Item(
            name        = data.get('name'),
            description = data.get('description', ''),
            price       = float(data.get('price')),
            category    = data.get('category', 'General'),
            in_stock    = data.get('in_stock', 'true') == 'true',
            image_url   = image_url
        )

        db.session.add(new_item)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Item added successfully! ✨'
        })

    except Exception as e:
        db.session.rollback()
        print(f"Add item error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/items/update/<int:item_id>', methods=['POST'])
def update_item(item_id):
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    try:
        item  = Item.query.get_or_404(item_id)
        data  = request.form
        image = request.files.get('image')

        if image and image.filename != '' and allowed_file(image.filename):
            item.image_url = upload_image(image)

        item.name        = data.get('name',        item.name)
        item.description = data.get('description', item.description)
        item.price       = float(data.get('price', item.price))
        item.category    = data.get('category',    item.category)
        item.in_stock    = data.get('in_stock', 'true') == 'true'

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Item updated successfully! ✨'
        })

    except Exception as e:
        db.session.rollback()
        print(f"Update item error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/items/delete/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    try:
        item = Item.query.get_or_404(item_id)

        if item.image_url and item.image_url.startswith('static/uploads/'):
            if os.path.exists(item.image_url):
                os.remove(item.image_url)

        db.session.delete(item)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Item deleted successfully!'
        })

    except Exception as e:
        db.session.rollback()
        print(f"Delete item error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/items/toggle/<int:item_id>', methods=['POST'])
def toggle_stock(item_id):
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    try:
        item = Item.query.get(item_id)
        if not item:
            return jsonify({
                'success': False,
                'message': 'Item not found!'
            }), 404

        item.in_stock = not item.in_stock
        db.session.commit()

        status_text = 'In Stock ✅' if item.in_stock else 'Out of Stock ❌'

        return jsonify({
            'success':  True,
            'in_stock': item.in_stock,
            'message':  f'Item marked as {status_text}'
        })

    except Exception as e:
        db.session.rollback()
        print(f"Toggle stock error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

# ==============================
# ORDERS API
# ==============================

@app.route('/api/orders/place', methods=['POST'])
def place_order():
    if not session.get('user_id'):
        return jsonify({
            'success':    False,
            'message':    'Please login first!',
            'need_login': True
        }), 401

    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Invalid request'}), 400

        if not data.get('items') or len(data.get('items')) == 0:
            return jsonify({'success': False, 'message': 'No items in order!'}), 400

        user = User.query.get(session['user_id'])
        if not user:
            return jsonify({'success': False, 'message': 'User not found!'}), 404

        new_order = Order(
            user_id          = user.id,
            customer_name    = data.get('customer_name',    user.fullname),
            customer_phone   = data.get('customer_phone',   user.phone),
            customer_address = data.get('customer_address', user.address),
            items            = str(data.get('items')),
            total_price      = float(data.get('total_price')),
            status           = 'Pending'
        )

        db.session.add(new_order)
        db.session.commit()

        return jsonify({
            'success':  True,
            'message':  'Order placed successfully! 🎉',
            'order_id': new_order.id
        })

    except Exception as e:
        db.session.rollback()
        print(f"Place order error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/orders/my', methods=['GET'])
def my_orders():
    if not session.get('user_id'):
        return jsonify({'success': False, 'message': 'Not logged in'}), 401

    try:
        orders = Order.query.filter_by(
            user_id=session['user_id']
        ).order_by(Order.date_ordered.desc()).all()

        return jsonify([{
            'id':           o.id,
            'items':        o.items,
            'total_price':  o.total_price,
            'status':       o.status,
            'date_ordered': o.date_ordered.strftime('%Y-%m-%d %H:%M')
        } for o in orders])

    except Exception as e:
        print(f"My orders error: {e}")
        return jsonify([])

@app.route('/api/orders', methods=['GET'])
def get_orders():
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    try:
        orders = Order.query.order_by(Order.date_ordered.desc()).all()
        return jsonify([{
            'id':               o.id,
            'customer_name':    o.customer_name,
            'customer_phone':   o.customer_phone,
            'customer_address': o.customer_address,
            'items':            o.items,
            'total_price':      o.total_price,
            'status':           o.status,
            'date_ordered':     o.date_ordered.strftime('%Y-%m-%d %H:%M'),
            'user_id':          o.user_id
        } for o in orders])

    except Exception as e:
        print(f"Get orders error: {e}")
        return jsonify([])

@app.route('/api/orders/status/<int:order_id>', methods=['POST'])
def update_order_status(order_id):
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    try:
        order  = Order.query.get_or_404(order_id)
        data   = request.get_json()
        status = data.get('status', order.status)

        valid_statuses = ['Pending', 'Confirmed', 'Delivered', 'Cancelled']
        if status not in valid_statuses:
            return jsonify({
                'success': False,
                'message': 'Invalid status!'
            }), 400

        order.status = status
        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Order status updated to {status}!'
        })

    except Exception as e:
        db.session.rollback()
        print(f"Update order status error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/users', methods=['GET'])
def get_users():
    if not session.get('admin_logged_in'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    try:
        users = User.query.all()
        return jsonify([{
            'id':          u.id,
            'fullname':    u.fullname,
            'email':       u.email,
            'phone':       u.phone,
            'address':     u.address,
            'created_at':  u.created_at.strftime('%Y-%m-%d %H:%M'),
            'order_count': len(u.orders)
        } for u in users])

    except Exception as e:
        print(f"Get users error: {e}")
        return jsonify([])

# ==============================
# RUN APP
# ==============================
if __name__ == '__main__':
    print("")
    print("  👑✨ Esirifuah's Palace is LIVE! ✨👑")
    print("  ══════════════════════════════════")
    print("  🏪 Store    → http://localhost:5000")
    print("  🔧 Admin    → http://localhost:5000/admin")
    print("  👤 Username → sandra")
    print("  🔑 Password → SandrasPalace2024")
    print("  ══════════════════════════════════")
    print("")
    app.run(debug=False, host='0.0.0.0', port=5000)