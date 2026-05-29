import json, secrets
from datetime import datetime, timezone

stamp = {
    "push_id": datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S") + "-" + secrets.token_hex(3),
    "pushed_at_local": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
}

with open("VERSION.json", "w", encoding="utf-8") as f:
    json.dump(stamp, f, indent=2, ensure_ascii=False)

print("PUSH_ID:", stamp["push_id"])