import os
import requests
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from dotenv import load_dotenv


load_dotenv()

app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-key-change-in-production")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///agrolink.db")
if app.config["SQLALCHEMY_DATABASE_URI"].startswith("postgresql+psycopg://"):
    app.config["SQLALCHEMY_DATABASE_URI"] = app.config["SQLALCHEMY_DATABASE_URI"].replace("postgresql+psycopg://", "postgresql+psycopg://", 1)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_pre_ping": True, "pool_recycle": 300}

WEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY", "")
WEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_BASE_URL = "https://api.openweathermap.org/data/2.5/forecast"

db      = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt  = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "Tafadhali ingia kwanza."
CORS(app)


# ── Models ──────────────────────────────────────────────────────────────────

class User(db.Model):
    __tablename__ = "users"
    id            = db.Column(db.Integer, primary_key=True)
    full_name     = db.Column(db.String(120), nullable=False)
    phone         = db.Column(db.String(20), unique=True, nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    region        = db.Column(db.String(80), nullable=True)
    role          = db.Column(db.String(20), default="farmer")
    is_active     = db.Column(db.Boolean, default=True)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    crops         = db.relationship("Crop", backref="owner", lazy=True)
    listings      = db.relationship("MarketListing", backref="seller", lazy=True)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    @property
    def is_authenticated(self): return True
    @property
    def is_anonymous(self): return False
    @property
    def is_active_user(self): return self.is_active
    def get_id(self): return str(self.id)


class Crop(db.Model):
    __tablename__ = "crops"
    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name_sw     = db.Column(db.String(100), nullable=False)
    name_en     = db.Column(db.String(100), nullable=False)
    category    = db.Column(db.String(50), nullable=False)
    season      = db.Column(db.String(50), nullable=True)
    hectares    = db.Column(db.Float, nullable=True)
    region      = db.Column(db.String(80), nullable=True)
    description = db.Column(db.Text, nullable=True)
    image_url   = db.Column(db.String(300), nullable=True)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at  = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    market_prices = db.relationship("MarketPrice", backref="crop", lazy=True)


class MarketPrice(db.Model):
    __tablename__ = "market_prices"
    id          = db.Column(db.Integer, primary_key=True)
    crop_id     = db.Column(db.Integer, db.ForeignKey("crops.id"), nullable=False)
    region      = db.Column(db.String(80), nullable=False)
    market      = db.Column(db.String(120), nullable=True)
    price_tzs   = db.Column(db.Float, nullable=False)
    unit        = db.Column(db.String(20), default="kg")
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)
    source      = db.Column(db.String(100), nullable=True)


