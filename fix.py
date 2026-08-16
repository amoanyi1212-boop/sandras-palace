import os

print("Checking app.py for issues...")

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Check for common issues
issues = []

if 'def get_orders' not in content:
    issues.append("get_orders function MISSING!")

if 'def get_items' not in content:
    issues.append("get_items function MISSING!")

if 'def get_users' not in content:
    issues.append("get_users function MISSING!")

if content.count('def get_orders') > 1:
    issues.append("DUPLICATE get_orders function!")

if issues:
    print("Issues found:")
    for i in issues:
        print("  ❌", i)
    print("")
    print("  Need to fix app.py!")
else:
    print("  ✅ All functions present")
    print("  Issue might be in admin.html")

print("")
print("Checking admin.html...")

with open('templates/admin.html', 'r', encoding='utf-8') as f:
    admin = f.read()

if 'loadOrders' not in admin:
    print("  ❌ loadOrders MISSING!")
elif admin.count('function loadOrders') > 1:
    print("  ❌ DUPLICATE loadOrders!")
else:
    print("  ✅ loadOrders present")

if 'loadDashboard' not in admin:
    print("  ❌ loadDashboard MISSING!")
else:
    print("  ✅ loadDashboard present")

print("")
print("Results above - paste them here!")