#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
برنامج إدارة الأعمال الشامل
Business Management System
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
import json

# إعداد التطبيق
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///business.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# إعداد قاعدة البيانات
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# إعداد نظام تسجيل الدخول
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'يرجى تسجيل الدخول للوصول إلى هذه الصفحة'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# نماذج قاعدة البيانات
class User(UserMixin, db.Model):
    """نموذج المستخدم"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Customer(db.Model):
    """نموذج العميل"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    city = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    orders = db.relationship('Order', backref='customer', lazy=True)

class Category(db.Model):
    """نموذج فئة المنتج"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    products = db.relationship('Product', backref='category', lazy=True)

class Product(db.Model):
    """نموذج المنتج"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    cost = db.Column(db.Float, default=0)
    stock_quantity = db.Column(db.Integer, default=0)
    min_stock_level = db.Column(db.Integer, default=5)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    order_items = db.relationship('OrderItem', backref='product', lazy=True)

class Order(db.Model):
    """نموذج الطلب"""
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, shipped, delivered, cancelled
    total_amount = db.Column(db.Float, default=0)
    notes = db.Column(db.Text)
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')

class OrderItem(db.Model):
    """نموذج عنصر الطلب"""
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)

# الصفحات الأساسية
@app.route('/')
def index():
    """الصفحة الرئيسية"""
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    
    # إحصائيات سريعة
    total_customers = Customer.query.count()
    total_products = Product.query.count()
    total_orders = Order.query.count()
    pending_orders = Order.query.filter_by(status='pending').count()
    
    # المنتجات منخفضة المخزون
    low_stock_products = Product.query.filter(Product.stock_quantity <= Product.min_stock_level).all()
    
    # الطلبات الأخيرة
    recent_orders = Order.query.order_by(Order.order_date.desc()).limit(5).all()
    
    return render_template('dashboard.html',
                         total_customers=total_customers,
                         total_products=total_products,
                         total_orders=total_orders,
                         pending_orders=pending_orders,
                         low_stock_products=low_stock_products,
                         recent_orders=recent_orders)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """صفحة تسجيل الدخول"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('اسم المستخدم أو كلمة المرور غير صحيحة', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """تسجيل الخروج"""
    logout_user()
    return redirect(url_for('login'))

# إدارة العملاء
@app.route('/customers')
@login_required
def customers():
    """صفحة العملاء"""
    customers = Customer.query.order_by(Customer.name).all()
    return render_template('customers.html', customers=customers)

@app.route('/customers/add', methods=['GET', 'POST'])
@login_required
def add_customer():
    """إضافة عميل جديد"""
    if request.method == 'POST':
        customer = Customer(
            name=request.form['name'],
            email=request.form['email'],
            phone=request.form['phone'],
            address=request.form['address'],
            city=request.form['city']
        )
        db.session.add(customer)
        db.session.commit()
        flash('تم إضافة العميل بنجاح', 'success')
        return redirect(url_for('customers'))
    
    return render_template('add_customer.html')

# إدارة المنتجات
@app.route('/products')
@login_required
def products():
    """صفحة المنتجات"""
    products = Product.query.order_by(Product.name).all()
    return render_template('products.html', products=products)

@app.route('/products/add', methods=['GET', 'POST'])
@login_required
def add_product():
    """إضافة منتج جديد"""
    if request.method == 'POST':
        product = Product(
            name=request.form['name'],
            description=request.form['description'],
            price=float(request.form['price']),
            cost=float(request.form.get('cost', 0)),
            stock_quantity=int(request.form['stock_quantity']),
            min_stock_level=int(request.form.get('min_stock_level', 5)),
            category_id=request.form.get('category_id') or None
        )
        db.session.add(product)
        db.session.commit()
        flash('تم إضافة المنتج بنجاح', 'success')
        return redirect(url_for('products'))
    
    categories = Category.query.all()
    return render_template('add_product.html', categories=categories)

# إدارة الطلبات
@app.route('/orders')
@login_required
def orders():
    """صفحة الطلبات"""
    orders = Order.query.order_by(Order.order_date.desc()).all()
    return render_template('orders.html', orders=orders)

@app.route('/orders/add', methods=['GET', 'POST'])
@login_required
def add_order():
    """إضافة طلب جديد"""
    if request.method == 'POST':
        order = Order(
            customer_id=request.form['customer_id'],
            notes=request.form.get('notes', '')
        )
        db.session.add(order)
        db.session.flush()  # للحصول على order.id
        
        # إضافة عناصر الطلب
        total_amount = 0
        items_data = json.loads(request.form['items'])
        
        for item_data in items_data:
            product = Product.query.get(item_data['product_id'])
            quantity = int(item_data['quantity'])
            unit_price = product.price
            total_price = quantity * unit_price
            
            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=quantity,
                unit_price=unit_price,
                total_price=total_price
            )
            db.session.add(order_item)
            
            # تحديث المخزون
            product.stock_quantity -= quantity
            total_amount += total_price
        
        order.total_amount = total_amount
        db.session.commit()
        flash('تم إضافة الطلب بنجاح', 'success')
        return redirect(url_for('orders'))
    
    customers = Customer.query.all()
    products = Product.query.filter(Product.stock_quantity > 0).all()
    return render_template('add_order.html', customers=customers, products=products)

# API endpoints
@app.route('/api/products')
@login_required
def api_products():
    """API للحصول على المنتجات"""
    products = Product.query.all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'price': p.price,
        'stock_quantity': p.stock_quantity
    } for p in products])

@app.route('/api/dashboard_data')
@login_required
def api_dashboard_data():
    """API لبيانات لوحة التحكم"""
    # مبيعات آخر 7 أيام
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    daily_sales = []
    for i in range(7):
        day = start_date + timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        
        orders = Order.query.filter(
            Order.order_date >= day_start,
            Order.order_date < day_end,
            Order.status != 'cancelled'
        ).all()
        
        total = sum(order.total_amount for order in orders)
        daily_sales.append({
            'date': day.strftime('%Y-%m-%d'),
            'total': total
        })
    
    return jsonify({
        'daily_sales': daily_sales
    })

def create_admin_user():
    """إنشاء مستخدم إداري افتراضي"""
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@business.com',
            full_name='مدير النظام',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("تم إنشاء المستخدم الإداري: admin / admin123")

def create_sample_data():
    """إنشاء بيانات تجريبية"""
    # إنشاء فئات
    if Category.query.count() == 0:
        categories = [
            Category(name='إلكترونيات', description='الأجهزة الإلكترونية'),
            Category(name='ملابس', description='الملابس والأزياء'),
            Category(name='كتب', description='الكتب والمراجع')
        ]
        for cat in categories:
            db.session.add(cat)
        db.session.commit()
    
    # إنشاء منتجات تجريبية
    if Product.query.count() == 0:
        electronics = Category.query.filter_by(name='إلكترونيات').first()
        products = [
            Product(name='لابتوب ديل', description='لابتوب للأعمال', price=2500, cost=2000, stock_quantity=10, category_id=electronics.id),
            Product(name='ماوس لاسلكي', description='ماوس بلوتوث', price=50, cost=30, stock_quantity=25, category_id=electronics.id),
            Product(name='قميص قطني', description='قميص رجالي قطني', price=75, cost=45, stock_quantity=15),
            Product(name='كتاب البرمجة', description='تعلم البرمجة', price=35, cost=20, stock_quantity=8)
        ]
        for product in products:
            db.session.add(product)
        db.session.commit()
    
    # إنشاء عملاء تجريبيين
    if Customer.query.count() == 0:
        customers = [
            Customer(name='أحمد محمد', email='ahmed@email.com', phone='01234567890', city='القاهرة'),
            Customer(name='فاطمة علي', email='fatma@email.com', phone='01987654321', city='الإسكندرية'),
            Customer(name='محمد حسن', email='mohamed@email.com', phone='01555666777', city='الجيزة')
        ]
        for customer in customers:
            db.session.add(customer)
        db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_admin_user()
        create_sample_data()
    
    print("🚀 تم تشغيل نظام إدارة الأعمال بنجاح!")
    print("🌐 افتح المتصفح واذهب إلى: http://localhost:5000")
    print("🔑 بيانات الدخول:")
    print("   اسم المستخدم: admin")
    print("   كلمة المرور: admin123")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)