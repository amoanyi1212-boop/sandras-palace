import os

print("")
print("  ========================================")
print("  Mobile Optimization")
print("  ========================================")
print("")

# ==============================
# FIX index.html
# ==============================
print("  Optimizing index.html for mobile...")

with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace the existing media query with comprehensive mobile styles
old_media = '''@media(max-width:768px){.hero h2{font-size:30px}.header-search{display:none}.cart-sidebar{width:100%;right:-100%;border-radius:0}.cart-head{border-radius:0}.items-grid{grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:15px}.container{padding:20px 15px}.item-img{height:150px}}'''

new_media = '''/* ===== TABLET ===== */
        @media(max-width:900px){
            .hero h2{font-size:36px}
            .items-grid{grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:20px}
        }

        /* ===== MOBILE ===== */
        @media(max-width:768px){
            /* Header */
            .header{padding:0 15px}
            .header-inner{height:65px}
            .header-search{display:none}
            .logo h1{font-size:18px}
            .logo-icon{font-size:28px}
            .logo p{display:none}
            .hdr-btn{padding:8px 12px;font-size:13px;gap:5px;border-radius:12px}
            .cart-count{width:20px;height:20px;font-size:10px;top:-6px;right:-6px}
            .notif-dot{min-width:18px;height:18px;font-size:9px}
            .header-right{gap:8px}

            /* Hero */
            .hero{padding:40px 20px}
            .hero h2{font-size:28px;margin-bottom:10px}
            .hero p{font-size:14px;margin-bottom:20px}
            .hero-search{flex-direction:column}
            .hero-search input{padding:14px 20px;font-size:14px}
            .hero-search button{padding:14px 20px;font-size:14px}

            /* Categories */
            .categories-bar{padding:12px 15px}
            .cat-btn{padding:8px 16px;font-size:12px}

            /* Container */
            .container{padding:20px 15px}
            .section-title h2{font-size:20px}

            /* Items Grid */
            .items-grid{grid-template-columns:repeat(2,1fr);gap:12px}
            .item-img{height:150px}
            .item-body{padding:12px}
            .item-name{font-size:14px}
            .item-price{font-size:18px}
            .item-desc{font-size:11px;margin-bottom:8px;-webkit-line-clamp:1}
            .item-cat{font-size:10px;margin-bottom:4px}
            .add-btn{padding:8px 12px;font-size:12px;border-radius:10px}
            .item-card:hover{transform:none}
            .oos-badge{padding:4px 10px;font-size:10px;top:10px;right:10px}

            /* Cart Sidebar */
            .cart-sidebar{width:100%;right:-100%;border-radius:0}
            .cart-head{border-radius:0;padding:20px}
            .cart-head h2{font-size:18px}
            .c-item{padding:12px 0}
            .c-img{width:55px;height:55px;border-radius:10px}
            .c-name{font-size:13px}
            .c-price{font-size:12px}
            .q-btn{width:26px;height:26px;font-size:14px}
            .q-num{font-size:14px}
            .cart-foot{padding:18px}
            .cart-total span:last-child{font-size:22px}
            .checkout-btn{padding:15px;font-size:15px}

            /* Modals */
            .modal{width:95%;max-width:none;border-radius:20px;max-height:95vh}
            .m-head{padding:18px 20px;border-radius:17px 17px 0 0}
            .m-head h2{font-size:18px}
            .m-body{padding:20px}
            .fg label{font-size:13px}
            .fg input,.fg textarea,.fg select{padding:12px 14px;font-size:13px;border-radius:12px}
            .m-btn{padding:14px;font-size:15px;border-radius:14px}

            /* Item Detail Modal */
            #d-img{height:200px!important}
            #d-name{font-size:22px!important}
            #d-price{font-size:26px!important}
            #d-desc{font-size:14px!important}
            #d-actions{flex-direction:column!important;gap:12px!important}
            #d-add{padding:14px!important;font-size:15px!important}
            #d-sub{font-size:16px!important}

            /* Order Modal */
            .o-summary{padding:15px}
            .o-summary h3{font-size:14px}
            .o-s-item{font-size:13px}
            .o-s-total{font-size:16px}
            .momo-box{padding:15px}
            .momo-num{font-size:18px}
            .momo-amt{font-size:16px;padding:10px}

            /* My Orders */
            .my-o-card{padding:14px}
            .my-o-head h4{font-size:13px}
            .my-o-price{font-size:14px}
            .confirm-btn{padding:10px;font-size:13px}
            .dispute-btn{padding:8px;font-size:12px}

            /* Notifications */
            .n-item{padding:12px}
            .n-title{font-size:13px}
            .n-msg{font-size:12px}

            /* User Dropdown */
            .dd-menu{min-width:200px;right:-10px}
            .dd-item{padding:12px 16px;font-size:13px}
            .dd-head{padding:14px 16px;font-size:13px}

            /* Success Modal */
            .success-content{padding:30px 20px}
            .success-content .s-icon{font-size:60px}
            .success-content h2{font-size:22px}
            .s-order-id{font-size:16px;padding:12px 20px}

            /* Toast */
            .toast{left:15px;right:15px;bottom:15px;font-size:14px;padding:14px 18px;border-radius:14px;text-align:center}

            /* Footer */
            .footer{padding:25px 15px;font-size:13px}

            /* Empty State */
            .empty-state{padding:40px 15px}
            .empty-state .e-icon{font-size:50px}
            .empty-state h3{font-size:18px}

            /* Popup Notification */
            #u-popup{max-width:calc(100% - 30px)!important;right:15px!important;left:15px!important}
        }

        /* ===== VERY SMALL PHONES ===== */
        @media(max-width:380px){
            .items-grid{grid-template-columns:1fr}
            .item-img{height:200px}
            .item-body{padding:15px}
            .item-name{font-size:16px}
            .item-price{font-size:20px}
            .hero h2{font-size:24px}
            .hero p{font-size:13px}
            .hdr-btn{padding:6px 10px;font-size:12px}
            .hdr-btn span:not(.cart-count):not(.notif-dot){display:none}
        }'''