class MarketListing(db.Model):
    __tablename__ = "market_listings"
    id           = db.Column(db.Integer, primary_key=True)
    seller_id    = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title        = db.Column(db.String(200), nullable=False)
    crop_name    = db.Column(db.String(100), nullable=False)
    quantity_kg  = db.Column(db.Float, nullable=False)
    price_tzs    = db.Column(db.Float, nullable=False)
    region       = db.Column(db.String(80), nullable=False)
    contact      = db.Column(db.String(50), nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    image_url    = db.Column(db.String(300), nullable=True)
    posted_at    = db.Column(db.DateTime, default=datetime.utcnow)


class WeatherLog(db.Model):
    __tablename__ = "weather_logs"
    id          = db.Column(db.Integer, primary_key=True)
    city        = db.Column(db.String(100), nullable=False)
    temperature = db.Column(db.Float)
    humidity    = db.Column(db.Float)
    description = db.Column(db.String(200))
    wind_speed  = db.Column(db.Float)
    icon        = db.Column(db.String(20))
    fetched_at  = db.Column(db.DateTime, default=datetime.utcnow)


# ── Login Manager ────────────────────────────────────────────────────────────

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ── Weather Service ──────────────────────────────────────────────────────────

def get_weather(city="Mbeya"):
    if not WEATHER_API_KEY:
        return {"error": "API key haijawekwa", "city": city, "success": False}
    params = {"q": f"{city},TZ", "appid": WEATHER_API_KEY, "units": "metric", "lang": "sw"}
    try:
        resp = requests.get(WEATHER_BASE_URL, params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        weather_data = {
            "city"        : city,
            "temperature" : data["main"]["temp"],
            "feels_like"  : data["main"]["feels_like"],
            "humidity"    : data["main"]["humidity"],
            "description" : data["weather"][0]["description"],
            "wind_speed"  : data["wind"]["speed"],
            "icon"        : data["weather"][0]["icon"],
            "success"     : True,
        }
        log = WeatherLog(city=city, temperature=weather_data["temperature"],
                        humidity=weather_data["humidity"], description=weather_data["description"],
                        wind_speed=weather_data["wind_speed"], icon=weather_data["icon"])
        db.session.add(log)
        db.session.commit()
        return weather_data
    except Exception as exc:
        cached = WeatherLog.query.filter_by(city=city).order_by(WeatherLog.fetched_at.desc()).first()
        if cached:
            return {"city": cached.city, "temperature": cached.temperature,
                    "humidity": cached.humidity, "description": cached.description,
                    "wind_speed": cached.wind_speed, "icon": cached.icon,
                    "success": True, "cached": True}
        return {"error": str(exc), "city": city, "success": False}


def get_forecast(city="Mbeya"):
    if not WEATHER_API_KEY:
        return []
    params = {"q": f"{city},TZ", "appid": WEATHER_API_KEY, "units": "metric", "cnt": 5}
    try:
        resp = requests.get(FORECAST_BASE_URL, params=params, timeout=5)
        resp.raise_for_status()
        return [{"dt_txt": i["dt_txt"], "temperature": i["main"]["temp"],
                 "description": i["weather"][0]["description"], "icon": i["weather"][0]["icon"]}
                for i in resp.json().get("list", [])]
    except:
        return []


# ── Routes ───────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    crops    = Crop.query.order_by(Crop.created_at.desc()).limit(6).all()
    listings = MarketListing.query.filter_by(is_available=True).order_by(MarketListing.posted_at.desc()).limit(8).all()
    weather  = get_weather("Mbeya")
    return render_template("index.html", crops=crops, listings=listings, weather=weather)


@app.route("/weather")
def weather_page():
    city     = request.args.get("city", "Mbeya")
    weather  = get_weather(city)
    forecast = get_forecast(city)
    return jsonify({"weather": weather, "forecast": forecast})


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data     = request.get_json() or request.form
        user     = User.query.filter_by(phone=data.get("phone")).first()
        if user and user.check_password(data.get("password", "")):
            login_user(user)
            return jsonify({"message": "Umeingia.", "role": user.role})
        return jsonify({"error": "Namba ya simu au nywila si sahihi."}), 401
    return render_template("auth/login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        data = request.get_json() or request.form
        if User.query.filter_by(phone=data.get("phone")).first():
            return jsonify({"error": "Namba ya simu tayari imetumika."}), 409
        user = User(
            full_name = data.get("full_name"),
            phone     = data.get("phone"),
            email     = data.get("email"),
            region    = data.get("region"),
            role      = data.get("role", "farmer"),
        )
        user.set_password(data.get("password"))
        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "Akaunti imefunguliwa.", "id": user.id}), 201
    return render_template("auth/register.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/dashboard")
@login_required
def dashboard():
    user_listings = MarketListing.query.filter_by(seller_id=current_user.id).order_by(MarketListing.posted_at.desc()).all()
    user_crops    = Crop.query.filter_by(user_id=current_user.id).all()
    return render_template("dashboard/dashboard.html", listings=user_listings, crops=user_crops)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/listings")
def listings():
    all_listings = MarketListing.query.filter_by(is_available=True).order_by(MarketListing.posted_at.desc()).all()
    return render_template("market/listings.html", listings=all_listings)


@app.route("/api/crops", methods=["GET"])
def api_crops():
    crops = Crop.query.order_by(Crop.created_at.desc()).all()
    return jsonify([{"id": c.id, "name_sw": c.name_sw, "name_en": c.name_en,
                     "category": c.category, "season": c.season, "region": c.region} for c in crops])


@app.route("/api/prices", methods=["GET"])
def api_prices():
    prices = MarketPrice.query.order_by(MarketPrice.recorded_at.desc()).limit(50).all()
    return jsonify([{"id": p.id, "crop_id": p.crop_id, "region": p.region,
                     "market": p.market, "price_tzs": p.price_tzs,
                     "recorded_at": p.recorded_at.isoformat()} for p in prices])


@app.route("/api/listings", methods=["GET"])
def api_listings():
    listings = MarketListing.query.filter_by(is_available=True).order_by(MarketListing.posted_at.desc()).all()
    return jsonify([{"id": l.id, "title": l.title, "crop_name": l.crop_name,
                     "quantity_kg": l.quantity_kg, "price_tzs": l.price_tzs,
                     "region": l.region, "contact": l.contact,
                     "posted_at": l.posted_at.isoformat()} for l in listings])


@app.route("/api/listings", methods=["POST"])
@login_required
def create_listing():
    data = request.get_json()
    listing = MarketListing(
        seller_id   = current_user.id,
        title       = data["title"],
        crop_name   = data["crop_name"],
        quantity_kg = float(data["quantity_kg"]),
        price_tzs   = float(data["price_tzs"]),
        region      = data["region"],
        contact     = data.get("contact", current_user.phone),
    )
    db.session.add(listing)
    db.session.commit()
    return jsonify({"message": "Orodha imeongezwa.", "id": listing.id}), 201


@app.route("/health")
def health():
    return jsonify({"status": "ok", "timestamp": datetime.utcnow().isoformat()})


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Ukurasa haukupatikana."}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Hitilafu ya seva."}), 500


