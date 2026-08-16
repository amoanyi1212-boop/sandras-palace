import os

print("")
print("  ========================================")
print("  Complete Archive Fix")
print("  ========================================")
print("")

# ==============================
# FIX app.py
# ==============================
print("  Fixing app.py...")

with open('app.py', 'r', encoding='utf-8') as f:
    app = f.read()

# 1. Make sure archive column exists in create_tables
if 'is_archived' not in app.split('create_tables')[1] if 'create_tables' in app else '':
    old_stock_cols = '''                    # Add stock columns to items table'''
    new_archive_col = '''                    # Add archive column to orders
                    try:
                        conn.execute(db.text(
                            "ALTER TABLE orders ADD COLUMN IF NOT EXISTS "
                            "is_archived BOOLEAN DEFAULT FALSE"
                        ))
                        conn.commit()
                    except Exception:
                        try:
                            conn.execute(db.text(
                                "ALTER TABLE orders ADD COLUMN "
                                "is_archived BOOLEAN DEFAULT FALSE"
                            ))
                            conn.commit()
                        except Exception:
                            pass

                    # Add stock columns to items table'''
    app = app.replace(old_stock_cols, new_archive_col)
    print("  ✅ Added is_archived column to create_tables")

# 2. Replace entire get_orders route
old_get_orders_start = '''@app.route("/api/orders", methods=["GET"])
def get_orders():
    if not session.get("admin_logged_in"):
        return jsonify([])
    try:'''

# Find and replace the whole get_orders function
import re

# Remove old get_orders completely
app = re.sub(
    r'@app\.route\("/api/orders", methods=\["GET"\]\)\ndef get_orders\(\):.*?(?=@app\.route)',
    '',
    app,
    flags=re.DOTALL
)

# Find where to insert new get_orders (before orders/status route)
old_status_route = '@app.route("/api/orders/status/'

new_get_orders = '''@app.route("/api/orders", methods=["GET"])
def get_orders():
    if not session.get("admin_logged_in"):
        return jsonify([])
    try:
        show = request.args.get("show", "active")

        if show == "archived":
            where = "WHERE COALESCE(is_archived, FALSE) = TRUE"
        elif show == "all":
            where = ""
        else:
            where = "WHERE COALESCE(is_archived, FALSE) = FALSE"

        query = """
            SELECT id, customer_name, customer_phone,
                   customer_address, items, total_price,
                   status, payment_status, transaction_id,
                   momo_number, date_ordered, delivered_at, user_id
            FROM orders
            """ + where + """
            ORDER BY date_ordered DESC
        """

        with db.engine.connect() as conn:
            rows = conn.execute(db.text(query)).fetchall()

        result = []
        for o in rows:
            try:
                result.append({
                    "id":               o[0],
                    "customer_name":    o[1]  or "",
                    "customer_phone":   o[2]  or "",
                    "customer_address": o[3]  or "",
                    "items":            o[4]  or "",
                    "total_price":      float(o[5]) if o[5] else 0,
                    "status":           o[6]  or "Pending",
                    "payment_status":   o[7]  or "Paid",
                    "transaction_id":   o[8]  or "",
                    "momo_number":      o[9]  or "",
                    "date_ordered":     str(o[10])[:16] if o[10] else "",
                    "delivered_at":     str(o[11])[:16] if o[11] else "",
                    "user_id":          o[12] or 0
                })
            except Exception as oe:
                print("Order row error:", oe)
                continue
        return jsonify(result)
    except Exception as e:
        print("Get orders error:", e)
        return jsonify([])

'''

app = app.replace(old_status_route, new_get_orders + old_status_route)
print("  ✅ Replaced get_orders with archive filter")

# 3. Add/replace archive routes
# First remove old archive routes if they exist
app = re.sub(
    r'# ={20,}\n# ARCHIVE ORDERS\n# ={20,}\n.*?(?=# ={20,}\n# DEBUG)',
    '',
    app,
    flags=re.DOTALL
)

old_debug = '''# ==============================
# DEBUG ROUTES
# =============================='''