html = html.replace(old_media, new_media)
print("  ✅ Added comprehensive mobile styles")

# Add touch-friendly improvements
old_body_style = "body{background:#fff5f7;color:#333}"
new_body_style = "body{background:#fff5f7;color:#333;-webkit-tap-highlight-color:transparent;-webkit-text-size-adjust:100%}"

html = html.replace(old_body_style, new_body_style)
print("  ✅ Added touch-friendly body styles")

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("  ✅ index.html saved!")
print("")

# ==============================
# FIX admin.html
# ==============================
print("  Optimizing admin.html for mobile...")

with open('templates/admin.html', 'r', encoding='utf-8') as f:
    admin = f.read()

old_admin_media = '''@media(max-width:900px){.sidebar{width:0;overflow:hidden}.main-content{margin-left:0}.stats-grid{grid-template-columns:1fr 1fr}.form-grid{grid-template-columns:1fr}}'''

new_admin_media = '''/* ===== TABLET ===== */
        @media(max-width:1100px){
            .stats-grid{grid-template-columns:repeat(3,1fr)}
        }

        /* ===== MOBILE ===== */
        @media(max-width:900px){
            .sidebar{width:0;overflow:hidden;padding:0}
            .main-content{margin-left:0;padding:15px}
            .stats-grid{grid-template-columns:1fr 1fr;gap:12px}
            .stat-card{padding:18px;border-radius:16px}
            .stat-icon{width:45px;height:45px;font-size:22px;border-radius:14px}
            .stat-info h3{font-size:22px}
            .stat-info p{font-size:11px}
            .form-grid{grid-template-columns:1fr}
            .topbar{flex-direction:column;gap:15px;align-items:flex-start}
            .topbar h1{font-size:22px}
            .card{padding:18px;border-radius:18px}
            .card-header{flex-direction:column;gap:10px;align-items:flex-start}
            .card-header h2{font-size:18px}
            table{min-width:600px}
            th{padding:10px 8px;font-size:11px}
            td{padding:10px 8px;font-size:12px}
            .btn-sm{padding:6px 12px;font-size:11px}
            .items-grid{grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:12px}
            .item-image{height:140px}
            .item-info{padding:12px}
            .item-info h3{font-size:14px}
            .item-info .price{font-size:16px}
            .search-bar{flex-direction:column}
            .search-bar input{min-width:auto}
            .modal{width:95%;padding:20px}
            .modal-header h2{font-size:18px}
            .notif-area{position:static}
            .notif-dropdown{position:fixed;right:10px;left:10px;top:80px;width:auto}
            .notif-btn{padding:10px 16px;font-size:16px}

            /* Dashboard grid */
            div[style*="grid-template-columns:1fr 1fr"]{grid-template-columns:1fr!important}

            /* Dispute Modal */
            .action-option{padding:12px}
            .action-title{font-size:13px}
            .action-desc{font-size:11px}
        }

        /* ===== SMALL PHONES ===== */
        @media(max-width:480px){
            .stats-grid{grid-template-columns:1fr;gap:10px}
            .stat-card{padding:15px}
            .topbar h1{font-size:20px}
            .items-grid{grid-template-columns:1fr}
            table{min-width:500px}
        }'''

