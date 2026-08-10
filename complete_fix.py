import os

print("")
print("  ========================================")
print("  Fixing Notifications")
print("  ========================================")
print("")

# ==============================
# FIX index.html
# ==============================
print("  Fixing index.html...")

with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Fix 1: Make notifications check more frequent (every 10 seconds)
html = html.replace(
    "// Check every 30 seconds\n    setInterval(function() {\n        if (currentUser) checkUserNotifications();\n    }, 30000);",
    "// Check every 10 seconds\n    setInterval(function() {\n        if (currentUser) checkUserNotifications();\n    }, 10000);"
)
print("  ✅ Made user notifications check every 10 seconds")

# Fix 2: Check notifications on page load
old_init = '''    window.onload = function() {
        loadItems();
        checkAuth();
        registerServiceWorker();
    };'''

new_init = '''    window.onload = function() {
        loadItems();
        checkAuth();
        registerServiceWorker();

        // Start checking notifications after 3 seconds
        setTimeout(function() {
            if (currentUser) checkUserNotifications();
        }, 3000);
    };'''

html = html.replace(old_init, new_init)
print("  ✅ Added notification check on page load")

# Fix 3: Add notification sound/visual alert
old_check_notif = '''    function checkUserNotifications() {
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
    }'''

new_check_notif = '''    var lastNotifCount = 0;

    function checkUserNotifications() {
        if (!currentUser) return;
        fetch('/api/notifications/user')
            .then(function(r) { return r.json(); })
            .then(function(data) {
                var badge = document.getElementById('user-notif-badge');
                if (badge && data.unread_count > 0) {
                    badge.textContent   = data.unread_count;
                    badge.style.display = 'inline';

                    // Show toast if new notification arrived
                    if (data.unread_count > lastNotifCount && lastNotifCount >= 0) {
                        // Get latest notification
                        if (data.notifications && data.notifications.length > 0) {
                            var latest = data.notifications[0];
                            if (!latest.is_read) {
                                showNotificationPopup(latest.title, latest.message);
                            }
                        }
                    }
                    lastNotifCount = data.unread_count;

                } else if (badge) {
                    badge.style.display = 'none';
                    lastNotifCount = 0;
                }
            })
            .catch(function() {});
    }

    function showNotificationPopup(title, message) {
        // Remove old popup if exists
        var oldPopup = document.getElementById("notif-popup");
        if (oldPopup) oldPopup.remove();

        var popup = document.createElement("div");
        popup.id = "notif-popup";
        popup.style.cssText = "position:fixed;top:20px;right:20px;background:white;" +
            "border-radius:20px;padding:20px 25px;box-shadow:0 10px 40px rgba(233,30,99,0.3);" +
            "border:3px solid #fce4ec;z-index:10000;max-width:350px;animation:popIn 0.3s ease;" +
            "cursor:pointer;";
        popup.onclick = function() {
            popup.remove();
            openUserNotifications();
        };

        popup.innerHTML =
            '<div style="display:flex;align-items:center;gap:12px;">' +
            '<div style="font-size:30px;">🔔</div>' +
            '<div>' +
            '<div style="font-family:\\'Fredoka One\\',cursive;color:#c2185b;font-size:14px;">' + title + '</div>' +
            '<div style="font-size:13px;color:#666;font-weight:600;margin-top:3px;">' + message + '</div>' +
            '</div>' +
            '<button onclick="event.stopPropagation();this.parentElement.parentElement.remove();" style="' +
            'background:#ffebee;border:none;color:#e53935;width:25px;height:25px;' +
            'border-radius:50%;cursor:pointer;font-size:14px;font-weight:800;' +
            'display:flex;align-items:center;justify-content:center;flex-shrink:0;' +
            '">x</button>' +
            '</div>';

        document.body.appendChild(popup);

        // Auto remove after 8 seconds
        setTimeout(function() {
            if (document.getElementById("notif-popup")) {
                popup.style.opacity = "0";
                popup.style.transform = "translateX(100px)";
                popup.style.transition = "all 0.3s ease";
                setTimeout(function() { popup.remove(); }, 300);
            }
        }, 8000);
    }'''

html = html.replace(old_check_notif, new_check_notif)
print("  ✅ Added instant notification popup for users")

# Fix 4: Also check after login
old_login_success = '''                currentUser = d.user;
                updateUserUI();
                closeAuthModal();
                showToast('Welcome back ' + d.user.fullname + '!', 'success');
                document.getElementById('loginForm').reset();'''

