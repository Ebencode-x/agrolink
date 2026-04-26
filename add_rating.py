content = open('app.py', encoding='utf-8').read()

new_code = """
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

@app.route("/api/seller/<int:seller_id>/rating", methods=["GET"])
def seller_rating_api(seller_id):
    return jsonify(get_seller_avg_rating(seller_id))
"""

target = '@app.errorhandler(404)'
content = content.replace(target, new_code + '\n' + target)
open('app.py', 'w', encoding='utf-8').write(content)
print('DONE!')
