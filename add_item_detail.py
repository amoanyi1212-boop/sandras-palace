import os

print("")
print("  ========================================")
print("  Adding Item Detail Modal")
print("  ========================================")
print("")

with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ==============================
# ADD ITEM DETAIL MODAL
# ==============================

# Add modal before toast div
old_toast = '<div class="toast" id="toast"></div>'

new_detail_modal = '''<!-- ITEM DETAIL -->
<div class="modal-overlay" id="detailModal">
    <div class="modal" style="max-width:600px">
        <div class="m-head">
            <h2 id="d-title">Item Details</h2>
            <button class="m-x" onclick="closeDetail()">✕</button>
        </div>
        <div class="m-body" style="padding:0">

            <!-- Big Image -->
            <div style="position:relative;overflow:hidden">
                <img id="d-img" src="" alt=""
                     style="width:100%;height:300px;object-fit:cover;background:#fff0f3"
                     onerror="this.src='https://via.placeholder.com/600x300?text=No+Image'" />
                <div id="d-oos-badge" style="
                    display:none;position:absolute;top:15px;right:15px;
                    background:linear-gradient(135deg,#e53935,#ef5350);
                    color:white;padding:8px 18px;border-radius:25px;
                    font-size:14px;font-weight:800;
                ">Sold Out</div>
            </div>

            <!-- Item Info -->
            <div style="padding:25px">

                <!-- Category -->
                <span id="d-cat" style="
                    background:#fce4ec;color:#c2185b;padding:5px 14px;
                    border-radius:25px;font-size:12px;font-weight:800;
                    display:inline-block;margin-bottom:12px;
                ">Category</span>

                <!-- Name -->
                <h2 id="d-name" style="
                    font-family:'Fredoka One',cursive;font-size:26px;
                    color:#c2185b;margin-bottom:10px;
                ">Item Name</h2>

                <!-- Price -->
                <div id="d-price" style="
                    font-family:'Fredoka One',cursive;font-size:30px;
                    color:#e91e63;margin-bottom:15px;
                ">GH₵ 0.00</div>

                <!-- Stock Status -->
                <div id="d-stock" style="margin-bottom:20px"></div>

                <!-- Description -->
                <div style="
                    background:#fff0f3;border-radius:16px;padding:20px;
                    margin-bottom:20px;border:2px solid #fce4ec;
                ">
                    <h3 style="
                        font-family:'Fredoka One',cursive;font-size:16px;
                        color:#c2185b;margin-bottom:10px;
                    ">📝 Description</h3>
                    <p id="d-desc" style="
                        font-size:15px;color:#555;line-height:1.8;
                        font-weight:600;white-space:pre-wrap;
                    ">No description available</p>
                </div>

                <!-- Date Added -->
                <p id="d-date" style="
                    font-size:13px;color:#aaa;font-weight:700;
                    margin-bottom:20px;
                ">Added: 2024-01-01</p>

                <!-- Quantity Selector + Add to Cart -->
                <div id="d-actions" style="
                    display:flex;align-items:center;gap:15px;
                ">
                    <div style="
                        display:flex;align-items:center;gap:10px;
                        background:#fff0f3;border-radius:14px;padding:8px 15px;
                    ">
                        <button onclick="changeDetailQty(-1)" style="
                            width:35px;height:35px;border:3px solid #fce4ec;
                            border-radius:10px;background:white;font-size:18px;
                            font-weight:800;cursor:pointer;display:flex;
                            align-items:center;justify-content:center;
                        ">−</button>
                        <span id="d-qty" style="
                            font-family:'Fredoka One',cursive;font-size:20px;
                            color:#c2185b;min-width:30px;text-align:center;
                        ">1</span>
                        <button onclick="changeDetailQty(1)" style="
                            width:35px;height:35px;border:3px solid #fce4ec;
                            border-radius:10px;background:white;font-size:18px;
                            font-weight:800;cursor:pointer;display:flex;
                            align-items:center;justify-content:center;
                        ">+</button>
                    </div>
                    <button id="d-add-btn" onclick="addFromDetail()" style="
                        flex:1;padding:15px 25px;
                        background:linear-gradient(135deg,#e91e63,#ff6f00);
                        color:white;border:none;border-radius:14px;
                        font-size:16px;font-weight:800;cursor:pointer;
                        font-family:'Nunito';transition:all 0.3s;
                    ">🛒 Add to Cart</button>
                </div>

                <!-- Total for selected qty -->
                <div id="d-subtotal" style="
                    text-align:right;margin-top:12px;
                    font-family:'Fredoka One',cursive;
                    font-size:18px;color:#e91e63;
                ">Subtotal: GH₵ 0.00</div>

            </div>
        </div>
    </div>
</div>

<div class="toast" id="toast"></div>'''

html = html.replace(old_toast, new_detail_modal)
print("  ✅ Added item detail modal")

# ==============================
# MAKE ITEM CARDS CLICKABLE
# ==============================

# Find the item card HTML and add onclick
old_card = "return'<div class=\"item-card'+(i.in_stock?'':' oos')+'\">"
new_card = "return'<div class=\"item-card'+(i.in_stock?'':' oos')+'\" onclick=\"openDetail('+i.id+')\" style=\"cursor:pointer\">"

