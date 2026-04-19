#!/usr/bin/env bash
set -e
[ -f ".env" ] && export $(grep -v '^#' .env | xargs)

case "${1:-help}" in
    init)
        flask db init
        echo "✅ migrations/ folder created."
        ;;
    migrate)
        flask db migrate -m "${2:-Auto migration}"
        echo "✅ Migration file created."
        ;;
    upgrade)
        flask db upgrade
        echo "✅ Database schema up to date."
        ;;
    seed)
        python3 -c "
from app import app, db, User, Crop, MarketPrice, MarketListing
with app.app_context():
    db.create_all()
    if not User.query.filter_by(phone='+255000000000').first():
        admin = User(full_name='Ebenezer Richard Masanja', phone='+255000000000',
                     email='admin@agrolink.co.tz', region='Mbeya', role='admin')
        admin.set_password('Admin@2025!')
        db.session.add(admin)
        db.session.flush()
        crops = [
            ('Mahindi','Maize','grain','masika','Mbeya'),
            ('Mpunga','Rice','grain','masika','Morogoro'),
            ('Kahawa','Coffee','cash','kiangazi','Kilimanjaro'),
            ('Viazi','Potatoes','vegetable','vuli','Mbeya'),
            ('Nyanya','Tomatoes','vegetable','vuli','Arusha'),
        ]
        for sw,en,cat,sea,reg in crops:
            db.session.add(Crop(user_id=admin.id,name_sw=sw,name_en=en,
                                category=cat,season=sea,region=reg))
        db.session.commit()
        print('✅ Seed data inserted.')
    else:
        print('⚠️  Admin already exists.')
"
        ;;
    *)
        echo "Usage: bash migrate.sh [init|migrate|upgrade|seed]"
        ;;
esac
