import os

print("")
print("  ========================================")
print("  Adding Notifications + Order Flow Fix")
print("  ========================================")
print("")

# ==============================
# UPDATE app.py - Add Notification Model
# ==============================
print("  Updating app.py...")

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add Notification model after Order model
old_model_end = '''ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "sandra")'''

new_model = '''class Notification(db.Model):
    __tablename__ = "notifications"
    id         = db.Column(db.Integer,     primary_key=True)
    user_id    = db.Column(db.Integer,     default=0)
    for_admin  = db.Column(db.Boolean,     default=False)
    title      = db.Column(db.String(200), nullable=False)
    message    = db.Column(db.String(500), nullable=False)
    is_read    = db.Column(db.Boolean,     default=False)
    order_id   = db.Column(db.Integer,     default=0)
    created_at = db.Column(db.DateTime,    default=datetime.utcnow)

ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "sandra")'''

content = content.replace(old_model_end, new_model)
print("  ✅ Added Notification model")

# Add notification table creation
old_columns = '''                    columns = [
                        ("payment_status", "VARCHAR(50)  DEFAULT 'Paid'"),
                        ("transaction_id", "VARCHAR(100) DEFAULT ''"),
                        ("momo_number",    "VARCHAR(100) DEFAULT ''"),
                    ]'''

new_columns = '''                    columns = [
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
                        pass'''

content = content.replace(old_columns, new_columns)
print("  ✅ Added notifications table creation")

# Update place_order to create notification for admin
old_place_success = '''        db.session.add(new_order)
        db.session.commit()

        return jsonify({
            "success":  True,
            "message":  "Order placed!",
            "order_id": new_order.id
        })'''

new_place_success = '''        db.session.add(new_order)
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
        })'''

content = content.replace(old_place_success, new_place_success)
print("  ✅ Added admin notification on new order")

# Update order status to create notification for customer + enforce flow
old_status_update = '''    try:
        order  = Order.query.get_or_404(order_id)
        data   = request.get_json()
        status = data.get("status", order.status)

        if status not in ["Pending", "Confirmed", "Delivered", "Cancelled"]:
            return jsonify({"success": False, "message": "Invalid status!"}), 400

        order.status = status
        db.session.commit()
        return jsonify({"success": True, "message": "Status updated to " + status})'''

new_status_update = '''    try:
        order  = Order.query.get_or_404(order_id)
        data   = request.get_json()
        status = data.get("status", order.status)

        if status not in ["Pending", "Confirmed", "Delivered", "Cancelled"]:
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

        return jsonify({"success": True, "message": "Status updated!"})'''

content = content.replace(old_status_update, new_status_update)
print("  ✅ Updated order flow + customer notifications")

# Add valid status update
old_valid = '''        if status not in ["Pending", "Confirmed", "Delivered", "Cancelled"]:'''
new_valid = '''        if status not in ["Pending", "Confirmed", "Delivered", "Cancelled", "Awaiting Delivery"]:'''
content   = content.replace(old_valid, new_valid)

# Add notification API routes before RUN section
old_run = '''# ==============================
# RUN
# =============================='''

new_notification_routes = '''# ==============================
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
# =============================='''

content = content.replace(old_run, new_notification_routes)
print("  ✅ Added notification API routes")
print("  ✅ Added delivery confirmation route")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("  ✅ app.py saved!")
print("")

# ==============================
# UPDATE admin.html - Add notifications bell + order flow
# ==============================
print("  Updating admin.html...")

with open('templates/admin.html', 'r', encoding='utf-8') as f:
    admin = f.read()

# Add notification bell to topbar
old_topbar = '''    <div class="topbar">
        <div>
            <h1 id="page-title">📊 Dashboard</h1>
            <p id="page-subtitle">Welcome back, Sandra! 👑</p>
        </div>
    </div>'''