new_archive_routes = '''# ==============================
# ARCHIVE ORDERS
# ==============================

@app.route("/api/orders/archive/<int:order_id>", methods=["POST"])
def archive_order(order_id):
    """Archive a single completed order"""
    if not session.get("admin_logged_in"):
        return jsonify({"success": False}), 401
    try:
        # Only allow archiving completed orders
        with db.engine.connect() as conn:
            order = conn.execute(db.text(
                "SELECT status FROM orders WHERE id = :id"
            ), {"id": order_id}).fetchone()

            if not order:
                return jsonify({"success": False, "message": "Order not found!"}), 404

            archivable = ["Delivered", "Cancelled", "Refunded", "Dispute Rejected"]
            if order[0] not in archivable:
                return jsonify({
                    "success": False,
                    "message": "Can only archive completed orders! Status: " + order[0]
                }), 400

            conn.execute(db.text(
                "UPDATE orders SET is_archived = TRUE WHERE id = :id"
            ), {"id": order_id})
            conn.commit()

        return jsonify({"success": True, "message": "Order archived!"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/orders/unarchive/<int:order_id>", methods=["POST"])
def unarchive_order(order_id):
    """Restore an archived order"""
    if not session.get("admin_logged_in"):
        return jsonify({"success": False}), 401
    try:
        with db.engine.connect() as conn:
            conn.execute(db.text(
                "UPDATE orders SET is_archived = FALSE WHERE id = :id"
            ), {"id": order_id})
            conn.commit()
        return jsonify({"success": True, "message": "Order restored!"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/orders/archive-completed", methods=["POST"])
def archive_all_completed():
    """Archive all completed orders at once"""
    if not session.get("admin_logged_in"):
        return jsonify({"success": False}), 401
    try:
        with db.engine.connect() as conn:
            # Only archive truly completed orders
            # Delivered = customer confirmed receipt
            # Cancelled = admin cancelled
            # Refunded = admin approved refund
            # Dispute Rejected = admin rejected dispute
            # NOT Awaiting Delivery = customer hasn't confirmed yet
            result = conn.execute(db.text(
                "UPDATE orders SET is_archived = TRUE "
                "WHERE status IN ('Delivered', 'Cancelled', 'Refunded', 'Dispute Rejected') "
                "AND COALESCE(is_archived, FALSE) = FALSE"
            ))
            conn.commit()
            count = result.rowcount
        return jsonify({
            "success": True,
            "message": str(count) + " orders archived!"
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# ==============================
# DEBUG ROUTES
# =============================='''

app = app.replace(old_debug, new_archive_routes)
print("  ✅ Added clean archive routes")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(app)

print("  ✅ app.py saved!")
print("")

# ==============================
# FIX admin.html
# ==============================
print("  Fixing admin.html...")

with open('templates/admin.html', 'r', encoding='utf-8') as f:
    admin = f.read()

# 1. Replace orders section header
old_orders_header = admin.split('🛒')[1].split('</div>')[0] if '🛒' in admin else ''

# Just find and replace the card-header for orders
# Use a more reliable approach
import re

# Replace the orders card header
admin = re.sub(
    r'(<div class="card-header">)\s*<h2>🛒[^<]*</h2>.*?</div>',
    '''<div class="card-header">
                <h2 id="orders-title">🛒 Active Orders</h2>
                <div style="display:flex;gap:6px;flex-wrap:wrap;align-items:center">
                    <button class="btn btn-sm" id="btn-active" onclick="loadOrders('active')" style="background:linear-gradient(135deg,#e91e63,#ff6f00);color:white;padding:6px 14px;font-size:12px">📋 Active</button>
                    <button class="btn btn-sm" id="btn-archived" onclick="loadOrders('archived')" style="background:#fce4ec;color:#c2185b;padding:6px 14px;font-size:12px">📦 Archived</button>
                    <button class="btn btn-sm" id="btn-all" onclick="loadOrders('all')" style="background:#fce4ec;color:#c2185b;padding:6px 14px;font-size:12px">🗂️ All</button>
                    <button class="btn btn-warning btn-sm" onclick="archiveAllDone()" style="padding:6px 14px;font-size:12px">📦 Archive Done</button>
                    <button class="btn btn-primary btn-sm" onclick="loadOrders()" style="padding:6px 14px;font-size:12px">🔄</button>
                </div>
            </div>''',
    admin,
    count=1,
    flags=re.DOTALL
)
print("  ✅ Replaced orders header")

# 2. Replace loadOrders function completely
old_load = '''function loadOrders(){
    fetch('/api/orders')'''

