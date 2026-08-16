import os

print("")
print("  ========================================")
print("  PREMIUM FEATURES - Safe Update")
print("  Part 1: Backend (app.py)")
print("  ========================================")
print("")

# ==============================
# BACKUP FIRST
# ==============================
print("  Creating backups...")
for f in ['app.py', 'templates/index.html', 'templates/admin.html']:
    try:
        with open(f, 'r', encoding='utf-8') as src:
            with open(f + '.bak', 'w', encoding='utf-8') as dst:
                dst.write(src.read())
        print("  ✅ Backed up:", f)
    except:
        pass
print("")

# ==============================
# UPDATE app.py
# ==============================
print("  Updating app.py...")

with open('app.py', 'r', encoding='utf-8') as f:
    app = f.read()

# ==============================
# 1. ADD NEW MODELS
# ==============================

# Add Review, Coupon, Wishlist models after Notification model
old_admin_section = '''# ==============================
# ADMIN
# =============================='''

new_models = '''class Review(db.Model):
    __tablename__ = "reviews"
    id         = db.Column(db.Integer,     primary_key=True)
    user_id    = db.Column(db.Integer,     db.ForeignKey("users.id"), nullable=False)
    item_id    = db.Column(db.Integer,     db.ForeignKey("items.id"), nullable=False)
    rating     = db.Column(db.Integer,     nullable=False)
    comment    = db.Column(db.String(500))
    user_name  = db.Column(db.String(100))
    created_at = db.Column(db.DateTime,    default=datetime.utcnow)

class Coupon(db.Model):
    __tablename__ = "coupons"
    id            = db.Column(db.Integer,     primary_key=True)
    code          = db.Column(db.String(50),  unique=True, nullable=False)
    discount_type = db.Column(db.String(20),  default="percentage")
    discount_value= db.Column(db.Float,       nullable=False)
    min_order     = db.Column(db.Float,       default=0)
    max_uses      = db.Column(db.Integer,     default=0)
    used_count    = db.Column(db.Integer,     default=0)
    is_active     = db.Column(db.Boolean,     default=True)
    expires_at    = db.Column(db.DateTime,    nullable=True)
    created_at    = db.Column(db.DateTime,    default=datetime.utcnow)

class Wishlist(db.Model):
    __tablename__ = "wishlists"
    id         = db.Column(db.Integer,  primary_key=True)
    user_id    = db.Column(db.Integer,  db.ForeignKey("users.id"), nullable=False)
    item_id    = db.Column(db.Integer,  db.ForeignKey("items.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ==============================
# ADMIN
# =============================='''

app = app.replace(old_admin_section, new_models)
print("  ✅ Added Review, Coupon, Wishlist models")

# ==============================
# 2. ADD TABLE CREATION
# ==============================

old_notif_table = '''                    try:
                        conn.execute(db.text("""
                            CREATE TABLE IF NOT EXISTS notifications ('''

new_tables = '''                    # Create reviews table
                    try:
                        conn.execute(db.text("""
                            CREATE TABLE IF NOT EXISTS reviews (
                                id         SERIAL PRIMARY KEY,
                                user_id    INTEGER NOT NULL,
                                item_id    INTEGER NOT NULL,
                                rating     INTEGER NOT NULL,
                                comment    VARCHAR(500),
                                user_name  VARCHAR(100),
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                            )
                        """))
                        conn.commit()
                    except Exception:
                        pass

                    # Create coupons table
                    try:
                        conn.execute(db.text("""
                            CREATE TABLE IF NOT EXISTS coupons (
                                id             SERIAL PRIMARY KEY,
                                code           VARCHAR(50) UNIQUE NOT NULL,
                                discount_type  VARCHAR(20) DEFAULT 'percentage',
                                discount_value FLOAT NOT NULL,
                                min_order      FLOAT DEFAULT 0,
                                max_uses       INTEGER DEFAULT 0,
                                used_count     INTEGER DEFAULT 0,
                                is_active      BOOLEAN DEFAULT TRUE,
                                expires_at     TIMESTAMP,
                                created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                            )
                        """))
                        conn.commit()
                    except Exception:
                        pass

                    # Create wishlists table
                    try:
                        conn.execute(db.text("""
                            CREATE TABLE IF NOT EXISTS wishlists (
                                id         SERIAL PRIMARY KEY,
                                user_id    INTEGER NOT NULL,
                                item_id    INTEGER NOT NULL,
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                            )
                        """))
                        conn.commit()
                    except Exception:
                        pass

                    try:
                        conn.execute(db.text("""
                            CREATE TABLE IF NOT EXISTS notifications ('''

