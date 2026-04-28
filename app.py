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
from supabase import create_client

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-key-change-in-production")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///agrolink.db")
if app.config["SQLALCHEMY_DATABASE_URI"].startswith("postgresql+psycopg://"):
    app.config["SQLALCHEMY_DATABASE_URI"] = app.config["SQLALCHEMY_DATABASE_URI"].replace("postgresql+psycopg://", "postgresql+psycopg://", 1)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_pre_ping": True, "pool_recycle": 300}

SUPABASE_URL      = os.environ.get("SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY", "")
supabase_client   = create_client(SUPABASE_URL, SUPABASE_ANON_KEY) if SUPABASE_URL else None

WEATHER_API_KEY   = os.environ.get("OPENWEATHER_API_KEY", "")
WEATHER_BASE_URL  = "https://api.openweathermap.org/data/2.5/weather"
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
    is_verified   = db.Column(db.Boolean, default=False)
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
    unit         = db.Column(db.String(20), default="kg")
    price_tzs    = db.Column(db.Float, nullable=False)
    region       = db.Column(db.String(80), nullable=False)
    contact      = db.Column(db.String(50), nullable=False)
    description  = db.Column(db.String(500), nullable=True)
    is_available = db.Column(db.Boolean, default=True)
    image_url    = db.Column(db.String(300), nullable=True)
    posted_at    = db.Column(db.DateTime, default=datetime.utcnow)


class ListingReport(db.Model):
    __tablename__ = "listing_reports"
    id          = db.Column(db.Integer, primary_key=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    listing_id  = db.Column(db.Integer, db.ForeignKey("market_listings.id"), nullable=False)
    reason      = db.Column(db.String(200), nullable=False)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint("reporter_id", "listing_id", name="unique_report"),)
    reporter = db.relationship("User", foreign_keys=[reporter_id], backref="reports_made")
    listing  = db.relationship("MarketListing", foreign_keys=[listing_id], backref="reports")


class SellerRating(db.Model):
    __tablename__ = "seller_ratings"
    id         = db.Column(db.Integer, primary_key=True)
    seller_id  = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    rater_id   = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    listing_id = db.Column(db.Integer, db.ForeignKey("market_listings.id"), nullable=False)
    stars      = db.Column(db.Integer, nullable=False)
    comment    = db.Column(db.String(300), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint("rater_id", "listing_id", name="unique_rating"),)
    seller  = db.relationship("User", foreign_keys=[seller_id], backref="ratings_received")
    rater   = db.relationship("User", foreign_keys=[rater_id], backref="ratings_given")
    listing = db.relationship("MarketListing", foreign_keys=[listing_id], backref="ratings")





class PricePredictionCache(db.Model):
    """Cache layer for Gemini AI price predictions — 6-hour TTL."""
    __tablename__ = "price_prediction_cache"
    id          = db.Column(db.Integer, primary_key=True)
    cache_key   = db.Column(db.String(200), unique=True, nullable=False, index=True)
    crop_name   = db.Column(db.String(100), nullable=False)
    region      = db.Column(db.String(80),  nullable=False)
    month       = db.Column(db.String(20),  nullable=False)
    ai_response = db.Column(db.Text, nullable=False)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

