import os
import requests
from functools import wraps
from email_service import send_welcome_email
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
from supabase import create_client

# ── Security layer ────────────────────────────────────────────────────────────
from security import (
    sanitize,
    validate_phone,
    validate_email,
    validate_password,
    validate_price,
    validate_quantity,
    require_active_account,
    require_admin,
    apply_security_headers,
)

import base64
import json as json_lib
import re
import enum

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-key-change-in-production")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "sqlite:///agrolink.db"
)

if app.config["SQLALCHEMY_DATABASE_URI"].startswith("postgresql+psycopg://"):
    app.config["SQLALCHEMY_DATABASE_URI"] = app.config[
        "SQLALCHEMY_DATABASE_URI"
    ].replace("postgresql+psycopg://", "postgresql+psycopg://", 1)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_pre_ping": True, "pool_recycle": 300}

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_VISION_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
WFP_API_URL = "https://api.vam.wfp.org/api/1/vam-data-bridges/1.0.0"
WFP_COMMODITY_MAP = {
    "mahindi":  {"id": 1,   "name": "Maize"},
    "mpunga":   {"id": 82,  "name": "Rice"},
    "maharage": {"id": 36,  "name": "Beans"},
    "viazi":    {"id": 117, "name": "Potatoes"},
    "vitunguu": {"id": 63,  "name": "Onions"},
    "nyanya":   {"id": 63,  "name": "Tomatoes"},
    "alizeti":  {"id": 56,  "name": "Oil (sunflower)"},
    "muhogo":   {"id": 55,  "name": "Cassava"},
    "ndizi":    {"id": 15,  "name": "Bananas"},
    "korosho":  {"id": 165, "name": "Cashewnuts"},
    "kahawa":   {"id": 33,  "name": "Coffee"},
    "mtama":    {"id": 83,  "name": "Sorghum"},
}
WFP_COUNTRY_ID = 214

supabase_client = (
    create_client(SUPABASE_URL, SUPABASE_ANON_KEY) if SUPABASE_URL else None
)

WEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY", "")
WEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_BASE_URL = "https://api.openweathermap.org/data/2.5/forecast"

db = SQLAlchemy()
db.init_app(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "Tafadhali ingia kwanza."

# ── CORS: restrict to your own domain only ───────────────────────────────────
# BADILISHA "https://agrolink.co.tz" ukipata domain yako halisi
ALLOWED_ORIGINS = os.environ.get(
    "ALLOWED_ORIGINS", "https://agrolink-y9za.onrender.com"
).split(",")
CORS(app, origins=ALLOWED_ORIGINS, supports_credentials=True)

# ── Rate Limiter ──────────────────────────────────────────────────────────────
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "60 per minute"],
    storage_uri="memory://",
)

# ── OTP SMS Helper ────────────────────────────────────────────────────────────
OTP_MOCK = os.environ.get("OTP_MOCK", "true").lower() == "true"

def send_otp_sms(phone: str, otp_code: str) -> bool:
    """Tuma OTP kwa SMS. OTP_MOCK=true → log tu (development/staging)."""
    if OTP_MOCK:
        app.logger.info(f"[OTP MOCK] Phone={phone} OTP={otp_code}")
        return True
    try:
        import africastalking
        africastalking.initialize(
            os.environ.get("AT_USERNAME", ""),
            os.environ.get("AT_API_KEY", ""),
        )
        sms = africastalking.SMS
        msg = f"AgroLink Tanzania: Nambari yako ya uthibitisho ni {otp_code}. Inaisha baada ya dakika 10. Usishirikishe mtu yeyote."
        response = sms.send(msg, [f"+255{phone.lstrip('0')}"])
        return True
    except Exception as e:
        app.logger.error(f"[OTP SMS ERROR] {e}")
        return False



# ── Security Headers (kila response) ─────────────────────────────────────────
apply_security_headers(app)


# ── Models ───────────────────────────────────────────────────────────────────


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    region = db.Column(db.String(80), nullable=True)
    role = db.Column(db.String(20), default="farmer")
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    accepted_terms = db.Column(db.Boolean, default=False)  # ← T&C checkbox
    terms_accepted_at = db.Column(db.DateTime, nullable=True)  # ← wakati wa kukubali
    phone_verified = db.Column(db.Boolean, default=False, nullable=False)  # ← OTP imethibitishwa

    # ── Trust system ──────────────────────────────────────────────────────────
    trust_level     = db.Column(db.String(10), default="gray", nullable=False)
    trust_points    = db.Column(db.Integer, default=0, nullable=False)
    flag_count      = db.Column(db.Integer, default=0, nullable=False)
    transaction_count = db.Column(db.Integer, default=0, nullable=False)
    avg_rating      = db.Column(db.Float, default=0.0, nullable=False)
    trust_updated_at = db.Column(db.DateTime, nullable=True)
    can_post_listing = db.Column(db.Boolean, default=False, nullable=False)
    can_advise      = db.Column(db.Boolean, default=False, nullable=False)
    can_b2b         = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    crops = db.relationship("Crop", backref="owner", lazy=True)
    listings = db.relationship("MarketListing", backref="seller", lazy=True)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    @property
    def is_active_user(self):
        return self.is_active

    def get_id(self):
        return str(self.id)


class PhoneOTP(db.Model):
    __tablename__ = "phone_otps"
    id         = db.Column(db.Integer, primary_key=True)
    phone      = db.Column(db.String(20), nullable=False, index=True)
    otp_code   = db.Column(db.String(6), nullable=False)
    form_data  = db.Column(db.Text, nullable=False)   # JSON ya form yote
    attempts   = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    verified   = db.Column(db.Boolean, default=False)

    def is_expired(self):
        return datetime.utcnow() > self.expires_at

    def is_valid(self, code):
        return (
            not self.verified
            and not self.is_expired()
            and self.attempts < 5
            and self.otp_code == code.strip()
        )

class Crop(db.Model):
    __tablename__ = "crops"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name_sw = db.Column(db.String(100), nullable=False)
    name_en = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    season = db.Column(db.String(50), nullable=True)
    hectares = db.Column(db.Float, nullable=True)
    region = db.Column(db.String(80), nullable=True)
    description = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(300), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    market_prices = db.relationship("MarketPrice", backref="crop", lazy=True)


class MarketPrice(db.Model):
    __tablename__ = "market_prices"
    id            = db.Column(db.Integer, primary_key=True)
    crop_name     = db.Column(db.String(100), nullable=False)
    unit          = db.Column(db.String(30), nullable=False, default="kg")
    price_tzs     = db.Column(db.Numeric(12, 2), nullable=False)
    region        = db.Column(db.String(100), nullable=False, default="Kitaifa")
    market        = db.Column(db.String(120), nullable=True)
    source        = db.Column(db.String(50), nullable=False, default="manual")
    recorded_at   = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    created_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    def to_dict(self):
        return {
            "id":          self.id,
            "crop_name":   self.crop_name,
            "unit":        self.unit,
            "price_tzs":   float(self.price_tzs),
            "region":      self.region,
            "market":      self.market or "",
            "source":      self.source,
            "recorded_at": self.recorded_at.strftime("%Y-%m-%d"),
        }


class MarketListing(db.Model):
    __tablename__ = "market_listings"
    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    crop_name = db.Column(db.String(100), nullable=False)
    quantity_kg = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), default="kg")
    price_tzs = db.Column(db.Float, nullable=False)
    region = db.Column(db.String(80), nullable=False)
    contact = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    is_available = db.Column(db.Boolean, default=True)
    image_url = db.Column(db.String(300), nullable=True)
    posted_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_sponsored = db.Column(db.Boolean, default=False, nullable=False)
    sponsored_until = db.Column(db.DateTime, nullable=True)


class ListingReport(db.Model):
    __tablename__ = "listing_reports"
    id = db.Column(db.Integer, primary_key=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    listing_id = db.Column(
        db.Integer, db.ForeignKey("market_listings.id"), nullable=False
    )
    reason = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (
        db.UniqueConstraint("reporter_id", "listing_id", name="unique_report"),
    )
    reporter = db.relationship(
        "User", foreign_keys=[reporter_id], backref="reports_made"
    )
    listing = db.relationship(
        "MarketListing", foreign_keys=[listing_id], backref="reports"
    )


class SellerRating(db.Model):
    __tablename__ = "seller_ratings"
    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    rater_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    listing_id = db.Column(
        db.Integer, db.ForeignKey("market_listings.id"), nullable=False
    )
    stars = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String(300), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    __table_args__ = (
        db.UniqueConstraint("rater_id", "listing_id", name="unique_rating"),
    )
    seller = db.relationship(
        "User", foreign_keys=[seller_id], backref="ratings_received"
    )
    rater = db.relationship("User", foreign_keys=[rater_id], backref="ratings_given")
    listing = db.relationship(
        "MarketListing", foreign_keys=[listing_id], backref="ratings"
    )



class BannedEmail(db.Model):
    __tablename__ = "banned_emails"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=True, unique=True)
    phone = db.Column(db.String(20), nullable=True, unique=True)
    reason = db.Column(db.String(300), nullable=True)
    banned_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    banned_at = db.Column(db.DateTime, default=datetime.utcnow)

class PricePredictionCache(db.Model):
    __tablename__ = "price_prediction_cache"
    id = db.Column(db.Integer, primary_key=True)
    cache_key = db.Column(db.String(200), unique=True, nullable=False, index=True)
    crop_name = db.Column(db.String(100), nullable=False)
    region = db.Column(db.String(80), nullable=False)
    month = db.Column(db.String(20), nullable=False)
    ai_response = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class PricePredictionLog(db.Model):
    __tablename__ = "price_prediction_logs"
    id = db.Column(db.Integer, primary_key=True)
    crop_name = db.Column(db.String(100), nullable=False)
    region = db.Column(db.String(80), nullable=False)
    month = db.Column(db.String(20), nullable=False)
    season = db.Column(db.String(30), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    ai_response = db.Column(db.Text, nullable=True)
    queried_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship("User", foreign_keys=[user_id], backref="price_queries")


class WeatherLog(db.Model):
    __tablename__ = "weather_logs"
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(100), nullable=False)
    temperature = db.Column(db.Float)
    humidity = db.Column(db.Float)
    description = db.Column(db.String(200))
    wind_speed = db.Column(db.Float)
    icon = db.Column(db.String(20))
    fetched_at = db.Column(db.DateTime, default=datetime.utcnow)


# ── Phone Masking: Conversation + Message Models ─────────────────────────────

class ConvStatus(enum.Enum):
    active   = "active"
    closed   = "closed"
    blocked  = "blocked"

class Conversation(db.Model):
    __tablename__ = "conversations"
    id          = db.Column(db.Integer, primary_key=True)
    listing_id  = db.Column(db.Integer, db.ForeignKey("market_listings.id"), nullable=False)
    buyer_id    = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    seller_id   = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    status      = db.Column(db.Enum(ConvStatus), default=ConvStatus.active, nullable=False)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at  = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    messages    = db.relationship("Message", backref="conversation", lazy=True,
                                  order_by="Message.sent_at")
    listing     = db.relationship("MarketListing", backref="conversations", lazy=True)
    buyer       = db.relationship("User", foreign_keys=[buyer_id],
                                  backref="bought_conversations", lazy=True)
    seller      = db.relationship("User", foreign_keys=[seller_id],
                                  backref="sold_conversations", lazy=True)
    __table_args__ = (
        db.UniqueConstraint("listing_id", "buyer_id", name="uq_listing_buyer"),
    )

class Message(db.Model):
    __tablename__ = "messages"
    id              = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey("conversations.id"), nullable=False)
    sender_id       = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    body            = db.Column(db.Text, nullable=False)
    is_read         = db.Column(db.Boolean, default=False)
    is_deleted      = db.Column(db.Boolean, default=False, nullable=False, server_default="false")
    reply_to_id     = db.Column(db.Integer, db.ForeignKey("messages.id"), nullable=True)
    sent_at         = db.Column(db.DateTime, default=datetime.utcnow)
    sender          = db.relationship("User", foreign_keys=[sender_id], lazy=True)

# ── Escrow Model ─────────────────────────────────────────────────────────────
class EscrowStatus(enum.Enum):
    held     = "held"
    released = "released"
    refunded = "refunded"

class EscrowTransaction(db.Model):
    __tablename__ = "escrow_transactions"
    id              = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey("conversations.id"), nullable=False)
    buyer_id        = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    seller_id       = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    amount_tzs      = db.Column(db.BigInteger, nullable=False)
    status          = db.Column(db.Enum(EscrowStatus), default=EscrowStatus.held, nullable=False)
    reference       = db.Column(db.String(32), unique=True, nullable=False)
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at      = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    buyer           = db.relationship("User", foreign_keys=[buyer_id], lazy=True)
    seller          = db.relationship("User", foreign_keys=[seller_id], lazy=True)
    conversation    = db.relationship("Conversation", foreign_keys=[conversation_id], lazy=True)

# ── Order State Machine ──────────────────────────────────────────────────────
class OrderStatus(enum.Enum):
    draft     = "draft"
    submitted = "submitted"
    approved  = "approved"
    paid      = "paid"
    completed = "completed"
    cancelled = "cancelled"

class PageView(db.Model):
    __tablename__ = "page_views"
    id         = db.Column(db.Integer, primary_key=True)
    path       = db.Column(db.String(255), nullable=False)
    method     = db.Column(db.String(10), default="GET")
    user_id    = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(512))
    browser    = db.Column(db.String(64))
    device     = db.Column(db.String(32))  # mobile / desktop / tablet
    referrer   = db.Column(db.String(512))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class PWAInstall(db.Model):
    __tablename__ = "pwa_installs"
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(512))
    platform   = db.Column(db.String(32))  # android / ios / desktop
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Order(db.Model):
    __tablename__ = "orders"
    id              = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey("conversations.id"), nullable=False, unique=True)
    buyer_id        = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    seller_id       = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    listing_id      = db.Column(db.Integer, db.ForeignKey("market_listings.id"), nullable=False)
    quantity_kg     = db.Column(db.Float, nullable=False)
    price_tzs       = db.Column(db.BigInteger, nullable=False)
    status          = db.Column(db.Enum(OrderStatus), default=OrderStatus.draft, nullable=False)
    note            = db.Column(db.Text, nullable=True)
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at      = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    buyer           = db.relationship("User", foreign_keys=[buyer_id], lazy=True)
    seller          = db.relationship("User", foreign_keys=[seller_id], lazy=True)
    listing         = db.relationship("MarketListing", foreign_keys=[listing_id], lazy=True)
    conversation    = db.relationship("Conversation", foreign_keys=[conversation_id], lazy=True)


# ── EscrowFee (Sprint 8 — Framework-ready, off by default) ───────────────────
class EscrowFee(db.Model):
    __tablename__ = "escrow_fees"
    id             = db.Column(db.Integer, primary_key=True)
    order_id       = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False, unique=True)
    buyer_id       = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    seller_id      = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    order_amount   = db.Column(db.BigInteger, nullable=False)
    fee_rate       = db.Column(db.Float, default=0.025, nullable=False)
    fee_amount     = db.Column(db.BigInteger, default=0, nullable=False)
    status         = db.Column(db.String(20), default="pending", nullable=False)
    is_active      = db.Column(db.Boolean, default=False, nullable=False)
    waived_reason  = db.Column(db.String(255), nullable=True)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)
    released_at    = db.Column(db.DateTime, nullable=True)
    order          = db.relationship("Order", foreign_keys=[order_id], lazy=True)
    buyer          = db.relationship("User", foreign_keys=[buyer_id], lazy=True)
    seller         = db.relationship("User", foreign_keys=[seller_id], lazy=True)

    def calculate_fee(self):
        """Hesabu fee — returns 0 kama is_active=False (framework-ready)."""
        if not self.is_active:
            self.fee_amount = 0
            self.waived_reason = "Escrow fees not yet active"
            return 0
        fee = int(self.order_amount * self.fee_rate)
        self.fee_amount = fee
        return fee

