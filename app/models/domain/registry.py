"""
Domain registry for controlled model exposure.
Avoids circular imports in large-scale architecture.
"""

from .banned_email import BannedEmail

DOMAIN_MODELS = [
    BannedEmail,
]