class PricePredictionLog(db.Model):
    """Logs every AI price prediction query for analytics and audit trail."""
    __tablename__ = "price_prediction_logs"
    id          = db.Column(db.Integer, primary_key=True)
    crop_name   = db.Column(db.String(100), nullable=False)
    region      = db.Column(db.String(80), nullable=False)
    month       = db.Column(db.String(20), nullable=False)
    season      = db.Column(db.String(30), nullable=True)
    user_id     = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    ai_response = db.Column(db.Text, nullable=True)
    queried_at  = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship("User", foreign_keys=[user_id], backref="price_queries")


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

    from datetime import timedelta
    cached = (WeatherLog.query.filter_by(city=city)
              .order_by(WeatherLog.fetched_at.desc()).first())
    if cached:
        age = datetime.utcnow() - cached.fetched_at
        if age < timedelta(minutes=30):
            return {
                "city": city, "temperature": cached.temperature,
                "humidity": cached.humidity, "description": cached.description,
                "wind_speed": cached.wind_speed, "icon": cached.icon,
                "success": True, "cached": True,
                "cache_age_mins": int(age.total_seconds() / 60)
            }

    tz_cities = {
        "mbeya":         {"lat": -8.9000,  "lon": 33.4600},
        "dar es salaam": {"lat": -6.7924,  "lon": 39.2083},
        "dodoma":        {"lat": -6.1730,  "lon": 35.7395},
        "arusha":        {"lat": -3.3869,  "lon": 36.6830},
        "mwanza":        {"lat": -2.5164,  "lon": 32.9175},
        "tanga":         {"lat": -5.0690,  "lon": 39.0987},
        "morogoro":      {"lat": -6.8160,  "lon": 37.6833},
        "iringa":        {"lat": -7.7700,  "lon": 35.6930},
        "kilimanjaro":   {"lat": -3.0674,  "lon": 37.3556},
        "tabora":        {"lat": -5.0167,  "lon": 32.8000},
        "kigoma":        {"lat": -4.8771,  "lon": 29.6278},
        "singida":       {"lat": -4.8185,  "lon": 34.7500},
        "songwe":        {"lat": -9.3500,  "lon": 33.2000},
        "lindi":         {"lat": -9.9970,  "lon": 39.7140},
        "mtwara":        {"lat": -10.2667, "lon": 40.1833},
        "kagera":        {"lat": -1.2833,  "lon": 31.7667},
        "geita":         {"lat": -2.8667,  "lon": 32.1667},
        "shinyanga":     {"lat": -3.6600,  "lon": 33.4200},
        "rukwa":         {"lat": -7.9000,  "lon": 31.4167},
        "ruvuma":        {"lat": -10.6833, "lon": 35.6500},
    }
    city_key = city.lower().strip()
    coords = tz_cities.get(city_key)
    if coords:
        params = {"lat": coords["lat"], "lon": coords["lon"],
                  "appid": WEATHER_API_KEY, "units": "metric", "lang": "sw"}
    else:
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


@app.route("/dashboard/add", methods=["GET", "POST"])
@login_required
def add_product():
    if request.method == "POST":
        data        = request.get_json() or request.form
        crop_name   = data.get("crop_name", "").strip()
        quantity    = data.get("quantity", 0)
        price       = data.get("price", 0)
        region      = data.get("location", current_user.region or "")
        contact     = current_user.phone or ""
        image_url   = data.get("image_url", "")
        unit        = data.get("unit", "kg")
        description = data.get("description", "")

        if not crop_name or not price:
            return jsonify({"error": "Jaza sehemu zote zinazohitajika."}), 400

        listing = MarketListing(
            seller_id    = current_user.id,
            title        = crop_name,
            crop_name    = crop_name,
            quantity_kg  = float(quantity),
            unit         = unit,
            price_tzs    = float(price),
            region       = region,
            contact      = contact,
            description  = description,
            image_url    = image_url,
            is_available = True
        )
        db.session.add(listing)
        db.session.commit()
        return jsonify({"message": "Orodha imeongezwa!", "id": listing.id}), 201
    crops = Crop.query.all()
    return render_template("dashboard/add_product.html", crops=crops)


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
                     "quantity_kg": l.quantity_kg, "unit": l.unit, "price_tzs": l.price_tzs,
                     "region": l.region, "contact": l.contact,
                     "posted_at": l.posted_at.isoformat()} for l in listings])


@app.route("/api/listings", methods=["POST"])
@login_required
def create_listing():
    data        = request.get_json()
    crop_name   = data.get("crop_name", "").strip()
    quantity    = data.get("quantity", 0)
    price       = data.get("price", 0)
    region      = data.get("region", current_user.region or "")
    contact     = data.get("contact", current_user.phone or "")
    image_url   = data.get("image_url", "")
    unit        = data.get("unit", "kg")
    description = data.get("description", "")

    if not crop_name or not price:
        return jsonify({"error": "Jaza sehemu zote zinazohitajika."}), 400

    listing = MarketListing(
        seller_id    = current_user.id,
        title        = crop_name,
        crop_name    = crop_name,
        quantity_kg  = float(quantity),
        unit         = unit,
        price_tzs    = float(price),
        region       = region,
        contact      = contact,
        description  = description,
        image_url    = image_url,
        is_available = True
    )
    db.session.add(listing)
    db.session.commit()
    return jsonify({"message": "Orodha imeongezwa.", "id": listing.id}), 201


