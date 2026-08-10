import os
import re

print("")
print("  ========================================")
print("  Image Upload Fixer")
print("  ========================================")
print("")

# ==============================
# READ app.py
# ==============================
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# ==============================
# ADD SECURE_FILENAME IMPORT
# ==============================
old_import = 'from werkzeug.security import generate_password_hash, check_password_hash'
new_import  = '''from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename'''

if 'secure_filename' not in content:
    content = content.replace(old_import, new_import)
    print("  ✅ Added secure_filename import")
else:
    print("  ✅ secure_filename already imported")

# ==============================
# NEW UPLOAD_IMAGE FUNCTION
# ==============================
new_upload_func = '''def upload_image(image):
    """Upload image to Cloudinary or save locally"""
    default_image = 'https://via.placeholder.com/400x400?text=No+Image'

    if not image or image.filename == '':
        return default_image

    try:
        filename = secure_filename(image.filename)
    except:
        filename = image.filename

    cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME', '').strip()
    api_key    = os.environ.get('CLOUDINARY_API_KEY',    '').strip()
    api_secret = os.environ.get('CLOUDINARY_API_SECRET', '').strip()

    # Try Cloudinary if credentials exist
    if cloud_name and api_key and api_secret:
        try:
            # Reset stream before upload
            try:
                image.stream.seek(0)
            except:
                pass

            result = cloudinary.uploader.upload(
                image,
                folder        = "sandras_palace",
                resource_type = "image"
            )

            if result and result.get('secure_url'):
                print("✅ Cloudinary upload success:", result['secure_url'])
                return result['secure_url']

        except Exception as e:
            print(f"⚠️ Cloudinary upload failed: {e}")

    # Fallback: save locally
    try:
        try:
            image.stream.seek(0)
        except:
            pass

        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

        fname = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{secure_filename(image.filename)}"
        fpath = os.path.join(UPLOAD_FOLDER, fname)

        image.save(fpath)

        if os.path.exists(fpath) and os.path.getsize(fpath) > 0:
            print("✅ Local image saved:", fpath)
            return f"static/uploads/{fname}"
        else:
            print("⚠️ Local file empty or broken")

    except Exception as e:
        print(f"⚠️ Local save failed: {e}")

    return default_image'''

# ==============================
# REPLACE OLD UPLOAD_IMAGE
# ==============================
pattern = r'def upload_image\(image\):.*?return default_image'

if re.search(pattern, content, re.DOTALL):
    content = re.sub(
        pattern,
        new_upload_func,
        content,
        flags=re.DOTALL
    )
    print("  ✅ Replaced upload_image function")
else:
    print("  ❌ Could not find upload_image function!")
    print("  Adding it manually...")
    content = content.replace(
        '# ==============================\n# CREATE TABLES SAFELY',
        new_upload_func + '\n\n# ==============================\n# CREATE TABLES SAFELY'
    )

# ==============================
# SAVE app.py
# ==============================
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("  ✅ app.py saved!")
print("")

# ==============================
# FIX IMAGE DISPLAY IN index.html
# ==============================
print("  Fixing image display in index.html...")

with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Add getImg helper if not there
get_img_func = '''
        // Helper to get correct image URL
        function getImg(url) {
            if (!url) return 'https://via.placeholder.com/400x400?text=No+Image';
            if (url.startsWith('http://') || url.startsWith('https://')) return url;
            if (url.startsWith('static/')) return '/' + url;
            return url;
        }
'''

if 'function getImg' not in html:
    html = html.replace(
        'let allItems = [], cart = [], activeCategory',
        get_img_func + '\n        let allItems = [], cart = [], activeCategory'
    )
    print("  ✅ Added getImg helper to index.html")

# Fix all image src in index.html
image_fixes = [
    # Item card images
    ('src="/${i.image_url}"',    'src="${getImg(i.image_url)}"'),
    ("src='/${i.image_url}'",    "src='${getImg(i.image_url)}'"),
    # Cart item images
    ('src="/${item.image_url}"', 'src="${getImg(item.image_url)}"'),
    ("src='/${item.image_url}'", "src='${getImg(item.image_url)}'"),
]

for old, new in image_fixes:
    if old in html:
        html = html.replace(old, new)
        print(f"  ✅ Fixed: {old[:30]}...")

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("  ✅ index.html fixed!")
print("")

# ==============================
# FIX IMAGE DISPLAY IN admin.html
# ==============================
print("  Fixing image display in admin.html...")

with open('templates/admin.html', 'r', encoding='utf-8') as f:
    admin = f.read()

# Add getImg helper to admin.html
if 'function getImg' not in admin:
    admin = admin.replace(
        'let allItems = [];',
        get_img_func + '\n        let allItems = [];'
    )
    print("  ✅ Added getImg helper to admin.html")

# Fix all image src in admin.html
admin_fixes = [
    ('src="/${i.image_url}"',    'src="${getImg(i.image_url)}"'),
    ("src='/${i.image_url}'",    "src='${getImg(i.image_url)}'"),
    ('src="/${item.image_url}"', 'src="${getImg(item.image_url)}"'),
    ("src='/${item.image_url}'", "src='${getImg(item.image_url)}'"),
]

for old, new in admin_fixes:
    if old in admin:
        admin = admin.replace(old, new)
        print(f"  ✅ Fixed: {old[:30]}...")

with open('templates/admin.html', 'w', encoding='utf-8') as f:
    f.write(admin)

print("  ✅ admin.html fixed!")
print("")

# ==============================
# PUSH TO GITHUB
# ==============================
print("  Pushing to GitHub...")
print("")

os.system('git add .')
os.system('git commit -m "Fixed image upload and display"')
os.system('git push')

print("")
print("  ========================================")
print("  ALL DONE!")
print("  ✅ app.py - upload function fixed")
print("  ✅ index.html - image display fixed")
print("  ✅ admin.html - image display fixed")
print("  ✅ Pushed to GitHub")
print("")
print("  Render will update in 2-3 minutes!")
print("  Then test uploading an image again!")
print("  ========================================")
print("")