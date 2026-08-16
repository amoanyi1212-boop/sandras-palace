import os

print("")
print("  ========================================")
print("  PREMIUM FEATURES - Part 2: Frontend")
print("  ========================================")
print("")

# ==============================
# UPDATE index.html
# ==============================
print("  Updating index.html...")

with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add wishlist heart icon CSS
old_body_css = "body{background:#fff5f7;color:#333}"
new_body_css = '''body{background:#fff5f7;color:#333}
        .wish-btn{position:absolute;top:12px;left:12px;background:white;border:none;width:35px;height:35px;border-radius:50%;font-size:18px;cursor:pointer;z-index:3;box-shadow:0 2px 8px rgba(0,0,0,0.15);display:flex;align-items:center;justify-content:center;transition:all 0.2s}
        .wish-btn:hover{transform:scale(1.2)}
        .wish-btn.active{background:#e91e63;color:white}
        .stars{display:flex;gap:3px}
        .star{cursor:pointer;font-size:22px;transition:all 0.1s}
        .star:hover{transform:scale(1.2)}
        .review-card{background:white;border-radius:14px;padding:15px;margin-bottom:10px;border:2px solid #fce4ec}
        .review-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px}
        .review-name{font-weight:800;color:#c2185b;font-size:14px}
        .review-date{font-size:11px;color:#aaa;font-weight:700}
        .review-text{font-size:13px;color:#555;font-weight:600;line-height:1.6}
        .coupon-input{display:flex;gap:10px;margin-bottom:15px}
        .coupon-input input{flex:1;padding:12px 14px;border:3px solid #fce4ec;border-radius:12px;font-size:14px;font-weight:600;outline:none;font-family:'Nunito'}
        .coupon-input button{padding:12px 20px;background:linear-gradient(135deg,#e91e63,#ff6f00);color:white;border:none;border-radius:12px;font-weight:800;cursor:pointer;font-family:'Nunito';white-space:nowrap}
        .coupon-success{background:#e8f5e9;border:2px solid #43a047;border-radius:12px;padding:12px;text-align:center;color:#2e7d32;font-weight:800;font-size:14px;margin-bottom:15px}
        .track-step{display:flex;align-items:center;gap:15px;padding:12px 0;position:relative}
        .track-icon{width:40px;height:40px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0}
        .track-icon.done{background:#e8f5e9;border:3px solid #43a047}
        .track-icon.pending{background:#f5f5f5;border:3px solid #ddd}
        .track-info{flex:1}
        .track-name{font-weight:800;font-size:14px}
        .track-name.done{color:#43a047}
        .track-name.pending{color:#aaa}
        .track-date{font-size:11px;color:#aaa;font-weight:700}
        .track-line{position:absolute;left:20px;top:52px;width:3px;height:20px;background:#ddd}
        .track-line.done{background:#43a047}'''

html = html.replace(old_body_css, new_body_css)
print("  ✅ Added CSS for wishlist, reviews, coupon, tracking")

# 2. Add wishlist heart to item cards
old_card_img = '''+'<div class="item-img-wrap"><img class="item-img" src="'+getImg(i.image_url)'''
new_card_img = '''+'<div class="item-img-wrap"><button class="wish-btn" onclick="event.stopPropagation();toggleWish('+i.id+')" id="wish-'+i.id+'">🤍</button><img class="item-img" src="'+getImg(i.image_url)'''

html = html.replace(old_card_img, new_card_img)
print("  ✅ Added wishlist heart to item cards")

# 3. Update detail modal to include reviews and wishlist
old_detail_date = '''<p id="d-date" style="font-size:13px;color:#aaa;font-weight:700;margin-bottom:20px">Added: -</p>'''

new_detail_date = '''<p id="d-date" style="font-size:13px;color:#aaa;font-weight:700;margin-bottom:15px">Added: -</p>

                <!-- Average Rating -->
                <div id="d-avg-rating" style="display:flex;align-items:center;gap:10px;margin-bottom:20px">
                    <div id="d-stars-display" style="font-size:20px"></div>
                    <span id="d-rating-text" style="font-weight:800;color:#f57f17;font-size:16px"></span>
                    <span id="d-review-count" style="font-size:13px;color:#aaa;font-weight:700"></span>
                </div>

                <!-- Wishlist Button -->
                <button id="d-wish-btn" onclick="toggleWishDetail()" style="
                    width:100%;padding:12px;margin-bottom:20px;
                    background:white;border:3px solid #fce4ec;border-radius:14px;
                    font-size:15px;font-weight:800;cursor:pointer;font-family:'Nunito';
                    color:#e91e63;transition:all 0.2s;display:flex;align-items:center;
                    justify-content:center;gap:8px;
                ">🤍 Add to Wishlist</button>'''

html = html.replace(old_detail_date, new_detail_date)
print("  ✅ Added rating display and wishlist to detail")

