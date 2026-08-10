import os
import re

print("")
print("  ========================================")
print("  Adding Mobile Money Payment System")
print("  ========================================")
print("")

# ==============================
# UPDATE app.py
# ==============================
print("  Updating app.py...")

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add transaction_id to Order model
old_order_model = '''class Order(db.Model):
    __tablename__ = 'orders'
    id               = db.Column(db.Integer, primary_key=True)
    user_id          = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    customer_name    = db.Column(db.String(100), nullable=False)
    customer_phone   = db.Column(db.String(20),  nullable=False)
    customer_address = db.Column(db.String(300), nullable=False)
    items            = db.Column(db.Text,        nullable=False)
    total_price      = db.Column(db.Float,       nullable=False)
    status           = db.Column(db.String(50),  default='Pending')
    date_ordered     = db.Column(db.DateTime,    default=datetime.utcnow)'''

new_order_model = '''class Order(db.Model):
    __tablename__ = 'orders'
    id               = db.Column(db.Integer, primary_key=True)
    user_id          = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    customer_name    = db.Column(db.String(100), nullable=False)
    customer_phone   = db.Column(db.String(20),  nullable=False)
    customer_address = db.Column(db.String(300), nullable=False)
    items            = db.Column(db.Text,        nullable=False)
    total_price      = db.Column(db.Float,       nullable=False)
    status           = db.Column(db.String(50),  default='Pending')
    payment_status   = db.Column(db.String(50),  default='Unpaid')
    transaction_id   = db.Column(db.String(100), default='')
    momo_number      = db.Column(db.String(20),  default='')
    date_ordered     = db.Column(db.DateTime,    default=datetime.utcnow)'''

content = content.replace(old_order_model, new_order_model)
print("  ✅ Updated Order model with payment fields")

# Update place_order route
old_place_order = '''        new_order = Order(
            user_id          = user.id,
            customer_name    = data.get('customer_name',    user.fullname),
            customer_phone   = data.get('customer_phone',   user.phone),
            customer_address = data.get('customer_address', user.address),
            items            = str(data.get('items')),
            total_price      = float(data.get('total_price')),
            status           = 'Pending'
        )'''

new_place_order = '''        new_order = Order(
            user_id          = user.id,
            customer_name    = data.get('customer_name',    user.fullname),
            customer_phone   = data.get('customer_phone',   user.phone),
            customer_address = data.get('customer_address', user.address),
            items            = str(data.get('items')),
            total_price      = float(data.get('total_price')),
            status           = 'Pending',
            payment_status   = 'Paid',
            transaction_id   = data.get('transaction_id',  ''),
            momo_number      = data.get('momo_number',     '')
        )'''

content = content.replace(old_place_order, new_place_order)
print("  ✅ Updated place_order to save payment details")

# Update get_orders to include payment info
old_get_orders = '''        return jsonify([{
            'id':               o.id,
            'customer_name':    o.customer_name,
            'customer_phone':   o.customer_phone,
            'customer_address': o.customer_address,
            'items':            o.items,
            'total_price':      o.total_price,
            'status':           o.status,
            'date_ordered':     o.date_ordered.strftime('%Y-%m-%d %H:%M'),
            'user_id':          o.user_id
        } for o in orders])'''

new_get_orders = '''        return jsonify([{
            'id':               o.id,
            'customer_name':    o.customer_name,
            'customer_phone':   o.customer_phone,
            'customer_address': o.customer_address,
            'items':            o.items,
            'total_price':      o.total_price,
            'status':           o.status,
            'payment_status':   o.payment_status  if o.payment_status  else 'Paid',
            'transaction_id':   o.transaction_id  if o.transaction_id  else '',
            'momo_number':      o.momo_number     if o.momo_number     else '',
            'date_ordered':     o.date_ordered.strftime('%Y-%m-%d %H:%M'),
            'user_id':          o.user_id
        } for o in orders])'''

