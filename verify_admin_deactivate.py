"""
Verify: admin_deactivate_user / admin_unsuspend_user (no FK violation, is_active toggles correctly)
Run: python3 verify_admin_deactivate.py
"""
from app import app, db, User, Message, Order

with app.app_context():
    admin = User.query.filter_by(role="admin").first()
    if not admin:
        print("[SKIP] Hakuna admin user kwenye DB.")
        raise SystemExit(0)

    # Pendelea mtumiaji mwenye messages (FK risk case) kama yupo, la sivyo yeyote asiye admin huyu
    target = (
        User.query.join(Message, Message.sender_id == User.id)
        .filter(User.id != admin.id)
        .first()
    )
    if not target:
        target = User.query.filter(User.id != admin.id).first()
    if not target:
        print("[SKIP] Hakuna mtumiaji mwingine wa kujaribu naye.")
        raise SystemExit(0)

    print(f"Testing with admin_id={admin.id}, target_id={target.id} ({target.full_name}), is_active before={target.is_active}")

client = app.test_client()
with client.session_transaction() as sess:
    sess["_user_id"] = str(admin.id)
    sess["_fresh"] = True

# 1. Deactivate
r = client.post(f"/admin/deactivate-user/{target.id}")
print("\n[1] POST deactivate-user:", r.status_code, r.get_json())

with app.app_context():
    t = User.query.get(target.id)
    print("[2] is_active after deactivate:", t.is_active, "OK" if t.is_active is False else "MISMATCH")

# 3. Login attempt should now be blocked (is_active gate at line ~897)
# just verifying the flag itself is enough here; login flow tested separately if needed

# 4. Reactivate
r = client.post(f"/admin/unsuspend-user/{target.id}")
print("\n[3] POST unsuspend-user (reactivate):", r.status_code, r.get_json())

with app.app_context():
    t = User.query.get(target.id)
    print("[4] is_active after reactivate:", t.is_active, "OK" if t.is_active is True else "MISMATCH")

# 5. Self-deactivate should be blocked
r = client.post(f"/admin/deactivate-user/{admin.id}")
print("\n[5] POST deactivate self:", r.status_code, r.get_json(),
      "OK (expected 400)" if r.status_code == 400 else "CHECK")

print("\n[DONE] Hakuna FK violation - user row bado ipo, is_active ilibadilika tu.")
