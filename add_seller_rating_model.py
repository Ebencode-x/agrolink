content = open('app.py', encoding='utf-8').read()

model = """
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


"""

content = content.replace('class WeatherLog(db.Model):', model + 'class WeatherLog(db.Model):')
open('app.py', 'w', encoding='utf-8').write(content)
print('DONE!')