@app.route("/health")
def health():
    return jsonify({"status": "ok", "timestamp": datetime.utcnow().isoformat()})



# -- Rating Helper --

def get_seller_avg_rating(seller_id):
    from sqlalchemy import func
    result = db.session.query(func.avg(SellerRating.stars)).filter_by(seller_id=seller_id).scalar()
    count  = SellerRating.query.filter_by(seller_id=seller_id).count()
    return {"avg": round(float(result), 1) if result else 0.0, "count": count}

@app.route("/listings/<int:listing_id>/rate", methods=["POST"])
@login_required
def rate_seller(listing_id):
    listing = MarketListing.query.get_or_404(listing_id)
    if listing.seller_id == current_user.id:
        return jsonify({"error": "Huwezi kujipa rating."}), 400
    data  = request.get_json() or request.form
    stars = int(data.get("stars", 0))
    if stars < 1 or stars > 5:
        return jsonify({"error": "Chagua nyota 1 hadi 5."}), 400
    existing = SellerRating.query.filter_by(rater_id=current_user.id, listing_id=listing_id).first()
    if existing:
        return jsonify({"error": "Tayari umisha-rate seller huyu."}), 409
    rating = SellerRating(
        seller_id  = listing.seller_id,
        rater_id   = current_user.id,
        listing_id = listing_id,
        stars      = stars,
        comment    = data.get("comment", "").strip()[:300]
    )
    db.session.add(rating)
    db.session.commit()
    info = get_seller_avg_rating(listing.seller_id)
    return jsonify({"message": "Asante! Rating imehifadhiwa.", "avg": info["avg"], "count": info["count"]}), 201


@app.route("/api/listing/<int:listing_id>/rating", methods=["GET"])
def listing_rating_api(listing_id):
    listing = MarketListing.query.get_or_404(listing_id)
    return jsonify(get_seller_avg_rating(listing.seller_id))

@app.route("/api/seller/<int:seller_id>/rating", methods=["GET"])
def seller_rating_api(seller_id):
    return jsonify(get_seller_avg_rating(seller_id))



# ── AI Price Prediction ───────────────────────────────────────────────────────


def get_cached_prediction(cache_key):
    """Return cached prediction if exists and under 6 hours old."""
    from datetime import timedelta
    cached = PricePredictionCache.query.filter_by(cache_key=cache_key).first()
    if cached:
        age = datetime.utcnow() - cached.created_at
        if age < timedelta(hours=6):
            import json as json_lib
            return json_lib.loads(cached.ai_response)
        db.session.delete(cached)
        db.session.commit()
    return None

def save_prediction_cache(cache_key, crop_sw, region, month, ai_response_text):
    """Save a new prediction to cache."""
    try:
        existing = PricePredictionCache.query.filter_by(cache_key=cache_key).first()
        if existing:
            existing.ai_response = ai_response_text
            existing.created_at  = datetime.utcnow()
        else:
            entry = PricePredictionCache(
                cache_key   = cache_key,
                crop_name   = crop_sw,
                region      = region,
                month       = month,
                ai_response = ai_response_text,
            )
            db.session.add(entry)
        db.session.commit()
    except Exception:
        db.session.rollback()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

TANZANIA_CROPS = {
    "mahindi":   {"en": "Maize",        "category": "staple",      "unit": "kg"},
    "mpunga":    {"en": "Rice (paddy)",  "category": "staple",      "unit": "kg"},
    "viazi":     {"en": "Potatoes",      "category": "staple",      "unit": "kg"},
    "muhogo":    {"en": "Cassava",       "category": "staple",      "unit": "kg"},
    "ndizi":     {"en": "Bananas",       "category": "horticulture","unit": "bunch"},
    "nyanya":    {"en": "Tomatoes",      "category": "horticulture","unit": "kg"},
    "vitunguu":  {"en": "Onions",        "category": "horticulture","unit": "kg"},
    "korosho":   {"en": "Cashew nuts",   "category": "cash_crop",   "unit": "kg"},
    "kahawa":    {"en": "Coffee",        "category": "cash_crop",   "unit": "kg"},
    "alizeti":   {"en": "Sunflower",     "category": "oilseed",     "unit": "kg"},
    "maharage":  {"en": "Beans",         "category": "pulse",       "unit": "kg"},
    "mtama":     {"en": "Sorghum",       "category": "cereal",      "unit": "kg"},
}

