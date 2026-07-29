"""
Verify: message hard-hide endpoints (delete-for-me, clear conversation, 10-min window)
Run: python3 verify_messages_hide.py
"""
from app import app, db, Conversation, Message, User

with app.app_context():
    conv = Conversation.query.first()
    if not conv:
        print("[SKIP] Hakuna conversation yoyote kwenye DB kujaribu nayo.")
        raise SystemExit(0)

    buyer = User.query.get(conv.buyer_id)
    msg = Message.query.filter_by(conversation_id=conv.id).first()
    print(f"Testing with conversation_id={conv.id}, buyer_id={buyer.id}, msg_id={msg.id if msg else None}")

client = app.test_client()

with client.session_transaction() as sess:
    sess["_user_id"] = str(buyer.id)
    sess["_fresh"] = True

with app.app_context():
    conv = Conversation.query.first()
    msg = Message.query.filter_by(conversation_id=conv.id).first()

# 1. GET messages (baseline)
r = client.get(f"/api/conversations/{conv.id}/messages")
print("\n[1] GET messages:", r.status_code)
before_count = len(r.get_json().get("messages", []))
print("    message count before:", before_count)

if msg:
    # 2. delete-for-me
    r = client.post(f"/api/messages/{msg.id}/delete-for-me")
    print("\n[2] POST delete-for-me:", r.status_code, r.get_json())

    # 3. GET messages again -> count should drop by 1
    r = client.get(f"/api/conversations/{conv.id}/messages")
    after_count = len(r.get_json().get("messages", []))
    print("[3] message count after delete-for-me:", after_count,
          "OK" if after_count == before_count - 1 else "MISMATCH")

# 4. clear conversation
r = client.post(f"/api/conversations/{conv.id}/clear")
print("\n[4] POST clear conversation:", r.status_code, r.get_json())

# 5. GET messages again -> should be 0 (all before cutoff)
r = client.get(f"/api/conversations/{conv.id}/messages")
after_clear = len(r.get_json().get("messages", []))
print("[5] message count after clear:", after_clear,
      "OK" if after_clear == 0 else "MISMATCH")

# 6. delete-for-everyone on an old message (if any exist older than 10 min) -> expect 400
with app.app_context():
    from datetime import datetime, timedelta
    old_msg = Message.query.filter(
        Message.sent_at < datetime.utcnow() - timedelta(minutes=10),
        Message.is_deleted == False,
    ).first()

if old_msg:
    r = client.delete(f"/api/messages/{old_msg.id}")
    print("\n[6] DELETE old message (>10min):", r.status_code, r.get_json(),
          "OK (expected 400)" if r.status_code == 400 else "CHECK")
else:
    print("\n[6] SKIP - hakuna ujumbe wa zamani zaidi ya dakika 10 kujaribu naye")

print("\n[DONE]")