# 4. Add reviews section after detail actions
old_detail_sub = '''<div id="d-sub" style="text-align:right;margin-top:12px;font-family:\'Fredoka One\',cursive;font-size:18px;color:#e91e63">Subtotal: GH₵ 0</div>
            </div>
        </div>
    </div>
</div>'''

new_detail_reviews = '''<div id="d-sub" style="text-align:right;margin-top:12px;font-family:'Fredoka One',cursive;font-size:18px;color:#e91e63">Subtotal: GH₵ 0</div>

                <!-- Reviews Section -->
                <div style="margin-top:25px;border-top:3px solid #fce4ec;padding-top:20px">
                    <h3 style="font-family:'Fredoka One',cursive;color:#c2185b;font-size:18px;margin-bottom:15px">⭐ Customer Reviews</h3>

                    <!-- Write Review -->
                    <div id="d-write-review" style="background:#fff0f3;border-radius:16px;padding:18px;margin-bottom:15px;border:2px solid #fce4ec">
                        <p style="font-weight:800;color:#555;font-size:14px;margin-bottom:10px">Write a Review:</p>
                        <div class="stars" id="d-star-input" style="margin-bottom:10px">
                            <span class="star" onclick="setRating(1)">☆</span>
                            <span class="star" onclick="setRating(2)">☆</span>
                            <span class="star" onclick="setRating(3)">☆</span>
                            <span class="star" onclick="setRating(4)">☆</span>
                            <span class="star" onclick="setRating(5)">☆</span>
                        </div>
                        <textarea id="d-review-text" placeholder="Share your experience..." style="width:100%;padding:12px;border:3px solid #fce4ec;border-radius:12px;font-size:13px;font-weight:600;outline:none;font-family:'Nunito';min-height:60px;resize:vertical;margin-bottom:10px"></textarea>
                        <button onclick="submitReview()" style="padding:10px 20px;background:linear-gradient(135deg,#e91e63,#ff6f00);color:white;border:none;border-radius:10px;font-weight:800;cursor:pointer;font-family:'Nunito';font-size:13px">Submit Review</button>
                    </div>

                    <!-- Reviews List -->
                    <div id="d-reviews-list"><p style="color:#aaa;font-size:13px;font-weight:700;text-align:center;padding:20px">No reviews yet. Be the first!</p></div>
                </div>
            </div>
        </div>
    </div>
</div>'''

html = html.replace(old_detail_sub, new_detail_reviews)
print("  ✅ Added reviews section to detail modal")

# 5. Add coupon input to checkout
old_order_summary = '''<div class="o-summary"><h3>🛒 Order</h3><div id="o-items"></div><div class="o-s-total"><span>Total</span><span id="o-total">GH₵ 0</span></div></div>'''

new_order_summary = '''<div class="o-summary">
                <h3>🛒 Order</h3>
                <div id="o-items"></div>
                <div class="o-s-total"><span>Subtotal</span><span id="o-subtotal">GH₵ 0</span></div>

                <!-- Coupon Code -->
                <div style="margin-top:15px;border-top:2px solid #fce4ec;padding-top:15px">
                    <div class="coupon-input">
                        <input type="text" id="o-coupon" placeholder="🎟️ Coupon code" style="text-transform:uppercase" />
                        <button onclick="applyCoupon()">Apply</button>
                    </div>
                    <div id="coupon-result"></div>
                </div>

                <div class="o-s-total" style="border-top:2px solid #fce4ec;padding-top:10px;margin-top:10px"><span>Total</span><span id="o-total">GH₵ 0</span></div>
            </div>'''

html = html.replace(old_order_summary, new_order_summary)
print("  ✅ Added coupon input to checkout")

# 6. Add wishlist + tracking modals before image viewer
old_img_viewer = '<!-- IMAGE VIEWER -->'

new_modals = '''<!-- WISHLIST -->
<div class="modal-overlay" id="wishModal">
    <div class="modal">
        <div class="m-head"><h2>❤️ My Wishlist</h2><button class="m-x" onclick="document.getElementById('wishModal').classList.remove('show')">✕</button></div>
        <div class="m-body"><div id="wish-list" style="max-height:400px;overflow-y:auto"><div class="empty-state"><div class="e-icon">❤️</div><p>Wishlist empty</p></div></div></div>
    </div>
</div>

<!-- ORDER TRACKING -->
<div class="modal-overlay" id="trackModal">
    <div class="modal">
        <div class="m-head"><h2>📍 Order Tracking</h2><button class="m-x" onclick="document.getElementById('trackModal').classList.remove('show')">✕</button></div>
        <div class="m-body">
            <h3 id="track-title" style="font-family:'Fredoka One',cursive;color:#c2185b;margin-bottom:20px">Order #0</h3>
            <div id="track-steps"></div>
        </div>
    </div>
</div>

<!-- IMAGE VIEWER -->'''

html = html.replace(old_img_viewer, new_modals)
print("  ✅ Added wishlist + tracking modals")