TANZANIA_REGIONS = [
    "Dar es Salaam", "Mwanza", "Arusha", "Dodoma", "Mbeya",
    "Morogoro", "Tanga", "Iringa", "Kilimanjaro", "Tabora",
    "Kigoma", "Singida", "Kagera", "Geita", "Shinyanga",
    "Rukwa", "Ruvuma", "Lindi", "Mtwara", "Songwe",
    "Simiyu", "Katavi", "Njombe", "Pwani", "Manyara"
]

def build_prediction_prompt(crop_sw, region, month):
    crop_info = TANZANIA_CROPS.get(crop_sw.lower(), {})
    crop_en   = crop_info.get("en", crop_sw)
    unit      = crop_info.get("unit", "kg")
    category  = crop_info.get("category", "general")

    return f"""You are an expert agricultural market analyst specializing in Tanzania's farming economy. Provide a precise crop price prediction based on real market knowledge.

QUERY:
- Crop: {crop_sw.title()} ({crop_en})
- Region: {region}, Tanzania
- Month: {month}
- Category: {category}
- Unit: per {unit}

Respond ONLY with a valid JSON object. No markdown, no explanation outside JSON.

{{
  "crop_sw": "{crop_sw}",
  "crop_en": "{crop_en}",
  "region": "{region}",
  "month": "{month}",
  "unit": "{unit}",
  "predicted_price_low": <integer in TZS>,
  "predicted_price_high": <integer in TZS>,
  "predicted_price_mid": <integer in TZS>,
  "trend": "rising" | "stable" | "falling",
  "trend_pct": <float, e.g. 8.5 means +8.5%>,
  "confidence": "high" | "medium" | "low",
  "season_context": "<1 sentence about the season and how it affects this crop in this region>",
  "market_advice": "<2-3 sentences: concrete advice for a Tanzanian farmer — when to sell, where, and why>",
  "key_factors": ["<factor 1>", "<factor 2>", "<factor 3>"],
  "best_markets": ["<market/town name>", "<market/town name>"]
}}

Use real Tanzanian market knowledge. Prices must be realistic TZS values (e.g. mahindi: 400-900 TZS/kg, nyanya: 800-2500 TZS/kg, korosho: 2000-4500 TZS/kg). Account for seasonal patterns, regional demand, post-harvest timing, and current market conditions in Tanzania."""


@app.route("/api/price-prediction", methods=["POST"])
def api_price_prediction():
    if not GEMINI_API_KEY:
        return jsonify({"error": "Huduma ya AI haipo. Wasiliana na msimamizi."}), 503

    data    = request.get_json() or {}
    crop_sw = data.get("crop", "").strip().lower()
    region  = data.get("region", "").strip()
    month   = data.get("month", "").strip()

    if not crop_sw or crop_sw not in TANZANIA_CROPS:
        return jsonify({"error": "Zao halijulikani. Chagua zao kutoka kwenye orodha."}), 400
    if not region:
        return jsonify({"error": "Taja mkoa wako."}), 400
    if not month:
        return jsonify({"error": "Taja mwezi."}), 400

    # ── Cache check ──────────────────────────────────────────────────────────
    cache_key  = f"{crop_sw}:{region.lower()}:{month.lower()}"
    cached     = get_cached_prediction(cache_key)
    if cached:
        return jsonify({"success": True, "prediction": cached, "cached": True})

    prompt = build_prediction_prompt(crop_sw, region, month)

    try:
        resp = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-lite:generateContent?key={GEMINI_API_KEY}",
            headers={"content-type": "application/json"},
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=20,
        )
        resp.raise_for_status()
        ai_text = resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()

        if ai_text.startswith("```"):
            ai_text = ai_text.split("```")[1]
            if ai_text.startswith("json"):
                ai_text = ai_text[4:]
            ai_text = ai_text.strip()

        import json as json_lib
        prediction = json_lib.loads(ai_text)

        # ── Save to cache ────────────────────────────────────────────────────
        save_prediction_cache(cache_key, crop_sw, region, month, ai_text)

        # ── Log to DB ────────────────────────────────────────────────────────
        try:
            log = PricePredictionLog(
                crop_name   = crop_sw,
                region      = region,
                month       = month,
                user_id     = current_user.id if current_user.is_authenticated else None,
                ai_response = ai_text,
            )
            db.session.add(log)
            db.session.commit()
        except Exception:
            db.session.rollback()

        return jsonify({"success": True, "prediction": prediction, "cached": False})

    except requests.exceptions.Timeout:
        return jsonify({"error": "AI imechukua muda mrefu. Jaribu tena."}), 504
    except requests.exceptions.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else 0
        if status == 429:
            return jsonify({"error": "Huduma ya AI imefika kikomo. Jaribu tena baada ya dakika chache."}), 429
        if status == 400:
            return jsonify({"error": "Ombi lisilo sahihi kwa AI. Jaribu tena."}), 400
        return jsonify({"error": "Huduma ya AI haipatikani kwa sasa."}), 502
    except requests.exceptions.RequestException:
        return jsonify({"error": "Tatizo la mtandao. Angalia muunganiko wako."}), 502
    except Exception:
        return jsonify({"error": "AI ilirudisha jibu lisilo sahihi. Jaribu tena."}), 500


