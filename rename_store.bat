@echo off
echo.
echo  ========================================
echo   Store Name Changer Tool
echo  ========================================
echo.

:: Change to the correct directory first
cd /d "%~dp0"

echo  Working in: %CD%
echo.

:: ==============================
:: CREATE A PYTHON SCRIPT TO DO
:: THE RENAMING (Avoids apostrophe issues)
:: ==============================

echo  Creating rename helper...

echo old_name = "Sandra's Palace" > rename_helper.py
echo new_name = "Esirifuah's Palace" >> rename_helper.py
echo welcome_old = "Welcome back, Sandra!" >> rename_helper.py
echo welcome_new = "Welcome back, Esirifuah!" >> rename_helper.py
echo. >> rename_helper.py
echo files = [ >> rename_helper.py
echo     "templates/index.html", >> rename_helper.py
echo     "templates/admin.html", >> rename_helper.py
echo     "templates/admin_login.html", >> rename_helper.py
echo     "app.py" >> rename_helper.py
echo ] >> rename_helper.py
echo. >> rename_helper.py
echo for filepath in files: >> rename_helper.py
echo     try: >> rename_helper.py
echo         with open(filepath, 'r', encoding='utf-8') as f: >> rename_helper.py
echo             content = f.read() >> rename_helper.py
echo         content = content.replace(old_name, new_name) >> rename_helper.py
echo         content = content.replace(welcome_old, welcome_new) >> rename_helper.py
echo         with open(filepath, 'w', encoding='utf-8') as f: >> rename_helper.py
echo             f.write(content) >> rename_helper.py
echo         print(f"Updated: {filepath}") >> rename_helper.py
echo     except Exception as e: >> rename_helper.py
echo         print(f"Error with {filepath}: {e}") >> rename_helper.py
echo. >> rename_helper.py
echo print("All files updated!") >> rename_helper.py

:: ==============================
:: RUN THE PYTHON SCRIPT
:: ==============================
echo  Running rename script...
echo.
python rename_helper.py

:: ==============================
:: CLEAN UP HELPER FILE
:: ==============================
del rename_helper.py

:: ==============================
:: GIT PUSH
:: ==============================
echo.
echo  Pushing changes to GitHub...
echo.

git add .
git commit -m "Renamed store to Esirifuah's Palace"
git push

echo.
echo  ========================================
echo   ALL DONE!
echo   Name changed to: Esirifuah's Palace
echo   Render will update in 2-3 minutes!
echo  ========================================
echo.
pause