content = content.replace(old_get_orders, new_get_orders)
print("  ✅ Updated get_orders to return payment info")

# Update my_orders to include payment info
old_my_orders = '''        return jsonify([{
            'id':           o.id,
            'items':        o.items,
            'total_price':  o.total_price,
            'status':       o.status,
            'date_ordered': o.date_ordered.strftime('%Y-%m-%d %H:%M')
        } for o in orders])'''

new_my_orders = '''        return jsonify([{
            'id':             o.id,
            'items':          o.items,
            'total_price':    o.total_price,
            'status':         o.status,
            'payment_status': o.payment_status if o.payment_status else 'Paid',
            'transaction_id': o.transaction_id if o.transaction_id else '',
            'date_ordered':   o.date_ordered.strftime('%Y-%m-%d %H:%M')
        } for o in orders])'''

content = content.replace(old_my_orders, new_my_orders)
print("  ✅ Updated my_orders to return payment info")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("  ✅ app.py saved!")
print("")

# ==============================
# UPDATE index.html
# ==============================
print("  Updating index.html...")

with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace order modal with payment modal
old_order_modal = '''    <!-- ORDER MODAL -->
    <div class="modal-overlay" id="orderModal">
        <div class="modal">
            <div class="modal-header"><h2>📋 Complete Your Order</h2><button class="modal-close" onclick="closeOrderModal()">✕</button></div>
            <div class="modal-body">
                <div class="order-summary"><h3>🛒 Order Summary</h3><div id="order-summary-items"></div><div class="order-summary-total"><span>Total</span><span id="order-summary-total">$0.00</span></div></div>
                <form id="orderForm">
                    <div class="form-group"><label>👤 Full Name</label><input type="text" id="cust-name" required /></div>
                    <div class="form-group"><label>📱 Phone</label><input type="tel" id="cust-phone" required /></div>
                    <div class="form-group"><label>📍 Delivery Address</label><textarea id="cust-address" required></textarea></div>
                    <button type="submit" class="modal-btn green">🚀 Place Order</button>
                </form>
            </div>
        </div>
    </div>'''