# 7. Add wishlist to user menu
old_user_menu = '''\'<div class="dd-item" onclick="openMyOrders()">📦 My Orders</div>\'+'''
new_user_menu = '''\'<div class="dd-item" onclick="openMyOrders()">📦 My Orders</div>\'+
            \'<div class="dd-item" onclick="openWishlist()">❤️ Wishlist</div>\'+'''

html = html.replace(old_user_menu, new_user_menu)
print("  ✅ Added wishlist to user menu")

# 8. Add tracking button to My Orders
old_order_card_foot = '''return\'<div class="my-o-card"><div class="my-o-head"><h4>Order #\'+o.id+\'</h4><span class="badge badge-\'+sc+\'">\'+o.status+\'</span></div><div class="my-o-items">\'+fmtItems(o.items)+\'</div><div class="my-o-foot"><span style="color:#aaa;font-size:13px">\'+o.date_ordered+\'</span><span class="my-o-price">GH&#8373; \'+o.total_price.toFixed(2)+\'</span></div>\'+btns+\'</div>\';'''

new_order_card_foot = '''var trackBtn=\'<button onclick="trackOrder(\'+o.id+\')" style="width:100%;padding:8px;margin-top:8px;background:none;border:2px solid #1976d2;color:#1976d2;border-radius:10px;font-weight:800;cursor:pointer;font-family:Nunito;font-size:12px">📍 Track Order</button>\';
            return\'<div class="my-o-card"><div class="my-o-head"><h4>Order #\'+o.id+\'</h4><span class="badge badge-\'+sc+\'">\'+o.status+\'</span></div><div class="my-o-items">\'+fmtItems(o.items)+\'</div><div class="my-o-foot"><span style="color:#aaa;font-size:13px">\'+o.date_ordered+\'</span><span class="my-o-price">GH&#8373; \'+o.total_price.toFixed(2)+\'</span></div>\'+btns+trackBtn+\'</div>\';'''

html = html.replace(old_order_card_foot, new_order_card_foot)
print("  ✅ Added track button to My Orders")

# 9. Add all new JavaScript functions
old_toast_fn = "function toast(m,t)"