@app.route("/api/price-prediction/crops", methods=["GET"])
def api_prediction_crops():
    """Returns the list of supported crops for the frontend selector."""
    crops = [
        {"sw": k, "en": v["en"], "category": v["category"], "unit": v["unit"]}
        for k, v in TANZANIA_CROPS.items()
    ]
    return jsonify({"crops": crops, "regions": TANZANIA_REGIONS})



@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("500.html"), 500


# ── Init DB & Run ────────────────────────────────────────────────────────────


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("FLASK_DEBUG", "false").lower() == "true")


@app.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "POST":
        data = request.get_json() or request.form
        old_password = data.get("old_password", "")
        new_password = data.get("new_password", "")
        confirm      = data.get("confirm_password", "")

        if not current_user.check_password(old_password):
            return jsonify({"error": "Nywila ya zamani si sahihi."}), 400
        if len(new_password) < 8:
            return jsonify({"error": "Nywila mpya lazima iwe na herufi 8 au zaidi."}), 400
        if new_password != confirm:
            return jsonify({"error": "Nywila mpya hazifanani."}), 400

        current_user.set_password(new_password)
        db.session.commit()
        return jsonify({"message": "Nywila imebadilishwa!"})

    return render_template("auth/change_password.html")

@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        data  = request.get_json() or request.form
        phone = data.get("phone")
        user  = User.query.filter_by(phone=phone).first()
        if not user:
            return jsonify({"error": "Namba ya simu haijapatikana."}), 404
        new_password = data.get("new_password")
        if not new_password or len(new_password) < 6:
            return jsonify({"error": "Nywila mpya iwe na herufi 6 au zaidi."}), 400
        user.set_password(new_password)
        db.session.commit()
        return jsonify({"message": "Nywila imebadilishwa. Ingia sasa."})
    return render_template("auth/forgot_password.html")