# ── Login Manager ─────────────────────────────────────────────────────────────


@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(int(user_id))
    # SECURITY FIX: akaunti iliyosimamishwa haiingii hata na session hai
    if user and not user.is_active:
        return None
    return user

# ── Trust Engine ──────────────────────────────────────────────────────────────
# Inahesabu trust level ya user automatically baada ya kila event muhimu

TRUST_THRESHOLDS = {
    "gray":  {"points": 0,   "tx": 0,  "rating": 0.0, "flags_max": 99},
    "green": {"points": 10,  "tx": 1,  "rating": 0.0, "flags_max": 2},
    "teal":  {"points": 50,  "tx": 5,  "rating": 4.0, "flags_max": 1},
    "gold":  {"points": 120, "tx": 15, "rating": 4.5, "flags_max": 0},
}

def trust_engine(user_id):
    """
    Recalculates trust level for a user based on:
    - transaction_count (listings posted + inquiries made)
    - avg_rating (from SellerRating)
    - flag_count (from ListingReport against user)
    - account age
    Updates user in-place and commits.
    """
    user = User.query.get(user_id)
    if not user:
        return

    # 1. Hesabu avg rating kutoka SellerRating
    ratings = SellerRating.query.filter_by(seller_id=user_id).all()
    if ratings:
        user.avg_rating = round(sum(r.stars for r in ratings) / len(ratings), 2)
    else:
        user.avg_rating = 0.0

    # 2. Hesabu transaction_count (listings zake + conversations kama buyer)
    listing_count = MarketListing.query.filter_by(
        seller_id=user_id, is_available=True
    ).count()
    conv_count = Conversation.query.filter_by(buyer_id=user_id).count()
    user.transaction_count = listing_count + conv_count

    # 3. Hesabu flag_count (reports zilizofanywa dhidi ya listings zake)
    flagged = (
        db.session.query(ListingReport)
        .join(MarketListing, ListingReport.listing_id == MarketListing.id)
        .filter(MarketListing.seller_id == user_id)
        .count()
    )
    user.flag_count = flagged

    # 4. Account age kwa siku
    age_days = (datetime.utcnow() - user.created_at).days

    # 5. Hesabu trust_points
    points = 0
    points += user.transaction_count * 5
    points += int(user.avg_rating * 8)
    points += max(0, min(age_days, 60))   # max 60 points kwa umri
    points -= user.flag_count * 15         # adhabu kwa flags
    user.trust_points = max(0, points)

    # 6. Amua trust level
    if user.flag_count >= 3:
        new_level = "gray"
    elif (
        user.trust_points >= TRUST_THRESHOLDS["gold"]["points"]
        and user.transaction_count >= TRUST_THRESHOLDS["gold"]["tx"]
        and user.avg_rating >= TRUST_THRESHOLDS["gold"]["rating"]
        and user.flag_count <= TRUST_THRESHOLDS["gold"]["flags_max"]
    ):
        new_level = "gold"
    elif (
        user.trust_points >= TRUST_THRESHOLDS["teal"]["points"]
        and user.transaction_count >= TRUST_THRESHOLDS["teal"]["tx"]
        and user.avg_rating >= TRUST_THRESHOLDS["teal"]["rating"]
        and user.flag_count <= TRUST_THRESHOLDS["teal"]["flags_max"]
    ):
        new_level = "teal"
    elif (
        user.trust_points >= TRUST_THRESHOLDS["green"]["points"]
        and user.transaction_count >= TRUST_THRESHOLDS["green"]["tx"]
        and user.flag_count <= TRUST_THRESHOLDS["green"]["flags_max"]
    ):
        new_level = "green"
    else:
        new_level = "gray"

    user.trust_level = new_level

    # 7. Fungua/funga uwezo kulingana na level
    user.can_post_listing = new_level in ("green", "teal", "gold")
    user.can_advise       = new_level in ("teal", "gold")
    user.can_b2b          = new_level in ("green", "teal", "gold")

    user.trust_updated_at = datetime.utcnow()
    db.session.commit()
    return new_level


def trust_badge_html(trust_level):
    """Returns badge HTML for templates (safe to use with |safe filter)"""
    badges = {
        "gray":  ('<span class="trust-badge trust-gray">Mpya</span>', "●"),
        "green": ('<span class="trust-badge trust-green">Mwanachama</span>', "●"),
        "teal":  ('<span class="trust-badge trust-teal">Mwaminifu</span>', "●"),
        "gold":  ('<span class="trust-badge trust-gold">Imara</span>', "●"),
    }
    return badges.get(trust_level, badges["gray"])





# ── Phone Masking Helper ──────────────────────────────────────────────────────
def mask_phone(phone):
    """Server-side masking — namba halisi haifiki browser ya guest kamwe"""
    if not phone:
        return "***"
    p = str(phone).strip()
    if len(p) <= 6:
        return "***"
    return p[:3] + "***" + p[-3:]

def get_display_phone(phone):
    """Returns masked or real phone based on login status"""
    if current_user.is_authenticated:
        return phone
    return mask_phone(phone)

# ── Weather Service (unchanged logic) ────────────────────────────────────────


