import resend
import os
from datetime import datetime

FROM_EMAIL = "AgroLink Tanzania <onboarding@resend.dev>"

def send_welcome_email(to_email: str, user_name: str, role: str) -> bool:
    resend.api_key = os.environ.get("RESEND_API_KEY")
    if not to_email:
        return False

    role_labels = {
        "farmer": "Mkulima",
        "buyer": "Mnunuzi",
        "agent": "Wakala",
    }
    role_label = role_labels.get(role, role.capitalize())

    try:
        resend.Emails.send({
            "from": FROM_EMAIL,
            "to": to_email,
            "subject": "Karibu AgroLink Tanzania!",
            "html": f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {{ font-family: Arial, sans-serif; background: #f4f4f4; margin: 0; padding: 0; }}
    .container {{ max-width: 600px; margin: 40px auto; background: #ffffff; border-radius: 8px; overflow: hidden; }}
    .header {{ background: #263d2f; padding: 32px; text-align: center; }}
    .header h1 {{ color: #ffffff; margin: 0; font-size: 24px; }}
    .header p {{ color: #a8c5a0; margin: 8px 0 0; font-size: 14px; }}
    .body {{ padding: 32px; color: #333333; }}
    .body h2 {{ color: #263d2f; font-size: 20px; }}
    .role-badge {{ display: inline-block; background: #e8f5e9; color: #263d2f; padding: 6px 16px; border-radius: 20px; font-weight: bold; font-size: 14px; margin: 8px 0; }}
    .cta {{ display: block; margin: 24px 0; text-align: center; }}
    .cta a {{ background: #263d2f; color: #ffffff; padding: 14px 32px; border-radius: 6px; text-decoration: none; font-size: 16px; }}
    .footer {{ background: #f9f9f9; padding: 16px 32px; text-align: center; font-size: 12px; color: #999999; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>AgroLink Tanzania</h1>
      <p>Soko la Kilimo la Kisasa</p>
    </div>
    <div class="body">
      <h2>Karibu, {user_name}!</h2>
      <p>Umefanikiwa kujisajili kama:</p>
      <div class="role-badge">{role_label}</div>
      <p>Akaunti yako iko tayari. Unaweza sasa kuingia na kuanza kutumia huduma zetu za soko la kilimo.</p>
      <div class="cta">
        <a href="https://agrolink-tanzania.onrender.com">Ingia Sasa</a>
      </div>
      <p>Kama una maswali, wasiliana nasi kupitia tovuti.</p>
    </div>
    <div class="footer">
      <p>&copy; {datetime.now().year} AgroLink Tanzania. Haki zote zimehifadhiwa.</p>
      <p>Barua pepe hii ilitumwa kwa {to_email}</p>
    </div>
  </div>
</body>
</html>""",
        })
        return True
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")
        return False