new_premium_js = '''// ===========================
// REVIEWS
// ===========================
var selectedRating = 0;

function setRating(r) {
    selectedRating = r;
    var stars = document.querySelectorAll('#d-star-input .star');
    stars.forEach(function(s, i) {
        s.textContent = i < r ? '★' : '☆';
        s.style.color = i < r ? '#f9a825' : '#ccc';
    });
}

function loadReviews(itemId) {
    fetch('/api/reviews/' + itemId)
    .then(function(r) { return r.json(); })
    .then(function(data) {
        // Show average rating
        var avgStars = '';
        for (var i = 1; i <= 5; i++) avgStars += i <= Math.round(data.avg_rating) ? '★' : '☆';
        document.getElementById('d-stars-display').textContent = avgStars;
        document.getElementById('d-stars-display').style.color = '#f9a825';
        document.getElementById('d-rating-text').textContent = data.avg_rating > 0 ? data.avg_rating + '/5' : '';
        document.getElementById('d-review-count').textContent = data.count > 0 ? '(' + data.count + ' reviews)' : '';

        // Show reviews list
        var list = document.getElementById('d-reviews-list');
        if (data.reviews.length === 0) {
            list.innerHTML = '<p style="color:#aaa;font-size:13px;font-weight:700;text-align:center;padding:20px">No reviews yet. Be the first!</p>';
        } else {
            list.innerHTML = data.reviews.map(function(r) {
                var stars = '';
                for (var i = 1; i <= 5; i++) stars += i <= r.rating ? '★' : '☆';
                return '<div class="review-card">' +
                    '<div class="review-header">' +
                    '<div><span class="review-name">' + r.user_name + '</span> <span style="color:#f9a825;font-size:14px">' + stars + '</span></div>' +
                    '<span class="review-date">' + r.created_at + '</span>' +
                    '</div>' +
                    '<p class="review-text">' + (r.comment || '') + '</p>' +
                    '</div>';
            }).join('');
        }
    })
    .catch(function() {});
}

function submitReview() {
    if (!user) { toast('Login to review!', 'error'); return; }
    if (!detailItem) return;
    if (selectedRating === 0) { toast('Select a rating!', 'error'); return; }

    var comment = document.getElementById('d-review-text').value.trim();

    fetch('/api/reviews/add', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            item_id: detailItem.id,
            rating: selectedRating,
            comment: comment
        })
    })
    .then(function(r) { return r.json(); })
    .then(function(d) {
        if (d.success) {
            toast(d.message, 'success');
            document.getElementById('d-review-text').value = '';
            setRating(0);
            loadReviews(detailItem.id);
        } else {
            toast(d.message || 'Error!', 'error');
        }
    })
    .catch(function() { toast('Error!', 'error'); });
}

// ===========================
// WISHLIST
// ===========================
var userWishlist = [];

function loadWishlistIds() {
    if (!user) return;
    fetch('/api/wishlist')
    .then(function(r) { return r.json(); })
    .then(function(items) {
        userWishlist = items.map(function(i) { return i.item_id; });
        updateWishlistIcons();
    })
    .catch(function() {});
}

function updateWishlistIcons() {
    allItems.forEach(function(i) {
        var btn = document.getElementById('wish-' + i.id);
        if (btn) {
            if (userWishlist.indexOf(i.id) > -1) {
                btn.textContent = '❤️';
                btn.classList.add('active');
            } else {
                btn.textContent = '🤍';
                btn.classList.remove('active');
            }
        }
    });
}

function toggleWish(itemId) {
    if (!user) { toast('Login first!', 'error'); return; }
    var inList = userWishlist.indexOf(itemId) > -1;

    if (inList) {
        fetch('/api/wishlist/remove/' + itemId, {method: 'DELETE'})
        .then(function(r) { return r.json(); })
        .then(function(d) {
            if (d.success) {
                userWishlist = userWishlist.filter(function(id) { return id !== itemId; });
                updateWishlistIcons();
                toast('Removed from wishlist', 'success');
            }
        });
    } else {
        fetch('/api/wishlist/add/' + itemId, {method: 'POST'})
        .then(function(r) { return r.json(); })
        .then(function(d) {
            if (d.success) {
                userWishlist.push(itemId);
                updateWishlistIcons();
                toast('Added to wishlist!', 'success');
            } else {
                toast(d.message || 'Error', 'error');
            }
        });
    }
}

function toggleWishDetail() {
    if (!detailItem) return;
    toggleWish(detailItem.id);
    updateDetailWishBtn();
}

function updateDetailWishBtn() {
    if (!detailItem) return;
    var btn = document.getElementById('d-wish-btn');
    if (userWishlist.indexOf(detailItem.id) > -1) {
        btn.innerHTML = '❤️ In Wishlist';
        btn.style.background = '#fce4ec';
        btn.style.borderColor = '#e91e63';
    } else {
        btn.innerHTML = '🤍 Add to Wishlist';
        btn.style.background = 'white';
        btn.style.borderColor = '#fce4ec';
    }
}

function openWishlist() {
    document.getElementById('dd-menu').classList.remove('show');
    if (!user) { openAuth('login'); return; }
    fetch('/api/wishlist')
    .then(function(r) { return r.json(); })
    .then(function(items) {
        var list = document.getElementById('wish-list');
        if (!items || items.length === 0) {
            list.innerHTML = '<div class="empty-state"><div class="e-icon">❤️</div><p>Wishlist is empty!</p></div>';
        } else {
            list.innerHTML = items.map(function(i) {
                return '<div style="display:flex;gap:12px;padding:12px 0;border-bottom:2px solid #fce4ec;align-items:center">' +
                    '<img src="' + getImg(i.image_url) + '" style="width:60px;height:60px;border-radius:10px;object-fit:cover" onerror="this.src=\'/static/noimg.png\'" />' +
                    '<div style="flex:1">' +
                    '<div style="font-family:Fredoka One,cursive;color:#c2185b;font-size:14px">' + i.name + '</div>' +
                    '<div style="font-family:Fredoka One,cursive;color:#e91e63;font-size:16px">GH&#8373; ' + i.price.toFixed(2) + '</div>' +
                    '<div style="font-size:11px;color:' + (i.in_stock ? '#43a047' : '#e53935') + ';font-weight:800">' + (i.in_stock ? '✅ In Stock (' + (i.stock_quantity || 0) + ')' : '❌ Out of Stock') + '</div>' +
                    '</div>' +
                    '<div style="display:flex;flex-direction:column;gap:5px">' +
                    '<button onclick="addToCart(' + i.item_id + ');document.getElementById(\'wishModal\').classList.remove(\'show\')" style="padding:6px 12px;background:linear-gradient(135deg,#e91e63,#ff6f00);color:white;border:none;border-radius:8px;font-weight:800;cursor:pointer;font-size:11px">🛒 Add</button>' +
                    '<button onclick="toggleWish(' + i.item_id + ');setTimeout(openWishlist,500)" style="padding:6px 12px;background:#ffebee;color:#e53935;border:none;border-radius:8px;font-weight:800;cursor:pointer;font-size:11px">🗑️</button>' +
                    '</div>' +
                    '</div>';
            }).join('');
        }
        document.getElementById('wishModal').classList.add('show');
    })
    .catch(function() { toast('Error!', 'error'); });
}

// ===========================
// COUPON
// ===========================
var appliedCoupon = null;
var originalTotal = 0;

function applyCoupon() {
    var code = document.getElementById('o-coupon').value.trim();
    if (!code) { toast('Enter a coupon code!', 'error'); return; }

    fetch('/api/coupons/validate', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({code: code, total: originalTotal})
    })
    .then(function(r) { return r.json(); })
    .then(function(d) {
        var result = document.getElementById('coupon-result');
        if (d.success) {
            appliedCoupon = d;
            result.innerHTML = '<div class="coupon-success">🎟️ ' + d.message + ' You save GH&#8373; ' + d.discount.toFixed(2) + '</div>';
            document.getElementById('o-total').textContent = 'GH\u20b5 ' + d.new_total.toFixed(2);
            document.getElementById('o-amt').textContent = 'Amount: GH\u20b5 ' + d.new_total.toFixed(2);
            toast('Coupon applied!', 'success');
        } else {
            appliedCoupon = null;
            result.innerHTML = '<div style="background:#ffebee;border:2px solid #ef5350;border-radius:12px;padding:12px;text-align:center;color:#c62828;font-weight:800;font-size:14px;margin-bottom:15px">' + d.message + '</div>';
            document.getElementById('o-total').textContent = 'GH\u20b5 ' + originalTotal.toFixed(2);
            document.getElementById('o-amt').textContent = 'Amount: GH\u20b5 ' + originalTotal.toFixed(2);
        }
    })
    .catch(function() { toast('Error!', 'error'); });
}

// ===========================
// ORDER TRACKING
// ===========================
function trackOrder(orderId) {
    fetch('/api/orders/track/' + orderId)
    .then(function(r) { return r.json(); })
    .then(function(d) {
        if (!d.success) { toast(d.message || 'Error!', 'error'); return; }

        document.getElementById('track-title').textContent = 'Order #' + d.order_id + ' - ' + d.status;

        var steps = document.getElementById('track-steps');
        steps.innerHTML = d.steps.map(function(s, i) {
            var isLast = i === d.steps.length - 1;
            return '<div class="track-step">' +
                '<div class="track-icon ' + (s.done ? 'done' : 'pending') + '">' + s.icon + '</div>' +
                '<div class="track-info">' +
                '<div class="track-name ' + (s.done ? 'done' : 'pending') + '">' + s.step + '</div>' +
                (s.date ? '<div class="track-date">' + s.date + '</div>' : '') +
                '</div>' +
                (!isLast ? '<div class="track-line ' + (s.done ? 'done' : '') + '"></div>' : '') +
                '</div>';
        }).join('');

        document.getElementById('trackModal').classList.add('show');
    })
    .catch(function() { toast('Error!', 'error'); });
}

// ===========================
// UPDATE EXISTING FUNCTIONS
// ===========================

// Load wishlist after auth check
var origCheckAuth = checkAuth;
checkAuth = function() {
    fetch('/api/auth/check').then(function(r) { return r.json(); }).then(function(d) {
        if (d.logged_in) { user = d.user; updateUI(); setTimeout(checkNotifs, 1000); setTimeout(loadWishlistIds, 1500); }
        else { user = null; updateUI(); }
    }).catch(function() {});
};

function toast(m,t)'''

