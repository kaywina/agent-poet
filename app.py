import json
import os
import time

def safety_check(text):
    t = text.lower()

    # Reject links and obvious contact info
    if "http://" in t or "https://" in t or "www." in t:
        return False, "contains_url"
    if "@" in t:
        return False, "contains_at_symbol"
    digits = sum(c.isdigit() for c in t)
    if digits >= 8:
        return False, "too_many_digits"

    # Basic denylist (MVP, expandable later)
    deny = [
        "kill yourself",
        "kys",
        "nazi"
    ]
    for phrase in deny:
        if phrase in t:
            return False, "denylist:" + phrase

    # Length guardrails (kernel says under 120 words)
    words = [w for w in text.strip().split() if w]
    if len(words) == 0:
        return False, "empty"
    if len(words) > 120:
        return False, "too_long"

    return True, "ok"

base = os.path.dirname(os.path.abspath(__file__))

def today_date_str():
    return time.strftime("%Y-%m-%d")

def state_path_for(date_str):
    return os.path.join(base, "state", date_str + ".json")

def load_or_init_state(date_str):
    path = state_path_for(date_str)
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    state = {
        "date": date_str,
        "status": "PENDING",
        "attempts": 0
    }
    with open(path, "w") as f:
        json.dump(state, f, indent=2, sort_keys=True)
    return state

date_str = today_date_str()
state = load_or_init_state(date_str)

print("Today's state file: %s" % state_path_for(date_str))
print("Status: %s" % state.get("status"))
print("Attempts: %s" % state.get("attempts"))

ok, reason = safety_check("This is a test poem.")
print("Safety check test: %s (%s)" % (ok, reason))