"""
Migration: Add trust system columns to User model
Run: python migrate_trust.py
"""
import os, sys
from datetime import datetime

# ── Read current User model block ─────────────────────────────────────────────
TARGET = "app.py"

with open(TARGET, "r") as f:
    content = f.read()

# Columns tunazoongeza
NEW_COLS = '''    trust_level     = db.Column(db.String(10), default="gray", nullable=False)
    trust_points    = db.Column(db.Integer, default=0, nullable=False)
    flag_count      = db.Column(db.Integer, default=0, nullable=False)
    transaction_count = db.Column(db.Integer, default=0, nullable=False)
    avg_rating      = db.Column(db.Float, default=0.0, nullable=False)
    trust_updated_at = db.Column(db.DateTime, nullable=True)
    can_post_listing = db.Column(db.Boolean, default=False, nullable=False)
    can_advise      = db.Column(db.Boolean, default=False, nullable=False)
    can_b2b         = db.Column(db.Boolean, default=False, nullable=False)
'''

# Anchor: weka baada ya accepted_terms block
ANCHOR = '    terms_accepted_at = db.Column(db.DateTime, nullable=True)  # ← wakati wa kukubali\n    created_at = db.Column(db.DateTime, default=datetime.utcnow)'

REPLACEMENT = '    terms_accepted_at = db.Column(db.DateTime, nullable=True)  # ← wakati wa kukubali\n\n    # ── Trust system ──────────────────────────────────────────────────────────\n' + NEW_COLS + '    created_at = db.Column(db.DateTime, default=datetime.utcnow)'

if ANCHOR not in content:
    print("❌ ANCHOR haikupatikana — angalia app.py manually")
    sys.exit(1)

if "trust_level" in content:
    print("⚠️  trust_level ipo tayari — migration imeshafanywa")
    sys.exit(0)

new_content = content.replace(ANCHOR, REPLACEMENT, 1)

with open(TARGET, "w") as f:
    f.write(new_content)

print("✅ User model updated — trust columns added")
print("   Columns mpya: trust_level, trust_points, flag_count,")
print("   transaction_count, avg_rating, trust_updated_at,")
print("   can_post_listing, can_advise, can_b2b")
print()
print("⏭  Hatua inayofuata: flask db migrate -m 'add trust system' && flask db upgrade")