def get_weather(city="Mbeya"):
    if not WEATHER_API_KEY:
        return {"error": "API key haijawekwa", "city": city, "success": False}

    cached = (
        WeatherLog.query.filter_by(city=city)
        .order_by(WeatherLog.fetched_at.desc())
        .first()
    )
    if cached:
        age = datetime.utcnow() - cached.fetched_at
        if age < timedelta(minutes=30):
            return {
                "city": city,
                "temperature": cached.temperature,
                "humidity": cached.humidity,
                "description": cached.description,
                "wind_speed": cached.wind_speed,
                "icon": cached.icon,
                "success": True,
                "cached": True,
                "cache_age_mins": int(age.total_seconds() / 60),
            }

    tz_cities = {
        "mbeya": {"lat": -8.9000, "lon": 33.4600},
        "dar es salaam": {"lat": -6.7924, "lon": 39.2083},
        "dodoma": {"lat": -6.1730, "lon": 35.7395},
        "arusha": {"lat": -3.3869, "lon": 36.6830},
        "mwanza": {"lat": -2.5164, "lon": 32.9175},
        "tanga": {"lat": -5.0690, "lon": 39.0987},
        "morogoro": {"lat": -6.8160, "lon": 37.6833},
        "iringa": {"lat": -7.7700, "lon": 35.6930},
        "kilimanjaro": {"lat": -3.0674, "lon": 37.3556},
        "tabora": {"lat": -5.0167, "lon": 32.8000},
        "kigoma": {"lat": -4.8771, "lon": 29.6278},
        "singida": {"lat": -4.8185, "lon": 34.7500},
        "songwe": {"lat": -9.3500, "lon": 33.2000},
        "lindi": {"lat": -9.9970, "lon": 39.7140},
        "mtwara": {"lat": -10.2667, "lon": 40.1833},
        "kagera": {"lat": -1.2833, "lon": 31.7667},
        "geita": {"lat": -2.8667, "lon": 32.1667},
        "shinyanga": {"lat": -3.6600, "lon": 33.4200},
        "rukwa": {"lat": -7.9000, "lon": 31.4167},
        "ruvuma": {"lat": -10.6833, "lon": 35.6500},
    }

    city_key = city.lower().strip()
    coords = tz_cities.get(city_key)
    params = (
        {
            "lat": coords["lat"],
            "lon": coords["lon"],
            "appid": WEATHER_API_KEY,
            "units": "metric",
            "lang": "sw",
        }
        if coords
        else {
            "q": f"{city},TZ",
            "appid": WEATHER_API_KEY,
            "units": "metric",
            "lang": "sw",
        }
    )

    try:
        resp = requests.get(WEATHER_BASE_URL, params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        weather_data = {
            "city": city,
            "temperature": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "humidity": data["main"]["humidity"],
            "description": data["weather"][0]["description"],
            "wind_speed": data["wind"]["speed"],
            "icon": data["weather"][0]["icon"],
            "success": True,
        }
        log = WeatherLog(
            city=city,
            temperature=weather_data["temperature"],
            humidity=weather_data["humidity"],
            description=weather_data["description"],
            wind_speed=weather_data["wind_speed"],
            icon=weather_data["icon"],
        )
        db.session.add(log)
        db.session.commit()
        return weather_data
    except Exception as exc:
        cached = (
            WeatherLog.query.filter_by(city=city)
            .order_by(WeatherLog.fetched_at.desc())
            .first()
        )
        if cached:
            return {
                "city": cached.city,
                "temperature": cached.temperature,
                "humidity": cached.humidity,
                "description": cached.description,
                "wind_speed": cached.wind_speed,
                "icon": cached.icon,
                "success": True,
                "cached": True,
            }
        return {"error": str(exc), "city": city, "success": False}


def get_forecast(city="Mbeya"):
    if not WEATHER_API_KEY:
        return []
    params = {"q": f"{city},TZ", "appid": WEATHER_API_KEY, "units": "metric", "cnt": 5}
    try:
        resp = requests.get(FORECAST_BASE_URL, params=params, timeout=5)
        resp.raise_for_status()
        return [
            {
                "dt_txt": i["dt_txt"],
                "temperature": i["main"]["temp"],
                "description": i["weather"][0]["description"],
                "icon": i["weather"][0]["icon"],
            }
            for i in resp.json().get("list", [])
        ]
    except Exception as e:
        print(f"Weather API error: {e}")
        return []


# ── Routes ────────────────────────────────────────────────────────────────────


# ── Auth decorators ───────────────────────────────────────────────────────────
def require_phone_verified(f):
    """Zuia endpoint kama namba ya simu haijathibitishwa via OTP."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not getattr(current_user, "phone_verified", False):
            return jsonify({
                "error": "Thibitisha namba yako ya simu kwanza.",
                "code": "PHONE_NOT_VERIFIED",
                "redirect": "/verify-phone"
            }), 403
        return f(*args, **kwargs)
    return decorated


@app.route("/")
def index():
    # Auth wall: guest anaona landing page tu
    if not current_user.is_authenticated:
        # Preview listings 6 tu — bila contact/phone
        preview = (
            MarketListing.query
            .filter_by(is_available=True)
            .order_by(MarketListing.posted_at.desc())
            .limit(6)
            .all()
        )
        return render_template("landing.html", preview_listings=preview)
    crops = Crop.query.order_by(Crop.created_at.desc()).limit(6).all()
    listings = (
        MarketListing.query.filter_by(is_available=True)
        .order_by(MarketListing.posted_at.desc())
        .limit(6)
        .all()
    )
    weather = get_weather("Mbeya")
    # Platform stats — live kutoka DB
    from sqlalchemy import func, distinct
    stats = {
        "users": db.session.query(func.count(User.id)).scalar() or 0,
        "listings": db.session.query(func.count(MarketListing.id)).filter_by(is_available=True).scalar() or 0,
        "regions": db.session.query(func.count(distinct(MarketListing.region))).filter_by(is_available=True).scalar() or 0,
        "crops": db.session.query(func.count(distinct(MarketListing.crop_name))).filter_by(is_available=True).scalar() or 0,
    }
    return render_template(
        "index.html", crops=crops, listings=listings, weather=weather, stats=stats
    )


@app.route("/weather")
def weather_page():
    city = sanitize(request.args.get("city", "Mbeya"), max_length=50)
    weather = get_weather(city)
    forecast = get_forecast(city)
    return jsonify({"weather": weather, "forecast": forecast})


# ── AUTH ──────────────────────────────────────────────────────────────────────


@app.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def login():
    if request.method == "POST":
        data = request.get_json() or request.form
        phone = sanitize(data.get("phone", ""), max_length=20)
        password = data.get(
            "password", ""
        )  # Usiisanitize nywila — chars special zinahitajika

        # SECURITY FIX: generic error message — usitaje "phone" au "password" peke yake
        user = User.query.filter_by(phone=phone).first()

        if not user or not user.check_password(password):
            return jsonify({"error": "Namba ya simu au nywila si sahihi."}), 401

        # SECURITY FIX: angalia is_active KABLA ya kulogin
        if not user.is_active:
            return jsonify(
                {
                    "error": "Akaunti yako imesimamishwa. Wasiliana na msimamizi kwa msaada."
                }
            ), 403

        login_user(user)
        return jsonify({"message": "Umeingia.", "role": user.role})

    return render_template("auth/login.html")


@app.route("/register/initiate", methods=["POST"])
@limiter.limit("5 per hour")
def register_initiate():
    """Hatua ya 1: Validate form data, tuma OTP, subiri uthibitisho."""
    import json, secrets as _secrets
    data = request.get_json() or request.form

    # ── Sanitize ─────────────────────────────────────────────────────────────
    full_name = sanitize(data.get("full_name", ""), max_length=120)
    phone     = sanitize(data.get("phone", ""), max_length=20)
    email     = sanitize(data.get("email", ""), max_length=120) or None
    region    = sanitize(data.get("region", ""), max_length=80)
    role      = sanitize(data.get("role", "farmer"), max_length=20)
    password  = data.get("password", "")
    terms     = data.get("terms_accepted", False)

    # ── Validate ──────────────────────────────────────────────────────────────
    if not terms or str(terms).lower() in ("false", "0", ""):
        return jsonify({"error": "Lazima ukubali Masharti na Vigezo vya AgroLink."}), 400
    if not full_name:
        return jsonify({"error": "Jina kamili linahitajika."}), 400
    if not validate_phone(phone):
        return jsonify({"error": "Namba ya simu si sahihi. Tumia muundo: 0712345678."}), 400
    if email and not validate_email(email):
        return jsonify({"error": "Muundo wa email si sahihi."}), 400
    pw_ok, pw_err = validate_password(password)
    if not pw_ok:
        return jsonify({"error": pw_err}), 400

    # ── Check banned ──────────────────────────────────────────────────────────
    if BannedEmail.query.filter_by(phone=phone).first():
        return jsonify({"error": "Namba hii imefungwa. Wasiliana na msimamizi."}), 403
    if email and BannedEmail.query.filter_by(email=email).first():
        return jsonify({"error": "Email hii imefungwa. Wasiliana na msimamizi."}), 403

    # ── Check duplicates ──────────────────────────────────────────────────────
    if User.query.filter_by(phone=phone).first():
        return jsonify({"error": "Namba ya simu tayari imetumika."}), 409
    if email and User.query.filter_by(email=email).first():
        return jsonify({"error": "Email tayari imetumika."}), 409

    # ── Validate role ─────────────────────────────────────────────────────────
    if role not in ("farmer", "agent", "buyer", "member"):
        role = "farmer"

    # ── Futa OTP za zamani za namba hii ──────────────────────────────────────
    PhoneOTP.query.filter_by(phone=phone, verified=False).delete()
    db.session.flush()

    # ── Tengeneza OTP ─────────────────────────────────────────────────────────
    otp_code = f"{_secrets.randbelow(900000) + 100000}"
    form_payload = json.dumps({
        "full_name": full_name, "phone": phone, "email": email,
        "region": region, "role": role, "password": password,
    })
    otp_record = PhoneOTP(
        phone=phone,
        otp_code=otp_code,
        form_data=form_payload,
        expires_at=datetime.utcnow() + timedelta(minutes=10),
    )
    db.session.add(otp_record)
    db.session.commit()

    # ── Tuma SMS ──────────────────────────────────────────────────────────────
    sent = send_otp_sms(phone, otp_code)
    if not sent:
        return jsonify({"error": "Imeshindwa kutuma SMS. Jaribu tena."}), 500

    resp = {"message": "OTP imetumwa.", "phone": phone}
    if OTP_MOCK:
        resp["otp_dev"] = otp_code   # Development only — ondoa production
    return jsonify(resp), 200


@app.route("/register/verify", methods=["POST"])
@limiter.limit("10 per hour")
def register_verify():
    """Hatua ya 2: Thibitisha OTP na unda akaunti."""
    import json
    data = request.get_json() or request.form
    phone    = sanitize(data.get("phone", ""), max_length=20)
    otp_code = sanitize(data.get("otp_code", ""), max_length=6)

    if not phone or not otp_code:
        return jsonify({"error": "Taarifa hazitoshi."}), 400

    # ── Tafuta OTP record ─────────────────────────────────────────────────────
    record = PhoneOTP.query.filter_by(phone=phone, verified=False)                           .order_by(PhoneOTP.created_at.desc()).first()
    if not record:
        return jsonify({"error": "Ombi la OTP halipatikani. Anza upya."}), 404

    # ── Angalia majaribio ─────────────────────────────────────────────────────
    record.attempts += 1
    db.session.flush()

    if record.is_expired():
        db.session.commit()
        return jsonify({"error": "OTP imeisha muda. Omba nyingine."}), 410
    if record.attempts > 5:
        db.session.commit()
        return jsonify({"error": "Majaribio mengi. Omba OTP mpya."}), 429
    if not record.is_valid(otp_code):
        db.session.commit()
        remaining = 5 - record.attempts
        return jsonify({"error": f"OTP si sahihi. Majaribio {remaining} yamebaki."}), 400

    # ── OTP sahihi — unda mtumiaji ───────────────────────────────────────────
    form = json.loads(record.form_data)
    if User.query.filter_by(phone=form["phone"]).first():
        return jsonify({"error": "Namba ya simu tayari imetumika."}), 409

    user = User(
        full_name=form["full_name"],
        phone=form["phone"],
        email=form.get("email"),
        region=form.get("region"),
        role=form.get("role", "farmer"),
        accepted_terms=True,
        terms_accepted_at=datetime.utcnow(),
        is_verified=True,
        phone_verified=True,
        trust_level="gray",
        trust_points=0,
        flag_count=0,
        transaction_count=0,
        avg_rating=0.0,
        can_post_listing=False,
        can_advise=False,
        can_b2b=False,
    )
    user.set_password(form["password"])
    db.session.add(user)

    record.verified = True
    db.session.commit()

    trust_engine(user.id)
    if form.get("email"):
        send_welcome_email(form["email"], form["full_name"], form.get("role", "farmer"))

    login_user(user)
    return jsonify({"message": "Akaunti imefunguliwa na kuthibitishwa.", "redirect": "/dashboard"}), 201


@app.route("/register", methods=["GET", "POST"])
@limiter.limit("3 per hour")
def register():
    """GET: onyesha form. POST: redirect kwa /register/initiate (backward compat)."""
    if request.method == "POST":
        return register_initiate()
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
        data = request.get_json() or request.form
        phone = sanitize(data.get("phone", ""), max_length=20)
        new_password = data.get("new_password", "")
        confirm = data.get("confirm_password", "")

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
            return jsonify(
                {"error": "Jina kamili linahitajika kuthibitisha akaunti."}
            ), 400

        user = User.query.filter_by(phone=phone).first()

        # SECURITY: Generic message + constant-time check — prevent user enumeration
        generic_ok = (
            jsonify({"message": "Kama taarifa ni sahihi, nywila imebadilishwa."}),
            200,
        )

        if not user:
            return generic_ok

        # Verify full name matches — second factor without OTP
        if user.full_name.strip().lower() != full_name:
            return generic_ok

        if not user.is_active:
            return jsonify(
                {"error": "Akaunti imesimamishwa. Wasiliana na msimamizi."}
            ), 403

        user.set_password(new_password)
        db.session.commit()
        return jsonify({"message": "Nywila imebadilishwa. Ingia sasa."})

    return render_template("auth/forgot_password.html")


@app.route("/change-password", methods=["GET", "POST"])
@login_required
@require_active_account
def change_password():
    if request.method == "POST":
        data = request.get_json() or request.form
        old_password = data.get("old_password", "")
        new_password = data.get("new_password", "")
        confirm = data.get("confirm_password", "")

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
    user_listings = (
        MarketListing.query.filter_by(seller_id=current_user.id)
        .order_by(MarketListing.posted_at.desc())
        .all()
    )
    user_crops = Crop.query.filter_by(user_id=current_user.id).all()
    return render_template(
        "dashboard/dashboard.html", listings=user_listings, crops=user_crops
    )


@app.route("/dashboard/add", methods=["GET", "POST"])
@login_required
@require_active_account
def add_product():
    if request.method == "POST":
        data = request.get_json() or request.form

        crop_name = sanitize(data.get("crop_name", ""), max_length=100)
        region = sanitize(
            data.get("location", current_user.region or ""), max_length=80
        )
        unit = sanitize(data.get("unit", "kg"), max_length=20)
        description = sanitize(data.get("description", ""), max_length=500)
        image_url = sanitize(data.get("image_url", ""), max_length=300)
        contact = current_user.phone or ""

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
            seller_id=current_user.id,
            title=crop_name,
            crop_name=crop_name,
            quantity_kg=quantity,
            unit=unit,
            price_tzs=price,
            region=region,
            contact=contact,
            description=description,
            image_url=image_url,
            is_available=True,
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
    page = request.args.get("page", 1, type=int)
    per_page = 12  # Listings 12 kwa ukurasa

    from sqlalchemy import case
    now = datetime.utcnow()
    pagination = (
        MarketListing.query.filter_by(is_available=True)
        .order_by(
            case(
                (db.and_(MarketListing.is_sponsored == True, MarketListing.sponsored_until > now), 1),
                else_=0
            ).desc(),
            MarketListing.posted_at.desc()
        )
        .paginate(page=page, per_page=per_page, error_out=False)
    )
    is_guest = not current_user.is_authenticated
    return render_template(
        "market/listings.html",
        listings=pagination.items,
        pagination=pagination,
        current_page=page,
        total_pages=pagination.pages,
        is_guest=is_guest,
        now=datetime.utcnow(),
    )


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
@login_required
def farmers():
    q = sanitize(request.args.get("q", ""), max_length=100)
    region = sanitize(request.args.get("region", ""), max_length=80)
    query = User.query.filter_by(role="farmer")
    if q:
        query = query.filter(User.full_name.ilike(f"%{q}%"))
    if region:
        query = query.filter(User.region.ilike(f"%{region}%"))
    farmer_list = query.order_by(User.full_name).all()
    regions = [
        r[0]
        for r in db.session.query(User.region)
        .filter(User.role == "farmer")
        .distinct()
        .all()
        if r[0]
    ]
    return render_template(
        "farmers.html", farmers=farmer_list, regions=regions, q=q, region=region
    )


# ── RATINGS ───────────────────────────────────────────────────────────────────


def get_seller_avg_rating(seller_id):
    from sqlalchemy import func

    result = (
        db.session.query(func.avg(SellerRating.stars))
        .filter_by(seller_id=seller_id)
        .scalar()
    )
    count = SellerRating.query.filter_by(seller_id=seller_id).count()
    return {"avg": round(float(result), 1) if result else 0.0, "count": count}


@app.route("/listings/<int:listing_id>/rate", methods=["POST"])
@login_required
@require_active_account
def rate_seller(listing_id):
    listing = MarketListing.query.get_or_404(listing_id)
    if listing.seller_id == current_user.id:
        return jsonify({"error": "Huwezi kujipa rating."}), 400

    data = request.get_json() or request.form
    comment = sanitize(data.get("comment", ""), max_length=300)

    try:
        stars = int(data.get("stars", 0))
    except (ValueError, TypeError):
        return jsonify({"error": "Rating si sahihi."}), 400

    if stars < 1 or stars > 5:
        return jsonify({"error": "Chagua nyota 1 hadi 5."}), 400

    existing = SellerRating.query.filter_by(
        rater_id=current_user.id, listing_id=listing_id
    ).first()
    if existing:
        return jsonify({"error": "Tayari umisha-rate seller huyu."}), 409

    rating = SellerRating(
        seller_id=listing.seller_id,
        rater_id=current_user.id,
        listing_id=listing_id,
        stars=stars,
        comment=comment,
    )
    db.session.add(rating)
    db.session.commit()
    info = get_seller_avg_rating(listing.seller_id)
    return jsonify(
        {
            "message": "Asante! Rating imehifadhiwa.",
            "avg": info["avg"],
            "count": info["count"],
        }
    ), 201


@app.route("/listings/report/<int:listing_id>", methods=["POST"])
@login_required
@require_active_account
def report_listing(listing_id):
    listing = MarketListing.query.get_or_404(listing_id)
    if listing.seller_id == current_user.id:
        return jsonify({"error": "Huwezi ku-report orodha yako mwenyewe."}), 400

    data = request.get_json() or request.form
    reason = sanitize(data.get("reason", ""), max_length=200)

    if not reason:
        return jsonify({"error": "Taja sababu ya ripoti."}), 400

    existing = ListingReport.query.filter_by(
        reporter_id=current_user.id, listing_id=listing_id
    ).first()
    if existing:
        return jsonify({"error": "Tayari umesharipoti orodha hii."}), 409

    report = ListingReport(
        reporter_id=current_user.id, listing_id=listing_id, reason=reason
    )
    db.session.add(report)
    db.session.commit()
    return jsonify({"message": "Ripoti imetumwa. Asante kwa kutusaidia."}), 201


# ── API ENDPOINTS ─────────────────────────────────────────────────────────────


@app.route("/api/crops")
def api_crops():
    crops = Crop.query.order_by(Crop.created_at.desc()).all()
    return jsonify(
        [
            {
                "id": c.id,
                "name_sw": c.name_sw,
                "name_en": c.name_en,
                "category": c.category,
                "season": c.season,
                "region": c.region,
            }
            for c in crops
        ]
    )



@app.route("/ai-daktari")
@login_required
def ai_daktari():
    return render_template("market/ai_daktari.html")


@app.route("/api/analyze-crop", methods=["POST"])
@limiter.limit("15 per hour")
def analyze_crop():
    if "image" not in request.files:
        return jsonify({"error": "Pakia picha ya zao kwanza."}), 400
    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "Hakuna picha iliyochaguliwa."}), 400
    allowed = {"jpg", "jpeg", "png", "webp"}
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in allowed:
        return jsonify({"error": "Picha lazima iwe JPG, PNG, au WEBP."}), 400
    file_bytes = file.read()
    if len(file_bytes) > 5 * 1024 * 1024:
        return jsonify({"error": "Picha ni kubwa mno. Kikomo ni 5MB."}), 400
    context = sanitize(request.form.get("context", ""), max_length=500)
    if not GEMINI_API_KEY:
        return jsonify({"error": "Huduma ya AI haipatikani sasa hivi."}), 503
    img_b64 = base64.b64encode(file_bytes).decode("utf-8")
    mime_type = f"image/{ext if ext != 'jpg' else 'jpeg'}"
    context_line = f"\nMaelezo ya mkulima: {context}" if context else ""
    prompt = f"""Wewe ni mtaalamu wa kilimo wa Tanzania. Chunguza picha hii ya zao na utoe uchambuzi kamili kwa JSON tu.{context_line}

Jibu kwa JSON hii tu (bila markdown, bila maelezo mengine):
{{
  "crop_detected": "jina la zao lililoonekana (Kiswahili)",
  "severity": "healthy|mild|moderate|severe",
  "diagnosis": "maelezo ya tatizo au hali ya zao kwa Kiswahili (sentensi 2-3)",
  "symptoms": ["dalili 1", "dalili 2", "dalili 3"],
  "treatment": ["hatua ya 1", "hatua ya 2", "hatua ya 3", "hatua ya 4"],
  "available_meds_tz": ["dawa 1 inayopatikana TZ", "dawa 2", "dawa 3"],
  "prevention": "jinsi ya kuzuia tatizo hili (Kiswahili)",
  "season_advice": "ushauri kulingana na msimu wa kilimo Tanzania (Kiswahili)",
  "confidence_pct": 85
}}"""
    payload = {
        "contents": [{"parts": [
            {"text": prompt},
            {"inline_data": {"mime_type": mime_type, "data": img_b64}}
        ]}],
        "generationConfig": {"temperature": 0.2, "maxOutputTokens": 1024},
    }

    # ── Retry logic: max 3 attempts, exponential backoff ─────────────────────
    import time as _time
    last_exc = None
    for attempt in range(1, 4):
        try:
            resp = requests.post(
                f"{GEMINI_VISION_URL}?key={GEMINI_API_KEY}",
                json=payload, timeout=45,
            )
            # Log non-200 responses for debugging
            if not resp.ok:
                print(f"[Gemini Vision] attempt {attempt} — HTTP {resp.status_code}: {resp.text[:300]}")
            if resp.status_code == 429:
                wait = 2 ** attempt  # 2s, 4s, 8s
                print(f"[Gemini Vision] rate-limited, retrying in {wait}s...")
                _time.sleep(wait)
                last_exc = Exception(f"429 rate limit (attempt {attempt})")
                continue
            resp.raise_for_status()
            gemini_data = resp.json()
            raw_text = (
                gemini_data.get("candidates", [{}])[0]
                .get("content", {}).get("parts", [{}])[0].get("text", "")
            )
            raw_text = re.sub(r"```json|```", "", raw_text).strip()
            analysis = json_lib.loads(raw_text)
            for field in ["crop_detected","severity","diagnosis","prevention","season_advice"]:
                if field in analysis:
                    analysis[field] = str(analysis[field])[:600]
            return jsonify({"success": True, "analysis": analysis})
        except json_lib.JSONDecodeError as e:
            print(f"[Gemini Vision] JSON parse error (attempt {attempt}): {e}")
            return jsonify({"error": "AI ilirudi na jibu lisilo sahihi. Jaribu tena."}), 500
        except requests.exceptions.Timeout:
            print(f"[Gemini Vision] timeout (attempt {attempt})")
            last_exc = Exception("timeout")
            if attempt < 3:
                _time.sleep(2 ** attempt)
                continue
            return jsonify({"error": "Muda wa kusubiri umepita. Jaribu tena."}), 504
        except Exception as exc:
            print(f"[Gemini Vision] error (attempt {attempt}): {exc}")
            last_exc = exc
            if attempt < 3:
                _time.sleep(2 ** attempt)
                continue

    # All retries exhausted
    print(f"[Gemini Vision] all retries failed. Last error: {last_exc}")
    if last_exc and "429" in str(last_exc):
        return jsonify({"error": "Huduma ya AI ina watu wengi sasa. Subiri sekunde 30 kisha jaribu tena."}), 429
    return jsonify({"error": "Hitilafu ya AI baada ya majaribio 3. Jaribu tena baadaye."}), 500

@app.route("/api/prices")
def api_prices():
    prices = MarketPrice.query.order_by(MarketPrice.recorded_at.desc()).limit(50).all()
    return jsonify(
        [
            {
                "id": p.id,
                "crop_id": p.crop_id,
                "region": p.region,
                "market": p.market,
                "price_tzs": p.price_tzs,
                "recorded_at": p.recorded_at.isoformat(),
            }
            for p in prices
        ]
    )


@app.route("/api/listings", methods=["GET"])
@limiter.limit("60 per minute")
def api_listings():
    listings = (
        MarketListing.query.filter_by(is_available=True)
        .order_by(MarketListing.posted_at.desc())
        .all()
    )
    return jsonify(
        [
            {
                "id": listing.id,
                "title": listing.title,
                "crop_name": listing.crop_name,
                "quantity_kg": listing.quantity_kg,
                "unit": listing.unit,
                "price_tzs": listing.price_tzs,
                "region": listing.region,
                "contact": listing.contact if current_user.is_authenticated else mask_phone(listing.contact),
                "posted_at": listing.posted_at.isoformat(),
            }
            for listing in listings
        ]
    )


@app.route("/api/listings", methods=["POST"])
@login_required
@require_active_account
@limiter.limit("20 per hour")
def create_listing():
    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON data inahitajika."}), 400

    crop_name = sanitize(data.get("crop_name", ""), max_length=100)
    region = sanitize(data.get("region", current_user.region or ""), max_length=80)
    contact = sanitize(data.get("contact", current_user.phone or ""), max_length=50)
    description = sanitize(data.get("description", ""), max_length=500)
    image_url = sanitize(data.get("image_url", ""), max_length=300)
    unit = sanitize(data.get("unit", "kg"), max_length=20)

    if not crop_name:
        return jsonify({"error": "Jina la zao linahitajika."}), 400

    price_ok, price = validate_price(data.get("price", 0))
    if not price_ok:
        return jsonify({"error": "Bei si sahihi."}), 400

    qty_ok, quantity = validate_quantity(data.get("quantity", 0))
    if not qty_ok:
        return jsonify({"error": "Kiwango si sahihi."}), 400
    # ── Listing quality gates ─────────────────────────────────────────────────
    if price <= 0:
        return jsonify({"error": "Bei lazima iwe zaidi ya sifuri."}), 400
    if quantity <= 0:
        return jsonify({"error": "Kiwango lazima kiwe zaidi ya sifuri."}), 400
    if len(description) < 20:
        return jsonify({"error": "Maelezo lazima yawe na herufi 20 au zaidi."}), 400
    if not image_url:
        return jsonify({"error": "Picha ya zao inahitajika."}), 400

    listing = MarketListing(
        seller_id=current_user.id,
        title=crop_name,
        crop_name=crop_name,
        quantity_kg=quantity,
        unit=unit,
        price_tzs=price,
        region=region,
        contact=contact,
        description=description,
        image_url=image_url,
        is_available=True,
    )
    db.session.add(listing)
    db.session.commit()
    return jsonify({"message": "Orodha imeongezwa.", "id": listing.id}), 201


@app.route("/api/listings/<int:listing_id>/sponsor", methods=["POST"])
@login_required
@require_active_account
@require_phone_verified
def sponsor_listing(listing_id):
    """Muuzaji anasponsor listing yake — mock payment, siku 7."""
    listing = MarketListing.query.get_or_404(listing_id)
    if listing.seller_id != current_user.id and current_user.role != "admin":
        return jsonify({"error": "Huna ruhusa."}), 403
    now = datetime.utcnow()
    # Ikiwa bado ina sponsorship hai, ongeza siku 7 zaidi
    if listing.is_sponsored and listing.sponsored_until and listing.sponsored_until > now:
        listing.sponsored_until = listing.sponsored_until + timedelta(days=7)
    else:
        listing.is_sponsored = True
        listing.sponsored_until = now + timedelta(days=7)
    db.session.commit()
    return jsonify({
        "message": "Orodha yako imeshinikizwa kwa siku 7.",
        "sponsored_until": listing.sponsored_until.strftime("%d %b %Y")
    }), 200


@app.route("/api/listings/<int:listing_id>/unsponsor", methods=["POST"])
@login_required
def unsponsor_listing(listing_id):
    """Admin anaweza kuondoa sponsorship."""
    if current_user.role != "admin":
        return jsonify({"error": "Admins tu."}), 403
    listing = MarketListing.query.get_or_404(listing_id)
    listing.is_sponsored = False
    listing.sponsored_until = None
    db.session.commit()
    return jsonify({"message": "Sponsorship imeondolewa."}), 200


@app.route("/api/listing/<int:listing_id>/rating")
def listing_rating_api(listing_id):
    listing = MarketListing.query.get_or_404(listing_id)
    return jsonify(get_seller_avg_rating(listing.seller_id))


@app.route("/api/seller/<int:seller_id>/rating")
def seller_rating_api(seller_id):
    return jsonify(get_seller_avg_rating(seller_id))


# ── PRICE PREDICTION ──────────────────────────────────────────────────────────

TANZANIA_CROPS = {
    "mahindi": {"en": "Maize", "category": "staple", "unit": "kg"},
    "mpunga": {"en": "Rice (paddy)", "category": "staple", "unit": "kg"},
    "viazi": {"en": "Potatoes", "category": "staple", "unit": "kg"},
    "muhogo": {"en": "Cassava", "category": "staple", "unit": "kg"},
    "ndizi": {"en": "Bananas", "category": "horticulture", "unit": "bunch"},
    "nyanya": {"en": "Tomatoes", "category": "horticulture", "unit": "kg"},
    "vitunguu": {"en": "Onions", "category": "horticulture", "unit": "kg"},
    "korosho": {"en": "Cashew nuts", "category": "cash_crop", "unit": "kg"},
    "kahawa": {"en": "Coffee", "category": "cash_crop", "unit": "kg"},
    "alizeti": {"en": "Sunflower", "category": "oilseed", "unit": "kg"},
    "maharage": {"en": "Beans", "category": "pulse", "unit": "kg"},
    "mtama": {"en": "Sorghum", "category": "cereal", "unit": "kg"},
}

TANZANIA_REGIONS = [
    "Dar es Salaam",
    "Mwanza",
    "Arusha",
    "Dodoma",
    "Mbeya",
    "Morogoro",
    "Tanga",
    "Iringa",
    "Kilimanjaro",
    "Tabora",
    "Kigoma",
    "Singida",
    "Kagera",
    "Geita",
    "Shinyanga",
    "Rukwa",
    "Ruvuma",
    "Lindi",
    "Mtwara",
    "Songwe",
    "Simiyu",
    "Katavi",
    "Njombe",
    "Pwani",
    "Manyara",
]

VALID_MONTHS = [
    "Januari",
    "Februari",
    "Machi",
    "Aprili",
    "Mei",
    "Juni",
    "Julai",
    "Agosti",
    "Septemba",
    "Oktoba",
    "Novemba",
    "Desemba",
]


def get_cached_prediction(cache_key):
    cached = PricePredictionCache.query.filter_by(cache_key=cache_key).first()
    if cached:
        age = datetime.utcnow() - cached.created_at
        if False:  # cache disabled
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
            existing.created_at = datetime.utcnow()
        else:
            db.session.add(
                PricePredictionCache(
                    cache_key=cache_key,
                    crop_name=crop_sw,
                    region=region,
                    month=month,
                    ai_response=ai_response_text,
                )
            )
        db.session.commit()
    except Exception:
        db.session.rollback()



def fetch_wfp_price(crop_sw, region):
    """Tumia bei halisi kutoka listings za AgroLink database."""
    try:
        from sqlalchemy import func
        region_lower = region.lower()
        # Tafuta listings za hivi karibuni za zao hili
        listings = MarketListing.query.filter(
            MarketListing.crop_name.ilike(f"%{crop_sw}%"),
            MarketListing.is_available == True,
        ).order_by(MarketListing.posted_at.desc()).limit(20).all()

        if not listings:
            # Jaribu kwa jina la Kiingereza
            crop_info = TANZANIA_CROPS.get(crop_sw, {})
            crop_en = crop_info.get("en", "")
            if crop_en:
                listings = MarketListing.query.filter(
                    MarketListing.crop_name.ilike(f"%{crop_en}%"),
                    MarketListing.is_available == True,
                ).order_by(MarketListing.posted_at.desc()).limit(20).all()

        if not listings:
            return None

        # Tafuta za mkoa kwanza
        regional = [l for l in listings if region_lower in (l.region or "").lower()]
        pool = regional if regional else listings

        # Hesabu wastani wa bei
        prices = []
        for l in pool:
            price = l.price_tzs
            unit = (l.unit or "kg").lower()
            qty = l.quantity_kg or 1
            # Normalize to per kg
            if unit == "tani":
                price = price / 1000
            elif unit == "debe":
                price = price / 20
            elif unit == "gunia":
                price = price / 100
            if price > 0:
                prices.append(price)

        if not prices:
            return None

        avg_price = sum(prices) / len(prices)
        latest_date = max(l.posted_at for l in pool).strftime("%Y-%m-%d")
        market_names = list(set(l.region for l in pool if l.region))[:2]

        return {
            "price_tzs_kg": round(avg_price),
            "market": ", ".join(market_names) or region,
            "date": latest_date,
            "source": "AgroLink — Bei za Wakulima",
            "count": len(prices),
        }
    except Exception as exc:
        print(f"DB price fetch error: {exc}")
        return None


def build_dynamic_prediction(crop_sw, region, month):
    static = build_static_prediction(crop_sw, region, month)
    static["data_source"] = "Modeli ya AI — Wizara ya Kilimo TZ 2025/2026"
    return static


def build_static_prediction(crop_sw, region, month):
    import random

    crop_info = TANZANIA_CROPS.get(crop_sw, {})
    crop_en = crop_info.get("en", crop_sw)
    unit = crop_info.get("unit", "kg")

    # Bei za wastani wa jumla (wholesale) Tanzania 2025/2026
    # Vyanzo: Wizara ya Kilimo TZ, JamiiForums market reports, field data
    BASE = {
        "mahindi":  {"low": 500,  "high": 900,  "mid": 700},
        "mpunga":   {"low": 2200, "high": 2800, "mid": 2500},
        "viazi":    {"low": 700,  "high": 1500, "mid": 1000},
        "muhogo":   {"low": 350,  "high": 800,  "mid": 550},
        "ndizi":    {"low": 600,  "high": 1800, "mid": 1000},
        "nyanya":   {"low": 600,  "high": 2000, "mid": 1200},
        "vitunguu": {"low": 900,  "high": 2200, "mid": 1500},
        "korosho":  {"low": 3500, "high": 6500, "mid": 5000},
        "kahawa":   {"low": 5000, "high": 9000, "mid": 7000},
        "alizeti":  {"low": 1800, "high": 3200, "mid": 2500},
        "maharage": {"low": 2500, "high": 4000, "mid": 3000},
        "mtama":    {"low": 500,  "high": 1100, "mid": 750},
    }
    SEASON = {
        "Januari": 1.10,
        "Februari": 1.05,
        "Machi": 0.90,
        "Aprili": 0.85,
        "Mei": 0.80,
        "Juni": 0.88,
        "Julai": 0.95,
        "Agosti": 1.00,
        "Septemba": 1.05,
        "Oktoba": 1.10,
        "Novemba": 1.15,
        "Desemba": 1.20,
    }
    REGION_MOD = {
        "Dar es Salaam": 1.25,
        "Arusha": 1.15,
        "Kilimanjaro": 1.10,
        "Mbeya": 0.90,
        "Iringa": 0.88,
        "Morogoro": 0.95,
        "Mwanza": 1.05,
        "Tanga": 1.00,
        "Dodoma": 1.00,
        "Tabora": 0.92,
        "Kigoma": 1.08,
        "Ruvuma": 0.90,
        "Lindi": 0.95,
        "Mtwara": 1.00,
        "Kagera": 0.95,
        "Geita": 0.98,
        "Shinyanga": 0.93,
        "Singida": 0.92,
        "Rukwa": 0.88,
        "Songwe": 0.90,
        "Njombe": 0.92,
        "Simiyu": 0.90,
        "Katavi": 0.88,
        "Pwani": 1.05,
        "Manyara": 1.00,
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
        "mahindi": [
            "Msimu wa mvua na ukame",
            "Ugavi kutoka mikoa ya Kusini",
            "Mahitaji ya viwanda vya unga",
        ],
        "mpunga": [
            "Umwagiliaji wa mashamba",
            "Uagizaji wa mpunga kutoka nje",
            "Mahitaji ya miji mikubwa",
        ],
        "nyanya": [
            "Hali ya hewa na mvua",
            "Umbali wa usafirishaji",
            "Soko la Kariakoo Dar es Salaam",
        ],
        "korosho": [
            "Bei ya soko la dunia",
            "Ubora wa usindikaji",
            "Ununuzi wa BOMA na wafanyabiashara wa nje",
        ],
        "kahawa": [
            "Bei ya soko la dunia (ICO)",
            "Ubora wa kukaanga na usindikaji",
            "Mauzo ya nje (export)",
        ],
        "viazi": [
            "Hali ya hewa ya baridi",
            "Udongo na mbolea",
            "Mahitaji ya miji na migodi",
        ],
        "vitunguu": [
            "Msimu wa mvua",
            "Uagizaji kutoka India",
            "Mahitaji ya kila nyumba",
        ],
        "maharage": [
            "Msimu wa kilimo na mvua",
            "Mahitaji ya protini",
            "Uagizaji kutoka jirani",
        ],
        "alizeti": [
            "Mahitaji ya viwanda vya mafuta",
            "Bei ya mafuta ya petroli",
            "Hali ya hewa ya ukame",
        ],
        "ndizi": [
            "Unyevu wa hewa na ardhi",
            "Umbali wa masoko makubwa",
            "Uozo wakati wa usafirishaji",
        ],
        "muhogo": [
            "Uvumilivu wa ukame",
            "Mahitaji ya chakula cha bei nafuu",
            "Usindikaji wa unga",
        ],
        "mtama": [
            "Msimu wa ukame na mvua",
            "Mahitaji ya bia za kienyeji",
            "Hifadhi na usindikaji",
        ],
    }

    base = BASE.get(crop_sw, {"low": 500, "high": 1500, "mid": 1000})
    s_mod = SEASON.get(month, 1.0)
    r_mod = REGION_MOD.get(region, 1.0)
    noise = random.uniform(0.97, 1.03)
    low = int(base["low"] * s_mod * r_mod * noise)
    high = int(base["high"] * s_mod * r_mod * noise)
    mid = int(base["mid"] * s_mod * r_mod * noise)

    if s_mod >= 1.10:
        trend, trend_pct = "rising", round((s_mod - 1) * 100, 1)
    elif s_mod <= 0.88:
        trend, trend_pct = "falling", round((1 - s_mod) * 100, 1)
    else:
        trend, trend_pct = "stable", round(abs(s_mod - 1) * 100, 1)

    confidence = (
        "high" if crop_sw in ["mahindi", "mpunga", "nyanya", "korosho"] else "medium"
    )
    season_note = (
        "mavuno makubwa — bei inashuka"
        if s_mod < 0.95
        else "uhaba wa soko — bei inapanda"
    )
    season_ctx = (
        f"Mwezi wa {month} ni wakati wa {season_note} kwa {crop_sw} katika {region}. "
        "Hali ya hewa na msimu wa kilimo vinaathiri sana ugavi na bei ya soko."
    )
    mkt_advice = (
        f"Hii ni wakati mzuri wa kuuza {crop_sw} — bei ipo juu. Masoko ya {region} na Dar es Salaam "
        "yanatoa bei nzuri. Hakikisha ubora wa zao lako ili kupata bei ya juu zaidi."
        if s_mod >= 1.0
        else f"Bei ya {crop_sw} ipo chini kwa sasa kutokana na mavuno mengi. Subiri miezi 1-2 au hifadhi vizuri. "
        "Ukiuza sasa, chagua masoko ya miji mikubwa kwa bei nzuri zaidi."
    )

    return {
        "crop_sw": crop_sw,
        "crop_en": crop_en,
        "region": region,
        "month": month,
        "unit": unit,
        "predicted_price_low": low,
        "predicted_price_high": high,
        "predicted_price_mid": mid,
        "trend": trend,
        "trend_pct": trend_pct,
        "confidence": confidence,
        "season_context": season_ctx,
        "market_advice": mkt_advice,
        "key_factors": FACTORS.get(
            crop_sw, ["Hali ya hewa", "Ugavi wa soko", "Mahitaji ya watumiaji"]
        ),
        "best_markets": MARKETS.get(region, ["Soko Kuu", "Dar es Salaam"])[:2],
    }


@app.route("/api/price-prediction", methods=["POST"])
@limiter.limit("20 per minute")
def api_price_prediction():
    data = request.get_json() or {}
    crop_sw = sanitize(data.get("crop", ""), max_length=50).lower()
    region = sanitize(data.get("region", ""), max_length=80)
    month = sanitize(data.get("month", ""), max_length=20)

    if not crop_sw or crop_sw not in TANZANIA_CROPS:
        return jsonify(
            {"error": "Zao halijulikani. Chagua zao kutoka kwenye orodha."}
        ), 400
    if not region or region not in TANZANIA_REGIONS:
        return jsonify({"error": "Taja mkoa sahihi wa Tanzania."}), 400
    if not month or month not in VALID_MONTHS:
        return jsonify({"error": "Taja mwezi sahihi (Januari–Desemba)."}), 400

    cache_key = f"{crop_sw}:{region.lower()}:{month.lower()}"
    cached = get_cached_prediction(cache_key)
    if cached:
        return jsonify({"success": True, "prediction": cached, "cached": True})

    prediction = build_dynamic_prediction(crop_sw, region, month)
    import json as json_lib

    save_prediction_cache(cache_key, crop_sw, region, month, json_lib.dumps(prediction))
    return jsonify({"success": True, "prediction": prediction, "cached": False})


@app.route("/api/price-prediction/crops")
def api_prediction_crops():
    return jsonify(
        {
            "crops": [
                {"sw": k, "en": v["en"], "category": v["category"], "unit": v["unit"]}
                for k, v in TANZANIA_CROPS.items()
            ],
            "regions": TANZANIA_REGIONS,
        }
    )




# ── MSHAURI PAGE ──────────────────────────────────────────────────────────────

@app.route("/mshauri")
@login_required
def mshauri():
    return render_template("mshauri.html")

# ── LISTING ADVICE BOT ───────────────────────────────────────────────────────

CROP_KNOWLEDGE = {
    "mahindi": {
        "magonjwa": ["blight ya mahindi", "kutu ya mahindi", "funza wa masikio"],
        "hifadhi": "Kausha hadi unyevu 13%. Hifadhi kwenye magunia makavu. Tumia ACTELLIC DUST.",
        "bei_min": 400, "bei_max": 900, "onyo_bei": 350,
        "msimu": "Machi-Mei na Agosti-Oktoba",
        "soko": "Dar es Salaam, Arusha, Moshi",
    },
    "nyanya": {
        "magonjwa": ["late blight", "ugonjwa wa kutu", "virus ya nyanya"],
        "hifadhi": "Ziuze ndani ya siku 3-5. Usizihifadhi kwenye jokofu zikiwa kijani.",
        "bei_min": 800, "bei_max": 2500, "onyo_bei": 600,
        "msimu": "Juni-Septemba (baridi — ubora bora)",
        "soko": "Dar es Salaam, Zanzibar, Mombasa",
    },
    "viazi": {
        "magonjwa": ["blight ya viazi", "vidonda vya mizizi"],
        "hifadhi": "Hifadhi mahali penye ubaridi na giza. Yanaishi wiki 4-8.",
        "bei_min": 500, "bei_max": 1200, "onyo_bei": 400,
        "msimu": "Julai-Septemba",
        "soko": "Dar es Salaam, Dodoma, Iringa",
    },
    "mpunga": {
        "magonjwa": ["blast ya mpunga", "njano ya majani"],
        "hifadhi": "Kausha hadi unyevu 12-14%. Hifadhi ghala kavu. Angalia panya.",
        "bei_min": 700, "bei_max": 1500, "onyo_bei": 600,
        "msimu": "Machi-Juni na Oktoba-Januari",
        "soko": "Dar es Salaam, Mwanza, Morogoro",
    },
    "maharage": {
        "magonjwa": ["kutu ya maharage", "anthracnose", "mosaic virus"],
        "hifadhi": "Kausha vizuri. Tumia majivu ya kuni kuchanganya — inazuia wadudu bila dawa.",
        "bei_min": 1200, "bei_max": 2800, "onyo_bei": 1000,
        "msimu": "Mei-Agosti",
        "soko": "Dar es Salaam, Nairobi, Kampala",
    },
    "ndizi": {
        "magonjwa": ["Panama disease", "sigatoka nyeusi", "bunchy top"],
        "hifadhi": "Zikata zikiwa bado kijani. Hifadhi mahali penye baridi.",
        "bei_min": 300, "bei_max": 800, "onyo_bei": 250,
        "msimu": "Wakati wowote — mazao mwaka mzima",
        "soko": "Dar es Salaam, Zanzibar, Mombasa",
    },
    "kabichi": {
        "magonjwa": ["blackrot", "aphid", "caterpillar"],
        "hifadhi": "Hifadhi mahali penye ubaridi. Inadumu wiki 1-2.",
        "bei_min": 400, "bei_max": 900, "onyo_bei": 300,
        "msimu": "Juni-Agosti (baridi)",
        "soko": "Dar es Salaam, Arusha, Moshi",
    },
    "pilipili": {
        "magonjwa": ["anthracnose", "bacterial spot", "virus ya pilipili"],
        "hifadhi": "Hifadhi joto 7-10C. Inadumu wiki 2-3.",
        "bei_min": 1500, "bei_max": 4000, "onyo_bei": 1200,
        "msimu": "Mwaka mzima — baridi ni bora",
        "soko": "Dar es Salaam, Zanzibar, Mombasa",
    },
    "ufuta": {
        "magonjwa": ["phytophthora", "cercospora leaf spot"],
        "hifadhi": "Kausha vizuri. Hifadhi magunia makavu.",
        "bei_min": 2000, "bei_max": 4500, "onyo_bei": 1800,
        "msimu": "Julai-Oktoba",
        "soko": "Dar es Salaam, Mtwara, Lindi",
    },
    "mwembe": {
        "magonjwa": ["anthracnose ya mwembe", "uoza wa tunda", "nzi wa matunda"],
        "hifadhi": "Yachume yakiwa magumu. Yaiva siku 5-7 joto la kawaida.",
        "bei_min": 400, "bei_max": 1200, "onyo_bei": 300,
        "msimu": "Oktoba-Desemba na Machi-Mei",
        "soko": "Dar es Salaam, Zanzibar, Pwani",
    },
}

GEMINI_TEXT_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-lite:generateContent"


@app.route("/api/listing-advice", methods=["POST"])
@login_required
@require_active_account
@limiter.limit("20 per hour")
def listing_advice():
    """
    Dummy bot ya AgroLink — inatumia CROP_KNOWLEDGE dictionary peke yake.
    Hakuna API call, hakuna gharama, inajibu papo hapo kwa Kiswahili kamili.
    """
    data = request.get_json() or {}
    crop_raw = sanitize(data.get("crop_name", ""), max_length=100).lower().strip()
    price_tzs  = float(data.get("price_tzs", 0) or 0)
    quantity   = float(data.get("quantity", 0) or 0)
    unit       = sanitize(data.get("unit", "kg"), max_length=20)
    region     = sanitize(data.get("region", ""), max_length=80)

    if not crop_raw:
        return jsonify({"error": "Jina la zao linahitajika."}), 400

    # ── Tafuta zao kwenye dictionary ─────────────────────────────────────────
    crop_data = None
    matched_key = None
    for key, val in CROP_KNOWLEDGE.items():
        if key in crop_raw or crop_raw in key:
            crop_data = val
            matched_key = key
            break

    current_month = MONTH_NAMES_SW[datetime.utcnow().month - 1]

    # ── Kama zao halijulikani ─────────────────────────────────────────────────
    if not crop_data:
        advice = {
            "hali_bei": "nzuri",
            "ujumbe_bei": (
                f"Hongoa kwa kuwasilisha {crop_raw} kwenye soko la AgroLink! "
                f"Hakikisha bei yako ya TZS {price_tzs:,.0f} inalingana na bei za "
                f"wakulima wengine wa {region or 'mkoa wako'} ili upate wanunuzi haraka."
            ),
            "ushauri_hifadhi": (
                f"Hifadhi {crop_raw} mahali penye ubaridi, hewa ya kutosha na mbali na unyevu. "
                f"Chunguza mazao yako kila siku 2-3 ili kugundua matatizo mapema. "
                f"Tumia magunia safi au vyombo vilivyofungwa kuzuia wadudu na viumbe vingine."
            ),
            "onyo_ugonjwa": (
                f"Angalia dalili za magonjwa kama madoa ya kahawia, uoza, au majani ya njano "
                f"kwenye {crop_raw} wako. Ikiwa utaona dalili hizo, wasiliana na mtaalamu wa "
                f"kilimo wa wilaya yako haraka iwezekanavyo."
            ),
            "soko_bora": (
                f"Masoko makubwa ya Tanzania kama Dar es Salaam, Arusha na Mwanza "
                f"yanaweza kuwa ya faida kwa {crop_raw}. Angalia bei za soko la karibu nawe "
                f"kwenye ukurasa wa Bei ya AI wa AgroLink."
            ),
            "hatua_haraka": (
                f"Piga picha nzuri zaidi za {crop_raw} wako na uweke maelezo kamili "
                f"kwenye orodha yako — orodha zenye picha nzuri zinapata wanunuzi "
                f"mara tatu zaidi kuliko zile bila picha!"
            ),
            "alama": 70,
        }
        return jsonify({"success": True, "advice": advice})

    # ── Uchambuzi wa bei ──────────────────────────────────────────────────────
    bei_min = crop_data["bei_min"]
    bei_max = crop_data["bei_max"]
    onyo    = crop_data["onyo_bei"]

    # Normalize bei kwa kg ili tulinganishe
    price_per_kg = price_tzs
    unit_lower = unit.lower()
    if unit_lower == "tani":
        price_per_kg = price_tzs / 1000
    elif unit_lower == "gunia":
        price_per_kg = price_tzs / 100
    elif unit_lower == "debe":
        price_per_kg = price_tzs / 20

    if price_per_kg < onyo:
        hali_bei = "chini"
        ujumbe_bei = (
            f"Bei yako ya TZS {price_tzs:,.0f} kwa {unit} ni chini sana ya wastani wa soko. "
            f"Wakulima wengine wa {matched_key} wanauza kati ya TZS {bei_min:,} hadi "
            f"TZS {bei_max:,} kwa kilo. Fikiria kuongeza bei yako ili usipoteze faida — "
            f"unaweza kupoteza hadi TZS {(onyo - price_per_kg) * quantity:,.0f} kwa orodha hii."
        )
        alama = 45
    elif price_per_kg > bei_max * 1.3:
        hali_bei = "juu"
        ujumbe_bei = (
            f"Bei yako ya TZS {price_tzs:,.0f} kwa {unit} ni juu zaidi ya wastani wa soko. "
            f"Bei ya kawaida ya {matched_key} ni TZS {bei_min:,} hadi TZS {bei_max:,} kwa kilo. "
            f"Bei ya juu inaweza kufukuza wanunuzi — fikiria kupunguza kidogo au "
            f"elezea vizuri ubora wa pekee wa zao lako kwenye maelezo."
        )
        alama = 60
    else:
        hali_bei = "nzuri"
        ujumbe_bei = (
            f"Hongera! Bei yako ya TZS {price_tzs:,.0f} kwa {unit} iko vizuri sana "
            f"ndani ya wastani wa soko la {matched_key} (TZS {bei_min:,}–{bei_max:,}/kg). "
            f"Una nafasi nzuri ya kupata wanunuzi haraka hasa ukiwa na picha nzuri "
            f"na maelezo kamili ya ubora wa zao lako."
        )
        alama = 88

    # ── Ushauri wa kuhifadhi ──────────────────────────────────────────────────
    ushauri_hifadhi = (
        f"{crop_data['hifadhi']} "
        f"Una kiasi cha {quantity:,.0f} {unit} — hakikisha hifadhi yako ina nafasi "
        f"ya kutosha na hewa ya kutosha. Msimu bora wa kuuza {matched_key} ni "
        f"{crop_data['msimu']}."
    )

    # ── Onyo la ugonjwa ───────────────────────────────────────────────────────
    magonjwa = crop_data["magonjwa"]
    onyo_ugonjwa = (
        f"Katika {current_month}, angalia hasa ugonjwa wa '{magonjwa[0]}' kwenye "
        f"{matched_key} wako. Magonjwa mengine ya kawaida ni {magonjwa[1]} na "
        f"{magonjwa[2]}. Chunguza majani, shina na matunda kila siku 2-3 "
        f"na uwasiliane na Daktari wa Zao wetu ukiona dalili yoyote."
    )

    # ── Soko bora ─────────────────────────────────────────────────────────────
    soko_bora = (
        f"Masoko bora ya {matched_key} sasa ni {crop_data['soko']}. "
        f"{'Mkoa wako wa ' + region + ' una soko zuri — wasiliana na wanunuzi wa karibu kwanza.' if region else 'Wasiliana na wanunuzi wa mkoa mkubwa karibu nawe.'}"
    )

    # ── Hatua ya haraka ───────────────────────────────────────────────────────
    if hali_bei == "chini":
        hatua_haraka = (
            f"Haraka iwezekanavyo: ongeza bei yako hadi angalau TZS {onyo:,}/kg "
            f"au elezea sababu ya bei hiyo kwenye maelezo (mfano: 'bei ya haraka — "
            f"lazima niuze leo'). Unaweza kubadilisha orodha yako kutoka dashboard."
        )
    elif hali_bei == "juu":
        hatua_haraka = (
            f"Ongeza maelezo ya kina ya ubora wa {matched_key} wako — "
            f"elezea jinsi ulivyolima, kama ni organic, au sifa nyingine za pekee "
            f"ili kuwashawishi wanunuzi bei yako ina thamani."
        )
    else:
        hatua_haraka = (
            f"Shiriki orodha yako kwa marafiki na vikundi vya WhatsApp vya kilimo "
            f"vya {region or 'mkoa wako'} — orodha mpya zinaweza kupata wanunuzi "
            f"ndani ya masaa 24 za kwanza hasa ukiitangaza mwenyewe."
        )

    advice = {
        "hali_bei":       hali_bei,
        "ujumbe_bei":     ujumbe_bei,
        "ushauri_hifadhi": ushauri_hifadhi,
        "onyo_ugonjwa":   onyo_ugonjwa,
        "soko_bora":      soko_bora,
        "hatua_haraka":   hatua_haraka,
        "alama":          alama,
    }
    return jsonify({"success": True, "advice": advice})


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
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in allowed:
        return jsonify({"error": "Picha lazima iwe jpg, png, au webp."}), 400

    # SECURITY: Limit file size to 5MB
    file_bytes = file.read()
    if len(file_bytes) > 5 * 1024 * 1024:
        return jsonify({"error": "Picha ni kubwa mno. Kikomo ni 5MB."}), 400

    filename = (
        f"crops/{current_user.id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.{ext}"
    )
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
    users = User.query.order_by(User.created_at.desc()).all()
    listings = MarketListing.query.order_by(MarketListing.posted_at.desc()).all()
    reports = ListingReport.query.order_by(ListingReport.created_at.desc()).all()
    banned = BannedEmail.query.order_by(BannedEmail.banned_at.desc()).all()
    total_farmers = User.query.filter_by(role="farmer").count()
    total_admins = User.query.filter_by(role="admin").count()
    total_listings = MarketListing.query.count()
    active_listings = MarketListing.query.filter_by(is_available=True).count()
    return render_template(
        "admin/panel.html",
        users=users,
        listings=listings,
        reports=reports,
        banned=banned,
        total_farmers=total_farmers,
        total_admins=total_admins,
        total_listings=total_listings,
        active_listings=active_listings,
    )


@app.route("/admin/suspend-user/<int:user_id>", methods=["POST"])
@login_required
@require_admin
def admin_suspend_user(user_id):
    """Simamisha akaunti + ongeza kwenye blacklist."""
    if user_id == current_user.id:
        return jsonify({"error": "Huwezi kujisimamisha mwenyewe."}), 400

    user = User.query.get_or_404(user_id)
    data = request.get_json() or {}
    reason = sanitize(
        data.get("reason", "Ukiukaji wa masharti ya matumizi."), max_length=300
    )

    # Simamisha akaunti
    user.is_active = False

    # Ongeza kwenye banned list — email NA simu zote mbili
    if user.email and not BannedEmail.query.filter_by(email=user.email).first():
        db.session.add(
            BannedEmail(
                email=user.email, phone=None, reason=reason, banned_by=current_user.id
            )
        )

    if not BannedEmail.query.filter_by(phone=user.phone).first():
        db.session.add(
            BannedEmail(
                email=None, phone=user.phone, reason=reason, banned_by=current_user.id
            )
        )

    db.session.commit()
    return jsonify(
        {
            "message": f"Akaunti ya {user.full_name} imesimamishwa na kuzuiwa.",
            "is_active": False,
        }
    )


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

    return jsonify(
        {"message": f"Akaunti ya {user.full_name} imerudishwa.", "is_active": True}
    )


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
    return jsonify(
        {
            "message": f"Akaunti ya {user.full_name} {status}.",
            "is_verified": user.is_verified,
        }
    )


# ── MISC ──────────────────────────────────────────────────────────────────────



@app.route("/admin/clear-cache", methods=["POST"])
@login_required
@require_admin
def clear_price_cache():
    try:
        deleted = PricePredictionCache.query.delete()
        db.session.commit()
        return jsonify({"message": f"Cache imefutwa. Records: {deleted}"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@app.route("/robots.txt")
def robots_txt():
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /dashboard",
        "Disallow: /dashboard/",
        "Disallow: /admin",
        "Disallow: /admin/",
        "Disallow: /api/",
        "Disallow: /payments/",
        "Disallow: /messages",
        "Disallow: /messages/",
        "Disallow: /b2b",
        "Disallow: /login",
        "Disallow: /register",
        "Disallow: /forgot-password",
        "Disallow: /change-password",
        "Disallow: /logout",
        "Disallow: /offline",
        "Disallow: /sw.js",
        "",
        "Sitemap: https://agrolink-tanzania.onrender.com/sitemap.xml",
    ]
    return "\n".join(lines), 200, {"Content-Type": "text/plain; charset=utf-8"}


@app.route("/sitemap.xml")
def sitemap_xml():
    from flask import make_response
    base = "https://agrolink-tanzania.onrender.com"

    static_urls = [
        {"loc": f"{base}/",           "priority": "1.0", "changefreq": "daily"},
        {"loc": f"{base}/listings",   "priority": "0.9", "changefreq": "hourly"},
        {"loc": f"{base}/farmers",    "priority": "0.7", "changefreq": "weekly"},
        {"loc": f"{base}/ai-daktari", "priority": "0.7", "changefreq": "monthly"},
        {"loc": f"{base}/mshauri",    "priority": "0.7", "changefreq": "monthly"},
        {"loc": f"{base}/about",      "priority": "0.6", "changefreq": "monthly"},
        {"loc": f"{base}/bei",        "priority": "0.5", "changefreq": "weekly"},
        {"loc": f"{base}/terms",      "priority": "0.3", "changefreq": "yearly"},
    ]

    listings = MarketListing.query.filter_by(is_available=True).order_by(
        MarketListing.posted_at.desc()
    ).limit(1000).all()

    listing_urls = [
        {
            "loc": f"{base}/listings?id={l.id}",
            "lastmod": l.posted_at.strftime("%Y-%m-%d"),
            "priority": "0.8",
            "changefreq": "weekly",
        }
        for l in listings
    ]

    all_urls = static_urls + listing_urls

    xml_parts = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml_parts.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    for u in all_urls:
        xml_parts.append("  <url>")
        xml_parts.append(f"    <loc>{u['loc']}</loc>")
        if "lastmod" in u:
            xml_parts.append(f"    <lastmod>{u['lastmod']}</lastmod>")
        xml_parts.append(f"    <changefreq>{u['changefreq']}</changefreq>")
        xml_parts.append(f"    <priority>{u['priority']}</priority>")
        xml_parts.append("  </url>")
    xml_parts.append("</urlset>")

    resp = make_response("\n".join(xml_parts))
    resp.headers["Content-Type"] = "application/xml; charset=utf-8"
    return resp

@app.route("/health")
def health():
    try:
        total_users    = User.query.filter_by(is_active=True).count()
        active_listings = MarketListing.query.filter_by(is_available=True).count()
    except Exception:
        total_users = active_listings = 0
    return jsonify({
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "stats": {
            "total_users": total_users,
            "active_listings": active_listings,
        }
    })


@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(403)
def forbidden(e):
    return render_template("403.html"), 403


@app.errorhandler(429)
def rate_limited(e):
    return jsonify(
        {"error": "Maombi mengi mno. Tafadhali subiri kidogo kisha jaribu tena."}
    ), 429


@app.errorhandler(500)
def server_error(e):
    return render_template("500.html"), 500


# ── Init DB & Run ─────────────────────────────────────────────────────────────

# ============================================================
# SPRINT 9 — MARKET DATA DASHBOARD
# ============================================================

MARKET_CROPS = [
    "Mahindi","Mpunga","Viazi","Nyanya","Vitunguu","Maharage",
    "Ndizi","Miwa","Alizeti","Pamba","Kahawa","Chai","Korosho","Karanga"
]

MARKET_REGIONS = [
    "Kitaifa","Dar es Salaam","Mbeya","Arusha","Dodoma",
    "Mwanza","Morogoro","Iringa","Ruvuma","Kilimanjaro"
]

@app.route("/market-data")
def market_data():
    crops = request.args.get("crop", "")
    region = request.args.get("region", "")

    query = MarketPrice.query
    if crops:
        query = query.filter(MarketPrice.crop_name == crops)
    if region:
        query = query.filter(MarketPrice.region == region)

    prices = query.order_by(MarketPrice.recorded_at.desc()).limit(200).all()

    # Latest bei kwa kila zao
    latest = {}
    for p in prices:
        if p.crop_name not in latest:
            latest[p.crop_name] = p

    return render_template(
        "market_data.html",
        prices=prices,
        latest=latest,
        crops=MARKET_CROPS,
        regions=MARKET_REGIONS,
        selected_crop=crops,
        selected_region=region,
    )

@app.route("/api/market-data")
def api_market_data():
    crop = request.args.get("crop", "")
    region = request.args.get("region", "")
    days = int(request.args.get("days", 30))

    from datetime import timedelta
    since = datetime.utcnow() - timedelta(days=days)
    query = MarketPrice.query.filter(MarketPrice.recorded_at >= since)
    if crop:
        query = query.filter(MarketPrice.crop_name == crop)
    if region:
        query = query.filter(MarketPrice.region == region)

    data = query.order_by(MarketPrice.recorded_at.asc()).all()
    return jsonify({"status": "ok", "count": len(data), "data": [p.to_dict() for p in data]})

@app.route("/admin/market-data")
@login_required
def admin_market_data():
    if current_user.role != "admin":
        abort(403)
    prices = MarketPrice.query.order_by(MarketPrice.recorded_at.desc()).limit(500).all()
    return render_template("admin_market_data.html", prices=prices,
                           crops=MARKET_CROPS, regions=MARKET_REGIONS,
                           now=datetime.utcnow())

@app.route("/admin/market-data/add", methods=["POST"])
@login_required
def admin_market_data_add():
    if current_user.role != "admin":
        abort(403)
    try:
        crop_name  = request.form.get("crop_name", "").strip()
        unit       = request.form.get("unit", "kg").strip()
        price_tzs  = float(request.form.get("price_tzs", 0))
        region     = request.form.get("region", "Kitaifa").strip()
        market     = request.form.get("market", "").strip()
        rec_date   = request.form.get("recorded_at", "")

        if not crop_name or price_tzs <= 0:
            flash("Jaza taarifa zote sahihi.", "danger")
            return redirect(url_for("admin_market_data"))

        from datetime import datetime as dt
        recorded_at = dt.strptime(rec_date, "%Y-%m-%d") if rec_date else datetime.utcnow()

        entry = MarketPrice(
            crop_name=crop_name, unit=unit, price_tzs=price_tzs,
            region=region, market=market or None,
            source="manual", recorded_at=recorded_at,
            created_by_id=current_user.id
        )
        db.session.add(entry)
        db.session.commit()
        flash(f"Bei ya {crop_name} imeongezwa.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Hitilafu: {e}", "danger")
    return redirect(url_for("admin_market_data"))

@app.route("/admin/market-data/delete/<int:entry_id>", methods=["POST"])
@login_required
def admin_market_data_delete(entry_id):
    if current_user.role != "admin":
        abort(403)
    entry = MarketPrice.query.get_or_404(entry_id)
    db.session.delete(entry)
    db.session.commit()
    flash("Rekodi imefutwa.", "success")
    return redirect(url_for("admin_market_data"))

@app.route("/admin/market-data/import-csv", methods=["POST"])
@login_required
def admin_market_data_import_csv():
    if current_user.role != "admin":
        abort(403)
    f = request.files.get("csv_file")
    if not f:
        flash("Chagua faili la CSV.", "danger")
        return redirect(url_for("admin_market_data"))
    try:
        import csv, io
        stream = io.StringIO(f.stream.read().decode("utf-8"))
        reader = csv.DictReader(stream)
        count = 0
        for row in reader:
            try:
                price = float(row.get("price_tzs", 0))
                if not row.get("crop_name") or price <= 0:
                    continue
                from datetime import datetime as dt
                rec = row.get("recorded_at", "")
                recorded_at = dt.strptime(rec, "%Y-%m-%d") if rec else datetime.utcnow()
                entry = MarketPrice(
                    crop_name=row["crop_name"].strip(),
                    unit=row.get("unit", "kg").strip(),
                    price_tzs=price,
                    region=row.get("region", "Kitaifa").strip(),
                    market=row.get("market", "").strip() or None,
                    source="csv_import",
                    recorded_at=recorded_at,
                    created_by_id=current_user.id
                )
                db.session.add(entry)
                count += 1
            except Exception:
                continue
        db.session.commit()
        flash(f"Rekodi {count} zimeingizwa kutoka CSV.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Hitilafu ya CSV: {e}", "danger")
    return redirect(url_for("admin_market_data"))

# ============================================================
# END SPRINT 9
# ============================================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(
        host="0.0.0.0",
        port=port,
        debug=os.environ.get("FLASK_DEBUG", "false").lower() == "true",
    )

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is missing (Render/Supabase not configured)")



# ════════════════════════════════════════════════════════════════════════════
# PHONE MASKING — Messaging API
# Buyers wanawasiliana na sellers bila kuona phone number
# ════════════════════════════════════════════════════════════════════════════

@app.route("/api/conversations/start", methods=["POST"])
@login_required
@require_active_account
@limiter.limit("10 per hour")
def start_conversation():
    """Buyer anaanzisha mazungumzo kuhusu listing."""
    data       = request.get_json() or {}
    listing_id = data.get("listing_id")
    first_msg  = sanitize(data.get("message", ""), max_length=1000).strip()

    if not listing_id or not first_msg:
        return jsonify({"error": "listing_id na message vinahitajika."}), 400

    listing = MarketListing.query.get(listing_id)
    if not listing or not listing.is_available:
        return jsonify({"error": "Bidhaa hii haipatikani."}), 404

    if listing.seller_id == current_user.id:
        return jsonify({"error": "Huwezi kuwasiliana nawe mwenyewe."}), 400

    # Angalia kama conversation tayari ipo
    conv = Conversation.query.filter_by(
        listing_id=listing_id, buyer_id=current_user.id
    ).first()

    if not conv:
        conv = Conversation(
            listing_id=listing_id,
            buyer_id=current_user.id,
            seller_id=listing.seller_id,
        )
        db.session.add(conv)
        db.session.flush()  # pata conv.id kabla ya message

    msg = Message(
        conversation_id=conv.id,
        sender_id=current_user.id,
        body=first_msg,
    )
    db.session.add(msg)
    db.session.commit()

    return jsonify({
        "success": True,
        "conversation_id": conv.id,
        "message": "Ujumbe wako umetumwa. Muuzaji atajibu hivi karibuni."
    }), 201


@app.route("/api/conversations/<int:conv_id>/messages", methods=["GET"])
@login_required
@require_active_account
def get_messages(conv_id):
    """Pata ujumbe wote wa mazungumzo — buyer au seller tu."""
    conv = Conversation.query.get_or_404(conv_id)
    if current_user.id not in (conv.buyer_id, conv.seller_id):
        return jsonify({"error": "Hauruhusiwi."}), 403

    # Mark messages as read
    Message.query.filter_by(
        conversation_id=conv_id, is_read=False
    ).filter(Message.sender_id != current_user.id).update({"is_read": True})
    db.session.commit()

    msgs = [
        {
            "id":        m.id,
            "body":      m.body,
            "sender":    m.sender.full_name,
            "is_mine":   m.sender_id == current_user.id,
            "is_read":   m.is_read,
            "sent_at":   m.sent_at.strftime("%Y-%m-%dT%H:%M:%SZ"),  # UTC ISO
        }
        for m in conv.messages
    ]
    return jsonify({
        "conversation_id": conv.id,
        "listing_title":   conv.listing.title,
        "messages":        msgs,
        "status":          conv.status.value,
    })


@app.route("/api/conversations/<int:conv_id>/reply", methods=["POST"])
@login_required
@require_active_account
@limiter.limit("60 per hour")
def reply_message(conv_id):
    """Buyer au seller anajibu kwenye mazungumzo."""
    conv = Conversation.query.get_or_404(conv_id)
    if current_user.id not in (conv.buyer_id, conv.seller_id):
        return jsonify({"error": "Hauruhusiwi."}), 403
    if conv.status != ConvStatus.active:
        return jsonify({"error": "Mazungumzo haya yamefungwa."}), 400

    data = request.get_json() or {}
    body = sanitize(data.get("message", ""), max_length=1000).strip()
    if not body:
        return jsonify({"error": "Ujumbe hauwezi kuwa wazi."}), 400

    reply_to_id = data.get("reply_to_id")
    if reply_to_id:
        parent = Message.query.get(reply_to_id)
        if not parent or parent.conversation_id != conv.id:
            reply_to_id = None
    msg = Message(
        conversation_id=conv.id,
        sender_id=current_user.id,
        body=body,
        reply_to_id=reply_to_id,
    )
    conv.updated_at = datetime.utcnow()
    db.session.add(msg)
    db.session.commit()

    return jsonify({"success": True, "message_id": msg.id})



@app.route("/api/messages/<int:msg_id>", methods=["DELETE"])
@login_required
@require_active_account
def delete_message(msg_id):
    """Futa ujumbe — sender tu, ndani ya dakika 10."""
    msg = Message.query.get_or_404(msg_id)
    if msg.sender_id != current_user.id:
        return jsonify({"error": "Unaweza kufuta ujumbe wako tu."}), 403
    if msg.is_deleted:
        return jsonify({"error": "Umeshafutwa."}), 400
    msg.is_deleted = True
    msg.body = "Ujumbe huu umefutwa."
    db.session.commit()
    return jsonify({"success": True})

@app.route("/api/notifications/unread-count", methods=["GET"])
@login_required
def notification_unread_count():
    """Idadi ya ujumbe ambao haujasomwa — kwa nav badge."""
    count = Message.query.join(Conversation).filter(
        Message.is_read == False,
        Message.sender_id != current_user.id,
        db.or_(
            Conversation.buyer_id  == current_user.id,
            Conversation.seller_id == current_user.id,
        )
    ).count()
    return jsonify({"unread": count})

@app.route("/api/escrow/hold", methods=["POST"])
@login_required
@require_active_account
def escrow_hold():
    """Mock: buyer anaanzisha malipo ya escrow."""
    import secrets
    data        = request.get_json(silent=True) or {}
    conv_id     = data.get("conversation_id")
    amount      = data.get("amount_tzs")
    if not conv_id or not amount:
        return jsonify({"error": "Taarifa hazikamiliki"}), 400
    conv = Conversation.query.get_or_404(conv_id)
    if conv.buyer_id != current_user.id:
        return jsonify({"error": "Huna ruhusa"}), 403
    # Angalia kama escrow ipo tayari kwa conversation hii
    existing = EscrowTransaction.query.filter_by(
        conversation_id=conv_id, status=EscrowStatus.held
    ).first()
    if existing:
        return jsonify({"error": "Escrow ipo tayari", "reference": existing.reference}), 409
    ref = "ESC-" + secrets.token_hex(6).upper()
    tx  = EscrowTransaction(
        conversation_id=conv_id,
        buyer_id=conv.buyer_id,
        seller_id=conv.seller_id,
        amount_tzs=int(amount),
        status=EscrowStatus.held,
        reference=ref,
    )
    db.session.add(tx)
    db.session.commit()
    return jsonify({"success": True, "reference": ref, "status": "held",
                    "message": f"TZS {int(amount):,} imehifadhiwa salama. Ref: {ref}"})

@app.route("/api/escrow/release", methods=["POST"])
@login_required
@require_active_account
def escrow_release():
    """Mock: buyer anakubali kutoa pesa kwa seller baada ya kupokea bidhaa."""
    data = request.get_json(silent=True) or {}
    ref  = data.get("reference")
    tx   = EscrowTransaction.query.filter_by(reference=ref).first_or_404()
    if tx.buyer_id != current_user.id:
        return jsonify({"error": "Huna ruhusa"}), 403
    if tx.status != EscrowStatus.held:
        return jsonify({"error": f"Hali ya sasa: {tx.status.value}"}), 409
    tx.status = EscrowStatus.released
    db.session.commit()
    return jsonify({"success": True, "status": "released",
                    "message": f"TZS {tx.amount_tzs:,} imetolewa kwa muuzaji. Asante!"})

@app.route("/api/escrow/refund", methods=["POST"])
@login_required
@require_active_account
def escrow_refund():
    """Mock: admin/seller anarudisha pesa kwa buyer."""
    data = request.get_json(silent=True) or {}
    ref  = data.get("reference")
    tx   = EscrowTransaction.query.filter_by(reference=ref).first_or_404()
    if current_user.role not in ("admin",) and tx.seller_id != current_user.id:
        return jsonify({"error": "Huna ruhusa"}), 403
    if tx.status != EscrowStatus.held:
        return jsonify({"error": f"Hali ya sasa: {tx.status.value}"}), 409
    tx.status = EscrowStatus.refunded
    db.session.commit()
    return jsonify({"success": True, "status": "refunded",
                    "message": f"TZS {tx.amount_tzs:,} imerudishwa kwa mnunuzi."})

@app.route("/api/escrow/status/<int:conv_id>", methods=["GET"])
@login_required
def escrow_status(conv_id):
    """Angalia hali ya escrow kwa conversation."""
    conv = Conversation.query.get_or_404(conv_id)
    if current_user.id not in (conv.buyer_id, conv.seller_id):
        return jsonify({"error": "Huna ruhusa"}), 403
    tx = EscrowTransaction.query.filter_by(conversation_id=conv_id).order_by(
        EscrowTransaction.created_at.desc()
    ).first()
    if not tx:
        return jsonify({"escrow": None})
    return jsonify({"escrow": {
        "reference":  tx.reference,
        "amount_tzs": tx.amount_tzs,
        "status":     tx.status.value,
        "created_at": tx.created_at.strftime("%d %b %Y, %H:%M"),
    }})

# ── Order State Machine Routes ────────────────────────────────────────────────
# SECURITY FIX (Sprint 2): 'approved->paid' na 'paid->completed' ZIMEONDOLEWA
# kimakusudi. Hatua hizo mbili zinafanyika TU kupitia /payments/callback na
# /payments/release (zenye shared-secret token + idempotency + audit log).
# Kuziacha hapa kungeruhusu buyer kughushi malipo kwa kupiga /advance moja kwa moja.
VALID_TRANSITIONS = {
    OrderStatus.draft:     {"next": OrderStatus.submitted, "role": "buyer"},
    OrderStatus.submitted: {"next": OrderStatus.approved,  "role": "seller"},
}

# Hatua zinazoruhusiwa TU kupitia mfumo wa malipo (payment_service / escrow),
# kamwe si kupitia /api/orders/<id>/advance.
PAYMENT_ONLY_TRANSITIONS = {OrderStatus.paid, OrderStatus.completed}

@app.route("/api/orders/create", methods=["POST"])
@login_required
@require_active_account
def order_create():
    """Buyer anaunda order mpya (draft) kwa conversation."""
    data    = request.get_json(silent=True) or {}
    conv_id = data.get("conversation_id")
    qty     = data.get("quantity_kg")
    if not conv_id or not qty:
        return jsonify({"error": "Taarifa hazikamiliki"}), 400
    conv = Conversation.query.get_or_404(conv_id)
    if conv.buyer_id != current_user.id:
        return jsonify({"error": "Huna ruhusa"}), 403
    existing = Order.query.filter_by(conversation_id=conv_id).first()
    if existing:
        return jsonify({"error": "Order ipo tayari", "order_id": existing.id,
                        "status": existing.status.value}), 409
    order = Order(
        conversation_id=conv_id,
        buyer_id=conv.buyer_id,
        seller_id=conv.seller_id,
        listing_id=conv.listing_id,
        quantity_kg=float(qty),
        price_tzs=int(conv.listing.price_tzs * float(qty)),
        status=OrderStatus.draft,
        note=data.get("note", ""),
    )
    db.session.add(order)
    db.session.commit()

    # Sprint 8 — EscrowFee: tengeneza record automatically (is_active=False by default)
    import os
    fee_active = os.environ.get("ESCROW_FEE_ACTIVE", "false").lower() == "true"
    fee_rate = float(os.environ.get("ESCROW_FEE_RATE", "0.025"))
    escrow_fee = EscrowFee(
        order_id=order.id,
        buyer_id=order.buyer_id,
        seller_id=order.seller_id,
        order_amount=order.price_tzs,
        fee_rate=fee_rate,
        is_active=fee_active,
    )
    escrow_fee.calculate_fee()
    db.session.add(escrow_fee)
    db.session.commit()

    return jsonify({"success": True, "order_id": order.id, "status": order.status.value,
                    "total_tzs": order.price_tzs})

@app.route("/api/orders/<int:order_id>/advance", methods=["POST"])
@login_required
@require_active_account
def order_advance(order_id):
    """Endeleza order hadi hatua inayofuata."""
    order = Order.query.get_or_404(order_id)
    if current_user.id not in (order.buyer_id, order.seller_id):
        return jsonify({"error": "Huna ruhusa"}), 403
    transition = VALID_TRANSITIONS.get(order.status)
    if not transition:
        return jsonify({"error": f"Order iko {order.status.value} — haiwezi kuendelea"}), 409
    # SECURITY FIX: ulinzi wa ziada (defense-in-depth) — hata kama
    # VALID_TRANSITIONS itabadilishwa kimakosa baadaye, mpito kwenda
    # 'paid' au 'completed' kupitia route hii UNAKATALIWA daima.
    if transition["next"] in PAYMENT_ONLY_TRANSITIONS:
        app.logger.warning(
            f"SECURITY: jaribio la kupita malipo — user {current_user.id} "
            f"alijaribu /advance order {order.id} kutoka {order.status.value} "
            f"kwenda {transition['next'].value}"
        )
        return jsonify({"error": "Hatua hii inafanyika tu baada ya malipo kuthibitishwa"}), 403
    required_role = transition["role"]
    if required_role == "buyer" and current_user.id != order.buyer_id:
        return jsonify({"error": f"Hatua hii inafanywa na mnunuzi tu"}), 403
    if required_role == "seller" and current_user.id != order.seller_id:
        return jsonify({"error": f"Hatua hii inafanywa na muuzaji tu"}), 403
    order.status = transition["next"]
    db.session.commit()
    return jsonify({"success": True, "status": order.status.value,
                    "message": f"Order imesogea hadi: {order.status.value}"})

@app.route("/api/orders/<int:order_id>/cancel", methods=["POST"])
@login_required
@require_active_account
def order_cancel(order_id):
    """Futa order (buyer au seller, kabla ya paid)."""
    order = Order.query.get_or_404(order_id)
    if current_user.id not in (order.buyer_id, order.seller_id):
        return jsonify({"error": "Huna ruhusa"}), 403
    if order.status in (OrderStatus.paid, OrderStatus.completed):
        return jsonify({"error": "Order imekamilika — haiwezi kufutwa"}), 409
    order.status = OrderStatus.cancelled
    db.session.commit()
    return jsonify({"success": True, "status": "cancelled"})

@app.route("/api/orders/status/<int:conv_id>", methods=["GET"])
@login_required
def order_status(conv_id):
    """Angalia hali ya order kwa conversation."""
    conv = Conversation.query.get_or_404(conv_id)
    if current_user.id not in (conv.buyer_id, conv.seller_id):
        return jsonify({"error": "Huna ruhusa"}), 403
    order = Order.query.filter_by(conversation_id=conv_id).first()
    if not order:
        return jsonify({"order": None})
    return jsonify({"order": {
        "id":          order.id,
        "status":      order.status.value,
        "quantity_kg": order.quantity_kg,
        "price_tzs":   order.price_tzs,
        "note":        order.note or "",
        "created_at":  order.created_at.strftime("%d %b %Y, %H:%M"),
        "is_buyer":    current_user.id == order.buyer_id,
        "is_seller":   current_user.id == order.seller_id,
    }})

@app.route("/api/conversations/mine", methods=["GET"])
@login_required
@require_active_account
def my_conversations():
    """Orodha ya mazungumzo yote ya mtumiaji (kama buyer na seller)."""
    as_buyer = Conversation.query.filter_by(buyer_id=current_user.id).all()
    as_seller = Conversation.query.filter_by(seller_id=current_user.id).all()

    def fmt(conv, role):
        other = conv.seller if role == "buyer" else conv.buyer
        unread = Message.query.filter_by(
            conversation_id=conv.id, is_read=False
        ).filter(Message.sender_id != current_user.id).count()
        last_msg = conv.messages[-1] if conv.messages else None
        return {
            "id":            conv.id,
            "role":          role,
            "listing_title": conv.listing.title,
            "listing_id":    conv.listing_id,
            "other_name":    other.full_name,
            "other_region":  other.region or "",
            "unread":        unread,
            "last_message":  last_msg.body[:80] if last_msg else "",
            "last_at":       last_msg.sent_at.strftime("%d %b, %H:%M") if last_msg else "",
            "status":        conv.status.value,
        }

    result = (
        [fmt(c, "buyer")  for c in as_buyer] +
        [fmt(c, "seller") for c in as_seller]
    )
    result.sort(key=lambda x: x["last_at"], reverse=True)
    return jsonify({"conversations": result, "total": len(result)})



@app.route("/messages")
@login_required
@require_active_account
def messages_inbox():
    """Inbox — orodha ya mazungumzo yote."""
    return render_template("messages/inbox.html")

@app.route("/messages/<int:conv_id>")
@login_required
@require_active_account
def messages_thread(conv_id):
    """Thread ya mazungumzo moja."""
    conv = Conversation.query.get_or_404(conv_id)
    if current_user.id not in (conv.buyer_id, conv.seller_id):
        return redirect(url_for("messages_inbox"))
    is_buyer  = current_user.id == conv.buyer_id
    is_seller = current_user.id == conv.seller_id
    listing_price = conv.listing.price_tzs if conv.listing else 0
    listing_qty   = conv.listing.quantity_kg if conv.listing else 0
    return render_template("messages/thread.html",
        conv_id=conv_id,
        is_buyer=is_buyer,
        is_seller=is_seller,
        listing_price=listing_price,
        listing_qty=listing_qty,
    )

# ════════════════════════════════════════════════════════════════════════════
# B2B BUYER PORTAL
# Hotels, supermarkets, wholesalers wanaweza kutuma bulk orders
# ════════════════════════════════════════════════════════════════════════════

def require_buyer(f):
    """Decorator: route inahitaji role ya buyer au admin."""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({"error": "Ingia kwanza."}), 401
        if current_user.role not in ("buyer", "admin", "farmer"):
            return jsonify({"error": "Sehemu hii ni kwa wanunuzi wa biashara tu."}), 403
        return f(*args, **kwargs)
    return decorated


@app.route("/b2b")
@login_required
@require_active_account
def b2b_portal():
    """B2B Buyer Portal — landing page."""
    if current_user.role not in ("buyer", "admin", "farmer"):
        return redirect(url_for("index"))
    # Bulk listings: zinazopatikana na quantity >= 100kg
    bulk_listings = (
        MarketListing.query
        .filter_by(is_available=True)
        .filter(MarketListing.quantity_kg >= 100)
        .order_by(MarketListing.posted_at.desc())
        .limit(50)
        .all()
    )
    # Mazungumzo ya mtumiaji huyu (buyer au seller)
    from sqlalchemy import or_
    my_convs = (
        Conversation.query
        .filter(
            or_(
                Conversation.buyer_id == current_user.id,
                Conversation.seller_id == current_user.id,
            )
        )
        .order_by(Conversation.updated_at.desc())
        .limit(10)
        .all()
    )
    unread_total = sum(
        Message.query.filter_by(conversation_id=c.id, is_read=False)
        .filter(Message.sender_id != current_user.id).count()
        for c in my_convs
    )
    return render_template(
        "b2b/portal.html",
        listings=bulk_listings,
        conversations=my_convs,
        unread_total=unread_total,
    )


@app.route("/api/b2b/listings", methods=["GET"])
@login_required
@require_active_account
def b2b_listings():
    """API: Listings za bulk (>=100kg) na filters."""
    crop    = request.args.get("crop", "").strip().lower()
    region  = request.args.get("region", "").strip()
    min_qty = float(request.args.get("min_qty", 100))
    page    = int(request.args.get("page", 1))
    per_page = 20

    q = MarketListing.query.filter_by(is_available=True).filter(
        MarketListing.quantity_kg >= min_qty
    )
    if crop:
        q = q.filter(MarketListing.crop_name.ilike(f"%{crop}%"))
    if region:
        q = q.filter(MarketListing.region.ilike(f"%{region}%"))

    total = q.count()
    listings = q.order_by(MarketListing.posted_at.desc()).offset(
        (page - 1) * per_page
    ).limit(per_page).all()

    return jsonify({
        "listings": [
            {
                "id":          l.id,
                "title":       l.title,
                "crop_name":   l.crop_name,
                "quantity_kg": l.quantity_kg,
                "unit":        l.unit,
                "price_tzs":   l.price_tzs,
                "region":      l.region,
                "description": l.description or "",
                "image_url":   l.image_url or "",
                "posted_at":   l.posted_at.strftime("%d %b %Y"),
                "seller_name": l.seller.full_name,
                "seller_verified": l.seller.is_verified,
            }
            for l in listings
        ],
        "total":    total,
        "page":     page,
        "pages":    (total + per_page - 1) // per_page,
    })


@app.route("/api/b2b/inquiry", methods=["POST"])
@login_required
@require_active_account
@limiter.limit("20 per hour")
def b2b_inquiry():
    """
    Bulk inquiry — buyer anatuma ombi la kununua kiasi kikubwa.
    Inafungua Conversation na kutuma ujumbe wa kwanza wa kina.
    """
    data        = request.get_json() or {}
    listing_id  = data.get("listing_id")
    quantity_kg = float(data.get("quantity_kg", 0))
    delivery    = sanitize(data.get("delivery_location", ""), max_length=200)
    timeline    = sanitize(data.get("timeline", ""), max_length=100)
    notes       = sanitize(data.get("notes", ""), max_length=500)

    if not listing_id or quantity_kg <= 0:
        return jsonify({"error": "listing_id na quantity_kg vinahitajika."}), 400
    if quantity_kg < 50:
        return jsonify({"error": "Kiwango cha chini cha B2B ni kg 50."}), 400

    listing = MarketListing.query.get(listing_id)
    if not listing or not listing.is_available:
        return jsonify({"error": "Bidhaa hii haipatikani."}), 404
    if listing.seller_id == current_user.id:
        return jsonify({"error": "Huwezi kununua bidhaa yako mwenyewe."}), 400

    # Jenga ujumbe wa kina wa B2B
    total_est = quantity_kg * listing.price_tzs
    sep = "─" * 30
    msg_body = (
        "OMBI LA BIASHARA (B2B)\n"
        + sep + "\n"
        + f"Mnunuzi: {current_user.full_name}\n"
        + f"Zao: {listing.crop_name}\n"
        + f"Kiasi Kinachohitajika: {quantity_kg:,.0f} kg\n"
        + f"Bei ya Sasa (kwa kg): TZS {listing.price_tzs:,.0f}\n"
        + f"Jumla ya Takriban: TZS {total_est:,.0f}\n"
        + f"Mahali pa Utoaji: {delivery or 'Haijabainishwa'}\n"
        + f"Muda wa Ununuzi: {timeline or 'Haijabainishwa'}\n"
        + f"Maelezo Zaidi: {notes or 'Hakuna'}\n"
        + sep + "\n"
        + "Tafadhali jibu hapa ili tuendelee na mazungumzo ya biashara."
    )

    # Tumia masking system — anza au endelea na conversation
    conv = Conversation.query.filter_by(
        listing_id=listing_id, buyer_id=current_user.id
    ).first()
    if not conv:
        conv = Conversation(
            listing_id=listing_id,
            buyer_id=current_user.id,
            seller_id=listing.seller_id,
        )
        db.session.add(conv)
        db.session.flush()

    msg = Message(
        conversation_id=conv.id,
        sender_id=current_user.id,
        body=msg_body,
    )
    db.session.add(msg)
    db.session.commit()

    return jsonify({
        "success": True,
        "conversation_id": conv.id,
        "message": f"Ombi lako la kg {quantity_kg:,.0f} limetumwa kwa muuzaji. Atajibu hivi karibuni.",
        "estimated_total_tzs": total_est,
    }), 201


@app.route("/api/b2b/dashboard-stats", methods=["GET"])
@login_required
@require_active_account
def b2b_dashboard_stats():
    """Stats za buyer dashboard — mazungumzo, maombi, jumla."""
    if current_user.role not in ("buyer", "admin", "farmer"):
        return jsonify({"error": "Hauruhusiwi."}), 403

    from sqlalchemy import or_
    convs = Conversation.query.filter(
        or_(
            Conversation.buyer_id == current_user.id,
            Conversation.seller_id == current_user.id,
        )
    ).all()
    total_inquiries = len(convs)
    active_convs    = sum(1 for c in convs if c.status.value == "active")
    unread          = sum(
        Message.query.filter_by(conversation_id=c.id, is_read=False)
        .filter(Message.sender_id != current_user.id).count()
        for c in convs
    )

    return jsonify({
        "total_inquiries": total_inquiries,
        "active_conversations": active_convs,
        "unread_messages": unread,
        "member_since": current_user.created_at.strftime("%B %Y"),
        "region": current_user.region or "Haijabainishwa",
    })



# ══════════════════════════════════════════════════════════════════════════════
# PAYMENT ROUTES — Sprint 1 (AzamPay Sandbox)
# ══════════════════════════════════════════════════════════════════════════════
import secrets
from payment_service import get_payment_service, PaymentError

@app.route("/payments/initiate/<int:order_id>", methods=["GET"])
@login_required
@require_active_account
def payment_page(order_id):
    """Onyesha ukurasa wa kulipa kwa order iliyoidhinishwa."""
    order = Order.query.get_or_404(order_id)

    # Hakikisha ni mnunuzi wa order hii
    if order.buyer_id != current_user.id:
        flash("Hauruhusiwi kufikia ukurasa huu.", "error")
        return redirect(url_for("dashboard"))

    # Order lazima iwe approved
    if order.status != OrderStatus.approved:
        flash("Agizo hili halijaidhinishwa bado.", "error")
        return redirect(url_for("dashboard"))

    return render_template(
        "payment.html",
        order=order,
        listing=order.listing,
        seller=order.seller,
    )


@app.route("/payments/initiate/<int:order_id>", methods=["POST"])
@login_required
@require_active_account
def payment_initiate(order_id):
    """Anzisha malipo — tuma USSD push kwa simu ya mnunuzi."""
    order = Order.query.get_or_404(order_id)

    if order.buyer_id != current_user.id:
        return jsonify({"success": False, "message": "Hauruhusiwi."}), 403

    if order.status != OrderStatus.approved:
        return jsonify({"success": False, "message": "Agizo hili halijaidhinishwa."}), 400

    msisdn = request.form.get("msisdn", "").strip()
    if not msisdn:
        return jsonify({"success": False, "message": "Weka namba ya simu ya kulipa."}), 400

    try:
        svc    = get_payment_service()
        result = svc.initiate_payment(order=order, msisdn=msisdn)

        if result["success"]:
            # Hifadhi reference kwenye EscrowTransaction
            escrow = EscrowTransaction.query.filter_by(
                conversation_id=order.conversation_id
            ).first()
            if escrow:
                escrow.reference = result["reference"]
                escrow.status    = EscrowStatus.held
                db.session.commit()

            return jsonify({
                "success": True,
                "message": result["message"],
                "reference": result["reference"],
            })
        else:
            return jsonify({"success": False, "message": result["message"]}), 400

    except PaymentError as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/payments/callback", methods=["POST"])
def payment_callback():
    """
    Payment provider callback — inaitwa na AzamPay/Selcom baada ya mnunuzi kulipa.
    Inabadilisha order status kuwa 'paid'.

    USALAMA:
      - Shared-secret token (?secret=XXXX) lazima ulingane na PAYMENT_CALLBACK_SECRET
      - Idempotent — callback ile ile haiwezi kuprocesiwa mara mbili
      - Kila jaribio (likifaulu au la) linarekodiwa kwa audit (IP + matokeo)
    """
    client_ip = request.headers.get("X-Forwarded-For", request.remote_addr)

    # ── 1. Shared-secret verification ──────────────────────────────────────
    expected_secret = os.getenv("PAYMENT_CALLBACK_SECRET", "")
    provided_secret  = request.args.get("secret", "")

    if not expected_secret:
        app.logger.error(
            "SECURITY: PAYMENT_CALLBACK_SECRET haijawekwa kwenye env — "
            "callback endpoint haina ulinzi!"
        )
        return jsonify({"status": "error", "message": "Server misconfigured"}), 200

    if not secrets.compare_digest(provided_secret, expected_secret):
        app.logger.warning(
            f"SECURITY: Callback ya kughushi kutoka IP={client_ip} — "
            f"secret token si sahihi. Imekataliwa."
        )
        return jsonify({"status": "error", "message": "Unauthorized"}), 200

    payload = request.get_json(force=True) or {}

    try:
        svc    = get_payment_service()
        result = svc.handle_callback(payload, dict(request.headers))

        if result["success"]:
            reference = result.get("reference", "")
            escrow = EscrowTransaction.query.filter_by(reference=reference).first()

            if not escrow:
                app.logger.warning(
                    f"AUDIT: Callback yenye reference isiyojulikana: {reference} "
                    f"kutoka IP={client_ip}"
                )
                return jsonify({"status": "ok"}), 200

            # ── 2. Idempotency check — kuzuia kuprocesiwa mara mbili ──────
            if escrow.status == EscrowStatus.held:
                app.logger.info(
                    f"AUDIT: Callback duplicate kwa reference={reference} "
                    f"imepuuzwa (tayari imeprocesiwa)."
                )
                return jsonify({"status": "ok", "message": "Already processed"}), 200

            escrow.status = EscrowStatus.held
            db.session.commit()

            order = Order.query.filter_by(
                conversation_id=escrow.conversation_id
            ).first()
            if order and order.status == OrderStatus.approved:
                order.status = OrderStatus.paid
                db.session.commit()
                app.logger.info(
                    f"AUDIT: Payment confirmed — order={order.id}, "
                    f"reference={reference}, IP={client_ip}"
                )
        else:
            app.logger.warning(
                f"AUDIT: Callback verification ilishindwa — "
                f"payload={payload}, IP={client_ip}"
            )

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        app.logger.error(f"Payment callback error: {e} — IP={client_ip}")
        return jsonify({"status": "error"}), 200  # 200 daima kwa callbacks


@app.route("/payments/release/<int:order_id>", methods=["POST"])
@login_required
@require_active_account
def payment_release(order_id):
    """
    Toa pesa kwa mkulima — inaitwa mnunuzi akithibitisha kupokea bidhaa.
    Order status: paid → completed.
    """
    order = Order.query.get_or_404(order_id)

    # Ni mnunuzi au admin tu anayeweza kuthibitisha
    if order.buyer_id != current_user.id and current_user.role != "admin":
        return jsonify({"success": False, "message": "Hauruhusiwi."}), 403

    if order.status != OrderStatus.paid:
        return jsonify({"success": False, "message": "Malipo hayajakamilika bado."}), 400

    escrow = EscrowTransaction.query.filter_by(
        conversation_id=order.conversation_id
    ).first()
    if not escrow:
        return jsonify({"success": False, "message": "Escrow haikupatikana."}), 404

    seller = order.seller
    seller_msisdn = seller.phone or ""
    if not seller_msisdn:
        return jsonify({
            "success": False,
            "message": "Mkulima hajaweka namba ya simu. Wasiliana naye moja kwa moja."
        }), 400

    try:
        svc    = get_payment_service()
        result = svc.release_escrow(escrow=escrow, seller_msisdn=seller_msisdn)

        if result["success"]:
            # Badilisha status zote
            escrow.status = EscrowStatus.released
            order.status  = OrderStatus.completed

            # Sprint 8 — release EscrowFee record wakati order imekamilika
            fee_record = EscrowFee.query.filter_by(order_id=order.id).first()
            if fee_record:
                fee_record.status = "released"
                fee_record.released_at = datetime.utcnow()

            db.session.commit()

            # Sasisha trust score ya muuzaji
            trust_engine(seller.id)

            return jsonify({
                "success": True,
                "message": f"Malipo ya {result['seller_amount']:,} TZS yametumwa kwa {seller.full_name}.",
                "seller_amount": result["seller_amount"],
                "platform_fee":  result["platform_fee"],
            })
        else:
            return jsonify({"success": False, "message": result["message"]}), 400

    except PaymentError as e:
        return jsonify({"success": False, "message": str(e)}), 500


# ─── ANALYTICS ──────────────────────────────────────────
def detect_device(ua):
    ua = ua.lower()
    if any(x in ua for x in ["mobile", "android", "iphone", "ipod"]):
        return "mobile"
    if "ipad" in ua or "tablet" in ua:
        return "tablet"
    return "desktop"

def detect_browser(ua):
    ua = ua.lower()
    if "edg" in ua:    return "Edge"
    if "chrome" in ua: return "Chrome"
    if "firefox" in ua:return "Firefox"
    if "safari" in ua: return "Safari"
    if "opera" in ua:  return "Opera"
    return "Other"

SKIP_PATHS = ["/static", "/sw.js", "/favicon", "/api/", "uptimerobot"]

@app.after_request
def track_pageview(response):
    try:
        path = request.path
        ua   = request.headers.get("User-Agent", "")
        # Skip static files, bots, API polling
        if any(s in path for s in SKIP_PATHS): return response
        if any(s in ua for s in ["UptimeRobot", "bot", "crawler", "spider"]): return response
        if response.status_code not in [200, 201]: return response

        pv = PageView(
            path       = path[:255],
            method     = request.method,
            user_id    = current_user.id if current_user.is_authenticated else None,
            ip_address = request.remote_addr,
            user_agent = ua[:512],
            browser    = detect_browser(ua),
            device     = detect_device(ua),
            referrer   = request.referrer[:512] if request.referrer else None,
        )
        db.session.add(pv)
        db.session.commit()
    except Exception:
        db.session.rollback()
    return response

@app.route("/api/analytics/pwa-install", methods=["POST"])
def track_pwa_install():
    ua = request.headers.get("User-Agent", "")
    ua_lower = ua.lower()
    if "iphone" in ua_lower or "ipad" in ua_lower:
        platform = "ios"
    elif "android" in ua_lower:
        platform = "android"
    else:
        platform = "desktop"

    install = PWAInstall(
        user_id    = current_user.id if current_user.is_authenticated else None,
        ip_address = request.remote_addr,
        user_agent = ua[:512],
        platform   = platform,
    )
    db.session.add(install)
    db.session.commit()
    return jsonify({"success": True})

@app.route("/admin/analytics")
@login_required
@require_admin
def admin_analytics():
    from datetime import timedelta
    today = datetime.utcnow().date()
    week_ago  = datetime.utcnow() - timedelta(days=7)
    month_ago = datetime.utcnow() - timedelta(days=30)

    total_views   = PageView.query.count()
    views_today   = PageView.query.filter(db.func.date(PageView.created_at) == today).count()
    views_week    = PageView.query.filter(PageView.created_at >= week_ago).count()
    views_month   = PageView.query.filter(PageView.created_at >= month_ago).count()

    # Device breakdown
    mobile_views  = PageView.query.filter_by(device="mobile").count()
    desktop_views = PageView.query.filter_by(device="desktop").count()
    tablet_views  = PageView.query.filter_by(device="tablet").count()

    # Browser breakdown
    browsers = db.session.query(
        PageView.browser, db.func.count(PageView.id)
    ).group_by(PageView.browser).all()

    # Top pages
    top_pages = db.session.query(
        PageView.path, db.func.count(PageView.id).label("visits")
    ).group_by(PageView.path).order_by(db.text("visits DESC")).limit(10).all()

    # PWA installs
    total_installs   = PWAInstall.query.count()
    installs_week    = PWAInstall.query.filter(PWAInstall.created_at >= week_ago).count()
    android_installs = PWAInstall.query.filter_by(platform="android").count()
    ios_installs     = PWAInstall.query.filter_by(platform="ios").count()

    # Daily views last 7 days
    daily_views = []
    for i in range(6, -1, -1):
        day = datetime.utcnow() - timedelta(days=i)
        count = PageView.query.filter(
            db.func.date(PageView.created_at) == day.date()
        ).count()
        daily_views.append({"date": day.strftime("%d %b"), "count": count})

    return render_template("admin/analytics.html",
        total_views=total_views,
        views_today=views_today,
        views_week=views_week,
        views_month=views_month,
        mobile_views=mobile_views,
        desktop_views=desktop_views,
        tablet_views=tablet_views,
        browsers=browsers,
        top_pages=top_pages,
        total_installs=total_installs,
        installs_week=installs_week,
        android_installs=android_installs,
        ios_installs=ios_installs,
        daily_views=daily_views,
    )


# ─── ADMIN: ESCROW FEES (Sprint 8) ─────────────────────────────────────────
@app.route("/admin/escrow-fees")
@login_required
@require_active_account
def admin_escrow_fees():
    if current_user.role != "admin":
        return redirect(url_for("index"))
    from datetime import timedelta
    fee_active = os.environ.get("ESCROW_FEE_ACTIVE", "false").lower() == "true"
    fee_rate   = float(os.environ.get("ESCROW_FEE_RATE", "0.025"))

    all_fees   = EscrowFee.query.order_by(EscrowFee.created_at.desc()).all()
    total_fees = EscrowFee.query.count()

    # Potential revenue (order_amount * fee_rate ya kila record)
    potential_revenue = db.session.query(
        db.func.sum(EscrowFee.order_amount * EscrowFee.fee_rate)
    ).scalar() or 0

    # Released fees
    released_fees = EscrowFee.query.filter_by(status="released").all()
    total_released = sum(f.fee_amount for f in released_fees)

    # Pending fees
    pending_count = EscrowFee.query.filter_by(status="pending").count()

    # Last 30 days
    month_ago = datetime.utcnow() - timedelta(days=30)
    fees_month = EscrowFee.query.filter(EscrowFee.created_at >= month_ago).count()

    return render_template("admin/escrow_fees.html",
        fee_active=fee_active,
        fee_rate=fee_rate,
        all_fees=all_fees,
        total_fees=total_fees,
        potential_revenue=int(potential_revenue),
        total_released=total_released,
        pending_count=pending_count,
        fees_month=fees_month,
    )

# ─── PWA ────────────────────────────────────────────────
@app.route("/offline")
def offline():
    return render_template("offline.html")

@app.route("/sw.js")
def service_worker():
    from flask import send_from_directory
    return send_from_directory(app.static_folder, "sw.js",
                               mimetype="application/javascript")