new_topbar = '''    <div class="topbar">
        <div>
            <h1 id="page-title">📊 Dashboard</h1>
            <p id="page-subtitle">Welcome back, Sandra! 👑</p>
        </div>
        <div style="position:relative;">
            <button onclick="toggleNotifications()" style="
                background:linear-gradient(135deg,#e91e63,#ff6f00);
                border:none; border-radius:15px; padding:12px 20px;
                color:white; font-size:18px; cursor:pointer;
                font-weight:800; font-family:'Nunito';
                position:relative;
            ">
                🔔
                <span id="notif-count" style="
                    position:absolute; top:-5px; right:-5px;
                    background:#e53935; color:white;
                    width:22px; height:22px; border-radius:50%;
                    font-size:11px; display:none;
                    align-items:center; justify-content:center;
                    font-weight:800;
                ">0</span>
            </button>

            <!-- Notification Dropdown -->
            <div id="notif-dropdown" style="
                display:none; position:absolute; right:0; top:55px;
                background:white; border-radius:20px; width:350px;
                max-height:450px; overflow-y:auto;
                box-shadow:0 10px 40px rgba(0,0,0,0.15);
                border:3px solid #fce4ec; z-index:500;
            ">
                <div style="
                    padding:18px 20px; background:#fff0f3;
                    border-radius:17px 17px 0 0;
                    display:flex; justify-content:space-between;
                    align-items:center;
                ">
                    <span style="font-family:'Fredoka One',cursive;color:#c2185b;font-size:16px;">
                        🔔 Notifications
                    </span>
                    <button onclick="markAllRead()" style="
                        background:none; border:none; color:#e91e63;
                        font-size:13px; font-weight:800; cursor:pointer;
                    ">Mark all read</button>
                </div>
                <div id="notif-list" style="padding:10px;">
                    <div style="text-align:center;padding:30px;color:#aaa;font-weight:700;">
                        No notifications
                    </div>
                </div>
            </div>
        </div>
    </div>'''

admin = admin.replace(old_topbar, new_topbar)
print("  ✅ Added notification bell to admin")

# Update order status select to enforce flow
old_order_select = '''                        \'<select class="status-select" onchange="updateStatus(\' + o.id + \', this.value)">\\' +
                        \'<option \' + (o.status === \\\'Pending\\\'   ? \\\'selected\\\' : \\\'\\\') + \'>Pending</option>\' +
                        \'<option \' + (o.status === \\\'Confirmed\\\' ? \\\'selected\\\' : \\\'\\\') + \'>Confirmed</option>\' +
                        \'<option \' + (o.status === \\\'Delivered\\\' ? \\\'selected\\\' : \\\'\\\') + \'>Delivered</option>\' +
                        \'<option \' + (o.status === \\\'Cancelled\\\' ? \\\'selected\\\' : \\\'\\\') + \'>Cancelled</option>\' +
                        \'</select>\\'''

# Instead let's replace the whole loadOrders order action
admin = admin.replace(
    "'<select class=\"status-select\" onchange=\"updateStatus(' + o.id + ', this.value)\">' +\n                        '<option ' + (o.status === 'Pending'   ? 'selected' : '') + '>Pending</option>' +\n                        '<option ' + (o.status === 'Confirmed' ? 'selected' : '') + '>Confirmed</option>' +\n                        '<option ' + (o.status === 'Delivered' ? 'selected' : '') + '>Delivered</option>' +\n                        '<option ' + (o.status === 'Cancelled' ? 'selected' : '') + '>Cancelled</option>' +\n                        '</select>'",
    "getOrderActions(o)"
)
print("  ✅ Updated order actions")

# Add helper functions before showToast
old_toast = '''    function showToast(msg, type) {'''