new_order_modal = '''    <!-- ORDER MODAL -->
    <div class="modal-overlay" id="orderModal">
        <div class="modal">
            <div class="modal-header">
                <h2>📋 Complete Your Order</h2>
                <button class="modal-close" onclick="closeOrderModal()">✕</button>
            </div>
            <div class="modal-body">

                <!-- Order Summary -->
                <div class="order-summary">
                    <h3>🛒 Order Summary</h3>
                    <div id="order-summary-items"></div>
                    <div class="order-summary-total">
                        <span>Total</span>
                        <span id="order-summary-total">GH₵ 0.00</span>
                    </div>
                </div>

                <!-- Step 1: Delivery Details -->
                <div id="step-1">
                    <h3 style="font-family:'Fredoka One';color:#c2185b;margin-bottom:15px;">
                        📍 Step 1: Delivery Details
                    </h3>
                    <div class="form-group">
                        <label>👤 Full Name</label>
                        <input type="text" id="cust-name" required />
                    </div>
                    <div class="form-group">
                        <label>📱 Phone</label>
                        <input type="tel" id="cust-phone" required />
                    </div>
                    <div class="form-group">
                        <label>📍 Delivery Address</label>
                        <textarea id="cust-address" required></textarea>
                    </div>
                    <button class="modal-btn" onclick="goToPayment()">
                        Next: Pay Now 💳
                    </button>
                </div>

                <!-- Step 2: Payment -->
                <div id="step-2" style="display:none;">
                    <h3 style="font-family:'Fredoka One';color:#c2185b;margin-bottom:15px;">
                        💳 Step 2: Make Payment
                    </h3>

                    <!-- MoMo Details Box -->
                    <div style="
                        background:linear-gradient(135deg,#fff8e1,#fff3cd);
                        border:3px solid #f9a825;
                        border-radius:18px;
                        padding:20px;
                        margin-bottom:20px;
                        text-align:center;
                    ">
                        <div style="font-size:40px;margin-bottom:10px;">📱</div>
                        <h3 style="font-family:'Fredoka One';color:#f57f17;font-size:18px;margin-bottom:15px;">
                            Send MTN Mobile Money To:
                        </h3>

                        <!-- Account 1 -->
                        <div style="
                            background:white;
                            border-radius:12px;
                            padding:15px;
                            margin-bottom:10px;
                            border:2px solid #fce4ec;
                        ">
                            <div style="font-size:24px;font-weight:800;color:#e91e63;font-family:'Fredoka One';">
                                0550618807
                            </div>
                            <div style="color:#888;font-weight:700;font-size:14px;margin-top:5px;">
                                👤 Sandra Nkrumah
                            </div>
                        </div>

                        <!-- Account 2 -->
                        <div style="
                            background:white;
                            border-radius:12px;
                            padding:15px;
                            margin-bottom:15px;
                            border:2px solid #fce4ec;
                        ">
                            <div style="font-size:24px;font-weight:800;color:#e91e63;font-family:'Fredoka One';">
                                0540882629
                            </div>
                            <div style="color:#888;font-weight:700;font-size:14px;margin-top:5px;">
                                👤 Milicent Nkrumah
                            </div>
                        </div>

                        <div id="amount-to-pay" style="
                            background:linear-gradient(135deg,#e91e63,#ff6f00);
                            color:white;
                            border-radius:12px;
                            padding:12px 20px;
                            font-family:'Fredoka One';
                            font-size:22px;
                        ">
                            Amount: GH₵ 0.00
                        </div>
                    </div>

                    <!-- Transaction ID Form -->
                    <form id="orderForm">
                        <div class="form-group">
                            <label>📱 Which number did you pay to? *</label>
                            <select id="momo-number" required style="
                                width:100%;padding:14px 16px;border:3px solid #fce4ec;
                                border-radius:14px;font-size:14px;font-weight:600;
                                outline:none;font-family:'Nunito';background:#fffbfc;
                            ">
                                <option value="">Select number...</option>
                                <option value="0550618807 - Sandra Nkrumah">
                                    0550618807 - Sandra Nkrumah
                                </option>
                                <option value="0540882629 - Milicent Nkrumah">
                                    0540882629 - Milicent Nkrumah
                                </option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>🔢 Transaction ID / Reference Number *</label>
                            <input
                                type="text"
                                id="transaction-id"
                                placeholder="e.g. 1234567890"
                                required
                            />
                            <small style="color:#aaa;font-size:12px;font-weight:700;">
                                Find this in your MoMo SMS after payment
                            </small>
                        </div>

                        <button type="submit" class="modal-btn green">
                            ✅ I Have Paid - Place Order
                        </button>

                        <button type="button"
                            onclick="backToDelivery()"
                            style="
                                width:100%;padding:12px;background:none;
                                border:3px solid #fce4ec;border-radius:16px;
                                font-size:15px;font-weight:800;cursor:pointer;
                                color:#888;margin-top:10px;font-family:'Nunito';
                            ">
                            ← Back
                        </button>
                    </form>
                </div>

            </div>
        </div>
    </div>'''

html = html.replace(old_order_modal, new_order_modal)
print("  ✅ Updated order modal with payment steps")

# Update openCheckout function
old_checkout = '''        function openCheckout() {
            if (cart.length === 0) { showToast('❌ Cart is empty!', 'error'); return; }
            if (!currentUser) { showToast('❌ Please login first!', 'error'); closeCart(); openAuthModal('login'); return; }

            const sd = document.getElementById('order-summary-items');
            const tp = cart.reduce((s, i) => s + (i.price * i.quantity), 0);
            sd.innerHTML = cart.map(i => `<div class="order-summary-item"><span>${i.name} x${i.quantity}</span><span>$${(i.price * i.quantity).toFixed(2)}</span></div>`).join('');
            document.getElementById('order-summary-total').textContent = '$' + tp.toFixed(2);

            document.getElementById('cust-name').value = currentUser.fullname;
            document.getElementById('cust-phone').value = currentUser.phone;
            document.getElementById('cust-address').value = currentUser.address;

            closeCart();
            document.getElementById('orderModal').classList.add('show');
        }
        function closeOrderModal() { document.getElementById('orderModal').classList.remove('show'); }'''

