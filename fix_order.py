import os

print("")
print("  ========================================")
print("  Fixing Place Order Button")
print("  ========================================")
print("")

with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ==============================
# REPLACE ENTIRE ORDER MODAL
# ==============================
print("  Replacing order modal...")

# Find and remove old order modal
import re

# Remove old order modal completely
html = re.sub(
    r'<!-- ORDER MODAL -->.*?</div>\s*\n\s*<!-- SUCCESS MODAL -->',
    '<!-- SUCCESS MODAL -->',
    html,
    flags=re.DOTALL
)

# Insert new clean order modal before success modal
new_modal = '''    <!-- ORDER MODAL -->
    <div class="modal-overlay" id="orderModal">
        <div class="modal">
            <div class="modal-header">
                <h2 id="order-modal-title">📋 Delivery Details</h2>
                <button class="modal-close" onclick="closeOrderModal()">✕</button>
            </div>
            <div class="modal-body">

                <!-- ORDER SUMMARY -->
                <div class="order-summary">
                    <h3>🛒 Your Order</h3>
                    <div id="order-summary-items"></div>
                    <div class="order-summary-total">
                        <span>Total</span>
                        <span id="order-summary-total">GH₵ 0.00</span>
                    </div>
                </div>

                <!-- STEP 1: DELIVERY -->
                <div id="step-delivery">
                    <div class="form-group">
                        <label>👤 Full Name</label>
                        <input type="text" id="cust-name" placeholder="Your full name" />
                    </div>
                    <div class="form-group">
                        <label>📱 Phone Number</label>
                        <input type="tel" id="cust-phone" placeholder="Your phone number" />
                    </div>
                    <div class="form-group">
                        <label>📍 Delivery Address</label>
                        <textarea id="cust-address" placeholder="Your delivery address"></textarea>
                    </div>
                    <button class="modal-btn" onclick="goToPayment()">
                        💳 Next: Make Payment
                    </button>
                </div>

                <!-- STEP 2: PAYMENT -->
                <div id="step-payment" style="display:none">

                    <!-- MoMo Box -->
                    <div style="
                        background:linear-gradient(135deg,#fff8e1,#fff3cd);
                        border:3px solid #f9a825;
                        border-radius:18px;
                        padding:20px;
                        margin-bottom:20px;
                        text-align:center;
                    ">
                        <div style="font-size:35px;margin-bottom:8px;">📱</div>
                        <h3 style="
                            font-family:'Fredoka One',cursive;
                            color:#f57f17;
                            font-size:17px;
                            margin-bottom:15px;
                        ">
                            Send MTN Mobile Money To:
                        </h3>

                        <!-- Account 1 -->
                        <div style="
                            background:white;border-radius:12px;
                            padding:12px 15px;margin-bottom:10px;
                            border:2px solid #fce4ec;
                        ">
                            <div style="
                                font-size:20px;font-weight:800;
                                color:#e91e63;font-family:'Fredoka One',cursive;
                            ">0550618807</div>
                            <div style="color:#888;font-size:13px;font-weight:700;margin-top:3px;">
                                👤 Sandra Nkrumah
                            </div>
                        </div>

                        <!-- Account 2 -->
                        <div style="
                            background:white;border-radius:12px;
                            padding:12px 15px;margin-bottom:15px;
                            border:2px solid #fce4ec;
                        ">
                            <div style="
                                font-size:20px;font-weight:800;
                                color:#e91e63;font-family:'Fredoka One',cursive;
                            ">0540882629</div>
                            <div style="color:#888;font-size:13px;font-weight:700;margin-top:3px;">
                                👤 Milicent Nkrumah
                            </div>
                        </div>

                        <!-- Amount -->
                        <div id="amount-display" style="
                            background:linear-gradient(135deg,#e91e63,#ff6f00);
                            color:white;border-radius:12px;
                            padding:12px 20px;
                            font-family:'Fredoka One',cursive;
                            font-size:20px;
                        ">
                            Amount: GH₵ 0.00
                        </div>
                    </div>

                    <!-- Transaction Form -->
                    <div class="form-group">
                        <label>📱 Which number did you pay to? *</label>
                        <select id="momo-number" style="
                            width:100%;padding:14px 16px;
                            border:3px solid #fce4ec;border-radius:14px;
                            font-size:14px;font-weight:600;outline:none;
                            font-family:'Nunito',sans-serif;background:#fffbfc;
                            cursor:pointer;
                        ">
                            <option value="">-- Select number --</option>
                            <option value="0550618807 - Sandra Nkrumah">
                                0550618807 - Sandra Nkrumah
                            </option>
                            <option value="0540882629 - Milicent Nkrumah">
                                0540882629 - Milicent Nkrumah
                            </option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label>🔢 Transaction ID *</label>
                        <input
                            type="text"
                            id="transaction-id"
                            placeholder="e.g. 1234567890"
                        />
                        <small style="color:#aaa;font-size:12px;font-weight:700;display:block;margin-top:5px;">
                            📩 Find this in your MoMo SMS after payment
                        </small>
                    </div>

                    <!-- Buttons -->
                    <button
                        class="modal-btn green"
                        onclick="submitOrder()"
                        id="place-order-btn"
                    >
                        ✅ I Have Paid - Place Order
                    </button>

                    <button
                        onclick="backToDelivery()"
                        style="
                            width:100%;padding:13px;background:none;
                            border:3px solid #fce4ec;border-radius:16px;
                            font-size:15px;font-weight:800;cursor:pointer;
                            color:#aaa;margin-top:10px;font-family:'Nunito';
                        "
                    >
                        ← Back to Delivery Details
                    </button>
                </div>

            </div>
        </div>
    </div>

    <!-- SUCCESS MODAL -->'''

