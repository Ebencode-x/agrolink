from flask import Flask, render_template, request, redirect

app = Flask(__name__)

# This is our temporary database (The "Heap")
all_products = []

@app.route('/')
def dashboard():
    return render_template('vendor_dashboard.html', products=all_products)

@app.route('/add', methods=['POST'])
def add_product():
    # Capture data from the form
    name = request.form.get('p_name')
    price = request.form.get('p_price')
    
    if name and price:
        all_products.append({'name': name, 'price': price})
    
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)