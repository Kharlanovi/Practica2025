from flask import Flask, render_template, request, jsonify, session
import os
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

PRODUCTS_FILE = "products.json"

def load_products():
    with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_products(products):
    with open(PRODUCTS_FILE, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=4)

PRODUCTS = load_products()

@app.before_request
def before_request():
    if 'cart' not in session:
        session['cart'] = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/catalog')
def catalog():
    return render_template('catalog.html')

@app.route('/catalog/wood')
def catalog_wood():
    return render_template('CatalogOneOne.html', products=PRODUCTS)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/cart')
def cart_page():
    return render_template('box.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/api/products')
def get_products():
    return jsonify(PRODUCTS)

@app.route('/api/cart/add', methods=['POST'])
def add_to_cart():
    try:
        data = request.get_json()
        product_id = str(data.get('product_id'))
        quantity = data.get('quantity', 1)
        
        product = next((p for p in PRODUCTS if str(p['id']) == product_id), None)
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        cart = session.get('cart', {})
        
        if product_id in cart:
            cart[product_id]['quantity'] += quantity
        else:
            cart[product_id] = {
                'product_id': product_id,
                'quantity': quantity,
                'name': product['name'],
                'price': product['price'],
                'image_url': product['image_url']
            }
        
        session['cart'] = cart
        session.modified = True
        
        return jsonify({
            'message': 'Product added to cart', 
            'cart_count': len(cart)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/cart')
def get_cart():
    cart = session.get('cart', {})
    cart_items = []
    total = 0
    
    for item_id, item in cart.items():
        item_total = item['quantity'] * item['price']
        total += item_total
        cart_items.append({
            'id': item_id,
            'product_id': item['product_id'],
            'name': item['name'],
            'price': item['price'],
            'quantity': item['quantity'],
            'total': item_total,
            'image_url': item['image_url']
        })
    
    return jsonify({
        'items': cart_items,
        'total': total,
        'count': len(cart_items)
    })

@app.route('/api/cart/update/<item_id>', methods=['PUT'])
def update_cart_item(item_id):
    data = request.get_json()
    quantity = data.get('quantity', 1)
    
    cart = session['cart']
    
    if item_id not in cart:
        return jsonify({'error': 'Item not found'}), 404
    
    if quantity <= 0:
        del cart[item_id]
    else:
        cart[item_id]['quantity'] = quantity
    
    session['cart'] = cart
    session.modified = True
    
    return jsonify({'message': 'Cart updated'})

@app.route('/api/cart/remove/<item_id>', methods=['DELETE'])
def remove_from_cart(item_id):
    cart = session['cart']
    
    if item_id not in cart:
        return jsonify({'error': 'Item not found'}), 404
    
    del cart[item_id]
    session['cart'] = cart
    session.modified = True
    
    return jsonify({'message': 'Item removed from cart'})

@app.route('/api/cart/clear', methods=['DELETE'])
def clear_cart():
    session['cart'] = {}
    session.modified = True
    
    return jsonify({'message': 'Cart cleared'})

@app.route('/admin/products')
def admin_products():
    return render_template('admin_products.html', products=PRODUCTS)

@app.route('/admin/products/edit/<int:product_id>', methods=['GET', 'POST'])
def admin_edit_product(product_id):
    product = next((p for p in PRODUCTS if p['id'] == product_id), None)

    if not product:
        return "Товар не найден", 404

    if request.method == 'POST':
        product['name'] = request.form['name']
        product['price'] = float(request.form['price'])
        product['image_url'] = request.form['image_url']

        save_products(PRODUCTS)

        return jsonify({"success": True})

    return render_template('admin_edit.html', product=product)

@app.route('/admin/products/delete/<int:product_id>', methods=['POST'])
def admin_delete_product(product_id):
    global PRODUCTS
    PRODUCTS = [p for p in PRODUCTS if p['id'] != product_id]

    save_products(PRODUCTS)

    return jsonify({"success": True})

@app.route('/admin/products/add', methods=['GET', 'POST'])
def admin_add_product():
    if request.method == 'POST':
        new_id = max([p['id'] for p in PRODUCTS]) + 1 if PRODUCTS else 1

        new_product = {
            'id': new_id,
            'name': request.form['name'],
            'price': float(request.form['price']),
            'image_url': request.form['image_url']
        }

        PRODUCTS.append(new_product)
        save_products(PRODUCTS)

        return jsonify({"success": True})

    return render_template('admin_edit.html', product=None)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