app = app.replace(old_notif_table, new_tables)
print("  ✅ Added new table creation")

# ==============================
# 3. ADD REVIEW ROUTES
# ==============================

old_debug = '''# ==============================
# DEBUG ROUTES
# =============================='''

new_routes = '''# ==============================
# REVIEWS
# ==============================

@app.route("/api/reviews/<int:item_id>", methods=["GET"])
def get_reviews(item_id):
    try:
        with db.engine.connect() as conn:
            rows = conn.execute(db.text(
                "SELECT id, user_id, rating, comment, user_name, created_at "
                "FROM reviews WHERE item_id = :iid "
                "ORDER BY created_at DESC"
            ), {"iid": item_id}).fetchall()

            reviews = []
            total_rating = 0
            for r in rows:
                reviews.append({
                    "id":         r[0],
                    "user_id":    r[1],
                    "rating":     r[2],
                    "comment":    r[3] or "",
                    "user_name":  r[4] or "Anonymous",
                    "created_at": str(r[5])[:16] if r[5] else ""
                })
                total_rating += r[2]

            avg_rating = round(total_rating / len(reviews), 1) if reviews else 0

            return jsonify({
                "reviews":    reviews,
                "count":      len(reviews),
                "avg_rating": avg_rating
            })
    except Exception as e:
        print("Get reviews error:", e)
        return jsonify({"reviews": [], "count": 0, "avg_rating": 0})

@app.route("/api/reviews/add", methods=["POST"])
def add_review():
    if not session.get("user_id"):
        return jsonify({"success": False, "message": "Login first!"}), 401
    try:
        data    = request.get_json()
        item_id = data.get("item_id")
        rating  = data.get("rating", 5)
        comment = data.get("comment", "")

        if not item_id or not rating:
            return jsonify({"success": False, "message": "Rating required!"})

        if rating < 1 or rating > 5:
            return jsonify({"success": False, "message": "Rating must be 1-5!"})

        user = User.query.get(session["user_id"])
        if not user:
            return jsonify({"success": False, "message": "User not found!"}), 404

        # Check if already reviewed
        with db.engine.connect() as conn:
            existing = conn.execute(db.text(
                "SELECT id FROM reviews WHERE user_id = :uid AND item_id = :iid"
            ), {"uid": user.id, "iid": item_id}).fetchone()

            if existing:
                # Update existing review
                conn.execute(db.text(
                    "UPDATE reviews SET rating = :r, comment = :c "
                    "WHERE user_id = :uid AND item_id = :iid"
                ), {"r": rating, "c": comment, "uid": user.id, "iid": item_id})
                conn.commit()
                return jsonify({"success": True, "message": "Review updated!"})

            # New review
            conn.execute(db.text(
                "INSERT INTO reviews (user_id, item_id, rating, comment, user_name) "
                "VALUES (:uid, :iid, :r, :c, :un)"
            ), {
                "uid": user.id,
                "iid": item_id,
                "r":   rating,
                "c":   comment,
                "un":  user.fullname
            })
            conn.commit()

        return jsonify({"success": True, "message": "Review added! Thank you!"})
    except Exception as e:
        print("Add review error:", e)
        return jsonify({"success": False, "message": str(e)}), 500

# ==============================
# COUPONS
# ==============================

@app.route("/api/coupons/validate", methods=["POST"])
def validate_coupon():
    try:
        data = request.get_json()
        code = data.get("code", "").strip().upper()
        total = float(data.get("total", 0))

        if not code:
            return jsonify({"success": False, "message": "Enter a coupon code!"})

        coupon = Coupon.query.filter_by(code=code, is_active=True).first()

        if not coupon:
            return jsonify({"success": False, "message": "Invalid coupon code!"})

        if coupon.expires_at and coupon.expires_at < datetime.utcnow():
            return jsonify({"success": False, "message": "Coupon has expired!"})

        if coupon.max_uses > 0 and coupon.used_count >= coupon.max_uses:
            return jsonify({"success": False, "message": "Coupon fully used!"})

        if total < coupon.min_order:
            return jsonify({"success": False,
                "message": "Minimum order GH" + chr(8373) + " " +
                str(coupon.min_order) + " required!"})

        if coupon.discount_type == "percentage":
            discount = total * (coupon.discount_value / 100)
            msg = str(int(coupon.discount_value)) + "% off!"
        else:
            discount = coupon.discount_value
            msg = "GH" + chr(8373) + " " + str(discount) + " off!"

        new_total = max(total - discount, 0)

        return jsonify({
            "success":    True,
            "message":    msg,
            "discount":   round(discount, 2),
            "new_total":  round(new_total, 2),
            "coupon_id":  coupon.id
        })

    except Exception as e:
        print("Coupon error:", e)
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/coupons/use/<int:coupon_id>", methods=["POST"])
def use_coupon(coupon_id):
    try:
        with db.engine.connect() as conn:
            conn.execute(db.text(
                "UPDATE coupons SET used_count = used_count + 1 "
                "WHERE id = :id"
            ), {"id": coupon_id})
            conn.commit()
        return jsonify({"success": True})
    except Exception:
        return jsonify({"success": False})

# Admin: Create coupon
@app.route("/api/coupons/create", methods=["POST"])
def create_coupon():
    if not session.get("admin_logged_in"):
        return jsonify({"success": False}), 401
    try:
        data = request.get_json()
        code = data.get("code", "").strip().upper()

        if not code or not data.get("discount_value"):
            return jsonify({"success": False, "message": "Code and value required!"})

        existing = Coupon.query.filter_by(code=code).first()
        if existing:
            return jsonify({"success": False, "message": "Code already exists!"})

        expires = None
        if data.get("expires_at"):
            try:
                expires = datetime.strptime(data["expires_at"], "%Y-%m-%d")
            except:
                pass

        coupon = Coupon(
            code           = code,
            discount_type  = data.get("discount_type", "percentage"),
            discount_value = float(data.get("discount_value")),
            min_order      = float(data.get("min_order", 0)),
            max_uses       = int(data.get("max_uses", 0)),
            is_active      = True,
            expires_at     = expires
        )
        db.session.add(coupon)
        db.session.commit()

        return jsonify({"success": True, "message": "Coupon created!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

# Admin: Get all coupons
@app.route("/api/coupons", methods=["GET"])
def get_coupons():
    if not session.get("admin_logged_in"):
        return jsonify([])
    try:
        coupons = Coupon.query.order_by(Coupon.created_at.desc()).all()
        return jsonify([{
            "id":             c.id,
            "code":           c.code,
            "discount_type":  c.discount_type,
            "discount_value": c.discount_value,
            "min_order":      c.min_order,
            "max_uses":       c.max_uses,
            "used_count":     c.used_count,
            "is_active":      c.is_active,
            "expires_at":     c.expires_at.strftime("%Y-%m-%d") if c.expires_at else "",
            "created_at":     c.created_at.strftime("%Y-%m-%d")
        } for c in coupons])
    except Exception:
        return jsonify([])

# Admin: Delete coupon
@app.route("/api/coupons/delete/<int:coupon_id>", methods=["DELETE"])
def delete_coupon(coupon_id):
    if not session.get("admin_logged_in"):
        return jsonify({"success": False}), 401
    try:
        coupon = Coupon.query.get(coupon_id)
        if coupon:
            db.session.delete(coupon)
            db.session.commit()
        return jsonify({"success": True, "message": "Coupon deleted!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

# Admin: Toggle coupon
@app.route("/api/coupons/toggle/<int:coupon_id>", methods=["POST"])
def toggle_coupon(coupon_id):
    if not session.get("admin_logged_in"):
        return jsonify({"success": False}), 401
    try:
        coupon = Coupon.query.get(coupon_id)
        if coupon:
            coupon.is_active = not coupon.is_active
            db.session.commit()
        return jsonify({"success": True})
    except Exception:
        return jsonify({"success": False})

# ==============================
# WISHLIST
# ==============================

@app.route("/api/wishlist", methods=["GET"])
def get_wishlist():
    if not session.get("user_id"):
        return jsonify([])
    try:
        with db.engine.connect() as conn:
            rows = conn.execute(db.text(
                "SELECT w.id, w.item_id, i.name, i.price, i.image_url, "
                "i.in_stock, i.stock_quantity "
                "FROM wishlists w JOIN items i ON w.item_id = i.id "
                "WHERE w.user_id = :uid "
                "ORDER BY w.created_at DESC"
            ), {"uid": session["user_id"]}).fetchall()

            return jsonify([{
                "id":             r[0],
                "item_id":        r[1],
                "name":           r[2],
                "price":          float(r[3]),
                "image_url":      r[4] or "/static/noimg.png",
                "in_stock":       r[5],
                "stock_quantity": r[6] or 0
            } for r in rows])
    except Exception as e:
        print("Wishlist error:", e)
        return jsonify([])

@app.route("/api/wishlist/add/<int:item_id>", methods=["POST"])
def add_to_wishlist(item_id):
    if not session.get("user_id"):
        return jsonify({"success": False, "message": "Login first!"}), 401
    try:
        uid = session["user_id"]
        with db.engine.connect() as conn:
            # Check if already in wishlist
            existing = conn.execute(db.text(
                "SELECT id FROM wishlists "
                "WHERE user_id = :uid AND item_id = :iid"
            ), {"uid": uid, "iid": item_id}).fetchone()

            if existing:
                return jsonify({"success": False, "message": "Already in wishlist!"})

            conn.execute(db.text(
                "INSERT INTO wishlists (user_id, item_id) "
                "VALUES (:uid, :iid)"
            ), {"uid": uid, "iid": item_id})
            conn.commit()

        return jsonify({"success": True, "message": "Added to wishlist!"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/wishlist/remove/<int:item_id>", methods=["DELETE"])
def remove_from_wishlist(item_id):
    if not session.get("user_id"):
        return jsonify({"success": False}), 401
    try:
        with db.engine.connect() as conn:
            conn.execute(db.text(
                "DELETE FROM wishlists "
                "WHERE user_id = :uid AND item_id = :iid"
            ), {"uid": session["user_id"], "iid": item_id})
            conn.commit()
        return jsonify({"success": True, "message": "Removed!"})
    except Exception:
        return jsonify({"success": False})

# ==============================
# SALES REPORTS
# ==============================

@app.route("/api/reports/sales", methods=["GET"])
def sales_report():
    if not session.get("admin_logged_in"):
        return jsonify({"success": False}), 401
    try:
        with db.engine.connect() as conn:
            # Total revenue
            total_rev = conn.execute(db.text(
                "SELECT COALESCE(SUM(total_price), 0) FROM orders "
                "WHERE status NOT IN ('Cancelled', 'Disputed', 'Refunded')"
            )).scalar()

            # Today's revenue
            today_rev = conn.execute(db.text(
                "SELECT COALESCE(SUM(total_price), 0) FROM orders "
                "WHERE status NOT IN ('Cancelled', 'Disputed', 'Refunded') "
                "AND date_ordered >= CURRENT_DATE"
            )).scalar()

            # This week
            week_rev = conn.execute(db.text(
                "SELECT COALESCE(SUM(total_price), 0) FROM orders "
                "WHERE status NOT IN ('Cancelled', 'Disputed', 'Refunded') "
                "AND date_ordered >= CURRENT_DATE - INTERVAL '7 days'"
            )).scalar()

            # This month
            month_rev = conn.execute(db.text(
                "SELECT COALESCE(SUM(total_price), 0) FROM orders "
                "WHERE status NOT IN ('Cancelled', 'Disputed', 'Refunded') "
                "AND date_ordered >= CURRENT_DATE - INTERVAL '30 days'"
            )).scalar()

            # Total orders
            total_orders = conn.execute(db.text(
                "SELECT COUNT(*) FROM orders"
            )).scalar()

            # Completed orders
            completed = conn.execute(db.text(
                "SELECT COUNT(*) FROM orders WHERE status = 'Delivered'"
            )).scalar()

            # Pending orders
            pending = conn.execute(db.text(
                "SELECT COUNT(*) FROM orders WHERE status = 'Pending'"
            )).scalar()

            # Cancelled
            cancelled = conn.execute(db.text(
                "SELECT COUNT(*) FROM orders WHERE status = 'Cancelled'"
            )).scalar()

            # Best selling items
            best_sellers = []
            try:
                rows = conn.execute(db.text(
                    "SELECT i.name, COUNT(o.id) as order_count, "
                    "COALESCE(SUM(o.total_price), 0) as revenue "
                    "FROM orders o, items i "
                    "WHERE o.items LIKE '%' || i.name || '%' "
                    "AND o.status NOT IN ('Cancelled', 'Disputed', 'Refunded') "
                    "GROUP BY i.name "
                    "ORDER BY order_count DESC LIMIT 10"
                )).fetchall()
                best_sellers = [{"name": r[0], "orders": r[1], "revenue": float(r[2])} for r in rows]
            except Exception:
                pass

            # Daily sales last 7 days
            daily_sales = []
            try:
                rows = conn.execute(db.text(
                    "SELECT DATE(date_ordered) as day, "
                    "COUNT(*) as orders, "
                    "COALESCE(SUM(total_price), 0) as revenue "
                    "FROM orders "
                    "WHERE status NOT IN ('Cancelled', 'Disputed', 'Refunded') "
                    "AND date_ordered >= CURRENT_DATE - INTERVAL '7 days' "
                    "GROUP BY DATE(date_ordered) "
                    "ORDER BY day"
                )).fetchall()
                daily_sales = [{"date": str(r[0]), "orders": r[1], "revenue": float(r[2])} for r in rows]
            except Exception:
                pass

        return jsonify({
            "total_revenue":    float(total_rev or 0),
            "today_revenue":    float(today_rev or 0),
            "week_revenue":     float(week_rev or 0),
            "month_revenue":    float(month_rev or 0),
            "total_orders":     total_orders or 0,
            "completed_orders": completed or 0,
            "pending_orders":   pending or 0,
            "cancelled_orders": cancelled or 0,
            "best_sellers":     best_sellers,
            "daily_sales":      daily_sales
        })
    except Exception as e:
        print("Sales report error:", e)
        return jsonify({
            "total_revenue": 0, "today_revenue": 0,
            "week_revenue": 0, "month_revenue": 0,
            "total_orders": 0, "completed_orders": 0,
            "pending_orders": 0, "cancelled_orders": 0,
            "best_sellers": [], "daily_sales": []
        })

# ==============================
# ORDER TRACKING
# ==============================

@app.route("/api/orders/track/<int:order_id>", methods=["GET"])
def track_order(order_id):
    if not session.get("user_id"):
        return jsonify({"success": False}), 401
    try:
        order = Order.query.get(order_id)
        if not order or order.user_id != session["user_id"]:
            return jsonify({"success": False, "message": "Order not found!"}), 404

        # Build timeline
        steps = [
            {"step": "Order Placed",      "icon": "📋", "done": True, "date": order.date_ordered.strftime("%Y-%m-%d %H:%M")},
            {"step": "Payment Confirmed",  "icon": "💳", "done": order.status != "Pending", "date": ""},
            {"step": "Order Confirmed",    "icon": "✅", "done": order.status in ["Confirmed","Awaiting Delivery","Delivered"], "date": ""},
            {"step": "Being Prepared",     "icon": "📦", "done": order.status in ["Confirmed","Awaiting Delivery","Delivered"], "date": ""},
            {"step": "Out for Delivery",   "icon": "🚚", "done": order.status in ["Awaiting Delivery","Delivered"], "date": order.delivered_at.strftime("%Y-%m-%d %H:%M") if order.delivered_at else ""},
            {"step": "Delivered",          "icon": "🎉", "done": order.status == "Delivered", "date": ""}
        ]

        if order.status == "Cancelled":
            steps = [
                {"step": "Order Placed",  "icon": "📋", "done": True, "date": order.date_ordered.strftime("%Y-%m-%d %H:%M")},
                {"step": "Cancelled",     "icon": "❌", "done": True, "date": ""}
            ]

        if order.status == "Disputed":
            steps.append({"step": "Disputed", "icon": "⚠️", "done": True, "date": ""})

        if order.status == "Refunded":
            steps.append({"step": "Refunded", "icon": "💰", "done": True, "date": ""})

        return jsonify({
            "success": True,
            "order_id": order.id,
            "status":   order.status,
            "total":    order.total_price,
            "items":    order.items,
            "steps":    steps
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# ==============================
# DEBUG ROUTES
# =============================='''

