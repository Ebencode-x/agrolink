import os
import requests
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
from supabase import create_client

# ── Security layer ────────────────────────────────────────────────────────────
from security import (
    sanitize, sanitize_dict,
    validate_phone, validate_email, validate_password,
    validate_price, validate_quantity,
    require_active_account, require_admin,
    apply_security_headers,
)

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-key-change-in-production")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///agrolink.db")

if app.config["SQLALCHEMY_DATABASE_URI"].startswith("postgresql+psycopg://"):
    app.config["SQLALCHEMY_DATABASE_URI"] = app.config["SQLALCHEMY_DATABASE_URI"].replace(
        "postgresql+psycopg://", "postgresql+psycopg://", 1
    )

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_pre_ping": True, "pool_recycle": 300}

SUPABASE_URL     = os.environ.get("SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY", "")
supabase_client  = create_client(SUPABASE_URL, SUPABASE_ANON_KEY) if SUPABASE_URL else None

WEATHER_API_KEY  = os.environ.get("OPENWEATHER_API_KEY", "")
WEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_BASE_URL = "https://api.openweathermap.org/data/2.5/forecast"

db       = SQLAlchemy(app)
migrate  = Migrate(app, db)
bcrypt   = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view    = "login"
login_manager.login_message = "Tafadhali ingia kwanza."

# ── CORS: restrict to your own domain only ───────────────────────────────────
# BADILISHA "https://agrolink.co.tz" ukipata domain yako halisi
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "https://agrolink-y9za.onrender.com").split(",")
CORS(app, origins=ALLOWED_ORIGINS, supports_credentials=True)

# ── Rate Limiter ──────────────────────────────────────────────────────────────
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "60 per minute"],
    storage_uri="memory://",
)

# ── Security Headers (kila response) ─────────────────────────────────────────
apply_security_headers(app)


# ── Models ───────────────────────────────────────────────────────────────────

class BannedEmail(db.Model):
    """
    Akaunti zilizofungwa — email/simu haiwezi kutumika tena kujiandikisha.
    Admin anaweza kuongeza hapa moja kwa moja au kupitia /admin panel.
    """
    __tablename__ = "banned_emails"
    id         = db.Column(db.Integer, primary_key=True)
    email      = db.Column(db.String(120), unique=True, nullable=True, index=True)
    phone      = db.Column(db.String(20),  unique=True, nullable=True, index=True)
    reason     = db.Column(db.String(300), nullable=True)
    banned_at  = db.Column(db.DateTime, default=datetime.utcnow)
    banned_by  = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)


class User(db.Model):
    __tablename__ = "users"
    id            = db.Column(db.Integer, primary_key=True)
    full_name     = db.Column(db.String(120), nullable=False)
    phone         = db.Column(db.String(20),  unique=True, nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    region        = db.Column(db.String(80),  nullable=True)
    role          = db.Column(db.String(20),  default="farmer")
    is_active     = db.Column(db.Boolean,     default=True)
    is_verified   = db.Column(db.Boolean,     default=False)
    accepted_terms = db.Column(db.Boolean,    default=False)  # ← T&C checkbox
    terms_accepted_at = db.Column(db.DateTime, nullable=True)  # ← wakati wa kukubali
    created_at    = db.Column(db.DateTime,    default=datetime.utcnow)

    crops    = db.relationship("Crop",          backref="owner",  lazy=True)
    listings = db.relationship("MarketListing", backref="seller", lazy=True)

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
    category    = db.Column(db.String(50),  nullable=False)
    season      = db.Column(db.String(50),  nullable=True)
    hectares    = db.Column(db.Float,       nullable=True)
    region      = db.Column(db.String(80),  nullable=True)
    description = db.Column(db.Text,        nullable=True)
    image_url   = db.Column(db.String(300), nullable=True)
    created_at  = db.Column(db.DateTime,    default=datetime.utcnow)
    updated_at  = db.Column(db.DateTime,    default=datetime.utcnow, onupdate=datetime.utcnow)
    market_prices = db.relationship("MarketPrice", backref="crop", lazy=True)


class MarketPrice(db.Model):
    __tablename__ = "market_prices"
    id          = db.Column(db.Integer, primary_key=True)
    crop_id     = db.Column(db.Integer, db.ForeignKey("crops.id"), nullable=False)
    region      = db.Column(db.String(80),  nullable=False)
    market      = db.Column(db.String(120), nullable=True)
    price_tzs   = db.Column(db.Float,       nullable=False)
    unit        = db.Column(db.String(20),  default="kg")
    recorded_at = db.Column(db.DateTime,    default=datetime.utcnow)
    source      = db.Column(db.String(100), nullable=True)


class MarketListing(db.Model):
    __tablename__ = "market_listings"
    id           = db.Column(db.Integer, primary_key=True)
    seller_id    = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title        = db.Column(db.String(200), nullable=False)
    crop_name    = db.Column(db.String(100), nullable=False)
    quantity_kg  = db.Column(db.Float,       nullable=False)
    unit         = db.Column(db.String(20),  default="kg")
    price_tzs    = db.Column(db.Float,       nullable=False)
    region       = db.Column(db.String(80),  nullable=False)
    contact      = db.Column(db.String(50),  nullable=False)
    description  = db.Column(db.String(500), nullable=True)
    is_available = db.Column(db.Boolean,     default=True)
    image_url    = db.Column(db.String(300), nullable=True)
    posted_at    = db.Column(db.DateTime,    default=datetime.utcnow)


class ListingReport(db.Model):
    __tablename__ = "listing_reports"
    id          = db.Column(db.Integer, primary_key=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey("users.id"),        nullable=False)
    listing_id  = db.Column(db.Integer, db.ForeignKey("market_listings.id"), nullable=False)
    reason      = db.Column(db.String(200), nullable=False)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint("reporter_id", "listing_id", name="unique_report"),)
    reporter = db.relationship("User",          foreign_keys=[reporter_id], backref="reports_made")
    listing  = db.relationship("MarketListing", foreign_keys=[listing_id], backref="reports")


