with open("app.py", "r") as f:
    content = f.read()

OLD = '''    msg_body = (
        f"OMBI LA BIASHARA (B2B)
"
        f"{'─' * 30}
"
        f"Mnunuzi: {current_user.full_name}
"
        f"Zao: {listing.crop_name}
"
        f"Kiasi Kinachohitajika: {quantity_kg:,.0f} kg
"
        f"Bei ya Sasa (kwa kg): TZS {listing.price_tzs:,.0f}
"
        f"Jumla ya Takriban: TZS {total_est:,.0f}
"
        f"Mahali pa Utoaji: {delivery or 'Haijabainishwa'}
"
        f"Muda wa Ununuzi: {timeline or 'Haijabainishwa'}
"
        f"Maelezo Zaidi: {notes or 'Hakuna'}
"
        f"{'─' * 30}
"
        f"Tafadhali jibu hapa ili tuendelee na mazungumzo ya biashara."
    )'''

NEW = '''    sep = "─" * 30
    msg_body = (
        "OMBI LA BIASHARA (B2B)\\n"
        + sep + "\\n"
        + f"Mnunuzi: {current_user.full_name}\\n"
        + f"Zao: {listing.crop_name}\\n"
        + f"Kiasi Kinachohitajika: {quantity_kg:,.0f} kg\\n"
        + f"Bei ya Sasa (kwa kg): TZS {listing.price_tzs:,.0f}\\n"
        + f"Jumla ya Takriban: TZS {total_est:,.0f}\\n"
        + f"Mahali pa Utoaji: {delivery or 'Haijabainishwa'}\\n"
        + f"Muda wa Ununuzi: {timeline or 'Haijabainishwa'}\\n"
        + f"Maelezo Zaidi: {notes or 'Hakuna'}\\n"
        + sep + "\\n"
        + "Tafadhali jibu hapa ili tuendelee na mazungumzo ya biashara."
    )'''

if OLD in content:
    content = content.replace(OLD, NEW, 1)
    with open("app.py", "w") as f:
        f.write(content)
    print("✅ FIXED — f-string newlines replaced")
else:
    print("❌ Block not found — checking raw bytes...")
    # Try finding the line manually
    lines = content.split("\n")
    for i, line in enumerate(lines, 1):
        if "OMBI LA BIASHARA" in line:
            print(f"  Found at line {i}: {repr(line)}")