app = app.replace(old_debug, new_routes)
print("  ✅ Added all new API routes")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(app)

print("  ✅ app.py saved!")
print("")
print("  Backend ready! Now updating frontend...")
print("  This will be in the next message...")
print("")

# Push backend first
os.system('git add .')
os.system('git commit -m "Added backend: reviews, coupons, wishlist, reports, tracking"')
os.system('git push')

print("")
print("  ========================================")
print("  PART 1 DONE - Backend Updated!")
print("  ========================================")
print("")
print("  New API Routes Added:")
print("  ⭐ /api/reviews/<item_id>     - Get reviews")
print("  ⭐ /api/reviews/add           - Add review")
print("  🎟️ /api/coupons/validate      - Check coupon")
print("  🎟️ /api/coupons/create        - Create coupon")
print("  🎟️ /api/coupons               - List coupons")
print("  ❤️ /api/wishlist              - Get wishlist")
print("  ❤️ /api/wishlist/add/<id>     - Add to wishlist")
print("  ❤️ /api/wishlist/remove/<id>  - Remove from wishlist")
print("  📊 /api/reports/sales         - Sales report")
print("  📍 /api/orders/track/<id>     - Order tracking")
print("")
print("  Render deploying backend now...")
print("  Run Part 2 script for frontend after deploy!")
print("  ========================================")
print("")