html = html.replace(old_toast_fn, new_premium_js)
print("  ✅ Added all premium JavaScript functions")

# 10. Update openDetail to load reviews and wishlist
old_open_detail_end = '''document.getElementById('detailModal').classList.add('show');'''
new_open_detail_end = '''document.getElementById('detailModal').classList.add('show');
    // Load reviews
    loadReviews(detailItem.id);
    // Update wishlist button
    updateDetailWishBtn();
    // Reset review input
    setRating(0);
    document.getElementById('d-review-text').value = '';'''

html = html.replace(old_open_detail_end, new_open_detail_end)
print("  ✅ Updated openDetail to load reviews")

# 11. Update openCheckout to save original total for coupons
old_checkout_fn = '''function openCheckout(){
    if(cart.length===0){toast('Cart empty!','error');return}
    if(!user){toast('Please login!','error');closeCart();openAuth('login');return}
    var tp=cart.reduce(function(s,i){return s+(i.price*i.quantity)},0);'''

new_checkout_fn = '''function openCheckout(){
    if(cart.length===0){toast('Cart empty!','error');return}
    if(!user){toast('Please login!','error');closeCart();openAuth('login');return}
    var tp=cart.reduce(function(s,i){return s+(i.price*i.quantity)},0);
    originalTotal = tp;
    appliedCoupon = null;
    document.getElementById('o-coupon').value = '';
    document.getElementById('coupon-result').innerHTML = '';
    document.getElementById('o-subtotal').textContent = 'GH\\u20b5 ' + tp.toFixed(2);'''

html = html.replace(old_checkout_fn, new_checkout_fn)
print("  ✅ Updated checkout for coupon support")

# 12. Update placeOrder to use coupon total and mark coupon as used
old_place_tp = '''var tp=cart.reduce(function(s,i){return s+(i.price*i.quantity)},0);'''

# Find the second occurrence (in placeOrder)
parts = html.split(old_place_tp)
if len(parts) >= 3:
    # Replace the second occurrence (in placeOrder function)
    parts[2] = parts[2]  # Keep the rest
    html = parts[0] + old_place_tp + parts[1] + '''var tp = appliedCoupon ? appliedCoupon.new_total : cart.reduce(function(s,i){return s+(i.price*i.quantity)},0);''' + parts[2]
    print("  ✅ Updated placeOrder to use coupon total")