# Check if already modified
if 'currentOrderView' in admin:
    # Already has archive code, replace it
    admin = re.sub(
        r'var currentOrderView.*?function loadOrders\([^)]*\)\{[^}]*fetch\(\'/api/orders',
        '''var currentOV='active';

function loadOrders(view){
    if(view)currentOV=view;else view=currentOV;
    var btns={active:document.getElementById('btn-active'),archived:document.getElementById('btn-archived'),all:document.getElementById('btn-all')};
    for(var k in btns){if(btns[k]){btns[k].style.background=k===view?'linear-gradient(135deg,#e91e63,#ff6f00)':'#fce4ec';btns[k].style.color=k===view?'white':'#c2185b'}}
    var titles={active:'🛒 Active Orders',archived:'📦 Archived Orders',all:'🗂️ All Orders'};
    var t=document.getElementById('orders-title');if(t)t.textContent=titles[view]||'🛒 Orders';
    fetch('/api/orders?show='+view''',
        admin,
        flags=re.DOTALL
    )
else:
    admin = admin.replace(old_load,
        '''var currentOV='active';

function loadOrders(view){
    if(view)currentOV=view;else view=currentOV;
    var btns={active:document.getElementById('btn-active'),archived:document.getElementById('btn-archived'),all:document.getElementById('btn-all')};
    for(var k in btns){if(btns[k]){btns[k].style.background=k===view?'linear-gradient(135deg,#e91e63,#ff6f00)':'#fce4ec';btns[k].style.color=k===view?'white':'#c2185b'}}
    var titles={active:'🛒 Active Orders',archived:'📦 Archived Orders',all:'🗂️ All Orders'};
    var t=document.getElementById('orders-title');if(t)t.textContent=titles[view]||'🛒 Orders';
    fetch('/api/orders?show='+view''')

print("  ✅ Updated loadOrders with filter")

# 3. Update getActions to show archive/restore buttons
old_actions_fn = '''function getActions(o){'''

new_actions_fn = '''function getActions(o){
    // Archived view - show restore button
    if(currentOV==='archived'){
        return'<button class="btn btn-sm btn-info" onclick="unarchiveOrd('+o.id+')" style="padding:4px 10px;font-size:11px">📤 Restore</button>';
    }
'''

# Only replace if not already modified
if 'currentOV===\'archived\'' not in admin:
    admin = admin.replace(old_actions_fn, new_actions_fn)
    print("  ✅ Updated getActions for archive view")
else:
    print("  ✅ getActions already has archive support")

# 4. Add archive buttons to completed statuses
# Delivered
old_del = "if(o.status==='Delivered')return'"
if '📦' not in admin.split("Delivered')return'")[1].split(';')[0] if "Delivered')return'" in admin else '':
    admin = admin.replace(
        "if(o.status==='Delivered')return'<span style=\"color:#43a047;font-weight:800;font-size:12px\">✅ Complete</span>'",
        "if(o.status==='Delivered')return'<span style=\"color:#43a047;font-weight:800;font-size:12px\">✅ Complete</span> <button class=\"btn btn-sm\" onclick=\"archiveOrd('+o.id+')\" style=\"background:#fce4ec;color:#c2185b;padding:4px 8px;font-size:10px\">📦</button>'"
    )

# Cancelled
if "Cancelled')return'" in admin and '📦' not in admin.split("Cancelled')return'")[1].split(';')[0]:
    admin = admin.replace(
        "if(o.status==='Cancelled')return'<span style=\"color:#e53935;font-weight:800;font-size:12px\">❌ Cancelled</span>'",
        "if(o.status==='Cancelled')return'<span style=\"color:#e53935;font-weight:800;font-size:12px\">❌ Cancelled</span> <button class=\"btn btn-sm\" onclick=\"archiveOrd('+o.id+')\" style=\"background:#fce4ec;color:#c2185b;padding:4px 8px;font-size:10px\">📦</button>'"
    )

# Refunded
if "Refunded')return'" in admin and '📦' not in admin.split("Refunded')return'")[1].split(';')[0]:
    admin = admin.replace(
        "if(o.status==='Refunded')return'<span style=\"color:#2e7d32;font-weight:800;font-size:12px\">💰 Refunded</span>'",
        "if(o.status==='Refunded')return'<span style=\"color:#2e7d32;font-weight:800;font-size:12px\">💰 Refunded</span> <button class=\"btn btn-sm\" onclick=\"archiveOrd('+o.id+')\" style=\"background:#fce4ec;color:#c2185b;padding:4px 8px;font-size:10px\">📦</button>'"
    )

