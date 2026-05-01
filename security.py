"""
security.py — AgroLink Security Layer
Weka faili hii kwenye root ya project (pamoja na app.py)
"""

import re
import bleach
from functools import wraps
from datetime import datetime, timedelta
from flask import request, jsonify, abort, g
from flask_login import current_user


# ── 1. INPUT SANITIZATION ─────────────────────────────────────────────────────

ALLOWED_TAGS = []  # Haturuhusu HTML yoyote kwenye input
ALLOWED_ATTRS = {}

def sanitize(value, max_length=None):
    """
    Safisha input yoyote ya mtumiaji.
    - Ondoa HTML tags (XSS prevention)
    - Strip whitespace
    - Punguza urefu kama max_length imewekwa
    """
    if value is None:
        return ""
    value = str(value)
    value = bleach.clean(value, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS, strip=True)
    value = value.strip()
    if max_length:
        value = value[:max_length]
    return value


def sanitize_dict(data: dict, rules: dict) -> dict:
    """
    Sanitize dictionary ya form data kwa sheria zilizowekwa.
    
    rules = {
        "field_name": {"max_length": 100, "required": True}
    }
    
    Returns cleaned data dict au raises ValueError kwa required fields.
    """
    cleaned = {}
    errors = []

    for field, opts in rules.items():
        raw = data.get(field, "")
        clean = sanitize(raw, max_length=opts.get("max_length"))

        if opts.get("required") and not clean:
            errors.append(f"Sehemu ya '{field}' inahitajika.")
            continue

        cleaned[field] = clean

    if errors:
        raise ValueError(" | ".join(errors))

    return cleaned


# ── 2. VALIDATION PATTERNS ───────────────────────────────────────────────────

PHONE_RE   = re.compile(r"^(\+?255|0)[67]\d{8}$")
EMAIL_RE   = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
NAME_RE    = re.compile(r"^[a-zA-ZÀ-ÿ\s'\-]{2,120}$")


def validate_phone(phone: str) -> bool:
    """Thibitisha namba ya simu ya Tanzania (+255 au 07x/06x)."""
    return bool(PHONE_RE.match(phone.strip())) if phone else False


def validate_email(email: str) -> bool:
    """Thibitisha muundo wa email."""
    if not email:
        return True  # Email si required
    return bool(EMAIL_RE.match(email.strip()))


def validate_password(password: str) -> tuple[bool, str]:
    """
    Thibitisha nguvu ya nywila.
    Returns (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Nywila lazima iwe na herufi 8 au zaidi."
    if not re.search(r"[A-Z]", password):
        return False, "Nywila lazima iwe na herufi kubwa angalau moja (A-Z)."
    if not re.search(r"[0-9]", password):
        return False, "Nywila lazima iwe na nambari angalau moja."
    return True, ""


def validate_price(value) -> tuple[bool, float]:
    """Thibitisha bei — lazima iwe nambari chanya."""
    try:
        price = float(value)
        if price <= 0:
            return False, 0.0
        if price > 100_000_000:  # 100M TZS ceiling
            return False, 0.0
        return True, price
    except (TypeError, ValueError):
        return False, 0.0


def validate_quantity(value) -> tuple[bool, float]:
    """Thibitisha kiwango — lazima iwe nambari chanya."""
    try:
        qty = float(value)
        if qty <= 0 or qty > 1_000_000:
            return False, 0.0
        return True, qty
    except (TypeError, ValueError):
        return False, 0.0


# ── 3. ACCOUNT SUSPENSION HELPERS ────────────────────────────────────────────

def require_active_account(f):
    """
    Decorator — angalia kwamba akaunti ya mtumiaji haijasimamishwa.
    Tumia BAADA ya @login_required.
    
    Mfano:
        @app.route("/dashboard")
        @login_required
        @require_active_account
        def dashboard(): ...
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_active:
            abort(403)
        return f(*args, **kwargs)
    return decorated


def require_admin(f):
    """
    Decorator — angalia kwamba mtumiaji ni admin.
    Tumia BAADA ya @login_required.
    Inabadilisha manual `if current_user.role != "admin": return redirect(...)` checks.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "admin":
            return jsonify({"error": "Hairuhusiwi. Unahitaji ruhusa ya admin."}), 403
        return f(*args, **kwargs)
    return decorated


# ── 4. SECURITY HEADERS ──────────────────────────────────────────────────────

def apply_security_headers(app):
    """
    Weka security headers kwenye kila response.
    Ita hii katika app.py baada ya kuunda Flask app:
    
        from security import apply_security_headers
        apply_security_headers(app)
    """
    @app.after_request
    def set_security_headers(response):
        # Kinga dhidi ya clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        
        # Kinga dhidi ya MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # XSS Protection (browser-level)
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Zuia referrer info isitoke nje
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # HSTS — baada ya kupata HTTPS domain (uncomment ukiwa tayari na domain)
        # response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Content Security Policy — zuia external scripts zisizoidhinishwa
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdnjs.cloudflare.com; "
            "font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com; "
            "img-src 'self' data: blob: https://*.supabase.co https://openweathermap.org; "
            "connect-src 'self' https://*.supabase.co https://api.openweathermap.org;"
        )
        
        return response

    return app


# ── 5. RATE LIMITING CONFIGURATION ──────────────────────────────────────────

def configure_rate_limits(limiter):
    """
    Rudisha dict ya rate limit decorators tayari kutumika.
    
    Tumia hivi katika app.py:
        from security import configure_rate_limits
        limits = configure_rate_limits(limiter)
        
        @app.route("/login", methods=["POST"])
        @limits["login"]
        def login(): ...
    """
    return {
        # Login — max 5 majaribio kwa dakika 1 kwa IP moja
        "login": limiter.limit("5 per minute"),

        # Register — max 3 akaunti mpya kwa saa 1 kwa IP moja  
        "register": limiter.limit("3 per hour"),

        # Password reset — max 3 per saa
        "forgot_password": limiter.limit("3 per hour"),

        # API endpoints za kawaida — max 60 kwa dakika
        "api_general": limiter.limit("60 per minute"),

        # Price prediction — max 20 kwa dakika (API ya bei)
        "price_prediction": limiter.limit("20 per minute"),

        # Upload picha — max 10 kwa saa
        "upload": limiter.limit("10 per hour"),
    }