admin = admin.replace(old_admin_media, new_admin_media)
print("  ✅ Added admin mobile styles")

# Add mobile menu toggle button
old_sidebar_after = '''<div class="main-content">
    <div class="topbar">'''

new_sidebar_after = '''<div class="main-content">
    <!-- Mobile Menu Button -->
    <button id="mobile-menu-btn" onclick="toggleMobileMenu()" style="
        display:none;position:fixed;bottom:20px;left:20px;z-index:99;
        width:55px;height:55px;border-radius:50%;
        background:linear-gradient(135deg,#e91e63,#ff6f00);
        color:white;border:none;font-size:24px;cursor:pointer;
        box-shadow:0 4px 20px rgba(233,30,99,0.4);
    ">☰</button>

    <div class="topbar">'''

admin = admin.replace(old_sidebar_after, new_sidebar_after)
print("  ✅ Added mobile menu button")

# Add mobile menu toggle JS and make button visible on mobile
old_admin_toast = "function toast(m,t)"
new_admin_mobile_js = '''// MOBILE MENU
function toggleMobileMenu(){
    var sidebar=document.querySelector('.sidebar');
    if(sidebar.style.width==='270px'){
        sidebar.style.width='0';sidebar.style.padding='0';
    }else{
        sidebar.style.width='270px';sidebar.style.padding='30px 20px';
        sidebar.style.position='fixed';sidebar.style.zIndex='200';
        sidebar.style.borderRadius='0 30px 30px 0';
    }
}

// Show mobile menu button on small screens
function checkMobileMenu(){
    var btn=document.getElementById('mobile-menu-btn');
    if(window.innerWidth<=900){btn.style.display='block'}
    else{btn.style.display='none';var sb=document.querySelector('.sidebar');sb.style.width='';sb.style.padding=''}
}
window.addEventListener('resize',checkMobileMenu);
checkMobileMenu();

// Close sidebar when clicking a menu item on mobile
document.querySelectorAll('.nav-menu a').forEach(function(a){
    a.addEventListener('click',function(){
        if(window.innerWidth<=900){
            var sb=document.querySelector('.sidebar');
            sb.style.width='0';sb.style.padding='0';
        }
    });
});

function toast(m,t)'''

admin = admin.replace(old_admin_toast, new_admin_mobile_js)
print("  ✅ Added mobile menu toggle JS")

# Add touch friendly body
admin = admin.replace(
    "body{background:#fff5f7;color:#333}",
    "body{background:#fff5f7;color:#333;-webkit-tap-highlight-color:transparent;-webkit-text-size-adjust:100%}"
)

with open('templates/admin.html', 'w', encoding='utf-8') as f:
    f.write(admin)

print("  ✅ admin.html saved!")
print("")

# ==============================
# FIX admin_login.html
# ==============================
print("  Optimizing admin_login.html for mobile...")

with open('templates/admin_login.html', 'r', encoding='utf-8') as f:
    login = f.read()

# Check if mobile styles already exist
if '@media' not in login:
    # Add mobile styles before </style>
    login = login.replace(
        '</style>',
        '''
        @media(max-width:768px){
            .login-card{padding:35px 25px;margin:15px;border-radius:25px;max-width:none}
            .login-logo .icon{font-size:50px}
            .login-logo h1{font-size:22px}
            .form-group input{padding:13px 15px 13px 42px}
            .login-btn{padding:14px}
        }
        </style>'''
    )
    print("  ✅ Added mobile styles to admin_login.html")
else:
    print("  ✅ admin_login.html already has mobile styles")

with open('templates/admin_login.html', 'w', encoding='utf-8') as f:
    f.write(login)

print("")

# ==============================
# PUSH TO GITHUB
# ==============================
print("  Pushing to GitHub...")
os.system('git add .')
os.system('git commit -m "Complete mobile optimization for all pages"')
os.system('git push')

print("")
print("  ========================================")
print("  ALL DONE! Mobile Optimized!")
print("")
print("  Customer Page (index.html):")
print("  ✅ Responsive header")
print("  ✅ 2-column grid on phones")
print("  ✅ 1-column on tiny phones")
print("  ✅ Full-width cart sidebar")
print("  ✅ Touch-friendly buttons")
print("  ✅ Readable text sizes")
print("  ✅ Optimized modals")
print("  ✅ Mobile notifications")
print("")
print("  Admin Page (admin.html):")
print("  ✅ Hamburger menu on mobile")
print("  ✅ Responsive stats grid")
print("  ✅ Scrollable tables")
print("  ✅ Full-width forms")
print("  ✅ Mobile notifications")
print("  ✅ Touch-friendly actions")
print("")
print("  Render updates in 2-3 minutes!")
print("  ========================================")
print("")