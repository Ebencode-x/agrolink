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


def send_partnership_notification(admin_email: str, org_name: str, org_type: str, interest_type: str, contact_name: str, contact_email: str, message: str) -> bool:
    resend.api_key = os.environ.get("RESEND_API_KEY")
    if not admin_email:
        return False
    interest_labels = {
        "institutional": "Ushirikiano wa Kitaasisi",
        "commercial": "Ushirikiano wa Kibiashara",
        "both": "Kitaasisi na Kibiashara",
    }
    interest_label = interest_labels.get(interest_type, interest_type.capitalize())
    try:
        resend.Emails.send({
            "from": FROM_EMAIL,
            "to": admin_email,
            "subject": f"Ombi jipya la ushirikiano: {org_name}",
            "html": f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {{ font-family: Arial, sans-serif; background: #f4f4f4; margin: 0; padding: 0; }}
    .container {{ max-width: 600px; margin: 40px auto; background: #ffffff; border-radius: 8px; overflow: hidden; }}
    .header {{ background: #263d2f; padding: 32px; text-align: center; }}
    .header h1 {{ color: #ffffff; margin: 0; font-size: 22px; }}
    .body {{ padding: 32px; color: #333333; }}
    .row {{ margin: 12px 0; }}
    .label {{ color: #666666; font-size: 13px; text-transform: uppercase; }}
    .value {{ color: #263d2f; font-size: 16px; font-weight: bold; }}
    .badge {{ display: inline-block; background: #e8f5e9; color: #263d2f; padding: 6px 16px; border-radius: 20px; font-weight: bold; font-size: 13px; }}
    .cta {{ display: block; margin: 24px 0; text-align: center; }}
    .cta a {{ background: #263d2f; color: #ffffff; padding: 14px 32px; border-radius: 6px; text-decoration: none; font-size: 16px; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>Ombi Jipya la Ushirikiano</h1>
    </div>
    <div class="body">
      <div class="row"><span class="label">Taasisi/Kampuni</span><br><span class="value">{org_name}</span></div>
      <div class="row"><span class="label">Aina</span><br>{org_type}</div>
      <div class="row"><span class="badge">{interest_label}</span></div>
      <div class="row"><span class="label">Mtu wa Mawasiliano</span><br>{contact_name} — {contact_email}</div>
      <div class="row"><span class="label">Ujumbe</span><br>{message}</div>
      <div class="cta">
        <a href="https://agrolink-tanzania.onrender.com/admin/ubia">Angalia kwenye Dashboard</a>
      </div>
    </div>
  </div>
</body>
</html>""",
        })
        return True
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")
        return False