html = html.replace(old_card, new_card)
print("  ✅ Made item cards clickable")

# Move add button click to stop propagation
old_add_btn = "(i.in_stock?'onclick=\"addToCart('+i.id+')\"':'disabled')"
new_add_btn = "(i.in_stock?'onclick=\"event.stopPropagation();addToCart('+i.id+')\"':'disabled')"

html = html.replace(old_add_btn, new_add_btn)
print("  ✅ Fixed add button click propagation")

# ==============================
# ADD JAVASCRIPT FUNCTIONS
# ==============================

old_toast_func = "function toast(m,t)"

new_detail_js = '''// ITEM DETAIL
var detailItem = null;
var detailQty  = 1;

function openDetail(id) {
    detailItem = allItems.find(function(i) { return i.id === id });
    if (!detailItem) return;
    detailQty = 1;

    document.getElementById('d-img').src     = getImg(detailItem.image_url);
    document.getElementById('d-title').textContent = detailItem.name;
    document.getElementById('d-name').textContent  = detailItem.name;
    document.getElementById('d-cat').textContent   = '📁 ' + detailItem.category;
    document.getElementById('d-price').textContent  = 'GH\\u20b5 ' + detailItem.price.toFixed(2);
    document.getElementById('d-desc').textContent   = detailItem.description || 'No description available for this item.';
    document.getElementById('d-date').textContent   = 'Added: ' + detailItem.date_added;
    document.getElementById('d-qty').textContent    = '1';
    document.getElementById('d-subtotal').textContent = 'Subtotal: GH\\u20b5 ' + detailItem.price.toFixed(2);

    // Stock badge
    if (detailItem.in_stock) {
        document.getElementById('d-stock').innerHTML = '<span class="badge badge-confirmed" style="font-size:14px;padding:8px 18px">✅ In Stock</span>';
        document.getElementById('d-oos-badge').style.display = 'none';
        document.getElementById('d-actions').style.display   = 'flex';
        document.getElementById('d-subtotal').style.display  = 'block';
    } else {
        document.getElementById('d-stock').innerHTML = '<span class="badge badge-cancelled" style="font-size:14px;padding:8px 18px">❌ Out of Stock</span>';
        document.getElementById('d-oos-badge').style.display = 'block';
        document.getElementById('d-actions').style.display   = 'none';
        document.getElementById('d-subtotal').style.display  = 'none';
    }

    document.getElementById('detailModal').classList.add('show');
}

function closeDetail() {
    document.getElementById('detailModal').classList.remove('show');
}

function changeDetailQty(change) {
    detailQty += change;
    if (detailQty < 1) detailQty = 1;
    if (detailQty > 99) detailQty = 99;
    document.getElementById('d-qty').textContent = detailQty;
    if (detailItem) {
        var subtotal = detailItem.price * detailQty;
        document.getElementById('d-subtotal').textContent = 'Subtotal: GH\\u20b5 ' + subtotal.toFixed(2);
    }
}

function addFromDetail() {
    if (!detailItem || !detailItem.in_stock) return;

    var existing = cart.find(function(c) { return c.id === detailItem.id });
    if (existing) {
        existing.quantity += detailQty;
    } else {
        var copy = {};
        for (var k in detailItem) copy[k] = detailItem[k];
        copy.quantity = detailQty;
        cart.push(copy);
    }

    updateCart();
    toast(detailItem.name + ' x' + detailQty + ' added!', 'success');

    // Animate button
    var btn = document.getElementById('d-add-btn');
    btn.textContent = '✅ Added!';
    btn.style.background = 'linear-gradient(135deg,#43a047,#66bb6a)';
    setTimeout(function() {
        btn.textContent = '🛒 Add to Cart';
        btn.style.background = 'linear-gradient(135deg,#e91e63,#ff6f00)';
    }, 1500);

    // Update main page button too
    var mainBtn = document.getElementById('cb-' + detailItem.id);
    if (mainBtn) {
        mainBtn.textContent = 'Added!';
        setTimeout(function() { mainBtn.textContent = '🛒 Add'; }, 1500);
    }
}

// Close detail modal
document.getElementById('detailModal').addEventListener('click', function(e) {
    if (e.target === this) closeDetail();
});

function toast(m,t)'''

html = html.replace(old_toast_func, new_detail_js)
print("  ✅ Added detail modal JavaScript")

# ==============================
# SAVE
# ==============================
with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("  ✅ index.html saved!")
print("")

# ==============================
# PUSH
# ==============================
print("  Pushing to GitHub...")
os.system('git add .')
os.system('git commit -m "Added item detail modal with description and quantity"')
os.system('git push')

print("")
print("  ========================================")
print("  ALL DONE!")
print("")
print("  When customer clicks an item they see:")
print("  ✅ Big product image")
print("  ✅ Product name")
print("  ✅ Price in GH₵")
print("  ✅ Stock status")
print("  ✅ Full description")
print("  ✅ Date added")
print("  ✅ Quantity selector (+ / -)")
print("  ✅ Add to Cart button")
print("  ✅ Subtotal calculation")
print("  ✅ Quick add button still works too")
print("")
print("  Render updates in 2-3 minutes!")
print("  ========================================")
print("")