new_helpers = '''    // ===========================
    // ORDER ACTION BUTTONS
    // ===========================
    function getOrderActions(o) {
        if (o.status === "Delivered") {
            return '<span style="color:#43a047;font-weight:800;font-size:13px;">✅ Completed</span>';
        }
        if (o.status === "Cancelled") {
            return '<span style="color:#e53935;font-weight:800;font-size:13px;">❌ Cancelled</span>';
        }
        if (o.status === "Awaiting Delivery") {
            return '<span style="color:#1976d2;font-weight:800;font-size:13px;">📦 Awaiting Customer</span>';
        }
        if (o.status === "Pending") {
            return '<button class="btn btn-success btn-sm" onclick="updateStatus(' + o.id + ',\\'Confirmed\\')">✅ Confirm</button> ' +
                   '<button class="btn btn-danger btn-sm" onclick="updateStatus(' + o.id + ',\\'Cancelled\\')">❌ Cancel</button>';
        }
        if (o.status === "Confirmed") {
            return '<button class="btn btn-primary btn-sm" onclick="updateStatus(' + o.id + ',\\'Delivered\\')">📦 Send</button>';
        }
        return '';
    }

    // ===========================
    // NOTIFICATIONS
    // ===========================
    function toggleNotifications() {
        var dd = document.getElementById("notif-dropdown");
        if (dd.style.display === "none") {
            dd.style.display = "block";
            loadNotifications();
        } else {
            dd.style.display = "none";
        }
    }

    function loadNotifications() {
        fetch("/api/notifications/admin")
            .then(function(r) { return r.json(); })
            .then(function(data) {
                var count = document.getElementById("notif-count");
                if (data.unread_count > 0) {
                    count.textContent    = data.unread_count;
                    count.style.display  = "flex";
                } else {
                    count.style.display  = "none";
                }

                var list = document.getElementById("notif-list");
                if (!data.notifications || data.notifications.length === 0) {
                    list.innerHTML = '<div style="text-align:center;padding:30px;color:#aaa;font-weight:700;">No notifications</div>';
                    return;
                }

                list.innerHTML = data.notifications.map(function(n) {
                    return '<div onclick="markNotifRead(' + n.id + ')" style="' +
                        'padding:14px 15px;border-bottom:2px solid #fce4ec;cursor:pointer;' +
                        'background:' + (n.is_read ? 'white' : '#fff0f3') + ';' +
                        'transition:all 0.2s;border-radius:10px;margin-bottom:5px;' +
                        '">' +
                        '<div style="font-weight:800;color:#c2185b;font-size:14px;margin-bottom:4px;">' +
                        (n.is_read ? '' : '🔴 ') + n.title +
                        '</div>' +
                        '<div style="font-size:13px;color:#666;font-weight:600;">' + n.message + '</div>' +
                        '<div style="font-size:11px;color:#aaa;margin-top:5px;font-weight:700;">' + n.created_at + '</div>' +
                        '</div>';
                }).join("");
            })
            .catch(function(e) { console.error("Notif error:", e); });
    }

    function markNotifRead(id) {
        fetch("/api/notifications/read/" + id, { method: "POST" })
            .then(function() { loadNotifications(); });
    }

    function markAllRead() {
        fetch("/api/notifications/read-all", { method: "POST" })
            .then(function() { loadNotifications(); showToast("All marked as read!", "success"); });
    }

    // Check notifications every 30 seconds
    setInterval(function() {
        fetch("/api/notifications/admin")
            .then(function(r) { return r.json(); })
            .then(function(data) {
                var count = document.getElementById("notif-count");
                if (data.unread_count > 0) {
                    count.textContent   = data.unread_count;
                    count.style.display = "flex";
                } else {
                    count.style.display = "none";
                }
            })
            .catch(function() {});
    }, 30000);

    // Close notification dropdown when clicking outside
    document.addEventListener("click", function(e) {
        if (!e.target.closest("[onclick*=\\'toggleNotifications\\']") &&
            !e.target.closest("#notif-dropdown")) {
            document.getElementById("notif-dropdown").style.display = "none";
        }
    });

    function showToast(msg, type) {'''

admin = admin.replace(old_toast, new_helpers)
print("  ✅ Added notification functions to admin")

# Add Awaiting Delivery status badge
old_badges = '''        .status-badge.cancelled { background:#ffebee; color:#e53935; }'''
new_badges = '''        .status-badge.cancelled { background:#ffebee; color:#e53935; }
        .status-badge.awaiting { background:#e3f2fd; color:#1976d2; }'''
admin = admin.replace(old_badges, new_badges)

# Fix status badge class for Awaiting Delivery
admin = admin.replace(
    "o.status.toLowerCase()",
    "(o.status === 'Awaiting Delivery' ? 'awaiting' : o.status.toLowerCase())"
)

with open('templates/admin.html', 'w', encoding='utf-8') as f:
    f.write(admin)

print("  ✅ admin.html saved!")
print("")

# ==============================
# UPDATE index.html - Add user notifications + delivery confirmation
# ==============================
print("  Updating index.html...")

with open('templates/index.html', 'r', encoding='utf-8') as f:
    index = f.read()

# Add notification bell to user dropdown
old_user_menu = '''                menu.innerHTML  =
                '<div class="dropdown-header">\\u{1f451} ' + currentUser.fullname + '</div>' +
                '<div class="dropdown-item" onclick="openMyOrders()">📦 My Orders</div>' +
                '<div class="dropdown-item" onclick="userLogout()">🚪 Logout</div>';'''

