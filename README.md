# AgroLink Tanzania

**Jukwaa la Kisasa la Kilimo — Connecting Tanzania's Farmers to Buyers Directly.**

[![Live Demo](https://img.shields.io/badge/Live%20Demo-agrolink--tanzania.onrender.com-10b981?style=for-the-badge&logo=render&logoColor=white)](https://agrolink-tanzania.onrender.com)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.x-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Supabase-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://supabase.com)
[![License](https://img.shields.io/badge/License-MIT-f59e0b?style=for-the-badge)](LICENSE)

---

## Overview

AgroLink Tanzania is a production-grade agricultural marketplace platform built for Tanzanian farmers and buyers. It eliminates middlemen by enabling farmers to list crops directly, get AI-powered price intelligence, and connect with buyers across all 25 regions of Tanzania mainland.

Built mobile-first, designed specifically for smartphone users in Tanzania's farming communities.

---

## Features

- **Soko la Mazao** — Farmers post crop listings with photos, quantities, and prices. Buyers browse and contact sellers directly via phone or WhatsApp.
- **Bei ya AI** — Smart price prediction engine for 12 crops across all 25 Tanzania regions, with seasonal and regional market intelligence. Powered by a caching layer with 6-hour TTL.
- **Hali ya Hewa** — Real-time weather data for 20+ Tanzanian cities via OpenWeatherMap API, with 30-minute intelligent caching.
- **Seller Ratings** — Star-based trust system allowing buyers to rate sellers per listing — one rating per buyer per listing enforced at DB level.
- **Listing Reports** — Community moderation — users can report suspicious or fraudulent listings.
- **Farmer Directory** — Browse and search registered farmers by name or region.
- **User Authentication** — Secure registration, login, password change, and forgot password flows.
- **Admin Panel** — Platform administrators manage users, listings, and reports.
- **Futuristic UI** — Glassmorphism design with Sora font, Lucide icons, and a green-amber palette — fully responsive.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11, Flask 3.x |
| Database | PostgreSQL (Supabase) |
| ORM | SQLAlchemy + Flask-Migrate |
| Auth | Flask-Login, Flask-Bcrypt |
| Storage | Supabase Storage (crop images) |
| Weather | OpenWeatherMap API |
| Deployment | Render (Web Service) |
| Frontend | Jinja2 Templates, Vanilla JS, Lucide Icons |
| Fonts | Sora (display), DM Sans (body) |

---

## Database Models

| Model | Description |
|---|---|
| `User` | Farmers and admins — phone, email, region, role |
| `Crop` | Crop reference data owned by a user |
| `MarketListing` | Active marketplace listings with image, price, quantity |
| `MarketPrice` | Historical price records by region and market |
| `SellerRating` | Star ratings per listing — one per buyer enforced |
| `ListingReport` | Community reports on suspicious listings |
| `PricePredictionCache` | Cached price predictions — 6-hour TTL |
| `PricePredictionLog` | Audit trail of all price prediction queries |
| `WeatherLog` | Cached weather responses — 30-minute TTL |

---

## Project Structure

agrolink/
├── app.py                  # Main Flask app — models, routes, services
├── requirements.txt        # Python dependencies
├── templates/
│   ├── base.html           # Base layout — nav, footer, mobile drawer
│   ├── index.html          # Homepage
│   ├── about.html          # About page
│   ├── farmers.html        # Farmer directory
│   ├── developer.html      # Developer profile
│   ├── 404.html            # Error pages
│   ├── auth/               # Login, register, change/forgot password
│   ├── dashboard/          # Farmer dashboard, add listing
│   ├── market/             # Listings marketplace, price intelligence
│   └── admin/              # Admin panel
└── migrations/             # Alembic migration files

---

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL database (Supabase recommended)
- OpenWeatherMap API key

### Local Setup

```bash
git clone https://github.com/Ebencode-x/agrolink.git
cd agrolink
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
flask db upgrade
python app.py
```

### Environment Variables

```env
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:password@host:5432/dbname
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-supabase-anon-key
OPENWEATHER_API_KEY=your-openweathermap-api-key
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/crops` | List all supported crops |
| GET | `/api/prices` | Latest 50 market prices |
| GET | `/api/listings` | All available marketplace listings |
| POST | `/api/listings` | Create a new listing (auth required) |
| POST | `/api/price-prediction` | Get price prediction for crop/region/month |
| GET | `/api/price-prediction/crops` | List all supported crops for prediction |
| GET | `/api/listing/:id/rating` | Get rating summary for a listing |
| POST | `/api/listing/:id/rate` | Submit a star rating (auth required) |
| POST | `/api/listing/:id/report` | Report a listing (auth required) |
| GET | `/weather?city=Mbeya` | Weather data for a Tanzanian city |
| GET | `/health` | Health check |

---

## Roadmap

- [x] Marketplace with crop listings
- [x] Seller rating system
- [x] Community listing reports
- [x] AI price prediction with caching
- [x] Real-time weather service
- [ ] Image upload for listings
- [ ] Pagination for marketplace
- [ ] Search and filter by crop/region
- [ ] SMS notifications for buyer inquiries
- [ ] WhatsApp share button per listing
- [ ] PWA support for offline browsing
- [ ] Listing auto-expiry after 30 days

---

## Author

**Ebenezer Richard Masanja**
ICT Student — Mbeya University of Science and Technology (MUST), Tanzania

[![GitHub](https://img.shields.io/badge/GitHub-Ebencode--x-181717?style=flat-square&logo=github)](https://github.com/Ebencode-x)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Ebenezer%20Masanja-0A66C2?style=flat-square&logo=linkedin)](https://www.linkedin.com/in/ebenezer-richard-masanja-a49437399)

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">
  <sub>Built with dedication in Mbeya, Tanzania — 2026</sub>
</div>
