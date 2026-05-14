from app.extensions import db


class BaseModel(db.Model):
    """
    Abstract base model for all domain entities.
    Ensures consistent ORM inheritance and future scalability.
    """
    __abstract__ = True