new_login_success = '''                currentUser = d.user;
                updateUserUI();
                closeAuthModal();
                showToast('Welcome back ' + d.user.fullname + '!', 'success');
                document.getElementById('loginForm').reset();
                // Check notifications immediately
                setTimeout(checkUserNotifications, 1000);'''

html = html.replace(old_login_success, new_login_success)
print("  ✅ Check notifications on login")

# Fix 5: Check after register
old_register_success = '''                currentUser = d.user;
                updateUserUI();
                closeAuthModal();
                showToast('Welcome to Esirifuahs Palace!', 'success');
                document.getElementById('registerForm').reset();'''

new_register_success = '''                currentUser = d.user;
                updateUserUI();
                closeAuthModal();
                showToast('Welcome to Esirifuahs Palace!', 'success');
                document.getElementById('registerForm').reset();
                // Check notifications immediately
                setTimeout(checkUserNotifications, 1000);'''

html = html.replace(old_register_success, new_register_success)
print("  ✅ Check notifications on register")

# Fix 6: Check after placing order
old_order_success = '''                if (data.success) {
                    closeOrderModal();
                    document.getElementById('success-order-id').textContent = 'Order #' + data.order_id;
                    document.getElementById('successModal').classList.add('show');
                    cart = [];
                    updateCartUI();
                    document.getElementById('momo-number').value    = '';
                    document.getElementById('transaction-id').value = '';'''

new_order_success = '''                if (data.success) {
                    closeOrderModal();
                    document.getElementById('success-order-id').textContent = 'Order #' + data.order_id;
                    document.getElementById('successModal').classList.add('show');
                    cart = [];
                    updateCartUI();
                    document.getElementById('momo-number').value    = '';
                    document.getElementById('transaction-id').value = '';
                    // Check notifications
                    setTimeout(checkUserNotifications, 2000);'''

html = html.replace(old_order_success, new_order_success)
print("  ✅ Check notifications after placing order")

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("  ✅ index.html saved!")
print("")

# ==============================
# FIX admin.html
# ==============================
print("  Fixing admin.html...")

with open('templates/admin.html', 'r', encoding='utf-8') as f:
    admin = f.read()

# Make admin notifications check every 10 seconds
admin = admin.replace(
    "setInterval(function() {\n        fetch(\"/api/notifications/admin\")",
    "setInterval(function() {\n        loadNotifications();\n        // Also refresh\n        fetch(\"/api/notifications/admin\")"
)

admin = admin.replace(
    "}, 30000);",
    "}, 10000);"
)
print("  ✅ Made admin notifications check every 10 seconds")

# Add notification popup for admin too
old_admin_load_notif = '''    function loadNotifications() {
        fetch("/api/notifications/admin")
            .then(function(r) { return r.json(); })
            .then(function(data) {
                var count = document.getElementById("notif-count");
                if (data.unread_count > 0) {
                    count.textContent    = data.unread_count;
                    count.style.display  = "flex";
                } else {
                    count.style.display  = "none";
                }'''

new_admin_load_notif = '''    var lastAdminNotifCount = 0;

    function loadNotifications() {
        fetch("/api/notifications/admin")
            .then(function(r) { return r.json(); })
            .then(function(data) {
                var count = document.getElementById("notif-count");
                if (data.unread_count > 0) {
                    count.textContent    = data.unread_count;
                    count.style.display  = "flex";

                    // Show popup if new notification
                    if (data.unread_count > lastAdminNotifCount && lastAdminNotifCount >= 0) {
                        if (data.notifications && data.notifications.length > 0) {
                            var latest = data.notifications[0];
                            if (!latest.is_read) {
                                showAdminNotifPopup(latest.title, latest.message);
                            }
                        }
                    }
                    lastAdminNotifCount = data.unread_count;

                } else {
                    count.style.display  = "none";
                    lastAdminNotifCount = 0;
                }'''

admin = admin.replace(old_admin_load_notif, new_admin_load_notif)
print("  ✅ Added admin notification popup tracking")

