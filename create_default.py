# create_default.py
# Run this once to create a default image

from PIL import Image, ImageDraw, ImageFont
import os

# Make sure uploads folder exists
os.makedirs('static/uploads', exist_ok=True)

# Create a simple default image
img = Image.new('RGB', (400, 400), color='#f0f2f5')
draw = ImageDraw.Draw(img)

# Draw a shopping bag emoji style
draw.rectangle([100, 150, 300, 350], fill='#1a1a2e', outline='#0f3460', width=3)
draw.rectangle([150, 130, 250, 160], fill='none', outline='#1a1a2e', width=8)

# Add text
draw.text((200, 370), "No Image", fill='#888888', anchor='mm')

# Save
img.save('static/uploads/default.png')
print("✅ Default image created!")