new_user_menu = '''                menu.innerHTML  =
                '<div class="dropdown-header">\\u{1f451} ' + currentUser.fullname + '</div>' +
                '<div class="dropdown-item" onclick="openUserNotifications()">🔔 Notifications <span id="user-notif-badge" style="background:#e53935;color:white;border-radius:50%;padding:2px 8px;font-size:11px;margin-left:5px;display:none;">0</span></div>' +
                '<div class="dropdown-item" onclick="openMyOrders()">📦 My Orders</div>' +
                '<div class="dropdown-item" onclick="userLogout()">🚪 Logout</div>';
            
            // Check notifications
            checkUserNotifications();'''

index = index.replace(old_user_menu, new_user_menu)
print("  ✅ Added notification to user menu")

# Add notification modal before toast div
old_toast_div = '''<!-- ===== TOAST ===== -->'''
new_notif_modal = '''<!-- ===== USER NOTIFICATIONS MODAL ===== -->
<div class="modal-overlay" id="userNotifModal">
    <div class="modal">
        <div class="modal-header">
            <h2>🔔 Notifications</h2>
            <button class="modal-close" onclick="document.getElementById('userNotifModal').classList.remove('show')">✕</button>
        </div>
        <div class="modal-body">
            <div id="user-notif-list" style="max-height:400px;overflow-y:auto;">
                <div class="empty-state">
                    <div class="empty-icon">🔔</div>
                    <p>No notifications</p>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- ===== TOAST ===== -->'''

index = index.replace(old_toast_div, new_notif_modal)
print("  ✅ Added user notification modal")

# Update My Orders to show delivery confirmation button
old_my_orders_display = '''                    list.innerHTML = orders.map(function(o) {
                        var statusClass = o.status.toLowerCase();
                        return '<div class="my-order-card">' +
                            '<div class="my-order-header">' +
                            '<h4>Order #' + o.id + '</h4>' +
                            '<span class="status-badge ' + statusClass + '">' + o.status + '</span>' +
                            '</div>' +
                            '<div class="my-order-items">' + formatItems(o.items) + '</div>' +
                            '<div class="my-order-footer">' +
                            '<span style="color:#aaa;font-size:13px">' + o.date_ordered + '</span>' +
                            '<span class="my-order-price">GH&#8373; ' + o.total_price.toFixed(2) + '</span>' +
                            '</div>' +
                            '</div>';
                    }).join('');'''

new_my_orders_display = '''                    list.innerHTML = orders.map(function(o) {
                        var statusClass = o.status === 'Awaiting Delivery' ? 'awaiting' : o.status.toLowerCase();
                        var confirmBtn  = '';
                        if (o.status === 'Awaiting Delivery') {
                            confirmBtn = '<button onclick="confirmDelivery(' + o.id + ')" style="' +
                                'width:100%;padding:10px;margin-top:10px;' +
                                'background:linear-gradient(135deg,#43a047,#66bb6a);' +
                                'color:white;border:none;border-radius:12px;' +
                                'font-weight:800;cursor:pointer;font-family:Nunito;font-size:14px;' +
                                '">\\u2705 Confirm I Received My Order</button>';
                        }
                        return '<div class="my-order-card">' +
                            '<div class="my-order-header">' +
                            '<h4>Order #' + o.id + '</h4>' +
                            '<span class="status-badge ' + statusClass + '">' + o.status + '</span>' +
                            '</div>' +
                            '<div class="my-order-items">' + formatItems(o.items) + '</div>' +
                            '<div class="my-order-footer">' +
                            '<span style="color:#aaa;font-size:13px">' + o.date_ordered + '</span>' +
                            '<span class="my-order-price">GH&#8373; ' + o.total_price.toFixed(2) + '</span>' +
                            '</div>' +
                            confirmBtn +
                            '</div>';
                    }).join('');'''

index = index.replace(old_my_orders_display, new_my_orders_display)
print("  ✅ Added delivery confirmation button")

# Add Awaiting Delivery status badge
index = index.replace(
    '.status-badge.cancelled { background:#ffebee; color:#e53935; }',
    '.status-badge.cancelled { background:#ffebee; color:#e53935; }\n        .status-badge.awaiting { background:#e3f2fd; color:#1976d2; }'
)

# Add notification functions before closing script
old_close_modals = '''    // ===========================
    // CLOSE MODALS ON OVERLAY
    // ==========================='''

