# AgroLink Tanzania

> **Jukwaa la Kisasa la Kilimo — Connecting Tanzania's Farmers to Buyers Directly.**

[![Live Demo](https://img.shields.io/badge/Live%20Demo-agrolink--tanzania.onrender.com-10b981?style=for-the-badge&logo=render&logoColor=white)](https://agrolink-tanzania.onrender.com)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.x-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Supabase-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://supabase.com)
[![License](https://img.shields.io/badge/License-MIT-f59e0b?style=for-the-badge)](LICENSE)

---

## Overview

AgroLink Tanzania is a production-grade agricultural platform built for Tanzanian farmers and buyers. It enables farmers to list their crops with real photos, set prices, and connect directly with buyers — eliminating unnecessary middlemen and bringing transparency to agricultural markets.

The platform is built mobile-first, designed specifically for smartphone users across Tanzania's farming regions.

### Key Features

- **Marketplace** — Farmers post crop listings with photos, quantities, and prices. Buyers browse and contact sellers directly via phone or WhatsApp.
- **Weather Service** — Real-time weather data for 20+ Tanzanian cities powered by OpenWeatherMap API, with 30-minute intelligent caching.
- **Farmer Directory** — Browse and search registered farmers by name or region.
- **User Authentication** — Secure registration, login, password change, and password reset flows.
- **Image Upload** — Crop photos uploaded to Supabase Storage and served via public CDN URLs.
- **Admin Panel** — Platform administrators can manage users and listings.
- **Futuristic UI** — Glassmorphism design with Sora font, Lucide icons, and a green-amber color palette — mobile-first across all pages.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11, Flask 3.x |
| Database | PostgreSQL (hosted on Supabase) |
| ORM | SQLAlchemy + Flask-Migrate |
| Auth | Flask-Login, Flask-Bcrypt |
| Storage | Supabase Storage (crop images) |
| Weather | OpenWeatherMap API |
| Deployment | Render (Web Service) |
| Frontend | Jinja2 Templates, Vanilla JS, Lucide Icons |
| Fonts | Sora (display), DM Sans (body) — Google Fonts |

---

## Project Structure

```
agrolink/
├── app.py                  # Main Flask application — routes, models, config
├── requirements.txt        # Python dependencies
├── render.yaml             # Render deployment configuration
├── Procfile                # Process definition for deployment
├── migrate.sh              # Database migration script
├── schema.sql              # Initial database schema
├── .env.example            # Environment variables template
├── .python-version         # Python version pin (3.11)
├── static/
│   └── favicon.svg         # AgroLink SVG favicon
├── templates/
│   ├── base.html           # Base layout — nav, footer, mobile drawer
│   ├── index.html          # Homepage — hero, marketplace preview, weather
│   ├── about.html          # About page
│   ├── farmers.html        # Farmer directory
│   ├── developer.html      # Developer profile
│   ├── 404.html            # Error page
│   ├── 500.html            # Error page
│   ├── auth/
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── change_password.html
│   │   └── forgot_password.html
│   ├── dashboard/
│   │   ├── dashboard.html  # Farmer dashboard — listings, stats
│   │   └── add_product.html # Add new crop listing with image upload
│   ├── market/
│   │   └── listings.html   # Full marketplace — search, filter, delete
│   └── admin/
│       └── panel.html      # Admin panel — manage users and listings
└── migrations/             # Flask-Migrate migration files
```

---

## Database Models

| Model | Description |
|---|---|
| `User` | Farmers and admins — phone, email, region, role |
| `Crop` | Crop reference data owned by a user |
| `MarketListing` | Active marketplace listings with image URL, price, quantity |
| `MarketPrice` | Historical price records by region and market |
| `WeatherLog` | Cached weather API responses (30-minute TTL) |

---

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL database (or Supabase project)
- Supabase account (for image storage)
- OpenWeatherMap API key

### Local Setup

```bash
# 1. Clone the repository
git clone https://github.com/Ebencode-x/agrolink.git
cd agrolink

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy environment variables template
cp .env.example .env
# Edit .env and fill in your values

# 5. Run database migrations
flask db upgrade

# 6. Start the development server
python app.py
```

### Environment Variables

```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:password@host:5432/dbname
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-supabase-anon-key
OPENWEATHER_API_KEY=your-openweathermap-api-key
```

---

## Deployment

AgroLink is deployed on **Render** as a Web Service.

The `render.yaml` file defines the build and start commands. PostgreSQL is hosted on Supabase. Environment variables are configured in the Render dashboard.

**Build command:**
```bash
pip install -r requirements.txt && flask db upgrade
```

**Start command:**
```bash
gunicorn app:app
```

Live at: [https://agrolink-tanzania.onrender.com](https://agrolink-tanzania.onrender.com)

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/crops` | List all crops |
| GET | `/api/prices` | Latest 50 market prices |
| GET | `/api/listings` | All available marketplace listings |
| POST | `/api/listings` | Create a new listing (auth required) |
| POST | `/api/upload-image` | Upload crop image to Supabase (auth required) |
| GET | `/weather?city=Mbeya` | Weather data for a Tanzanian city |
| GET | `/health` | API health check |

---

## Screenshots

> Mobile-first design — built for Tanzania's smartphone farming community.

| Marketplace | Dashboard | Weather |
|---|---|---|
| Crop listings with photos, prices, and direct contact | Farmer dashboard with listing management | Real-time weather for 20+ Tanzanian cities |

---

## Roadmap

- [ ] SMS notifications for new buyer inquiries
- [ ] Seller verification and trust badges
- [ ] Buyer rating system for sellers
- [ ] Listing auto-expiry after 30 days
- [ ] PWA support for offline browsing
- [ ] WhatsApp share button per listing
- [ ] Swahili / English language toggle

---

## Author

**Ebenezer Richard Masanja**
First-year ICT Student — Mbeya University of Science and Technology (MUST), Tanzania

[![GitHub](https://img.shields.io/badge/GitHub-Ebencode--x-181717?style=flat-square&logo=github)](https://github.com/Ebencode-x)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Ebenezer%20Masanja-0A66C2?style=flat-square&logo=linkedin)](https://www.linkedin.com/in/ebenezer-richard-masanja-a49437399)
[![Credly](https://img.shields.io/badge/Credly-Certifications-FF6B00?style=flat-square&logo=credly)](https://www.credly.com/earner/dashboard)

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">
  <sub>Built with dedication in Mbeya, Tanzania — 2025</sub>
</div>