# Add coupon use after successful order
old_wa_check = '''if(d.whatsapp_url){setTimeout(function(){window.open(d.whatsapp_url,\'_blank\')},2500)}'''
new_wa_check = '''if(d.whatsapp_url){setTimeout(function(){window.open(d.whatsapp_url,'_blank')},2500)}
                if(appliedCoupon&&appliedCoupon.coupon_id){fetch('/api/coupons/use/'+appliedCoupon.coupon_id,{method:'POST'})}
                appliedCoupon=null;'''

html = html.replace(old_wa_check, new_wa_check)
print("  ✅ Added coupon use tracking after order")

# 13. Add close handlers for new modals
old_deact_close = '''document.getElementById('deactModal').addEventListener('click',function(e){if(e.target===this)this.classList.remove('show')});'''

new_deact_close = '''document.getElementById('deactModal').addEventListener('click',function(e){if(e.target===this)this.classList.remove('show')});
document.getElementById('wishModal').addEventListener('click',function(e){if(e.target===this)this.classList.remove('show')});
document.getElementById('trackModal').addEventListener('click',function(e){if(e.target===this)this.classList.remove('show')});'''

html = html.replace(old_deact_close, new_deact_close)
print("  ✅ Added close handlers for new modals")

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

# 1. Add Coupons and Reports nav items
old_users_nav = '''<li><a onclick="showSection('users')" id="nav-users">👥 Users</a></li>'''
new_users_nav = '''<li><a onclick="showSection('users')" id="nav-users">👥 Users</a></li>
        <li><a onclick="showSection('coupons')" id="nav-coupons">🎟️ Coupons</a></li>
        <li><a onclick="showSection('reports')" id="nav-reports">📊 Reports</a></li>'''

admin = admin.replace(old_users_nav, new_users_nav)
print("  ✅ Added Coupons and Reports nav")

# 2. Add nav items to showSection
old_show_section = '''var t={'dashboard':['📊 Dashboard','Overview'],'add-item':['➕ Add Item','Add product'],'manage-items':['📦 Items','Manage stock'],'orders':['🛒 Orders','Manage orders'],'users':['👥 Users','Registered users']};'''

new_show_section = '''var t={'dashboard':['📊 Dashboard','Overview'],'add-item':['➕ Add Item','Add product'],'manage-items':['📦 Items','Manage stock'],'orders':['🛒 Orders','Manage orders'],'users':['👥 Users','Registered users'],'coupons':['🎟️ Coupons','Manage discount codes'],'reports':['📊 Reports','Sales analytics']};'''

admin = admin.replace(old_show_section, new_show_section)

old_section_load = '''if(s==='dashboard')loadDashboard();if(s==='manage-items')loadItems();if(s==='orders')loadOrders();if(s==='users')loadUsers();'''
new_section_load = '''if(s==='dashboard')loadDashboard();if(s==='manage-items')loadItems();if(s==='orders')loadOrders();if(s==='users')loadUsers();if(s==='coupons')loadCoupons();if(s==='reports')loadReports();'''

admin = admin.replace(old_section_load, new_section_load)
print("  ✅ Updated section navigation")

# 3. Add Coupons and Reports sections before closing main-content div
old_users_section_end = '''</div>
</div>

<!-- EDIT MODAL -->'''