new_checkout = '''        function openCheckout() {
            if (cart.length === 0) { showToast('❌ Cart is empty!', 'error'); return; }
            if (!currentUser) { showToast('❌ Please login first!', 'error'); closeCart(); openAuthModal('login'); return; }

            const sd = document.getElementById('order-summary-items');
            const tp = cart.reduce((s, i) => s + (i.price * i.quantity), 0);
            sd.innerHTML = cart.map(i => `
                <div class="order-summary-item">
                    <span>${i.name} x${i.quantity}</span>
                    <span>GH₵ ${(i.price * i.quantity).toFixed(2)}</span>
                </div>`).join('');

            document.getElementById('order-summary-total').textContent = 'GH₵ ' + tp.toFixed(2);
            document.getElementById('amount-to-pay').textContent = 'Amount: GH₵ ' + tp.toFixed(2);

            document.getElementById('cust-name').value    = currentUser.fullname;
            document.getElementById('cust-phone').value   = currentUser.phone;
            document.getElementById('cust-address').value = currentUser.address;

            // Show step 1 first
            document.getElementById('step-1').style.display = 'block';
            document.getElementById('step-2').style.display = 'none';

            closeCart();
            document.getElementById('orderModal').classList.add('show');
        }

        function closeOrderModal() {
            document.getElementById('orderModal').classList.remove('show');
            // Reset to step 1
            document.getElementById('step-1').style.display = 'block';
            document.getElementById('step-2').style.display = 'none';
        }

        function goToPayment() {
            const name    = document.getElementById('cust-name').value;
            const phone   = document.getElementById('cust-phone').value;
            const address = document.getElementById('cust-address').value;

            if (!name || !phone || !address) {
                showToast('❌ Please fill all delivery details!', 'error');
                return;
            }

            // Go to payment step
            document.getElementById('step-1').style.display = 'none';
            document.getElementById('step-2').style.display = 'block';
        }

        function backToDelivery() {
            document.getElementById('step-1').style.display = 'block';
            document.getElementById('step-2').style.display = 'none';
        }'''

html = html.replace(old_checkout, new_checkout)
print("  ✅ Updated checkout flow with payment steps")

# Update place order form submission
old_submit = '''        document.getElementById('orderForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            const tp = cart.reduce((s, i) => s + (i.price * i.quantity), 0);
            try {
                const r = await fetch('/api/orders/place', { method: 'POST', headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        customer_name: document.getElementById('cust-name').value,
                        customer_phone: document.getElementById('cust-phone').value,
                        customer_address: document.getElementById('cust-address').value,
                        items: cart.map(i => ({ id: i.id, name: i.name, price: i.price, quantity: i.quantity })),
                        total_price: tp
                    }) });
                const d = await r.json();
                if (d.success) {
                    closeOrderModal();
                    document.getElementById('success-order-id').textContent = 'Order #' + d.order_id;
                    document.getElementById('successModal').classList.add('show');
                    cart = []; updateCartUI(); this.reset();
                }
                else if (d.need_login) { showToast('❌ Please login first!', 'error'); closeOrderModal(); openAuthModal('login'); }
                else showToast('❌ ' + d.message, 'error');
            } catch (ex) { showToast('❌ Error!', 'error'); }
        });'''

