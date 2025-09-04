#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام إدارة الأعمال - ملف الإعداد والتثبيت
Business Management System - Setup Script
"""

import os
import subprocess
import sys

def print_header():
    print("=" * 60)
    print("🏢 نظام إدارة الأعمال - معالج الإعداد")
    print("Business Management System - Setup Wizard")
    print("=" * 60)
    print()

def check_python():
    """فحص إصدار Python"""
    print("🐍 فحص إصدار Python...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 7:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - متوافق")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - غير متوافق")
        print("يرجى تثبيت Python 3.7 أو أحدث")
        return False

def install_requirements():
    """تثبيت المتطلبات"""
    print("\n📦 تثبيت المكتبات المطلوبة...")
    
    if not os.path.exists('requirements.txt'):
        print("❌ ملف requirements.txt غير موجود")
        return False
    
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ تم تثبيت جميع المكتبات بنجاح")
        return True
    except subprocess.CalledProcessError:
        print("❌ فشل في تثبيت المكتبات")
        print("جرب تشغيل الأمر يدوياً: pip install -r requirements.txt")
        return False

def create_database():
    """إنشاء قاعدة البيانات"""
    print("\n🗄️ إعداد قاعدة البيانات...")
    try:
        # استيراد التطبيق وإنشاء قاعدة البيانات
        import app
        with app.app.app_context():
            app.db.create_all()
            app.create_admin_user()
            app.create_sample_data()
        print("✅ تم إعداد قاعدة البيانات بنجاح")
        return True
    except Exception as e:
        print(f"❌ فشل في إعداد قاعدة البيانات: {e}")
        return False

def run_app():
    """تشغيل التطبيق"""
    print("\n🚀 تشغيل التطبيق...")
    print("🌐 افتح المتصفح واذهب إلى: http://localhost:5000")
    print("🔑 بيانات الدخول:")
    print("   اسم المستخدم: admin")
    print("   كلمة المرور: admin123")
    print()
    print("اضغط Ctrl+C لإيقاف التطبيق")
    print("=" * 60)
    
    try:
        import app
        app.app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n🛑 تم إيقاف التطبيق")
    except Exception as e:
        print(f"❌ خطأ في تشغيل التطبيق: {e}")

def main():
    """الدالة الرئيسية"""
    print_header()
    
    # فحص Python
    if not check_python():
        input("اضغط Enter للخروج...")
        return
    
    # تثبيت المتطلبات
    if not install_requirements():
        input("اضغط Enter للخروج...")
        return
    
    # إعداد قاعدة البيانات
    if not create_database():
        input("اضغط Enter للخروج...")
        return
    
    print("\n🎉 تم الإعداد بنجاح!")
    print("هل تريد تشغيل التطبيق الآن؟ (y/n): ", end="")
    
    choice = input().lower()
    if choice in ['y', 'yes', 'نعم', '']:
        run_app()
    else:
        print("\n💡 لتشغيل التطبيق لاحقاً، استخدم الأمر:")
        print("python app.py")
        print("\nأو انقر على ملف: فتح_التطبيق.html")

if __name__ == "__main__":
    main()