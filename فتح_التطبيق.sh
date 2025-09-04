#!/bin/bash

# تعيين الترميز للعربية
export LANG=ar_SA.UTF-8

clear
echo "==================================================="
echo "           🏢 نظام إدارة الأعمال"
echo "==================================================="
echo ""
echo "🚀 جاري فتح التطبيق..."
echo ""

# محاولة فتح التطبيق في المتصفح
if command -v xdg-open > /dev/null; then
    xdg-open http://localhost:5000
elif command -v open > /dev/null; then
    open http://localhost:5000
elif command -v start > /dev/null; then
    start http://localhost:5000
else
    echo "❌ لم يتم العثور على أمر فتح المتصفح"
    echo "📱 يرجى فتح المتصفح يدوياً والذهاب إلى:"
    echo "   http://localhost:5000"
fi

echo "✅ تم فتح التطبيق في المتصفح!"
echo ""
echo "🔑 بيانات تسجيل الدخول:"
echo "   اسم المستخدم: admin"
echo "   كلمة المرور: admin123"
echo ""
echo "💡 إذا لم يفتح التطبيق، تأكد من:"
echo "   - تشغيل التطبيق أولاً"
echo "   - عدم حجب المتصفح للموقع"
echo ""
echo "📱 يمكنك أيضاً نسخ هذا الرابط ولصقه في المتصفح:"
echo "   http://localhost:5000"
echo ""
echo "==================================================="
echo "اضغط أي زر للخروج..."
read -n 1