new_submit = '''        document.getElementById('orderForm').addEventListener('submit', async function(e) {
            e.preventDefault();

            const transactionId = document.getElementById('transaction-id').value.trim();
            const momoNumber    = document.getElementById('momo-number').value;

            if (!transactionId) {
                showToast('❌ Please enter your Transaction ID!', 'error');
                return;
            }

            if (!momoNumber) {
                showToast('❌ Please select which number you paid to!', 'error');
                return;
            }

            const tp = cart.reduce((s, i) => s + (i.price * i.quantity), 0);

            try {
                const r = await fetch('/api/orders/place', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        customer_name:    document.getElementById('cust-name').value,
                        customer_phone:   document.getElementById('cust-phone').value,
                        customer_address: document.getElementById('cust-address').value,
                        items:            cart.map(i => ({
                            id:       i.id,
                            name:     i.name,
                            price:    i.price,
                            quantity: i.quantity
                        })),
                        total_price:    tp,
                        transaction_id: transactionId,
                        momo_number:    momoNumber
                    })
                });

                const d = await r.json();

                if (d.success) {
                    closeOrderModal();
                    document.getElementById('success-order-id').textContent = 'Order #' + d.order_id;
                    document.getElementById('successModal').classList.add('show');
                    cart = [];
                    updateCartUI();
                    this.reset();
                }
                else if (d.need_login) {
                    showToast('❌ Please login first!', 'error');
                    closeOrderModal();
                    openAuthModal('login');
                }
                else {
                    showToast('❌ ' + d.message, 'error');
                }
            } catch (ex) {
                showToast('❌ Something went wrong!', 'error');
            }
        });'''

html = html.replace(old_submit, new_submit)
print("  ✅ Updated order form submission with payment details")

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("  ✅ index.html saved!")
print("")

# ==============================
# UPDATE admin.html
# ==============================
print("  Updating admin.html...")

with open('templates/admin.html', 'r', encoding='utf-8') as f:
    admin = f.read()

# Update orders table header to include payment columns
old_orders_header = '''                        <thead>
                            <tr>
                                <th>#ID</th><th>Customer</th><th>Phone</th><th>Address</th>
                                <th>Items</th><th>Total</th><th>Status</th><th>Date</th><th>Action</th>
                            </tr>
                        </thead>'''

new_orders_header = '''                        <thead>
                            <tr>
                                <th>#ID</th><th>Customer</th><th>Phone</th><th>Address</th>
                                <th>Items</th><th>Total</th><th>Paid To</th>
                                <th>Trans ID</th><th>Status</th><th>Date</th><th>Action</th>
                            </tr>
                        </thead>'''

admin = admin.replace(old_orders_header, new_orders_header)
print("  ✅ Updated orders table header")

# Update loadOrders function to show payment info
old_load_orders = '''                tbody.innerHTML = allOrders.map(o => `
                    <tr>
                        <td>#${o.id}</td><td>${o.customer_name}</td><td>${o.customer_phone}</td>
                        <td>${o.customer_address}</td><td>${formatItems(o.items)}</td>
                        <td>$${o.total_price.toFixed(2)}</td>
                        <td><span class="status-badge ${o.status.toLowerCase()}">${o.status}</span></td>
                        <td>${o.date_ordered}</td>
                        <td><select class="status-select" onchange="updateStatus(${o.id}, this.value)">
                            <option ${o.status === 'Pending' ? 'selected' : ''}>Pending</option>
                            <option ${o.status === 'Confirmed' ? 'selected' : ''}>Confirmed</option>
                            <option ${o.status === 'Delivered' ? 'selected' : ''}>Delivered</option>
                            <option ${o.status === 'Cancelled' ? 'selected' : ''}>Cancelled</option>
                        </select></td>
                    </tr>
                `).join('');'''

