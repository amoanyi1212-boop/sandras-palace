import os

print("Fixing placeholder images...")

# Fix index.html
with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace all placeholder URLs
html = html.replace(
    "https://via.placeholder.com/400?text=No+Image",
    "/static/noimg.png"
)
html = html.replace(
    "https://via.placeholder.com/400x400?text=No+Image",
    "/static/noimg.png"
)
html = html.replace(
    "https://via.placeholder.com/240x210?text=No+Image",
    "/static/noimg.png"
)
html = html.replace(
    "https://via.placeholder.com/600x300?text=No+Image",
    "/static/noimg.png"
)
html = html.replace(
    "https://via.placeholder.com/70?text=?",
    "/static/noimg.png"
)

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Fixed index.html")

# Fix admin.html
with open('templates/admin.html', 'r', encoding='utf-8') as f:
    admin = f.read()

admin = admin.replace(
    "https://via.placeholder.com/250x180?text=No+Image",
    "/static/noimg.png"
)
admin = admin.replace(
    "https://via.placeholder.com/400x400?text=No+Image",
    "/static/noimg.png"
)

with open('templates/admin.html', 'w', encoding='utf-8') as f:
    f.write(admin)

print("Fixed admin.html")

# Fix app.py
with open('app.py', 'r', encoding='utf-8') as f:
    app = f.read()

app = app.replace(
    '"https://via.placeholder.com/400x400?text=No+Image"',
    '"/static/noimg.png"'
)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(app)

print("Fixed app.py")

# Create a simple no-image PNG using Python
print("Creating noimg.png...")
try:
    from PIL import Image, ImageDraw
    img = Image.new('RGB', (400, 400), color='#fce4ec')
    draw = ImageDraw.Draw(img)
    # Draw a simple camera icon shape
    draw.rectangle([120, 140, 280, 260], outline='#e91e63', width=5)
    draw.ellipse([160, 160, 240, 240], outline='#e91e63', width=5)
    draw.text((140, 275), "No Image", fill='#e91e63')
    img.save('static/noimg.png')
    print("Created noimg.png with PIL")
except Exception as e:
    print("PIL failed:", e)
    # Create minimal PNG without PIL
    import struct
    import zlib

    def create_simple_png():
        # Minimal valid pink PNG 1x1 pixel
        def png_chunk(chunk_type, data):
            chunk_len = struct.pack('>I', len(data))
            chunk_data = chunk_type + data
            chunk_crc = struct.pack('>I', zlib.crc32(chunk_data) & 0xffffffff)
            return chunk_len + chunk_data + chunk_crc

        signature = b'\x89PNG\r\n\x1a\n'
        ihdr = png_chunk(b'IHDR', struct.pack('>IIBBBBB', 1, 1, 8, 2, 0, 0, 0))
        raw_data = b'\x00\xe9\x1e\x63'
        compressed = zlib.compress(raw_data)
        idat = png_chunk(b'IDAT', compressed)
        iend = png_chunk(b'IEND', b'')
        return signature + ihdr + idat + iend

    with open('static/noimg.png', 'wb') as f:
        f.write(create_simple_png())
    print("Created minimal noimg.png")

# Update .gitignore to include noimg.png
with open('.gitignore', 'r') as f:
    gi = f.read()

if 'noimg.png' not in gi:
    with open('.gitignore', 'a') as f:
        f.write('\n# Keep no-image placeholder\n!static/noimg.png\n')
    print("Updated .gitignore")

# Push
os.system('git add .')
os.system('git commit -m "Fixed placeholder images - removed via.placeholder.com"')
os.system('git push')

print("")
print("ALL DONE!")
print("Render updates in 2-3 minutes!")