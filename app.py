from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "agro_secure_matrix_key_2026" # Persistent Key

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///agrolink.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- MODELS ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20))
    region = db.Column(db.String(50))
    products = db.relationship('Product', backref='owner', lazy=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# --- AUTH DECORATOR ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session: return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- CORE ROUTES ---
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u_name = request.form.get("u_name")
        u_pass = request.form.get("u_pass")
        
        # 1. Validation First
        if len(u_pass) < 6:
            flash("SECURITY_ALERT: Password too weak! Minimum 6 characters required.")
            return redirect(url_for('login'))

        user = User.query.filter_by(username=u_name).first()
        
        if user:
            if check_password_hash(user.password, u_pass):
                session["user_id"], session["username"] = user.id, user.username
                return redirect(url_for('dashboard'))
            flash("PROTOCOL_ERROR: Authentication Failed. Invalid Credentials.")
        else:
            # Automatic Registration if user doesn't exist
            hashed_pw = generate_password_hash(u_pass, method='pbkdf2:sha256')
            new_user = User(username=u_name, password=hashed_pw, 
                           phone=request.form.get("u_phone"), 
                           region=request.form.get("u_region"))
            db.session.add(new_user)
            db.session.commit()
            session["user_id"], session["username"] = new_user.id, new_user.username
            return redirect(url_for('dashboard'))
            
    return render_template("login.html")

@app.route("/")
@login_required
def dashboard():
    # Tunachuja bidhaa zionekane za huyo mtumiaji tu kwa usalama zaidi
    user_products = Product.query.filter_by(user_id=session['user_id']).all()
    return render_template("vendor_dashboard.html", products=user_products)

@app.route("/market")
def market():
    return render_template("market.html", products=Product.query.all())

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)