new_load_orders = '''                tbody.innerHTML = allOrders.map(o => `
                    <tr>
                        <td>#${o.id}</td>
                        <td>${o.customer_name}</td>
                        <td>${o.customer_phone}</td>
                        <td>${o.customer_address}</td>
                        <td>${formatItems(o.items)}</td>
                        <td style="font-family:'Fredoka One';color:#e91e63;">
                            GH₵ ${o.total_price.toFixed(2)}
                        </td>
                        <td>
                            <span style="font-size:12px;font-weight:700;color:#555;">
                                ${o.momo_number || 'N/A'}
                            </span>
                        </td>
                        <td>
                            <span style="
                                background:#e8f5e9;color:#43a047;
                                padding:4px 10px;border-radius:20px;
                                font-size:12px;font-weight:800;
                            ">
                                ${o.transaction_id || 'N/A'}
                            </span>
                        </td>
                        <td>
                            <span class="status-badge ${o.status.toLowerCase()}">
                                ${o.status}
                            </span>
                        </td>
                        <td>${o.date_ordered}</td>
                        <td>
                            <select class="status-select" onchange="updateStatus(${o.id}, this.value)">
                                <option ${o.status === 'Pending'   ? 'selected' : ''}>Pending</option>
                                <option ${o.status === 'Confirmed' ? 'selected' : ''}>Confirmed</option>
                                <option ${o.status === 'Delivered' ? 'selected' : ''}>Delivered</option>
                                <option ${o.status === 'Cancelled' ? 'selected' : ''}>Cancelled</option>
                            </select>
                        </td>
                    </tr>
                `).join('');'''

admin = admin.replace(old_load_orders, new_load_orders)
print("  ✅ Updated orders table to show payment info")

# Update recent orders on dashboard too
old_recent = '''                    otb.innerHTML = recentOrders.map(o => `
                        <tr><td>#${o.id}</td><td>${o.customer_name}</td>
                        <td>$${o.total_price.toFixed(2)}</td>
                        <td><span class="status-badge ${o.status.toLowerCase()}">${o.status}</span></td></tr>
                    `).join('');'''

new_recent = '''                    otb.innerHTML = recentOrders.map(o => `
                        <tr>
                            <td>#${o.id}</td>
                            <td>${o.customer_name}</td>
                            <td style="font-family:'Fredoka One';color:#e91e63;">
                                GH₵ ${o.total_price.toFixed(2)}
                            </td>
                            <td>
                                <span style="background:#e8f5e9;color:#43a047;padding:4px 10px;border-radius:20px;font-size:11px;font-weight:800;">
                                    ${o.transaction_id || 'N/A'}
                                </span>
                            </td>
                            <td><span class="status-badge ${o.status.toLowerCase()}">${o.status}</span></td>
                        </tr>
                    `).join('');'''

admin = admin.replace(old_recent, new_recent)
print("  ✅ Updated dashboard recent orders")

# Update recent orders table header on dashboard
old_dash_header = '''                            <thead><tr><th>#</th><th>Customer</th><th>Total</th><th>Status</th></tr></thead>'''
new_dash_header = '''                            <thead><tr><th>#</th><th>Customer</th><th>Total</th><th>Trans ID</th><th>Status</th></tr></thead>'''

admin = admin.replace(old_dash_header, new_dash_header)
print("  ✅ Updated dashboard table header")

with open('templates/admin.html', 'w', encoding='utf-8') as f:
    f.write(admin)

print("  ✅ admin.html saved!")
print("")

# ==============================
# PUSH TO GITHUB
# ==============================
print("  Pushing to GitHub...")
print("")

os.system('git add .')
os.system('git commit -m "Added MTN MoMo payment system"')
os.system('git push')

print("")
print("  ========================================")
print("  ALL DONE!")
print("  ✅ app.py    - Payment fields added")
print("  ✅ index.html - MoMo payment steps added")
print("  ✅ admin.html - Transaction ID column added")
print("")
print("  Payment Numbers Added:")
print("  📱 0550618807 - Sandra Nkrumah")
print("  📱 0540882629 - Milicent Nkrumah")
print("")
print("  Render will update in 2-3 minutes!")
print("  ========================================")
print("")