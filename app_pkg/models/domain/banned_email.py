from datetime import datetime
from app.extensions import db


class BannedEmail(db.Model):
    """
    Domain model: banned emails and phone numbers.
    Used to prevent re-registration of blocked users.
    """

    __tablename__ = "banned_emails"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=True, index=True)
    phone = db.Column(db.String(20), unique=True, nullable=True, index=True)
    reason = db.Column(db.String(300), nullable=True)
    banned_at = db.Column(db.DateTime, default=datetime.utcnow)
    banned_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
