"""
Sprint 9 Finale — HDX/WFP Tanzania food prices auto-import.
Inakimbia kama standalone script (Render cron job) — si sehemu ya request cycle ya app.py.

Workflow:
1. Tumia HDX CKAN API (package_show) kupata URL halisi ya CSV resource ya sasa
   (haitegemei URL ya kudumu — HDX hubadilisha resource_id wakati mwingine)
2. Download CSV (WFP food prices format)
3. Chuja Tanzania pekee, mazao yanayofaa AgroLink (crops zilizopo MARKET_CROPS)
4. Convert bei USD -> TZS (exchange rate ya live)
5. Ingiza kwenye market_prices, source='hdx_wfp', status='approved'
6. Epuka duplicate (crop_name + region + recorded_at + source)
"""

import csv
import io
import json
import urllib.request
from datetime import datetime, timedelta

from app import app, db, MarketPrice  # type: ignore

HDX_PACKAGE_API = "https://data.humdata.org/api/3/action/package_show?id=wfp-food-prices-for-united-republic-of-tanzania"
EXCHANGE_RATE_API = "https://api.exchangerate-api.com/v4/latest/USD"

CROP_MAP = {
    "maize": "Mahindi",
    "maize (white)": "Mahindi",
    "rice": "Mpunga",
    "rice (imported)": "Mpunga",
    "beans": "Maharage",
    "beans (dry)": "Maharage",
    "potatoes (irish)": "Viazi",
    "potatoes": "Viazi",
    "tomatoes": "Nyanya",
    "onions": "Vitunguu",
    "bananas": "Ndizi",
    "sugar": "Miwa",
    "sunflower oil": "Alizeti",
    "cotton": "Pamba",
    "coffee": "Kahawa",
    "tea": "Chai",
    "cashew nuts": "Korosho",
    "groundnuts": "Karanga",
    "groundnuts (shelled)": "Karanga",
}

REGION_MAP = {
    "dar es salaam": "Dar es Salaam",
    "mbeya": "Mbeya",
    "arusha": "Arusha",
    "dodoma": "Dodoma",
    "mwanza": "Mwanza",
    "morogoro": "Morogoro",
    "iringa": "Iringa",
    "ruvuma": "Ruvuma",
    "kilimanjaro": "Kilimanjaro",
}


def get_csv_url():
    req = urllib.request.Request(HDX_PACKAGE_API, headers={"User-Agent": "AgroLink-Tanzania/1.0"})
    with urllib.request.urlopen(req, timeout=30) as res:
        data = json.loads(res.read().decode())

    if not data.get("success"):
        raise RuntimeError("HDX API haikufanikiwa kurudisha data")

    resources = data["result"]["resources"]
    for r in resources:
        if r.get("format", "").upper() == "CSV" and "qc" not in r.get("name", "").lower():
            return r["url"]

    raise RuntimeError("Hakuna CSV resource iliyopatikana kwenye HDX package")


def get_usd_to_tzs_rate():
    try:
        req = urllib.request.Request(EXCHANGE_RATE_API, headers={"User-Agent": "AgroLink-Tanzania/1.0"})
        with urllib.request.urlopen(req, timeout=15) as res:
            data = json.loads(res.read().decode())
        rate = data.get("rates", {}).get("TZS")
        if rate and rate > 0:
            return float(rate)
    except Exception as e:
        print(f"Exchange rate fetch imeshindwa: {e} — natumia fallback")
    return 2600.0


def run_import():
    print("=== HDX/WFP Tanzania Market Price Import ===")
    print(f"Wakati: {datetime.utcnow().isoformat()}")

    csv_url = get_csv_url()
    print(f"CSV URL: {csv_url}")

    usd_to_tzs = get_usd_to_tzs_rate()
    print(f"USD -> TZS rate: {usd_to_tzs}")

    req = urllib.request.Request(csv_url, headers={"User-Agent": "AgroLink-Tanzania/1.0"})
    chunks = []
    with urllib.request.urlopen(req, timeout=120) as res:
        while True:
            chunk = res.read(65536)
            if not chunk:
                break
            chunks.append(chunk)
    raw = b"".join(chunks).decode("utf-8", errors="ignore")

    lines = raw.splitlines()
    reader = csv.DictReader(lines)

    inserted = 0
    skipped_old = 0
    skipped_crop = 0
    skipped_duplicate = 0

    cutoff_date = datetime.utcnow() - timedelta(days=60)

    with app.app_context():
        for i, row in enumerate(reader):
            if i == 0 and row.get("date", "").startswith("#"):
                continue

            commodity_raw = (row.get("commodity") or "").strip().lower()
            region_raw = (row.get("admin1") or row.get("market") or "").strip().lower()
            date_raw = (row.get("date") or "").strip()
            price_raw = (row.get("price") or row.get("usdprice") or "").strip()
            currency = (row.get("currency") or "").strip().upper()
            unit_raw = (row.get("unit") or "kg").strip().lower()

            crop_name = CROP_MAP.get(commodity_raw)
            if not crop_name:
                skipped_crop += 1
                continue

            region = REGION_MAP.get(region_raw, "Kitaifa")

            try:
                recorded_at = datetime.strptime(date_raw, "%Y-%m-%d")
            except ValueError:
                continue

            if recorded_at < cutoff_date:
                skipped_old += 1
                continue

            try:
                price_val = float(price_raw)
            except ValueError:
                continue

            if price_val <= 0:
                continue

            if currency == "USD":
                price_tzs = price_val * usd_to_tzs
            elif currency == "TZS":
                price_tzs = price_val
            else:
                continue

            unit = "kg" if "kg" in unit_raw else unit_raw[:30]

            exists = MarketPrice.query.filter_by(
                crop_name=crop_name, region=region,
                recorded_at=recorded_at, source="hdx_wfp"
            ).first()
            if exists:
                skipped_duplicate += 1
                continue

            entry = MarketPrice(
                crop_name=crop_name,
                unit=unit,
                price_tzs=round(price_tzs, 2),
                region=region,
                market=None,
                source="hdx_wfp",
                recorded_at=recorded_at,
                created_by_id=None,
                submitted_by_id=None,
                status="approved",
            )
            db.session.add(entry)
            inserted += 1

        db.session.commit()

    print(f"Imeingizwa: {inserted}")
    print(f"Imerukwa (zao halifahamiki): {skipped_crop}")
    print(f"Imerukwa (tarehe ya zamani): {skipped_old}")
    print(f"Imerukwa (duplicate): {skipped_duplicate}")
    print("=== Import imekamilika ===")


if __name__ == "__main__":
    try:
        run_import()
    except Exception as e:
        print(f"Import imeshindwa: {e}")
        raise