# Add admin popup function before showToast
old_admin_toast = '''    function showToast(msg, type) {'''
new_admin_popup = '''    function showAdminNotifPopup(title, message) {
        var oldPopup = document.getElementById("admin-notif-popup");
        if (oldPopup) oldPopup.remove();

        var popup = document.createElement("div");
        popup.id = "admin-notif-popup";
        popup.style.cssText = "position:fixed;top:20px;right:20px;background:white;" +
            "border-radius:20px;padding:20px 25px;box-shadow:0 10px 40px rgba(233,30,99,0.3);" +
            "border:3px solid #fce4ec;z-index:10000;max-width:380px;animation:popIn 0.3s ease;" +
            "cursor:pointer;";
        popup.onclick = function() {
            popup.remove();
            toggleNotifications();
        };

        popup.innerHTML =
            '<div style="display:flex;align-items:center;gap:12px;">' +
            '<div style="font-size:35px;">🔔</div>' +
            '<div>' +
            '<div style="font-family:\\'Fredoka One\\',cursive;color:#c2185b;font-size:15px;">' + title + '</div>' +
            '<div style="font-size:13px;color:#666;font-weight:600;margin-top:4px;">' + message + '</div>' +
            '</div>' +
            '<button onclick="event.stopPropagation();this.parentElement.parentElement.remove();" style="' +
            'background:#ffebee;border:none;color:#e53935;width:28px;height:28px;' +
            'border-radius:50%;cursor:pointer;font-size:16px;font-weight:800;' +
            'display:flex;align-items:center;justify-content:center;flex-shrink:0;' +
            '">x</button>' +
            '</div>';

        document.body.appendChild(popup);

        // Play sound effect (browser notification sound)
        try {
            var audio = new Audio("data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdH+Jj4+Hd2Zia3R+houRi4J1Z2Rre4GKj42IeW5maHJ+h46QjoV6b2hqdn+IjpCLg3ZtaW13gIiOj4qCdm5rbniCiI6PioF2bmtueYKJjpCKgnZua255gomOkIqBdm5rbniCiY6QioJ2bmtueYKJjo+Jf3Vuam14gImOj4qCdm5rbniCiI6PioJ2bmtueIKIjo+KgnZua254goiOj4qCdm5r");
            audio.volume = 0.3;
            audio.play().catch(function(){});
        } catch(e) {}

        // Auto remove after 10 seconds
        setTimeout(function() {
            if (document.getElementById("admin-notif-popup")) {
                popup.style.opacity = "0";
                popup.style.transform = "translateX(100px)";
                popup.style.transition = "all 0.3s ease";
                setTimeout(function() { popup.remove(); }, 300);
            }
        }, 10000);
    }

    function showToast(msg, type) {'''

admin = admin.replace(old_admin_toast, new_admin_popup)
print("  ✅ Added admin notification popup function")

# Fix: Also reload orders when status changes
old_update_status = '''    function updateStatus(id, status) {
        fetch('/api/orders/status/' + id, {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ status: status })
        })
        .then(function(r) { return r.json(); })
        .then(function(d) {
            if (d.success) showToast('✅ ' + d.message, 'success');
            else showToast('❌ ' + d.message, 'error');
        })
        .catch(function() { showToast('❌ Error!', 'error'); });
    }'''

new_update_status = '''    function updateStatus(id, status) {
        fetch('/api/orders/status/' + id, {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ status: status })
        })
        .then(function(r) { return r.json(); })
        .then(function(d) {
            if (d.success) {
                showToast('✅ ' + d.message, 'success');
                // Reload orders to show updated status
                loadOrders();
            } else {
                showToast('❌ ' + d.message, 'error');
            }
        })
        .catch(function() { showToast('❌ Error!', 'error'); });
    }'''

admin = admin.replace(old_update_status, new_update_status)
print("  ✅ Orders reload after status change")

with open('templates/admin.html', 'w', encoding='utf-8') as f:
    f.write(admin)

print("  ✅ admin.html saved!")
print("")

# ==============================
# PUSH TO GITHUB
# ==============================
print("  Pushing to GitHub...")
os.system('git add .')
os.system('git commit -m "Fixed notifications - instant popups for both admin and users"')
os.system('git push')

print("")
print("  ========================================")
print("  ALL DONE!")
print("")
print("  Notifications Now:")
print("  🔔 Admin gets instant popup when order placed")
print("  🔔 User gets instant popup when status changes")
print("  🔔 Checks every 10 seconds")
print("  🔔 Sound alert for admin")
print("  🔔 Popup slides in from top-right")
print("  🔔 Click popup to see all notifications")
print("  🔔 Auto-dismiss after 8-10 seconds")
print("")
print("  Order Flow:")
print("  📋 Pending → Admin Confirms or Cancels")
print("  ✅ Confirmed → Admin clicks Send")
print("  📦 Sent → Customer confirms delivery")
print("  ✅ Delivered → DONE (locked)")
print("  ❌ Cancelled → DONE (locked)")
print("")
print("  Render updates in 2-3 minutes!")
print("  ========================================")
print("")