html = html.replace('<!-- SUCCESS MODAL -->', new_modal)
print("  ✅ Order modal replaced!")

# ==============================
# REPLACE ORDER JAVASCRIPT
# ==============================
print("  Replacing order JavaScript...")

# Remove old checkout/order functions
html = re.sub(
    r'// === CHECKOUT ===.*?document\.getElementById\(\'myOrdersModal\'\)\.addEventListener',
    '// === CHECKOUT ===\n\n        // CHECKOUT FUNCTIONS\n\n        document.getElementById(\'myOrdersModal\').addEventListener',
    html,
    flags=re.DOTALL
)

# Add new clean checkout functions before closing script tag
new_js = '''
        // ===========================
        // CHECKOUT FUNCTIONS
        // ===========================

        function openCheckout() {
            if (cart.length === 0) {
                showToast('❌ Your cart is empty!', 'error');
                return;
            }
            if (!currentUser) {
                showToast('❌ Please login first!', 'error');
                closeCart();
                openAuthModal('login');
                return;
            }

            // Fill order summary
            const tp = cart.reduce((s, i) => s + (i.price * i.quantity), 0);

            document.getElementById('order-summary-items').innerHTML = cart.map(i => `
                <div class="order-summary-item">
                    <span>${i.name} x${i.quantity}</span>
                    <span>GH₵ ${(i.price * i.quantity).toFixed(2)}</span>
                </div>
            `).join('');

            document.getElementById('order-summary-total').textContent = 'GH₵ ' + tp.toFixed(2);
            document.getElementById('amount-display').textContent      = 'Amount: GH₵ ' + tp.toFixed(2);

            // Pre-fill delivery details
            document.getElementById('cust-name').value    = currentUser.fullname  || '';
            document.getElementById('cust-phone').value   = currentUser.phone     || '';
            document.getElementById('cust-address').value = currentUser.address   || '';

            // Reset to step 1
            document.getElementById('step-delivery').style.display = 'block';
            document.getElementById('step-payment').style.display  = 'none';
            document.getElementById('order-modal-title').textContent = '📋 Delivery Details';

            // Show modal
            closeCart();
            document.getElementById('orderModal').classList.add('show');
        }

        function closeOrderModal() {
            document.getElementById('orderModal').classList.remove('show');
        }

        function goToPayment() {
            const name    = document.getElementById('cust-name').value.trim();
            const phone   = document.getElementById('cust-phone').value.trim();
            const address = document.getElementById('cust-address').value.trim();

            if (!name) {
                showToast('❌ Please enter your name!', 'error');
                return;
            }
            if (!phone) {
                showToast('❌ Please enter your phone number!', 'error');
                return;
            }
            if (!address) {
                showToast('❌ Please enter your delivery address!', 'error');
                return;
            }

            // Go to payment step
            document.getElementById('step-delivery').style.display = 'none';
            document.getElementById('step-payment').style.display  = 'block';
            document.getElementById('order-modal-title').textContent = '💳 Make Payment';
        }

        function backToDelivery() {
            document.getElementById('step-delivery').style.display = 'block';
            document.getElementById('step-payment').style.display  = 'none';
            document.getElementById('order-modal-title').textContent = '📋 Delivery Details';
        }

        async function submitOrder() {
            const momoNumber    = document.getElementById('momo-number').value.trim();
            const transactionId = document.getElementById('transaction-id').value.trim();

            if (!momoNumber) {
                showToast('❌ Please select which number you paid to!', 'error');
                return;
            }

            if (!transactionId) {
                showToast('❌ Please enter your Transaction ID!', 'error');
                return;
            }

            // Disable button to prevent double submit
            const btn = document.getElementById('place-order-btn');
            btn.textContent = '⏳ Placing Order...';
            btn.disabled    = true;

            const tp = cart.reduce((s, i) => s + (i.price * i.quantity), 0);

            const orderData = {
                customer_name:    document.getElementById('cust-name').value.trim(),
                customer_phone:   document.getElementById('cust-phone').value.trim(),
                customer_address: document.getElementById('cust-address').value.trim(),
                items:            cart.map(i => ({
                    id:       i.id,
                    name:     i.name,
                    price:    i.price,
                    quantity: i.quantity
                })),
                total_price:    tp,
                transaction_id: transactionId,
                momo_number:    momoNumber
            };

            try {
                const response = await fetch('/api/orders/place', {
                    method:  'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body:    JSON.stringify(orderData)
                });

                const data = await response.json();

                if (data.success) {
                    // Show success
                    closeOrderModal();
                    document.getElementById('success-order-id').textContent = 'Order #' + data.order_id;
                    document.getElementById('successModal').classList.add('show');

                    // Clear cart
                    cart = [];
                    updateCartUI();

                    // Reset form
                    document.getElementById('momo-number').value    = '';
                    document.getElementById('transaction-id').value = '';

                } else if (data.need_login) {
                    showToast('❌ Please login first!', 'error');
                    closeOrderModal();
                    openAuthModal('login');

                } else {
                    showToast('❌ ' + data.message, 'error');
                }

            } catch (err) {
                console.error('Order error:', err);
                showToast('❌ Something went wrong! Please try again.', 'error');
            }

            // Re-enable button
            btn.textContent = '✅ I Have Paid - Place Order';
            btn.disabled    = false;
        }

'''

# Insert new JS before closing script tag
html = html.replace(
    '        document.getElementById(\'authModal\').addEventListener',
    new_js + '\n        document.getElementById(\'authModal\').addEventListener'
)

print("  ✅ Order JavaScript replaced!")

# Save
with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("  ✅ index.html saved!")
print("")

# Push to GitHub
print("  Pushing to GitHub...")
os.system('git add .')
os.system('git commit -m "Fixed place order button and payment flow"')
os.system('git push')

print("")
print("  ========================================")
print("  ALL DONE!")
print("")
print("  Order Flow:")
print("  1. Customer clicks Checkout")
print("  2. Fills delivery details")
print("  3. Clicks Next: Make Payment")
print("  4. Sees MoMo numbers and amount")
print("  5. Pays on their phone")
print("  6. Enters Transaction ID")
print("  7. Clicks Place Order")
print("  8. Order confirmed!")
print("")
print("  Render updates in 2-3 minutes!")
print("  ========================================")
print("")