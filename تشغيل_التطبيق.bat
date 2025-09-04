@echo off
chcp 65001 >nul
color 0A
echo.
echo ===================================================
echo           🏢 نظام إدارة الأعمال
echo ===================================================
echo.
echo 🔄 جاري تشغيل التطبيق...
echo.

REM الانتقال إلى مجلد التطبيق
cd /d "%~dp0"

REM تشغيل التطبيق
echo 🐍 بدء تشغيل خادم Flask...
python app.py

REM إذا فشل python، جرب python3
if errorlevel 1 (
    echo.
    echo ⚠️  محاولة استخدام python3...
    python3 app.py
)

REM إذا فشل كلاهما
if errorlevel 1 (
    echo.
    echo ❌ خطأ: لم يتم العثور على Python
    echo.
    echo 💡 يرجى تثبيت Python أولاً من:
    echo    https://www.python.org/downloads/
    echo.
    echo 📋 أو استخدم الأمر التالي:
    echo    pip install -r requirements.txt
    echo    python app.py
    echo.
)

echo.
echo ===================================================
pause