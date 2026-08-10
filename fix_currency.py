import os

files_to_update = [
    "templates/index.html",
    "templates/admin.html",
]

replacements = [
    # JavaScript template literal price displays
    ['$${i.price.toFixed(2)}', 'GH₵ ${i.price.toFixed(2)}'],
    ['$${item.price.toFixed(2)}', 'GH₵ ${item.price.toFixed(2)}'],
    ['$${o.total_price.toFixed(2)}', 'GH₵ ${o.total_price.toFixed(2)}'],
    ['$${(i.price * i.quantity).toFixed(2)}', 'GH₵ ${(i.price * i.quantity).toFixed(2)}'],
    ['$${(item.price * item.quantity).toFixed(2)}', 'GH₵ ${(item.price * item.quantity).toFixed(2)}'],

    # Cart totals
    ["'$' + tp.toFixed(2)", "'GH₵ ' + tp.toFixed(2)"],
    ["'$' + totalPrice.toFixed(2)", "'GH₵ ' + totalPrice.toFixed(2)"],
    ["'$0.00'", "'GH₵ 0.00'"],
    ["$0.00", "GH₵ 0.00"],

    # Form labels
    ["Price ($) *", "Price (GH₵) *"],
    ["Price ($)", "Price (GH₵)"],
    ['💰 Price ($) *', '💰 Price (GH₵) *'],
    ['💰 Price ($)', '💰 Price (GH₵)'],
    ['💰 Price *', '💰 Price (GH₵) *'],
]

print("")
print("  ========================================")
print("  Currency Changer - Ghana Cedis GH₵")
print("  ========================================")
print("")

for filepath in files_to_update:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        changes = 0
        for old, new in replacements:
            if old in content:
                content = content.replace(old, new)
                changes += 1

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"  ✅ Updated: {filepath} ({changes} changes)")
    except Exception as e:
        print(f"  ❌ Error with {filepath}: {e}")

print("")
print("  ✅ Currency changed to Ghana Cedis GH₵!")
print("")

# Push to GitHub
print("  Pushing to GitHub...")
os.system('git add .')
os.system('git commit -m "Changed currency to Ghana Cedis GH₵"')
os.system('git push')

print("")
print("  ========================================")
print("  ALL DONE!")
print("  Currency: $ → GH₵")
print("  Render updates in 2-3 minutes!")
print("  ========================================")
print("")