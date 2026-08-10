@echo off
echo.
echo  ========================================
echo   Esirifuah's Palace - PWA Installer
echo  ========================================
echo.

:: Change to correct directory
cd /d "%~dp0"
echo  Working in: %CD%
echo.

:: ==============================
:: STEP 1 - CREATE PYTHON SCRIPT
:: FOR ICONS
:: ==============================
echo  Step 1: Creating app icons...

echo from PIL import Image, ImageDraw > create_pwa.py
echo import os >> create_pwa.py
echo. >> create_pwa.py
echo def create_icon(size, filename): >> create_pwa.py
echo     # Create pink gradient background >> create_pwa.py
echo     img = Image.new('RGB', (size, size), color='#e91e63') >> create_pwa.py
echo     draw = ImageDraw.Draw(img) >> create_pwa.py
echo. >> create_pwa.py
echo     # Draw orange circle >> create_pwa.py
echo     margin = size // 8 >> create_pwa.py
echo     draw.ellipse( >> create_pwa.py
echo         [margin, margin, size-margin, size-margin], >> create_pwa.py
echo         fill='#ff6f00' >> create_pwa.py
echo     ) >> create_pwa.py
echo. >> create_pwa.py
echo     # Draw inner pink circle >> create_pwa.py
echo     margin2 = size // 4 >> create_pwa.py
echo     draw.ellipse( >> create_pwa.py
echo         [margin2, margin2, size-margin2, size-margin2], >> create_pwa.py
echo         fill='#e91e63' >> create_pwa.py
echo     ) >> create_pwa.py
echo. >> create_pwa.py
echo     # Draw E letter >> create_pwa.py
echo     from PIL import ImageFont >> create_pwa.py
echo     font_size = size // 3 >> create_pwa.py
echo     try: >> create_pwa.py
echo         font = ImageFont.truetype("arial.ttf", font_size) >> create_pwa.py
echo     except: >> create_pwa.py
echo         try: >> create_pwa.py
echo             font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size) >> create_pwa.py
echo         except: >> create_pwa.py
echo             font = ImageFont.load_default() >> create_pwa.py
echo. >> create_pwa.py
echo     text = "E" >> create_pwa.py
echo     bbox = draw.textbbox((0, 0), text, font=font) >> create_pwa.py
echo     text_width = bbox[2] - bbox[0] >> create_pwa.py
echo     text_height = bbox[3] - bbox[1] >> create_pwa.py
echo     x = (size - text_width) // 2 >> create_pwa.py
echo     y = (size - text_height) // 2 >> create_pwa.py
echo     draw.text((x, y), text, fill='white', font=font) >> create_pwa.py
echo. >> create_pwa.py
echo     # Save >> create_pwa.py
echo     img.save(filename) >> create_pwa.py
echo     print(f"Created: {filename}") >> create_pwa.py
echo. >> create_pwa.py
echo os.makedirs('static', exist_ok=True) >> create_pwa.py
echo create_icon(192, 'static/icon-192.png') >> create_pwa.py
echo create_icon(512, 'static/icon-512.png') >> create_pwa.py
echo print("All icons created!") >> create_pwa.py

:: Run the icon creator
python create_pwa.py

:: Clean up
del create_pwa.py

echo  Icons created!
echo.

:: ==============================
:: STEP 2 - CREATE manifest.json
:: ==============================
echo  Step 2: Creating manifest.json...

echo { > static\manifest.json
echo     "name": "Esirifuah's Palace", >> static\manifest.json
echo     "short_name": "Esirifuah's", >> static\manifest.json
echo     "description": "Shop with Love at Esirifuah's Palace", >> static\manifest.json
echo     "start_url": "/", >> static\manifest.json
echo     "display": "standalone", >> static\manifest.json
echo     "background_color": "#fff5f7", >> static\manifest.json
echo     "theme_color": "#e91e63", >> static\manifest.json
echo     "orientation": "portrait", >> static\manifest.json
echo     "icons": [ >> static\manifest.json
echo         { >> static\manifest.json
echo             "src": "/static/icon-192.png", >> static\manifest.json
echo             "sizes": "192x192", >> static\manifest.json
echo             "type": "image/png", >> static\manifest.json
echo             "purpose": "any maskable" >> static\manifest.json
echo         }, >> static\manifest.json
echo         { >> static\manifest.json
echo             "src": "/static/icon-512.png", >> static\manifest.json
echo             "sizes": "512x512", >> static\manifest.json
echo             "type": "image/png", >> static\manifest.json
echo             "purpose": "any maskable" >> static\manifest.json
echo         } >> static\manifest.json
echo     ] >> static\manifest.json
echo } >> static\manifest.json

