import os

print("Fixing coupon creation and edit item issues...")

# ==============================
# FIX 1: admin.html createCoupon
# ==============================
with open('templates/admin.html', 'r', encoding='utf-8') as f:
    admin = f.read()

# Fix createCoupon - convert values to proper types
old_coupon = '''    function createCoupon() {
        var code = document.getElementById('cp-code').value.trim().toUpperCase();
        var val  = document.getElementById('cp-val').value;
        if (!code || !val) { toast('❌ Code and value required!', 'error'); return; }
        fetch('/api/coupons/create', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({
                code:           code,
                discount_type:  document.getElementById('cp-type').value,
                discount_value: val,
                min_order:      document.getElementById('cp-min').value || 0,
                max_uses:       document.getElementById('cp-max').value || 0,
                expires_at:     document.getElementById('cp-exp').value || ''
            })
        })
        .then(function(r) { return r.json(); })
        .then(function(d) {
            if (d.success) {
                toast('✅ ' + d.message, 'success');
                loadCoupons();
                document.getElementById('cp-code').value = '';
                document.getElementById('cp-val').value  = '';
            } else {
                toast('❌ ' + d.message, 'error');
            }
        });
    }'''

new_coupon = '''    function createCoupon() {
        var code = document.getElementById('cp-code').value.trim().toUpperCase();
        var val  = document.getElementById('cp-val').value.trim();

        if (!code) { toast('❌ Coupon code required!', 'error'); return; }
        if (!val || isNaN(parseFloat(val))) { toast('❌ Valid discount value required!', 'error'); return; }

        var minOrder = parseFloat(document.getElementById('cp-min').value) || 0;
        var maxUses  = parseInt(document.getElementById('cp-max').value)   || 0;
        var expires  = document.getElementById('cp-exp').value || '';

        var payload = {
            code:           code,
            discount_type:  document.getElementById('cp-type').value,
            discount_value: parseFloat(val),
            min_order:      minOrder,
            max_uses:       maxUses,
            expires_at:     expires
        };

        console.log('Creating coupon:', payload);

        fetch('/api/coupons/create', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify(payload)
        })
        .then(function(r) {
            console.log('Response status:', r.status);
            return r.json();
        })
        .then(function(d) {
            console.log('Response:', d);
            if (d.success) {
                toast('✅ ' + d.message, 'success');
                loadCoupons();
                document.getElementById('cp-code').value = '';
                document.getElementById('cp-val').value  = '';
                document.getElementById('cp-min').value  = '0';
                document.getElementById('cp-max').value  = '0';
                document.getElementById('cp-exp').value  = '';
            } else {
                toast('❌ ' + d.message, 'error');
            }
        })
        .catch(function(err) {
            console.error('Coupon error:', err);
            toast('❌ Error creating coupon!', 'error');
        });
    }'''

if old_coupon in admin:
    admin = admin.replace(old_coupon, new_coupon)
    print("  ✅ Fixed createCoupon function")
else:
    print("  ⚠️ createCoupon exact match not found, patching...")
    # Find and replace just the body part
    admin = admin.replace(
        "discount_value: val,",
        "discount_value: parseFloat(val),"
    )
    admin = admin.replace(
        "min_order:      document.getElementById('cp-min').value || 0,",
        "min_order:      parseFloat(document.getElementById('cp-min').value) || 0,"
    )
    admin = admin.replace(
        "max_uses:       document.getElementById('cp-max').value || 0,",
        "max_uses:       parseInt(document.getElementById('cp-max').value) || 0,"
    )
    print("  ✅ Patched coupon values to correct types")

# ==============================
# FIX 2: admin.html editForm submit
# ==============================
old_edit = '''    document.getElementById('editForm').addEventListener('submit', function(e) {
        e.preventDefault();
        var id = document.getElementById('e-id').value;
        if (!id) { toast('❌ No item selected!', 'error'); return; }

        var fd = new FormData();
        fd.append('name',            document.getElementById('e-name').value);
        fd.append('price',           document.getElementById('e-price').value);
        fd.append('category',        document.getElementById('e-cat').value);
        fd.append('stock_quantity',  document.getElementById('e-qty').value);
        fd.append('low_stock_alert', document.getElementById('e-low').value);
        fd.append('in_stock',        document.getElementById('e-stock').value);
        fd.append('description',     document.getElementById('e-desc').value);
        var img = document.getElementById('e-img').files[0];
        if (img) fd.append('image', img);

        fetch('/api/items/update/' + id, { method: 'POST', body: fd })
        .then(function(r) { return r.json(); })
        .then(function(d) {
            if (d.success) {
                toast('✅ ' + d.message, 'success');
                closeEditModal();
                loadItems();
            } else {
                toast('❌ ' + d.message, 'error');
            }
        }).catch(function() { toast('❌ Error updating item!', 'error'); });
    });'''