# Rejected
if "Rejected')return'" in admin and '📦' not in admin.split("Rejected')return'")[1].split(';')[0]:
    admin = admin.replace(
        "if(o.status==='Dispute Rejected')return'<span style=\"color:#c62828;font-weight:800;font-size:12px\">❌ Rejected</span>'",
        "if(o.status==='Dispute Rejected')return'<span style=\"color:#c62828;font-weight:800;font-size:12px\">❌ Rejected</span> <button class=\"btn btn-sm\" onclick=\"archiveOrd('+o.id+')\" style=\"background:#fce4ec;color:#c2185b;padding:4px 8px;font-size:10px\">📦</button>'"
    )

print("  ✅ Added archive buttons to completed orders")

# 5. Add archive functions - remove old ones first if they exist
admin = admin.replace('// ARCHIVE\n', '')
admin = re.sub(r'function archiveOrder\(.*?\}', '', admin, flags=re.DOTALL)
admin = re.sub(r'function unarchiveOrder\(.*?\}', '', admin, flags=re.DOTALL)
admin = re.sub(r'function archiveAllCompleted\(.*?\}', '', admin, flags=re.DOTALL)

old_toast = "function toast(m,t)"

new_archive_js = '''// ARCHIVE FUNCTIONS
function archiveOrd(id){
    if(!confirm('Archive this order?'))return;
    fetch('/api/orders/archive/'+id,{method:'POST'})
    .then(function(r){return r.json()})
    .then(function(d){
        if(d.success){toast('📦 '+d.message,'success');loadOrders()}
        else toast(d.message||'Error!','error');
    }).catch(function(){toast('Error!','error')});
}

function unarchiveOrd(id){
    fetch('/api/orders/unarchive/'+id,{method:'POST'})
    .then(function(r){return r.json()})
    .then(function(d){
        if(d.success){toast('📤 '+d.message,'success');loadOrders()}
        else toast(d.message||'Error!','error');
    }).catch(function(){toast('Error!','error')});
}

function archiveAllDone(){
    if(!confirm('Archive all completed orders?\\n\\nThis includes:\\n✅ Delivered (customer confirmed)\\n❌ Cancelled\\n💰 Refunded\\n❌ Dispute Rejected\\n\\nNOT: Awaiting Delivery'))return;
    fetch('/api/orders/archive-completed',{method:'POST'})
    .then(function(r){return r.json()})
    .then(function(d){
        if(d.success){toast('📦 '+d.message,'success');loadOrders()}
        else toast(d.message||'Error!','error');
    }).catch(function(){toast('Error!','error')});
}

function toast(m,t)'''

admin = admin.replace(old_toast, new_archive_js)
print("  ✅ Added clean archive JavaScript")

with open('templates/admin.html', 'w', encoding='utf-8') as f:
    f.write(admin)

print("  ✅ admin.html saved!")
print("")

# ==============================
# PUSH
# ==============================
print("  Pushing to GitHub...")
os.system('git add .')
os.system('git commit -m "Complete archive feature - only confirmed deliveries"')
os.system('git push')

print("")
print("  ========================================")
print("  ARCHIVE FEATURE COMPLETE!")
print("")
print("  Orders Page Now Has:")
print("  📋 Active  - Pending, Confirmed, Awaiting")
print("  📦 Archived - Completed orders")
print("  🗂️ All     - Everything")
print("")
print("  Can Be Archived:")
print("  ✅ Delivered (customer confirmed)")
print("  ❌ Cancelled")
print("  💰 Refunded")
print("  ❌ Dispute Rejected")
print("")
print("  Cannot Be Archived:")
print("  📋 Pending")
print("  ✅ Confirmed")
print("  📦 Awaiting Delivery")
print("  ⚠️ Disputed")
print("")
print("  Bulk Archive:")
print("  Click 'Archive Done' to archive")
print("  all completed orders at once!")
print("")
print("  Restore:")
print("  Click 📤 Restore in archived view")
print("  to bring order back to active!")
print("")
print("  Render updates in 2-3 minutes!")
print("  ========================================")
print("")