echo  manifest.json created!
echo.

:: ==============================
:: STEP 3 - CREATE sw.js
:: ==============================
echo  Step 3: Creating service worker...

echo const CACHE_NAME = "esirifuahs-palace-v1"; > static\sw.js
echo const urlsToCache = ["/", "/static/manifest.json", "/static/icon-192.png", "/static/icon-512.png"]; >> static\sw.js
echo. >> static\sw.js
echo self.addEventListener("install", function(event) { >> static\sw.js
echo     event.waitUntil( >> static\sw.js
echo         caches.open(CACHE_NAME).then(function(cache) { >> static\sw.js
echo             return cache.addAll(urlsToCache); >> static\sw.js
echo         }) >> static\sw.js
echo     ); >> static\sw.js
echo }); >> static\sw.js
echo. >> static\sw.js
echo self.addEventListener("fetch", function(event) { >> static\sw.js
echo     event.respondWith( >> static\sw.js
echo         caches.match(event.request).then(function(response) { >> static\sw.js
echo             if (response) { return response; } >> static\sw.js
echo             return fetch(event.request); >> static\sw.js
echo         }) >> static\sw.js
echo     ); >> static\sw.js
echo }); >> static\sw.js
echo. >> static\sw.js
echo self.addEventListener("activate", function(event) { >> static\sw.js
echo     event.waitUntil( >> static\sw.js
echo         caches.keys().then(function(cacheNames) { >> static\sw.js
echo             return Promise.all( >> static\sw.js
echo                 cacheNames.filter(function(cacheName) { >> static\sw.js
echo                     return cacheName !== CACHE_NAME; >> static\sw.js
echo                 }).map(function(cacheName) { >> static\sw.js
echo                     return caches.delete(cacheName); >> static\sw.js
echo                 }) >> static\sw.js
echo             ); >> static\sw.js
echo         }) >> static\sw.js
echo     ); >> static\sw.js
echo }); >> static\sw.js

echo  sw.js created!
echo.

:: ==============================
:: STEP 4 - UPDATE index.html
:: ==============================
echo  Step 4: Updating index.html...