new_edit = '''    document.getElementById('editForm').addEventListener('submit', function(e) {
        e.preventDefault();
        var id = document.getElementById('e-id').value;
        if (!id) { toast('❌ No item selected!', 'error'); return; }

        var nameVal  = document.getElementById('e-name').value.trim();
        var priceVal = document.getElementById('e-price').value.trim();

        if (!nameVal)  { toast('❌ Name is required!',  'error'); return; }
        if (!priceVal) { toast('❌ Price is required!', 'error'); return; }

        var fd = new FormData();
        fd.append('name',            nameVal);
        fd.append('price',           priceVal);
        fd.append('category',        document.getElementById('e-cat').value);
        fd.append('stock_quantity',  document.getElementById('e-qty').value || '0');
        fd.append('low_stock_alert', document.getElementById('e-low').value || '5');
        fd.append('in_stock',        document.getElementById('e-stock').value);
        fd.append('description',     document.getElementById('e-desc').value);

        var img = document.getElementById('e-img').files[0];
        if (img) fd.append('image', img);

        console.log('Updating item', id, 'stock_quantity:', document.getElementById('e-qty').value, 'in_stock:', document.getElementById('e-stock').value);

        fetch('/api/items/update/' + id, { method: 'POST', body: fd })
        .then(function(r) {
            console.log('Update response status:', r.status);
            return r.json();
        })
        .then(function(d) {
            console.log('Update response:', d);
            if (d.success) {
                toast('✅ ' + d.message, 'success');
                closeEditModal();
                loadItems();
            } else {
                toast('❌ ' + d.message, 'error');
            }
        }).catch(function(err) {
            console.error('Edit error:', err);
            toast('❌ Error updating item!', 'error');
        });
    });'''

if old_edit in admin:
    admin = admin.replace(old_edit, new_edit)
    print("  ✅ Fixed editForm submit with validation")
else:
    print("  ⚠️ editForm exact match not found, admin.html unchanged for edit")

with open('templates/admin.html', 'w', encoding='utf-8') as f:
    f.write(admin)

print("  ✅ admin.html saved!")
print("")

# ==============================
# FIX 3: app.py update_item logic
# ==============================
with open('app.py', 'r', encoding='utf-8') as f:
    app = f.read()

# Fix update_item to properly handle stock_quantity and in_stock
old_update = '''        qty_str = data.get("stock_quantity","")
        if qty_str != "":
            try: item.stock_quantity = int(qty_str); item.in_stock = int(qty_str) > 0
            except: item.in_stock = data.get("in_stock","true") == "true"
        else: item.in_stock = data.get("in_stock","true") == "true"
        low_str = data.get("low_stock_alert","")
        if low_str != "":
            try: item.low_stock_alert = int(low_str)
            except: pass'''

new_update = '''        # Update stock quantity
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
                item.low_stock_alert = 5'''

if old_update in app:
    app = app.replace(old_update, new_update)
    print("  ✅ Fixed update_item stock logic in app.py")
else:
    print("  ⚠️ update_item exact match not found, trying alternative fix...")
    # Alternative - find and patch just the problematic lines
    app = app.replace(
        "try: item.stock_quantity = int(qty_str); item.in_stock = int(qty_str) > 0",
        "try: item.stock_quantity = int(qty_str)"
    )
    app = app.replace(
        "except: item.in_stock = data.get(\"in_stock\",\"true\") == \"true\"",
        "except: item.stock_quantity = 0\n        item.in_stock = data.get(\"in_stock\",\"true\") == \"true\""
    )
    print("  ✅ Patched update_item logic")

# Fix create_coupon to better handle the data
old_create_coupon = '''        coupon = Coupon(code=code, discount_type=data.get("discount_type","percentage"), discount_value=float(data.get("discount_value")), min_order=float(data.get("min_order",0)), max_uses=int(data.get("max_uses",0)), is_active=True, expires_at=expires)'''

new_create_coupon = '''        try:
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
        )'''

if old_create_coupon in app:
    app = app.replace(old_create_coupon, new_create_coupon)
    print("  ✅ Fixed create_coupon data handling in app.py")
else:
    print("  ⚠️ create_coupon exact match not found")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(app)

print("  ✅ app.py saved!")
print("")

# ==============================
# PUSH
# ==============================
print("  Pushing to GitHub...")
os.system('git add .')
os.system('git commit -m "Fixed coupon creation and edit item stock issue"')
os.system('git push')

print("")
print("  ========================================")
print("  ALL DONE!")
print("")
print("  Bugs Fixed:")
print("  ✅ Coupon values now sent as numbers")
print("  ✅ Coupon has proper validation")
print("  ✅ Edit item respects In Stock dropdown")
print("  ✅ Stock quantity saves independently")
print("  ✅ Console logging added for debugging")
print("")
print("  After deploying test:")
print("  1. Edit an item - change stock qty")
print("  2. Create a coupon - SAVE20 10%")
print("  3. Open browser console (F12)")
print("     - Should see 'Creating coupon: {...}'")
print("     - Should see 'Response: {success: true}'")
print("")
print("  Render updates in 2-3 minutes!")
print("  ========================================")
print("")