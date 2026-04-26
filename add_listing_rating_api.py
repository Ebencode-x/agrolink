content = open('app.py', encoding='utf-8').read()

new_route = """
@app.route("/api/listing/<int:listing_id>/rating", methods=["GET"])
def listing_rating_api(listing_id):
    listing = MarketListing.query.get_or_404(listing_id)
    return jsonify(get_seller_avg_rating(listing.seller_id))
"""

content = content.replace(
    '@app.route("/api/seller/<int:seller_id>/rating"',
    new_route + '\n@app.route("/api/seller/<int:seller_id>/rating"'
)
open('app.py', 'w', encoding='utf-8').write(content)
print('DONE!')