new_sections = '''</div>

    <!-- COUPONS -->
    <div class="section" id="section-coupons">
        <div class="card">
            <div class="card-header"><h2>🎟️ Create Coupon</h2></div>
            <div class="form-grid">
                <div class="form-group"><label>Code *</label><input type="text" id="cp-code" placeholder="e.g. SAVE20" style="text-transform:uppercase" /></div>
                <div class="form-group"><label>Discount Type</label><select id="cp-type"><option value="percentage">Percentage (%)</option><option value="fixed">Fixed Amount (GH₵)</option></select></div>
                <div class="form-group"><label>Discount Value *</label><input type="number" id="cp-value" placeholder="e.g. 20" min="0" step="0.01" /></div>
                <div class="form-group"><label>Min Order (GH₵)</label><input type="number" id="cp-min" placeholder="0" min="0" value="0" /></div>
                <div class="form-group"><label>Max Uses (0=unlimited)</label><input type="number" id="cp-max" placeholder="0" min="0" value="0" /></div>
                <div class="form-group"><label>Expires On</label><input type="date" id="cp-expires" /></div>
            </div>
            <button class="btn btn-primary" onclick="createCoupon()">🎟️ Create Coupon</button>
        </div>
        <div class="card">
            <div class="card-header"><h2>📋 All Coupons</h2><button class="btn btn-primary btn-sm" onclick="loadCoupons()">🔄</button></div>
            <div class="table-wrapper">
                <table>
                    <thead><tr><th>Code</th><th>Type</th><th>Value</th><th>Min Order</th><th>Used</th><th>Max</th><th>Status</th><th>Expires</th><th>Action</th></tr></thead>
                    <tbody id="coupons-body"><tr><td colspan="9"><div class="empty-state"><p>No coupons</p></div></td></tr></tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- REPORTS -->
    <div class="section" id="section-reports">
        <div class="stats-grid" style="grid-template-columns:repeat(4,1fr)">
            <div class="stat-card"><div class="stat-icon yellow">💰</div><div class="stat-info"><h3 id="r-total" style="font-size:20px">GH₵ 0</h3><p>Total Revenue</p></div></div>
            <div class="stat-card"><div class="stat-icon green">📅</div><div class="stat-info"><h3 id="r-today" style="font-size:20px">GH₵ 0</h3><p>Today</p></div></div>
            <div class="stat-card"><div class="stat-icon blue">📆</div><div class="stat-info"><h3 id="r-week" style="font-size:20px">GH₵ 0</h3><p>This Week</p></div></div>
            <div class="stat-card"><div class="stat-icon pink">📅</div><div class="stat-info"><h3 id="r-month" style="font-size:20px">GH₵ 0</h3><p>This Month</p></div></div>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:25px">
            <div class="card">
                <div class="card-header"><h2>📊 Order Stats</h2></div>
                <div id="r-order-stats" style="display:flex;flex-wrap:wrap;gap:15px">
                    <div style="flex:1;min-width:120px;background:#e8f5e9;border-radius:14px;padding:18px;text-align:center"><div style="font-family:'Fredoka One',cursive;font-size:28px;color:#43a047" id="r-completed">0</div><div style="font-size:12px;font-weight:800;color:#666">Completed</div></div>
                    <div style="flex:1;min-width:120px;background:#fff8e1;border-radius:14px;padding:18px;text-align:center"><div style="font-family:'Fredoka One',cursive;font-size:28px;color:#f9a825" id="r-pending">0</div><div style="font-size:12px;font-weight:800;color:#666">Pending</div></div>
                    <div style="flex:1;min-width:120px;background:#ffebee;border-radius:14px;padding:18px;text-align:center"><div style="font-family:'Fredoka One',cursive;font-size:28px;color:#e53935" id="r-cancelled">0</div><div style="font-size:12px;font-weight:800;color:#666">Cancelled</div></div>
                </div>
            </div>
            <div class="card">
                <div class="card-header"><h2>🏆 Best Sellers</h2></div>
                <div id="r-best-sellers"><div class="empty-state" style="padding:20px"><p>No data yet</p></div></div>
            </div>
        </div>
        <div class="card">
            <div class="card-header"><h2>📈 Daily Sales (Last 7 Days)</h2></div>
            <div id="r-daily" style="display:flex;gap:10px;align-items:flex-end;height:200px;padding:20px 0"><div class="empty-state" style="width:100%"><p>No data yet</p></div></div>
        </div>
    </div>
</div>

<!-- EDIT MODAL -->'''

admin = admin.replace(old_users_section_end, new_sections)
print("  ✅ Added Coupons and Reports sections")

# 4. Add coupon and report functions before toast
old_admin_toast = "function toast(m,t)"