new_notif_functions = '''    // ===========================
    // USER NOTIFICATIONS
    // ===========================
    function checkUserNotifications() {
        if (!currentUser) return;
        fetch('/api/notifications/user')
            .then(function(r) { return r.json(); })
            .then(function(data) {
                var badge = document.getElementById('user-notif-badge');
                if (badge && data.unread_count > 0) {
                    badge.textContent   = data.unread_count;
                    badge.style.display = 'inline';
                } else if (badge) {
                    badge.style.display = 'none';
                }
            })
            .catch(function() {});
    }

    // Check every 30 seconds
    setInterval(function() {
        if (currentUser) checkUserNotifications();
    }, 30000);

    function openUserNotifications() {
        document.getElementById('dropdown-menu').classList.remove('show');
        fetch('/api/notifications/user')
            .then(function(r) { return r.json(); })
            .then(function(data) {
                var list = document.getElementById('user-notif-list');
                if (!data.notifications || data.notifications.length === 0) {
                    list.innerHTML = '<div class="empty-state"><div class="empty-icon">🔔</div><p>No notifications yet</p></div>';
                } else {
                    list.innerHTML = data.notifications.map(function(n) {
                        return '<div style="' +
                            'padding:15px;border-bottom:2px solid #fce4ec;' +
                            'background:' + (n.is_read ? 'white' : '#fff0f3') + ';' +
                            'border-radius:12px;margin-bottom:8px;' +
                            '">' +
                            '<div style="font-weight:800;color:#c2185b;font-size:14px;margin-bottom:5px;">' +
                            (n.is_read ? '' : '🔴 ') + n.title +
                            '</div>' +
                            '<div style="font-size:13px;color:#666;font-weight:600;">' + n.message + '</div>' +
                            '<div style="font-size:11px;color:#aaa;margin-top:6px;font-weight:700;">' + n.created_at + '</div>' +
                            '</div>';
                    }).join('');
                }
                document.getElementById('userNotifModal').classList.add('show');

                // Mark all as read
                fetch('/api/notifications/read-all', { method: 'POST' })
                    .then(function() { checkUserNotifications(); });
            })
            .catch(function() {
                showToast('Error loading notifications!', 'error');
            });
    }

    function confirmDelivery(orderId) {
        if (!confirm('Confirm you received your order?')) return;
        fetch('/api/orders/confirm-delivery/' + orderId, { method: 'POST' })
            .then(function(r) { return r.json(); })
            .then(function(d) {
                if (d.success) {
                    showToast('Delivery confirmed! Thank you!', 'success');
                    openMyOrders();
                } else {
                    showToast(d.message || 'Error!', 'error');
                }
            })
            .catch(function() { showToast('Error!', 'error'); });
    }

    // ===========================
    // CLOSE MODALS ON OVERLAY
    // ==========================='''

index = index.replace(old_close_modals, new_notif_functions)

# Add userNotifModal close handler
index = index.replace(
    "document.getElementById('myOrdersModal').addEventListener('click', function(e) {\n        if (e.target === this) document.getElementById('myOrdersModal').classList.remove('show');\n    });",
    "document.getElementById('myOrdersModal').addEventListener('click', function(e) {\n        if (e.target === this) document.getElementById('myOrdersModal').classList.remove('show');\n    });\n    document.getElementById('userNotifModal').addEventListener('click', function(e) {\n        if (e.target === this) document.getElementById('userNotifModal').classList.remove('show');\n    });"
)

print("  ✅ Added user notification functions")

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(index)

print("  ✅ index.html saved!")
print("")

# ==============================
# PUSH TO GITHUB
# ==============================
print("  Pushing to GitHub...")
os.system('git add .')
os.system('git commit -m "Added notifications + order flow enforcement"')
os.system('git push')

print("")
print("  ========================================")
print("  ALL DONE!")
print("")
print("  New Features:")
print("  🔔 Admin gets notification when order placed")
print("  🔔 Customer gets notification on status change")
print("  📋 Order Flow Enforced:")
print("     Pending → Confirm or Cancel")
print("     Confirmed → Mark as Sent")
print("     Sent → Customer confirms delivery")
print("     Delivered ← Cannot be changed")
print("     Cancelled ← Cannot be changed")
print("")
print("  Render updates in 2-3 minutes!")
print("  ========================================")
print("")