@app.route("/api/upload-image", methods=["POST"])
@login_required
def upload_image():
    if "file" not in request.files:
        return jsonify({"error": "Hakuna faili."}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Chagua picha kwanza."}), 400
    if not supabase_client:
        return jsonify({"error": "Storage haipo."}), 500
    allowed = {"jpg", "jpeg", "png", "webp"}
    ext = file.filename.rsplit(".", 1)[-1].lower()
    if ext not in allowed:
        return jsonify({"error": "Picha lazima iwe jpg, png, au webp."}), 400
    filename = f"crops/{current_user.id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.{ext}"
    file_bytes = file.read()
    supabase_client.storage.from_("crop-images").upload(
        filename, file_bytes, {"content-type": file.content_type}
    )
    public_url = f"{SUPABASE_URL}/storage/v1/object/public/crop-images/{filename}"
    return jsonify({"url": public_url})

@app.route("/bei")
def price_intelligence():
    return render_template("market/price_intelligence.html")


@app.route("/farmers")
def farmers():
    q      = request.args.get("q", "").strip()
    region = request.args.get("region", "").strip()
    query  = User.query.filter_by(role="farmer")
    if q:
        query = query.filter(User.full_name.ilike(f"%{q}%"))
    if region:
        query = query.filter(User.region.ilike(f"%{region}%"))
    farmers = query.order_by(User.full_name).all()
    regions = db.session.query(User.region).filter(User.role=="farmer").distinct().all()
    regions = [r[0] for r in regions if r[0]]
    return render_template("farmers.html", farmers=farmers, regions=regions, q=q, region=region)

@app.route("/admin")
@login_required
def admin_panel():
    if current_user.role != "admin":
        return redirect(url_for("index"))
    users    = User.query.order_by(User.created_at.desc()).all()
    listings = MarketListing.query.order_by(MarketListing.posted_at.desc()).all()
    total_farmers  = User.query.filter_by(role="farmer").count()
    total_admins   = User.query.filter_by(role="admin").count()
    total_listings = MarketListing.query.count()
    active_listings= MarketListing.query.filter_by(is_available=True).count()
    reports = ListingReport.query.order_by(ListingReport.created_at.desc()).all()
    return render_template("admin/panel.html",
        users=users, listings=listings, reports=reports,
        total_farmers=total_farmers, total_admins=total_admins,
        total_listings=total_listings, active_listings=active_listings)

@app.route("/admin/delete-listing/<int:listing_id>", methods=["POST"])
@login_required
def admin_delete_listing(listing_id):
    if current_user.role != "admin":
        return jsonify({"error": "Hairuhusiwi."}), 403
    listing = MarketListing.query.get_or_404(listing_id)
    db.session.delete(listing)
    db.session.commit()
    return jsonify({"message": "Orodha imefutwa."})

@app.route("/admin/delete-user/<int:user_id>", methods=["POST"])
@login_required
def admin_delete_user(user_id):
    if current_user.role != "admin":
        return jsonify({"error": "Hairuhusiwi."}), 403
    if user_id == current_user.id:
        return jsonify({"error": "Huwezi kujifuta mwenyewe."}), 400
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "Mtumiaji amefutwa."})

@app.route("/developer")
def developer():
    return render_template("developer.html")

@app.route("/listings/report/<int:listing_id>", methods=["POST"])
@login_required
def report_listing(listing_id):
    listing = MarketListing.query.get_or_404(listing_id)
    if listing.seller_id == current_user.id:
        return jsonify({"error": "Huwezi ku-report orodha yako mwenyewe."}), 400
    data   = request.get_json() or request.form
    reason = data.get("reason", "").strip()
    if not reason:
        return jsonify({"error": "Taja sababu ya ripoti."}), 400
    existing = ListingReport.query.filter_by(reporter_id=current_user.id, listing_id=listing_id).first()
    if existing:
        return jsonify({"error": "Tayari umesharipoti orodha hii."}), 409
    report = ListingReport(reporter_id=current_user.id, listing_id=listing_id, reason=reason)
    db.session.add(report)
    db.session.commit()
    return jsonify({"message": "Ripoti imetumwa. Asante kwa kutusaidia."}), 201

@app.route("/dashboard/delete-listing/<int:listing_id>", methods=["POST"])
@login_required
def delete_listing(listing_id):
    listing = MarketListing.query.get_or_404(listing_id)
    if listing.seller_id != current_user.id:
        return jsonify({"error": "Hairuhusiwi."}), 403
    db.session.delete(listing)
    db.session.commit()
    return jsonify({"message": "Orodha imefutwa."})
@app.route("/admin/verify-user/<int:user_id>", methods=["POST"])
@login_required
def admin_verify_user(user_id):
    if current_user.role != "admin":
        return jsonify({"error": "Hairuhusiwi."}), 403
    user = User.query.get_or_404(user_id)
    user.is_verified = not user.is_verified
    db.session.commit()
    status = "imethibitishwa" if user.is_verified else "imeondolewa uthibitisho"
    return jsonify({"message": f"Akaunti ya {user.full_name} {status}.", "is_verified": user.is_verified})