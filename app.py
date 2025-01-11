from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://construction_store_user:Pr9b9eVWvDzSXvwSO17sf7zpOkBISCEQ@dpg-cu14cm56l47c73a00460-a.oregon-postgres.render.com/construction_store'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# جداول قاعدة البيانات
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    price_per_unit = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), nullable=False)  # مثل كجم، متر، قطعة

class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    discount = db.Column(db.Float, default=0.0)  # إضافة حقل الخصم
    sale_date = db.Column(db.Date, default=datetime.utcnow)


class Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    supplier_name = db.Column(db.String(100), nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    purchase_date = db.Column(db.Date, default=datetime.utcnow)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    expense_type = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    expense_date = db.Column(db.Date, default=datetime.utcnow)

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False, unique=True)
    address = db.Column(db.String(200), nullable=True)

# إنشاء قاعدة البيانات
with app.app_context():
    db.create_all()

# الصفحة الرئيسية
@app.route('/')
def index():
    return render_template('index.html')

# تسجيل المبيعات
@app.route('/sales', methods=['GET', 'POST'])
def sales():
    items = Item.query.all()  # جلب الأصناف المتاحة
    if request.method == 'POST':
        product_name = request.form.get('product_name')
        quantity = request.form.get('quantity', type=float)
        discount = request.form.get('discount', type=float, default=0.0)
        sale_date_str = request.form.get('sale_date')

        if not product_name or not sale_date_str or quantity is None:
            return "تأكد من ملء جميع الحقول المطلوبة!", 400

        try:
            sale_date = datetime.strptime(sale_date_str, '%Y-%m-%d').date()
        except ValueError:
            return "تنسيق التاريخ غير صالح!", 400

        item = Item.query.filter_by(name=product_name).first()
        if not item:
            return "الصنف غير موجود!", 400

        total_price = max((item.price_per_unit * quantity) - discount, 0)

        sale = Sale(
            product_name=product_name,
            quantity=quantity,
            price=total_price,
            sale_date=sale_date
        )
        db.session.add(sale)
        db.session.commit()
        return redirect(url_for('sales'))

    all_sales = Sale.query.all()
    items_dict = {item.name: {'unit': item.unit, 'price_per_unit': item.price_per_unit} for item in items}
    return render_template('sales.html', sales=all_sales, items=items, items_dict=items_dict)

@app.route('/sales/delete/<int:sale_id>', methods=['POST'])
def delete_sale(sale_id):
    sale = Sale.query.get_or_404(sale_id)
    db.session.delete(sale)
    db.session.commit()
    return redirect(url_for('sales'))

@app.route('/sales/edit/<int:sale_id>', methods=['GET', 'POST'])
def edit_sale(sale_id):
    sale = Sale.query.get_or_404(sale_id)
    items = Item.query.all()

    if request.method == 'POST':
        sale.product_name = request.form.get('product_name', sale.product_name)
        sale.quantity = request.form.get('quantity', type=float, default=sale.quantity)
        sale.discount = request.form.get('discount', type=float, default=0.0)

        sale_date_str = request.form.get('sale_date', sale.sale_date)
        try:
            sale.sale_date = datetime.strptime(sale_date_str, '%Y-%m-%d').date()
        except ValueError:
            return "تنسيق التاريخ غير صالح!", 400

        item = Item.query.filter_by(name=sale.product_name).first()
        if not item:
            return "الصنف غير موجود!", 400

        sale.price = max((item.price_per_unit * sale.quantity) - sale.discount, 0)
        db.session.commit()
        return redirect(url_for('sales'))

    return render_template('edit_sale.html', sale=sale, items=items)

@app.route('/items', methods=['GET', 'POST'])
def items():
    if request.method == 'POST':
        name = request.form['name']
        price_per_unit = float(request.form['price_per_unit'])
        unit = request.form['unit']
        item = Item(name=name, price_per_unit=price_per_unit, unit=unit)
        db.session.add(item)
        db.session.commit()
        return redirect(url_for('items'))
    all_items = Item.query.all()
    return render_template('items.html', items=all_items)

@app.route('/delete_item/<int:item_id>')
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('items'))

@app.route('/edit_item/<int:item_id>', methods=['GET', 'POST'])
def edit_item(item_id):
    item = Item.query.get_or_404(item_id)
    if request.method == 'POST':
        item.name = request.form['name']
        item.price_per_unit = float(request.form['price_per_unit'])
        item.unit = request.form['unit']
        db.session.commit()
        return redirect(url_for('items'))
    return render_template('edit_item.html', item=item)


# تسجيل المشتريات
@app.route('/purchases', methods=['GET', 'POST'])
def purchases():
    if request.method == 'POST':
        supplier_name = request.form['supplier_name']
        product_name = request.form['product_name']
        quantity = int(request.form['quantity'])
        price = float(request.form['price'])
        purchase_date = request.form['purchase_date']
        purchase = Purchase(supplier_name=supplier_name, product_name=product_name, quantity=quantity, price=price, purchase_date=purchase_date)
        db.session.add(purchase)
        db.session.commit()
        return redirect(url_for('purchases'))
    all_purchases = Purchase.query.all()
    return render_template('purchases.html', purchases=all_purchases)

# تسجيل المصاريف
@app.route('/expenses', methods=['GET', 'POST'])
def expenses():
    if request.method == 'POST':
        expense_type = request.form['expense_type']
        amount = float(request.form['amount'])
        expense_date = request.form['expense_date']
        expense = Expense(expense_type=expense_type, amount=amount, expense_date=expense_date)
        db.session.add(expense)
        db.session.commit()
        return redirect(url_for('expenses'))
    all_expenses = Expense.query.all()
    return render_template('expenses.html', expenses=all_expenses)

@app.route('/customers', methods=['GET', 'POST'])
def customers():
    if request.method == 'POST':
        # استلام بيانات العميل من النموذج
        name = request.form['name']
        phone = request.form['phone']
        address = request.form.get('address', '')

        # إنشاء سجل جديد
        new_customer = Customer(name=name, phone=phone, address=address)
        db.session.add(new_customer)
        db.session.commit()

        return redirect(url_for('customers'))

    # جلب جميع العملاء من قاعدة البيانات
    all_customers = Customer.query.all()
    return render_template('customers.html', customers=all_customers)

# عرض التقارير
@app.route('/reports')
def report():
    total_sales = db.session.query(db.func.sum(Sale.price)).scalar() or 0
    total_purchases = db.session.query(db.func.sum(Purchase.price)).scalar() or 0
    total_expenses = db.session.query(db.func.sum(Expense.amount)).scalar() or 0
    total_discounts = db.session.query(
        db.func.sum((Item.price_per_unit * Sale.quantity) - Sale.price)
    ).join(Item, Item.name == Sale.product_name).scalar() or 0
    net_profit = total_sales - total_purchases - total_expenses
    
    # أرباح كل صنف
    profit_by_item = db.session.query(
        Sale.product_name,
        db.func.sum(Sale.price).label('total_sales'),
        db.func.sum(Sale.quantity).label('total_quantity')
    ).group_by(Sale.product_name).all()
    
    return render_template(
        'reports.html', 
        total_sales=total_sales, 
        total_purchases=total_purchases, 
        total_expenses=total_expenses, 
        total_discounts=total_discounts,
        net_profit=net_profit,
        profit_by_item=profit_by_item
    )

if __name__ == '__main__':
    app.run(debug=True)