:: Create Python script to update index.html
echo import re > update_html.py
echo. >> update_html.py
echo with open('templates/index.html', 'r', encoding='utf-8') as f: >> update_html.py
echo     content = f.read() >> update_html.py
echo. >> update_html.py
echo # Add PWA meta tags to head >> update_html.py
echo pwa_head = ''' >> update_html.py
echo     ^<^!-- PWA Support --^> >> update_html.py
echo     ^<link rel="manifest" href="/static/manifest.json"^> >> update_html.py
echo     ^<meta name="theme-color" content="#e91e63"^> >> update_html.py
echo     ^<meta name="apple-mobile-web-app-capable" content="yes"^> >> update_html.py
echo     ^<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent"^> >> update_html.py
echo     ^<meta name="apple-mobile-web-app-title" content="Esirifuah Palace"^> >> update_html.py
echo     ^<link rel="apple-touch-icon" href="/static/icon-192.png"^>''' >> update_html.py
echo. >> update_html.py
echo # Add PWA install banner before body close >> update_html.py
echo pwa_body = ''' >> update_html.py
echo     ^<^!-- PWA Install Banner --^> >> update_html.py
echo     ^<div id="install-banner" style="display:none;position:fixed;bottom:20px;left:50%;transform:translateX(-50%);background:linear-gradient(135deg,#e91e63,#ff6f00);color:white;padding:15px 25px;border-radius:25px;box-shadow:0 8px 30px rgba(233,30,99,0.4);z-index:9999;align-items:center;gap:12px;font-family:'Nunito',sans-serif;font-weight:800;font-size:15px;animation:slideUp 0.5s ease;"^> >> update_html.py
echo         ^<span style="font-size:25px"^>^</span^> >> update_html.py
echo         ^<div^> >> update_html.py
echo             ^<div^>Add to Home Screen!^</div^> >> update_html.py
echo             ^<div style="font-size:12px;opacity:0.8"^>Install Esirifuah Palace as an app^</div^> >> update_html.py
echo         ^</div^> >> update_html.py
echo         ^<button onclick="installApp()" style="background:white;color:#e91e63;border:none;padding:8px 18px;border-radius:15px;font-weight:800;cursor:pointer;font-family:'Nunito';font-size:14px;"^>Install ^</button^> >> update_html.py
echo         ^<button onclick="dismissBanner()" style="background:rgba(255,255,255,0.2);color:white;border:none;padding:8px 12px;border-radius:15px;font-weight:800;cursor:pointer;font-size:14px;"^>^</button^> >> update_html.py
echo     ^</div^> >> update_html.py
echo     ^<style^> >> update_html.py
echo     @keyframes slideUp { from { transform:translateX(-50%) translateY(100px);opacity:0; } to { transform:translateX(-50%) translateY(0);opacity:1; } } >> update_html.py
echo     ^</style^> >> update_html.py
echo     ^<script^> >> update_html.py
echo     let deferredPrompt; >> update_html.py
echo     if ('serviceWorker' in navigator) { >> update_html.py
echo         window.addEventListener('load', function() { >> update_html.py
echo             navigator.serviceWorker.register('/static/sw.js') >> update_html.py
echo                 .then(function(reg) { console.log('SW registered!'); }) >> update_html.py
echo                 .catch(function(err) { console.log('SW error:', err); }); >> update_html.py
echo         }); >> update_html.py
echo     } >> update_html.py
echo     window.addEventListener('beforeinstallprompt', function(e) { >> update_html.py
echo         e.preventDefault(); >> update_html.py
echo         deferredPrompt = e; >> update_html.py
echo         var banner = document.getElementById('install-banner'); >> update_html.py
echo         banner.style.display = 'flex'; >> update_html.py
echo     }); >> update_html.py
echo     function installApp() { >> update_html.py
echo         document.getElementById('install-banner').style.display = 'none'; >> update_html.py
echo         if (deferredPrompt) { >> update_html.py
echo             deferredPrompt.prompt(); >> update_html.py
echo             deferredPrompt.userChoice.then(function(result) { >> update_html.py
echo                 console.log('Install result:', result.outcome); >> update_html.py
echo                 deferredPrompt = null; >> update_html.py
echo             }); >> update_html.py
echo         } >> update_html.py
echo     } >> update_html.py
echo     function dismissBanner() { >> update_html.py
echo         document.getElementById('install-banner').style.display = 'none'; >> update_html.py
echo     } >> update_html.py
echo     window.addEventListener('appinstalled', function() { >> update_html.py
echo         document.getElementById('install-banner').style.display = 'none'; >> update_html.py
echo     }); >> update_html.py
echo     ^</script^>''' >> update_html.py
echo. >> update_html.py
echo # Only add if not already added >> update_html.py
echo if 'manifest.json' not in content: >> update_html.py
echo     content = content.replace('</head>', pwa_head + '\n</head>') >> update_html.py
echo     content = content.replace('</body>', pwa_body + '\n</body>') >> update_html.py
echo     print('PWA added to index.html!') >> update_html.py
echo else: >> update_html.py
echo     print('PWA already exists in index.html!') >> update_html.py
echo. >> update_html.py
echo with open('templates/index.html', 'w', encoding='utf-8') as f: >> update_html.py
echo     f.write(content) >> update_html.py

python update_html.py
del update_html.py

echo  index.html updated!
echo.

:: ==============================
:: STEP 5 - UPDATE .gitignore
:: ==============================
echo  Step 5: Updating .gitignore...

echo. >> .gitignore
echo # Keep PWA icons >> .gitignore
echo !static/icon-192.png >> .gitignore
echo !static/icon-512.png >> .gitignore
echo !static/manifest.json >> .gitignore
echo !static/sw.js >> .gitignore

echo  .gitignore updated!
echo.

:: ==============================
:: STEP 6 - GIT PUSH
:: ==============================
echo  Step 6: Pushing to GitHub...
echo.

git add .
git commit -m "Added PWA - Install as App support"
git push

echo.
echo  ========================================
echo   ALL DONE! PWA Successfully Added!
echo  ========================================
echo.
echo   What happens next:
echo   1. Render will redeploy in 2-3 minutes
echo   2. Visit your site on a phone
echo   3. Android: A banner will appear
echo      asking to install the app
echo   4. iPhone: Tap Share then
echo      Add to Home Screen
echo   5. An app icon will appear!
echo  ========================================
echo.
pause