# ── Init DB & Run ────────────────────────────────────────────────────────────

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("FLASK_DEBUG", "false").lower() == "true")


@app.route("/seed-market-data")
def seed_market_data():
    try:
        # Unda user wa demo kwanza
        if not User.query.filter_by(phone='+255700000001').first():
            demo = User(
                full_name="Soko la AgroLink",
                phone='+255700000001',
                email='demo@agrolink.co.tz',
                region='Mbeya', role='agent'
            )
            demo.set_password('Demo@2025!')
            db.session.add(demo)
            db.session.flush()
        else:
            demo = User.query.filter_by(phone='+255700000001').first()

        # Listings za kwanza
        sample_listings = [
            ('Mahindi Mazuri — Mbeya 2025','Mahindi',500,850,'Mbeya','+255712000001'),
            ('Mpunga wa Morogoro — Ubora wa Juu','Mpunga',1000,1200,'Morogoro','+255712000002'),
            ('Kahawa Arabica — Kilimanjaro','Kahawa',200,4500,'Kilimanjaro','+255712000003'),
            ('Viazi Mbeya — Safi na Kubwa','Viazi',800,600,'Mbeya','+255712000004'),
            ('Nyanya Mpya — Arusha','Nyanya',300,1100,'Arusha','+255712000005'),
            ('Alizeti — Singida','Alizeti',600,900,'Singida','+255712000006'),
            ('Chai — Iringa','Chai',150,3500,'Iringa','+255712000007'),
            ('Mhogo — Tabora','Mhogo',1200,400,'Tabora','+255712000008'),
        ]

        added = 0
        for title,crop,qty,price,region,contact in sample_listings:
            if not MarketListing.query.filter_by(title=title).first():
                db.session.add(MarketListing(
                    seller_id=demo.id, title=title, crop_name=crop,
                    quantity_kg=qty, price_tzs=price,
                    region=region, contact=contact
                ))
                added += 1

        db.session.commit()
        return jsonify({"status": f"✅ Mazao {added} yameongezwa kwenye soko!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
