import json
import os
import time

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