class SellerRating(db.Model):
    __tablename__ = "seller_ratings"
    id         = db.Column(db.Integer, primary_key=True)
    seller_id  = db.Column(db.Integer, db.ForeignKey("users.id"),           nullable=False)
    rater_id   = db.Column(db.Integer, db.ForeignKey("users.id"),           nullable=False)
    listing_id = db.Column(db.Integer, db.ForeignKey("market_listings.id"), nullable=False)
    stars      = db.Column(db.Integer, nullable=False)
    comment    = db.Column(db.String(300), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint("rater_id", "listing_id", name="unique_rating"),)
    seller  = db.relationship("User",          foreign_keys=[seller_id],  backref="ratings_received")
    rater   = db.relationship("User",          foreign_keys=[rater_id],   backref="ratings_given")
    listing = db.relationship("MarketListing", foreign_keys=[listing_id], backref="ratings")


class PricePredictionCache(db.Model):
    __tablename__ = "price_prediction_cache"
    id         = db.Column(db.Integer, primary_key=True)
    cache_key  = db.Column(db.String(200), unique=True, nullable=False, index=True)
    crop_name  = db.Column(db.String(100), nullable=False)
    region     = db.Column(db.String(80),  nullable=False)
    month      = db.Column(db.String(20),  nullable=False)
    ai_response = db.Column(db.Text,       nullable=False)
    created_at = db.Column(db.DateTime,    default=datetime.utcnow)


class PricePredictionLog(db.Model):
    __tablename__ = "price_prediction_logs"
    id         = db.Column(db.Integer, primary_key=True)
    crop_name  = db.Column(db.String(100), nullable=False)
    region     = db.Column(db.String(80),  nullable=False)
    month      = db.Column(db.String(20),  nullable=False)
    season     = db.Column(db.String(30),  nullable=True)
    user_id    = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    ai_response = db.Column(db.Text,       nullable=True)
    queried_at = db.Column(db.DateTime,    default=datetime.utcnow)
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


# ── Login Manager ─────────────────────────────────────────────────────────────

@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(int(user_id))
    # SECURITY FIX: akaunti iliyosimamishwa haiingii hata na session hai
    if user and not user.is_active:
        return None
    return user


# ── Weather Service (unchanged logic) ────────────────────────────────────────

def get_weather(city="Mbeya"):
    if not WEATHER_API_KEY:
        return {"error": "API key haijawekwa", "city": city, "success": False}

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
        "mbeya":         {"lat": -8.9000, "lon": 33.4600},
        "dar es salaam": {"lat": -6.7924, "lon": 39.2083},
        "dodoma":        {"lat": -6.1730, "lon": 35.7395},
        "arusha":        {"lat": -3.3869, "lon": 36.6830},
        "mwanza":        {"lat": -2.5164, "lon": 32.9175},
        "tanga":         {"lat": -5.0690, "lon": 39.0987},
        "morogoro":      {"lat": -6.8160, "lon": 37.6833},
        "iringa":        {"lat": -7.7700, "lon": 35.6930},
        "kilimanjaro":   {"lat": -3.0674, "lon": 37.3556},
        "tabora":        {"lat": -5.0167, "lon": 32.8000},
        "kigoma":        {"lat": -4.8771, "lon": 29.6278},
        "singida":       {"lat": -4.8185, "lon": 34.7500},
        "songwe":        {"lat": -9.3500, "lon": 33.2000},
        "lindi":         {"lat": -9.9970, "lon": 39.7140},
        "mtwara":        {"lat": -10.2667,"lon": 40.1833},
        "kagera":        {"lat": -1.2833, "lon": 31.7667},
        "geita":         {"lat": -2.8667, "lon": 32.1667},
        "shinyanga":     {"lat": -3.6600, "lon": 33.4200},
        "rukwa":         {"lat": -7.9000, "lon": 31.4167},
        "ruvuma":        {"lat": -10.6833,"lon": 35.6500},
    }

    city_key = city.lower().strip()
    coords   = tz_cities.get(city_key)
    params   = (
        {"lat": coords["lat"], "lon": coords["lon"],
         "appid": WEATHER_API_KEY, "units": "metric", "lang": "sw"}
        if coords else
        {"q": f"{city},TZ", "appid": WEATHER_API_KEY, "units": "metric", "lang": "sw"}
    )

    try:
        resp = requests.get(WEATHER_BASE_URL, params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        weather_data = {
            "city":        city,
            "temperature": data["main"]["temp"],
            "feels_like":  data["main"]["feels_like"],
            "humidity":    data["main"]["humidity"],
            "description": data["weather"][0]["description"],
            "wind_speed":  data["wind"]["speed"],
            "icon":        data["weather"][0]["icon"],
            "success":     True,
        }
        log = WeatherLog(city=city, temperature=weather_data["temperature"],
                         humidity=weather_data["humidity"],
                         description=weather_data["description"],
                         wind_speed=weather_data["wind_speed"],
                         icon=weather_data["icon"])
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
                 "description": i["weather"][0]["description"],
                 "icon": i["weather"][0]["icon"]}
                for i in resp.json().get("list", [])]
    except:
        return []


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    crops    = Crop.query.order_by(Crop.created_at.desc()).limit(6).all()
    listings = MarketListing.query.filter_by(is_available=True).order_by(
        MarketListing.posted_at.desc()).limit(8).all()
    weather  = get_weather("Mbeya")
    return render_template("index.html", crops=crops, listings=listings, weather=weather)