new_admin_js = '''// COUPONS
function loadCoupons(){
    fetch('/api/coupons').then(function(r){return r.json()}).then(function(coupons){
        var tb=document.getElementById('coupons-body');
        if(!coupons||coupons.length===0){tb.innerHTML='<tr><td colspan="9"><div class="empty-state"><p>No coupons</p></div></td></tr>';return}
        tb.innerHTML=coupons.map(function(c){
            return'<tr><td style="font-weight:800;color:#c2185b">'+c.code+'</td><td>'+c.discount_type+'</td><td style="font-weight:800">'+(c.discount_type==='percentage'?c.discount_value+'%':'GH&#8373; '+c.discount_value)+'</td><td>GH&#8373; '+c.min_order+'</td><td>'+c.used_count+'</td><td>'+(c.max_uses||'∞')+'</td><td><span class="badge '+(c.is_active?'badge-confirmed':'badge-cancelled')+'">'+(c.is_active?'Active':'Inactive')+'</span></td><td>'+(c.expires_at||'Never')+'</td><td><button class="btn btn-sm '+(c.is_active?'btn-warning':'btn-success')+'" onclick="toggleCoupon('+c.id+')">'+(c.is_active?'Off':'On')+'</button> <button class="btn btn-danger btn-sm" onclick="deleteCoupon('+c.id+')">🗑️</button></td></tr>';
        }).join('');
    });
}

function createCoupon(){
    var data={code:document.getElementById('cp-code').value.trim().toUpperCase(),discount_type:document.getElementById('cp-type').value,discount_value:document.getElementById('cp-value').value,min_order:document.getElementById('cp-min').value||0,max_uses:document.getElementById('cp-max').value||0,expires_at:document.getElementById('cp-expires').value||''};
    if(!data.code||!data.discount_value){toast('Code and value required!','error');return}
    fetch('/api/coupons/create',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)})
    .then(function(r){return r.json()}).then(function(d){
        if(d.success){toast('Coupon created!','success');loadCoupons();document.getElementById('cp-code').value='';document.getElementById('cp-value').value=''}
        else toast(d.message||'Error!','error');
    });
}

function toggleCoupon(id){fetch('/api/coupons/toggle/'+id,{method:'POST'}).then(function(){loadCoupons();toast('Updated!','success')})}
function deleteCoupon(id){if(!confirm('Delete coupon?'))return;fetch('/api/coupons/delete/'+id,{method:'DELETE'}).then(function(){loadCoupons();toast('Deleted!','success')})}

// REPORTS
function loadReports(){
    fetch('/api/reports/sales').then(function(r){return r.json()}).then(function(d){
        document.getElementById('r-total').textContent='GH\\u20b5 '+d.total_revenue.toFixed(2);
        document.getElementById('r-today').textContent='GH\\u20b5 '+d.today_revenue.toFixed(2);
        document.getElementById('r-week').textContent='GH\\u20b5 '+d.week_revenue.toFixed(2);
        document.getElementById('r-month').textContent='GH\\u20b5 '+d.month_revenue.toFixed(2);
        document.getElementById('r-completed').textContent=d.completed_orders;
        document.getElementById('r-pending').textContent=d.pending_orders;
        document.getElementById('r-cancelled').textContent=d.cancelled_orders;

        // Best sellers
        var bs=document.getElementById('r-best-sellers');
        if(d.best_sellers.length===0)bs.innerHTML='<p style="color:#aaa;text-align:center;padding:20px">No sales data yet</p>';
        else bs.innerHTML=d.best_sellers.map(function(b,i){
            return'<div style="display:flex;align-items:center;gap:12px;padding:10px 0;border-bottom:2px solid #fce4ec"><span style="font-family:Fredoka One,cursive;color:#c2185b;font-size:18px;width:30px">#'+(i+1)+'</span><div style="flex:1"><div style="font-weight:800;color:#333;font-size:14px">'+b.name+'</div><div style="font-size:12px;color:#aaa;font-weight:700">'+b.orders+' orders</div></div><span style="font-family:Fredoka One,cursive;color:#e91e63">GH\\u20b5 '+b.revenue.toFixed(2)+'</span></div>';
        }).join('');

        // Daily chart
        var dc=document.getElementById('r-daily');
        if(d.daily_sales.length===0)dc.innerHTML='<div class="empty-state" style="width:100%"><p>No data yet</p></div>';
        else{
            var maxRev=Math.max.apply(null,d.daily_sales.map(function(s){return s.revenue}))||1;
            dc.innerHTML=d.daily_sales.map(function(s){
                var h=Math.max((s.revenue/maxRev)*150,5);
                var day=s.date.split('-')[2];
                return'<div style="flex:1;display:flex;flex-direction:column;align-items:center;gap:5px"><div style="font-family:Fredoka One,cursive;color:#e91e63;font-size:11px">GH\\u20b5'+Math.round(s.revenue)+'</div><div style="width:100%;height:'+h+'px;background:linear-gradient(180deg,#e91e63,#ff6f00);border-radius:8px 8px 0 0;min-width:30px"></div><div style="font-size:11px;font-weight:800;color:#888">'+day+'</div><div style="font-size:10px;color:#aaa">'+s.orders+'</div></div>';
            }).join('');
        }
    }).catch(function(){});
}

function toast(m,t)'''

admin = admin.replace(old_admin_toast, new_admin_js)
print("  ✅ Added coupon + report JavaScript")

with open('templates/admin.html', 'w', encoding='utf-8') as f:
    f.write(admin)

print("  ✅ admin.html saved!")
print("")

# ==============================
# PUSH TO GITHUB
# ==============================
print("  Pushing to GitHub...")
os.system('git add .')
os.system('git commit -m "Added premium features: reviews, coupons, wishlist, reports, tracking"')
os.system('git push')

# Clean up backups
for f in ['app.py.bak', 'templates/index.html.bak', 'templates/admin.html.bak']:
    try:
        os.remove(f)
    except:
        pass

print("")
print("  ========================================")
print("  ALL PREMIUM FEATURES ADDED!")
print("")
print("  ⭐ Product Reviews:")
print("     - Rate 1-5 stars")
print("     - Write comment")
print("     - See average rating")
print("     - See all reviews")
print("")
print("  🎟️ Discount Coupons:")
print("     - Admin creates codes")
print("     - Percentage or fixed")
print("     - Min order amount")
print("     - Expiry dates")
print("     - Usage limits")
print("")
print("  ❤️ Wishlist:")
print("     - Heart icon on products")
print("     - Save items for later")
print("     - Quick add to cart")
print("     - Wishlist page")
print("")
print("  📊 Sales Reports:")
print("     - Total/daily/weekly/monthly revenue")
print("     - Order stats")
print("     - Best selling products")
print("     - Daily sales chart")
print("")
print("  📍 Order Tracking:")
print("     - Visual timeline")
print("     - Step by step progress")
print("     - Track button in My Orders")
print("")
print("  Render updates in 2-3 minutes!")
print("  ========================================")
print("")