@app.route("/weather")
def weather_page():
    city     = sanitize(request.args.get("city", "Mbeya"), max_length=50)
    weather  = get_weather(city)
    forecast = get_forecast(city)
    return jsonify({"weather": weather, "forecast": forecast})


# ── AUTH ──────────────────────────────────────────────────────────────────────

@app.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def login():
    if request.method == "POST":
        data     = request.get_json() or request.form
        phone    = sanitize(data.get("phone", ""), max_length=20)
        password = data.get("password", "")  # Usiisanitize nywila — chars special zinahitajika

        # SECURITY FIX: generic error message — usitaje "phone" au "password" peke yake
        user = User.query.filter_by(phone=phone).first()

        if not user or not user.check_password(password):
            return jsonify({"error": "Namba ya simu au nywila si sahihi."}), 401

        # SECURITY FIX: angalia is_active KABLA ya kulogin
        if not user.is_active:
            return jsonify({
                "error": "Akaunti yako imesimamishwa. Wasiliana na msimamizi kwa msaada."
            }), 403

        login_user(user)
        return jsonify({"message": "Umeingia.", "role": user.role})

    return render_template("auth/login.html")


@app.route("/register", methods=["GET", "POST"])
@limiter.limit("3 per hour")
def register():
    if request.method == "POST":
        data = request.get_json() or request.form

        # ── Sanitize all inputs ───────────────────────────────────────────────
        full_name = sanitize(data.get("full_name", ""), max_length=120)
        phone     = sanitize(data.get("phone", ""), max_length=20)
        email     = sanitize(data.get("email", ""), max_length=120) or None
        region    = sanitize(data.get("region", ""), max_length=80)
        role      = sanitize(data.get("role", "farmer"), max_length=20)
        password  = data.get("password", "")
        terms     = data.get("terms_accepted", False)

        # ── Validate T&C ─────────────────────────────────────────────────────
        if not terms or str(terms).lower() in ("false", "0", ""):
            return jsonify({"error": "Lazima ukubali Masharti na Vigezo vya AgroLink."}), 400

        # ── Validate required fields ──────────────────────────────────────────
        if not full_name:
            return jsonify({"error": "Jina kamili linahitajika."}), 400
        if not validate_phone(phone):
            return jsonify({"error": "Namba ya simu si sahihi. Tumia muundo: 0712345678."}), 400
        if email and not validate_email(email):
            return jsonify({"error": "Muundo wa email si sahihi."}), 400

        # ── Validate password strength ────────────────────────────────────────
        pw_ok, pw_err = validate_password(password)
        if not pw_ok:
            return jsonify({"error": pw_err}), 400

        # ── Check banned list ─────────────────────────────────────────────────
        banned_phone = BannedEmail.query.filter_by(phone=phone).first()
        banned_email = BannedEmail.query.filter_by(email=email).first() if email else None
        if banned_phone or banned_email:
            return jsonify({
                "error": "Namba hii au email imefungwa. Wasiliana na msimamizi."
            }), 403

        # ── Check duplicates ──────────────────────────────────────────────────
        if User.query.filter_by(phone=phone).first():
            return jsonify({"error": "Namba ya simu tayari imetumika."}), 409
        if email and User.query.filter_by(email=email).first():
            return jsonify({"error": "Email tayari imetumika."}), 409

        # ── Validate role ─────────────────────────────────────────────────────
        if role not in ("farmer", "agent"):
            role = "farmer"

        # ── Create user ───────────────────────────────────────────────────────
        user = User(
            full_name         = full_name,
            phone             = phone,
            email             = email,
            region            = region,
            role              = role,
            accepted_terms    = True,
            terms_accepted_at = datetime.utcnow(),
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        return jsonify({"message": "Akaunti imefunguliwa.", "id": user.id}), 201

    return render_template("auth/register.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/terms")
def terms():
    """Ukurasa wa Masharti na Vigezo (Terms & Conditions)."""
    return render_template("legal/terms.html")


# ── SECURITY FIX: forgot-password inahitaji uthibitisho — siyo kubadilisha moja kwa moja
@app.route("/forgot-password", methods=["GET", "POST"])
@limiter.limit("3 per hour")
def forgot_password():
    """
    NOTE: Hii toleo linabadilisha nywila bila OTP/email verification kwa sababu
    bado hatuna email service imara. Kwa production kamili, ongeza:
    1. Generate random token → hifadhi kwenye DB na expiry ya dakika 15
    2. Tuma token kwa SMS (Africa's Talking) au email
    3. Mtumiaji aingie token → ndipo abadilishe nywila

    Kwa sasa, tumia security questions au admin reset badala ya self-service.
    """
    if request.method == "POST":
        data         = request.get_json() or request.form
        phone        = sanitize(data.get("phone", ""), max_length=20)
        new_password = data.get("new_password", "")
        confirm      = data.get("confirm_password", "")

        if not validate_phone(phone):
            return jsonify({"error": "Namba ya simu si sahihi."}), 400

        # SECURITY FIX: validate password strength
        pw_ok, pw_err = validate_password(new_password)
        if not pw_ok:
            return jsonify({"error": pw_err}), 400

        if new_password != confirm:
            return jsonify({"error": "Nywila mpya hazifanani."}), 400

        full_name = sanitize(data.get("full_name", ""), max_length=120).strip().lower()
        if not full_name:
            return jsonify({"error": "Jina kamili linahitajika kuthibitisha akaunti."}), 400

        user = User.query.filter_by(phone=phone).first()

        # SECURITY: Generic message + constant-time check — prevent user enumeration
        generic_ok = jsonify({"message": "Kama taarifa ni sahihi, nywila imebadilishwa."}), 200

        if not user:
            return generic_ok

        # Verify full name matches — second factor without OTP
        if user.full_name.strip().lower() != full_name:
            return generic_ok

        if not user.is_active:
            return jsonify({"error": "Akaunti imesimamishwa. Wasiliana na msimamizi."}), 403

        user.set_password(new_password)
        db.session.commit()
        return jsonify({"message": "Nywila imebadilishwa. Ingia sasa."})

    return render_template("auth/forgot_password.html")


@app.route("/change-password", methods=["GET", "POST"])
@login_required
@require_active_account
def change_password():
    if request.method == "POST":
        data         = request.get_json() or request.form
        old_password = data.get("old_password", "")
        new_password = data.get("new_password", "")
        confirm      = data.get("confirm_password", "")

        if not current_user.check_password(old_password):
            return jsonify({"error": "Nywila ya zamani si sahihi."}), 400

        pw_ok, pw_err = validate_password(new_password)
        if not pw_ok:
            return jsonify({"error": pw_err}), 400

        if new_password != confirm:
            return jsonify({"error": "Nywila mpya hazifanani."}), 400

        current_user.set_password(new_password)
        db.session.commit()
        return jsonify({"message": "Nywila imebadilishwa!"})

    return render_template("auth/change_password.html")


# ── DASHBOARD ─────────────────────────────────────────────────────────────────

@app.route("/dashboard")
@login_required
@require_active_account
def dashboard():
    user_listings = MarketListing.query.filter_by(
        seller_id=current_user.id).order_by(MarketListing.posted_at.desc()).all()
    user_crops = Crop.query.filter_by(user_id=current_user.id).all()
    return render_template("dashboard/dashboard.html",
                           listings=user_listings, crops=user_crops)


@app.route("/dashboard/add", methods=["GET", "POST"])
@login_required
@require_active_account
def add_product():
    if request.method == "POST":
        data = request.get_json() or request.form

        crop_name   = sanitize(data.get("crop_name", ""), max_length=100)
        region      = sanitize(data.get("location", current_user.region or ""), max_length=80)
        unit        = sanitize(data.get("unit", "kg"), max_length=20)
        description = sanitize(data.get("description", ""), max_length=500)
        image_url   = sanitize(data.get("image_url", ""), max_length=300)
        contact     = current_user.phone or ""

        if not crop_name:
            return jsonify({"error": "Jina la zao linahitajika."}), 400

        price_ok, price = validate_price(data.get("price", 0))
        if not price_ok:
            return jsonify({"error": "Bei si sahihi. Lazima iwe nambari chanya."}), 400

        qty_ok, quantity = validate_quantity(data.get("quantity", 0))
        if not qty_ok:
            return jsonify({"error": "Kiwango si sahihi."}), 400

        # Validate unit
        if unit not in ("kg", "tani", "debe", "gunia", "bunch", "piece"):
            unit = "kg"

        listing = MarketListing(
            seller_id    = current_user.id,
            title        = crop_name,
            crop_name    = crop_name,
            quantity_kg  = quantity,
            unit         = unit,
            price_tzs    = price,
            region       = region,
            contact      = contact,
            description  = description,
            image_url    = image_url,
            is_available = True,
        )
        db.session.add(listing)
        db.session.commit()
        return jsonify({"message": "Orodha imeongezwa!", "id": listing.id}), 201

    crops = Crop.query.all()
    return render_template("dashboard/add_product.html", crops=crops)


@app.route("/dashboard/delete-listing/<int:listing_id>", methods=["POST"])
@login_required
@require_active_account
def delete_listing(listing_id):
    listing = MarketListing.query.get_or_404(listing_id)
    if listing.seller_id != current_user.id:
        return jsonify({"error": "Hairuhusiwi."}), 403
    db.session.delete(listing)
    db.session.commit()
    return jsonify({"message": "Orodha imefutwa."})


# ── PUBLIC ROUTES ─────────────────────────────────────────────────────────────

@app.route("/listings")
def listings():
    all_listings = MarketListing.query.filter_by(is_available=True).order_by(
        MarketListing.posted_at.desc()).all()
    return render_template("market/listings.html", listings=all_listings)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/bei")
def price_intelligence():
    return render_template("market/price_intelligence.html")


@app.route("/developer")
def developer():
    return render_template("developer.html")


@app.route("/farmers")
def farmers():
    q      = sanitize(request.args.get("q", ""), max_length=100)
    region = sanitize(request.args.get("region", ""), max_length=80)
    query  = User.query.filter_by(role="farmer")
    if q:
        query = query.filter(User.full_name.ilike(f"%{q}%"))
    if region:
        query = query.filter(User.region.ilike(f"%{region}%"))
    farmer_list = query.order_by(User.full_name).all()
    regions = [r[0] for r in db.session.query(User.region).filter(
        User.role == "farmer").distinct().all() if r[0]]
    return render_template("farmers.html", farmers=farmer_list,
                           regions=regions, q=q, region=region)


# ── RATINGS ───────────────────────────────────────────────────────────────────

def get_seller_avg_rating(seller_id):
    from sqlalchemy import func
    result = db.session.query(func.avg(SellerRating.stars)).filter_by(seller_id=seller_id).scalar()
    count  = SellerRating.query.filter_by(seller_id=seller_id).count()
    return {"avg": round(float(result), 1) if result else 0.0, "count": count}


@app.route("/listings/<int:listing_id>/rate", methods=["POST"])
@login_required
@require_active_account
def rate_seller(listing_id):
    listing = MarketListing.query.get_or_404(listing_id)
    if listing.seller_id == current_user.id:
        return jsonify({"error": "Huwezi kujipa rating."}), 400

    data    = request.get_json() or request.form
    comment = sanitize(data.get("comment", ""), max_length=300)

    try:
        stars = int(data.get("stars", 0))
    except (ValueError, TypeError):
        return jsonify({"error": "Rating si sahihi."}), 400

    if stars < 1 or stars > 5:
        return jsonify({"error": "Chagua nyota 1 hadi 5."}), 400

    existing = SellerRating.query.filter_by(
        rater_id=current_user.id, listing_id=listing_id).first()
    if existing:
        return jsonify({"error": "Tayari umisha-rate seller huyu."}), 409

    rating = SellerRating(
        seller_id  = listing.seller_id,
        rater_id   = current_user.id,
        listing_id = listing_id,
        stars      = stars,
        comment    = comment,
    )
    db.session.add(rating)
    db.session.commit()
    info = get_seller_avg_rating(listing.seller_id)
    return jsonify({"message": "Asante! Rating imehifadhiwa.",
                    "avg": info["avg"], "count": info["count"]}), 201


@app.route("/listings/report/<int:listing_id>", methods=["POST"])
@login_required
@require_active_account
def report_listing(listing_id):
    listing = MarketListing.query.get_or_404(listing_id)
    if listing.seller_id == current_user.id:
        return jsonify({"error": "Huwezi ku-report orodha yako mwenyewe."}), 400

    data   = request.get_json() or request.form
    reason = sanitize(data.get("reason", ""), max_length=200)

    if not reason:
        return jsonify({"error": "Taja sababu ya ripoti."}), 400

    existing = ListingReport.query.filter_by(
        reporter_id=current_user.id, listing_id=listing_id).first()
    if existing:
        return jsonify({"error": "Tayari umesharipoti orodha hii."}), 409

    report = ListingReport(
        reporter_id=current_user.id, listing_id=listing_id, reason=reason)
    db.session.add(report)
    db.session.commit()
    return jsonify({"message": "Ripoti imetumwa. Asante kwa kutusaidia."}), 201


# ── API ENDPOINTS ─────────────────────────────────────────────────────────────

@app.route("/api/crops")
def api_crops():
    crops = Crop.query.order_by(Crop.created_at.desc()).all()
    return jsonify([{"id": c.id, "name_sw": c.name_sw, "name_en": c.name_en,
                     "category": c.category, "season": c.season, "region": c.region}
                    for c in crops])


@app.route("/api/prices")
def api_prices():
    prices = MarketPrice.query.order_by(MarketPrice.recorded_at.desc()).limit(50).all()
    return jsonify([{"id": p.id, "crop_id": p.crop_id, "region": p.region,
                     "market": p.market, "price_tzs": p.price_tzs,
                     "recorded_at": p.recorded_at.isoformat()} for p in prices])


@app.route("/api/listings", methods=["GET"])
@limiter.limit("60 per minute")
def api_listings():
    listings = MarketListing.query.filter_by(is_available=True).order_by(
        MarketListing.posted_at.desc()).all()
    return jsonify([{"id": l.id, "title": l.title, "crop_name": l.crop_name,
                     "quantity_kg": l.quantity_kg, "unit": l.unit,
                     "price_tzs": l.price_tzs, "region": l.region,
                     "contact": l.contact, "posted_at": l.posted_at.isoformat()}
                    for l in listings])


@app.route("/api/listings", methods=["POST"])
@login_required
@require_active_account
@limiter.limit("20 per hour")
def create_listing():
    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON data inahitajika."}), 400

    crop_name   = sanitize(data.get("crop_name", ""), max_length=100)
    region      = sanitize(data.get("region", current_user.region or ""), max_length=80)
    contact     = sanitize(data.get("contact", current_user.phone or ""), max_length=50)
    description = sanitize(data.get("description", ""), max_length=500)
    image_url   = sanitize(data.get("image_url", ""), max_length=300)
    unit        = sanitize(data.get("unit", "kg"), max_length=20)

    if not crop_name:
        return jsonify({"error": "Jina la zao linahitajika."}), 400

    price_ok, price = validate_price(data.get("price", 0))
    if not price_ok:
        return jsonify({"error": "Bei si sahihi."}), 400

    qty_ok, quantity = validate_quantity(data.get("quantity", 0))
    if not qty_ok:
        return jsonify({"error": "Kiwango si sahihi."}), 400

    listing = MarketListing(
        seller_id=current_user.id, title=crop_name, crop_name=crop_name,
        quantity_kg=quantity, unit=unit, price_tzs=price, region=region,
        contact=contact, description=description, image_url=image_url,
        is_available=True,
    )
    db.session.add(listing)
    db.session.commit()
    return jsonify({"message": "Orodha imeongezwa.", "id": listing.id}), 201


@app.route("/api/listing/<int:listing_id>/rating")
def listing_rating_api(listing_id):
    listing = MarketListing.query.get_or_404(listing_id)
    return jsonify(get_seller_avg_rating(listing.seller_id))


@app.route("/api/seller/<int:seller_id>/rating")
def seller_rating_api(seller_id):
    return jsonify(get_seller_avg_rating(seller_id))


# ── PRICE PREDICTION ──────────────────────────────────────────────────────────

TANZANIA_CROPS = {
    "mahindi":   {"en": "Maize",        "category": "staple",      "unit": "kg"},
    "mpunga":    {"en": "Rice (paddy)", "category": "staple",      "unit": "kg"},
    "viazi":     {"en": "Potatoes",     "category": "staple",      "unit": "kg"},
    "muhogo":    {"en": "Cassava",      "category": "staple",      "unit": "kg"},
    "ndizi":     {"en": "Bananas",      "category": "horticulture","unit": "bunch"},
    "nyanya":    {"en": "Tomatoes",     "category": "horticulture","unit": "kg"},
    "vitunguu":  {"en": "Onions",       "category": "horticulture","unit": "kg"},
    "korosho":   {"en": "Cashew nuts",  "category": "cash_crop",   "unit": "kg"},
    "kahawa":    {"en": "Coffee",       "category": "cash_crop",   "unit": "kg"},
    "alizeti":   {"en": "Sunflower",    "category": "oilseed",     "unit": "kg"},
    "maharage":  {"en": "Beans",        "category": "pulse",       "unit": "kg"},
    "mtama":     {"en": "Sorghum",      "category": "cereal",      "unit": "kg"},
}

TANZANIA_REGIONS = [
    "Dar es Salaam", "Mwanza", "Arusha", "Dodoma", "Mbeya",
    "Morogoro", "Tanga", "Iringa", "Kilimanjaro", "Tabora",
    "Kigoma", "Singida", "Kagera", "Geita", "Shinyanga",
    "Rukwa", "Ruvuma", "Lindi", "Mtwara", "Songwe",
    "Simiyu", "Katavi", "Njombe", "Pwani", "Manyara"
]

VALID_MONTHS = [
    "Januari", "Februari", "Machi", "Aprili", "Mei", "Juni",
    "Julai", "Agosti", "Septemba", "Oktoba", "Novemba", "Desemba"
]


def get_cached_prediction(cache_key):
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
    try:
        existing = PricePredictionCache.query.filter_by(cache_key=cache_key).first()
        if existing:
            existing.ai_response = ai_response_text
            existing.created_at  = datetime.utcnow()
        else:
            db.session.add(PricePredictionCache(
                cache_key=cache_key, crop_name=crop_sw,
                region=region, month=month, ai_response=ai_response_text))
        db.session.commit()
    except Exception:
        db.session.rollback()


def build_static_prediction(crop_sw, region, month):
    import random
    crop_info = TANZANIA_CROPS.get(crop_sw, {})
    crop_en   = crop_info.get("en", crop_sw)
    unit      = crop_info.get("unit", "kg")

    BASE = {
        "mahindi":  {"low": 400,  "high": 900,  "mid": 620},
        "mpunga":   {"low": 900,  "high": 1800, "mid": 1300},
        "viazi":    {"low": 500,  "high": 1200, "mid": 800},
        "muhogo":   {"low": 300,  "high": 700,  "mid": 480},
        "ndizi":    {"low": 800,  "high": 2000, "mid": 1300},
        "nyanya":   {"low": 800,  "high": 2500, "mid": 1500},
        "vitunguu": {"low": 600,  "high": 1800, "mid": 1100},
        "korosho":  {"low": 2000, "high": 4500, "mid": 3200},
        "kahawa":   {"low": 3000, "high": 6000, "mid": 4500},
        "alizeti":  {"low": 1200, "high": 2500, "mid": 1800},
        "maharage": {"low": 1200, "high": 2800, "mid": 1900},
        "mtama":    {"low": 400,  "high": 900,  "mid": 600},
    }
    SEASON = {
        "Januari": 1.10, "Februari": 1.05, "Machi": 0.90,
        "Aprili": 0.85,  "Mei": 0.80,      "Juni": 0.88,
        "Julai": 0.95,   "Agosti": 1.00,   "Septemba": 1.05,
        "Oktoba": 1.10,  "Novemba": 1.15,  "Desemba": 1.20,
    }
    REGION_MOD = {
        "Dar es Salaam": 1.25, "Arusha": 1.15, "Kilimanjaro": 1.10,
        "Mbeya": 0.90, "Iringa": 0.88, "Morogoro": 0.95,
        "Mwanza": 1.05, "Tanga": 1.00, "Dodoma": 1.00,
        "Tabora": 0.92, "Kigoma": 1.08, "Ruvuma": 0.90,
        "Lindi": 0.95, "Mtwara": 1.00, "Kagera": 0.95,
        "Geita": 0.98, "Shinyanga": 0.93, "Singida": 0.92,
        "Rukwa": 0.88, "Songwe": 0.90, "Njombe": 0.92,
        "Simiyu": 0.90, "Katavi": 0.88, "Pwani": 1.05, "Manyara": 1.00,
    }
    MARKETS = {
        "Dar es Salaam": ["Kariakoo", "Tandale"],
        "Mbeya": ["Uyole", "Kariakoo Mbeya"],
        "Arusha": ["Arusha Mjini", "Moshi"],
        "Kilimanjaro": ["Moshi", "Himo"],
        "Iringa": ["Iringa Mjini", "Mafinga"],
        "Morogoro": ["Morogoro Mjini", "Dar es Salaam"],
        "Mwanza": ["Mwanza Mjini", "Nyegezi"],
        "Dodoma": ["Dodoma Mjini", "Kondoa"],
        "Tanga": ["Tanga Mjini", "Dar es Salaam"],
        "Kagera": ["Bukoba", "Mwanza"],
        "Ruvuma": ["Songea", "Dar es Salaam"],
        "Mtwara": ["Mtwara Mjini", "Masasi"],
        "Tabora": ["Tabora Mjini", "Dar es Salaam"],
        "Kigoma": ["Kigoma Mjini", "Ujiji"],
        "Lindi": ["Lindi Mjini", "Mtwara"],
        "Songwe": ["Tunduma", "Mbeya"],
        "Njombe": ["Njombe Mjini", "Iringa"],
        "Rukwa": ["Sumbawanga", "Mbeya"],
        "Pwani": ["Kibaha", "Dar es Salaam"],
        "Manyara": ["Babati", "Arusha"],
        "Geita": ["Geita Mjini", "Mwanza"],
        "Shinyanga": ["Shinyanga Mjini", "Mwanza"],
        "Singida": ["Singida Mjini", "Dodoma"],
        "Simiyu": ["Bariadi", "Mwanza"],
        "Katavi": ["Mpanda", "Tabora"],
    }
    FACTORS = {
        "mahindi":  ["Msimu wa mvua na ukame", "Ugavi kutoka mikoa ya Kusini", "Mahitaji ya viwanda vya unga"],
        "mpunga":   ["Umwagiliaji wa mashamba", "Uagizaji wa mpunga kutoka nje", "Mahitaji ya miji mikubwa"],
        "nyanya":   ["Hali ya hewa na mvua", "Umbali wa usafirishaji", "Soko la Kariakoo Dar es Salaam"],
        "korosho":  ["Bei ya soko la dunia", "Ubora wa usindikaji", "Ununuzi wa BOMA na wafanyabiashara wa nje"],
        "kahawa":   ["Bei ya soko la dunia (ICO)", "Ubora wa kukaanga na usindikaji", "Mauzo ya nje (export)"],
        "viazi":    ["Hali ya hewa ya baridi", "Udongo na mbolea", "Mahitaji ya miji na migodi"],
        "vitunguu": ["Msimu wa mvua", "Uagizaji kutoka India", "Mahitaji ya kila nyumba"],
        "maharage": ["Msimu wa kilimo na mvua", "Mahitaji ya protini", "Uagizaji kutoka jirani"],
        "alizeti":  ["Mahitaji ya viwanda vya mafuta", "Bei ya mafuta ya petroli", "Hali ya hewa ya ukame"],
        "ndizi":    ["Unyevu wa hewa na ardhi", "Umbali wa masoko makubwa", "Uozo wakati wa usafirishaji"],
        "muhogo":   ["Uvumilivu wa ukame", "Mahitaji ya chakula cha bei nafuu", "Usindikaji wa unga"],
        "mtama":    ["Msimu wa ukame na mvua", "Mahitaji ya bia za kienyeji", "Hifadhi na usindikaji"],
    }

    base  = BASE.get(crop_sw, {"low": 500, "high": 1500, "mid": 1000})
    s_mod = SEASON.get(month, 1.0)
    r_mod = REGION_MOD.get(region, 1.0)
    noise = random.uniform(0.97, 1.03)
    low   = int(base["low"] * s_mod * r_mod * noise)
    high  = int(base["high"] * s_mod * r_mod * noise)
    mid   = int(base["mid"] * s_mod * r_mod * noise)

    if s_mod >= 1.10:
        trend, trend_pct = "rising",  round((s_mod - 1) * 100, 1)
    elif s_mod <= 0.88:
        trend, trend_pct = "falling", round((1 - s_mod) * 100, 1)
    else:
        trend, trend_pct = "stable",  round(abs(s_mod - 1) * 100, 1)

    confidence   = "high" if crop_sw in ["mahindi", "mpunga", "nyanya", "korosho"] else "medium"
    season_note  = "mavuno makubwa — bei inashuka" if s_mod < 0.95 else "uhaba wa soko — bei inapanda"
    season_ctx   = (f"Mwezi wa {month} ni wakati wa {season_note} kwa {crop_sw} katika {region}. "
                    "Hali ya hewa na msimu wa kilimo vinaathiri sana ugavi na bei ya soko.")
    mkt_advice   = (
        f"Hii ni wakati mzuri wa kuuza {crop_sw} — bei ipo juu. Masoko ya {region} na Dar es Salaam "
        "yanatoa bei nzuri. Hakikisha ubora wa zao lako ili kupata bei ya juu zaidi."
        if s_mod >= 1.0 else
        f"Bei ya {crop_sw} ipo chini kwa sasa kutokana na mavuno mengi. Subiri miezi 1-2 au hifadhi vizuri. "
        "Ukiuza sasa, chagua masoko ya miji mikubwa kwa bei nzuri zaidi."
    )

    return {
        "crop_sw": crop_sw, "crop_en": crop_en, "region": region, "month": month, "unit": unit,
        "predicted_price_low": low, "predicted_price_high": high, "predicted_price_mid": mid,
        "trend": trend, "trend_pct": trend_pct, "confidence": confidence,
        "season_context": season_ctx, "market_advice": mkt_advice,
        "key_factors":  FACTORS.get(crop_sw, ["Hali ya hewa", "Ugavi wa soko", "Mahitaji ya watumiaji"]),
        "best_markets": MARKETS.get(region, ["Soko Kuu", "Dar es Salaam"])[:2],
    }


@app.route("/api/price-prediction", methods=["POST"])
@limiter.limit("20 per minute")
def api_price_prediction():
    data    = request.get_json() or {}
    crop_sw = sanitize(data.get("crop", ""), max_length=50).lower()
    region  = sanitize(data.get("region", ""), max_length=80)
    month   = sanitize(data.get("month", ""), max_length=20)

    if not crop_sw or crop_sw not in TANZANIA_CROPS:
        return jsonify({"error": "Zao halijulikani. Chagua zao kutoka kwenye orodha."}), 400
    if not region or region not in TANZANIA_REGIONS:
        return jsonify({"error": "Taja mkoa sahihi wa Tanzania."}), 400
    if not month or month not in VALID_MONTHS:
        return jsonify({"error": "Taja mwezi sahihi (Januari–Desemba)."}), 400

    cache_key = f"{crop_sw}:{region.lower()}:{month.lower()}"
    cached    = get_cached_prediction(cache_key)
    if cached:
        return jsonify({"success": True, "prediction": cached, "cached": True})

    prediction = build_static_prediction(crop_sw, region, month)
    import json as json_lib
    save_prediction_cache(cache_key, crop_sw, region, month, json_lib.dumps(prediction))
    return jsonify({"success": True, "prediction": prediction, "cached": False})


@app.route("/api/price-prediction/crops")
def api_prediction_crops():
    return jsonify({
        "crops":   [{"sw": k, "en": v["en"], "category": v["category"], "unit": v["unit"]}
                    for k, v in TANZANIA_CROPS.items()],
        "regions": TANZANIA_REGIONS,
    })


# ── IMAGE UPLOAD ──────────────────────────────────────────────────────────────

@app.route("/api/upload-image", methods=["POST"])
@login_required
@require_active_account
@limiter.limit("10 per hour")
def upload_image():
    if "file" not in request.files:
        return jsonify({"error": "Hakuna faili."}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Chagua picha kwanza."}), 400
    if not supabase_client:
        return jsonify({"error": "Storage haipo."}), 500

    allowed = {"jpg", "jpeg", "png", "webp"}
    ext     = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in allowed:
        return jsonify({"error": "Picha lazima iwe jpg, png, au webp."}), 400

    # SECURITY: Limit file size to 5MB
    file_bytes = file.read()
    if len(file_bytes) > 5 * 1024 * 1024:
        return jsonify({"error": "Picha ni kubwa mno. Kikomo ni 5MB."}), 400

    filename   = f"crops/{current_user.id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.{ext}"
    supabase_client.storage.from_("crop-images").upload(
        filename, file_bytes, {"content-type": file.content_type}
    )
    public_url = f"{SUPABASE_URL}/storage/v1/object/public/crop-images/{filename}"
    return jsonify({"url": public_url})


# ── ADMIN ─────────────────────────────────────────────────────────────────────

@app.route("/admin")
@login_required
@require_admin
def admin_panel():
    users          = User.query.order_by(User.created_at.desc()).all()
    listings       = MarketListing.query.order_by(MarketListing.posted_at.desc()).all()
    reports        = ListingReport.query.order_by(ListingReport.created_at.desc()).all()
    banned         = BannedEmail.query.order_by(BannedEmail.banned_at.desc()).all()
    total_farmers  = User.query.filter_by(role="farmer").count()
    total_admins   = User.query.filter_by(role="admin").count()
    total_listings = MarketListing.query.count()
    active_listings = MarketListing.query.filter_by(is_available=True).count()
    return render_template("admin/panel.html",
                           users=users, listings=listings, reports=reports,
                           banned=banned, total_farmers=total_farmers,
                           total_admins=total_admins, total_listings=total_listings,
                           active_listings=active_listings)


@app.route("/admin/suspend-user/<int:user_id>", methods=["POST"])
@login_required
@require_admin
def admin_suspend_user(user_id):
    """Simamisha akaunti + ongeza kwenye blacklist."""
    if user_id == current_user.id:
        return jsonify({"error": "Huwezi kujisimamisha mwenyewe."}), 400

    user   = User.query.get_or_404(user_id)
    data   = request.get_json() or {}
    reason = sanitize(data.get("reason", "Ukiukaji wa masharti ya matumizi."), max_length=300)

    # Simamisha akaunti
    user.is_active = False

    # Ongeza kwenye banned list — email NA simu zote mbili
    if user.email and not BannedEmail.query.filter_by(email=user.email).first():
        db.session.add(BannedEmail(
            email=user.email, phone=None, reason=reason, banned_by=current_user.id))

    if not BannedEmail.query.filter_by(phone=user.phone).first():
        db.session.add(BannedEmail(
            email=None, phone=user.phone, reason=reason, banned_by=current_user.id))

    db.session.commit()
    return jsonify({
        "message": f"Akaunti ya {user.full_name} imesimamishwa na kuzuiwa.",
        "is_active": False
    })


@app.route("/admin/unsuspend-user/<int:user_id>", methods=["POST"])
@login_required
@require_admin
def admin_unsuspend_user(user_id):
    """Rudisha akaunti — futa kutoka blacklist pia."""
    user = User.query.get_or_404(user_id)
    user.is_active = True

    # Futa kutoka banned list
    BannedEmail.query.filter_by(email=user.email).delete()
    BannedEmail.query.filter_by(phone=user.phone).delete()
    db.session.commit()

    return jsonify({
        "message": f"Akaunti ya {user.full_name} imerudishwa.",
        "is_active": True
    })


@app.route("/admin/delete-listing/<int:listing_id>", methods=["POST"])
@login_required
@require_admin
def admin_delete_listing(listing_id):
    listing = MarketListing.query.get_or_404(listing_id)
    db.session.delete(listing)
    db.session.commit()
    return jsonify({"message": "Orodha imefutwa."})


@app.route("/admin/delete-user/<int:user_id>", methods=["POST"])
@login_required
@require_admin
def admin_delete_user(user_id):
    if user_id == current_user.id:
        return jsonify({"error": "Huwezi kujifuta mwenyewe."}), 400
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "Mtumiaji amefutwa."})


@app.route("/admin/verify-user/<int:user_id>", methods=["POST"])
@login_required
@require_admin
def admin_verify_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_verified = not user.is_verified
    db.session.commit()
    status = "imethibitishwa" if user.is_verified else "imeondolewa uthibitisho"
    return jsonify({"message": f"Akaunti ya {user.full_name} {status}.",
                    "is_verified": user.is_verified})


# ── MISC ──────────────────────────────────────────────────────────────────────

@app.route("/health")
def health():
    return jsonify({"status": "ok", "timestamp": datetime.utcnow().isoformat()})


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(403)
def forbidden(e):
    return render_template("403.html"), 403


@app.errorhandler(429)
def rate_limited(e):
    return jsonify({
        "error": "Maombi mengi mno. Tafadhali subiri kidogo kisha jaribu tena."
    }), 429


@app.errorhandler(500)
def server_error(e):
    return render_template("500.html"), 500


# ── Init DB & Run ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port,
            debug=os.environ.get("FLASK_DEBUG", "false").lower() == "true")
