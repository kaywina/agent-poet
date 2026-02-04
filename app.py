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

def generate_poem_stub(attempt):
    # Deterministic fake outputs for testing
    samples = [
        "This is a quiet poem about light and morning.",
        "Visit http://example.com for more poetry.",  # should fail
        "Numbers everywhere 1234567890",              # should fail
        "A small poem rests here, finished and gentle."
    ]
    return samples[attempt % len(samples)]

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

def publish_today():
    date_str = today_date_str()
    state = load_or_init_state(date_str)

    # Load config locally
    with open(os.path.join(base, "config.json")) as f:
        config = json.load(f)

    if state.get("status") != "READY":
        print("Nothing to publish. Status:", state.get("status"))
        return

    draft_path = os.path.join(base, "drafts", date_str + ".txt")
    if not os.path.exists(draft_path):
        print("Draft missing, cannot publish.")
        return

    with open(draft_path) as f:
        poem = f.read()

    # Write to site repo
    site_repo = os.path.abspath(os.path.join(base, config["site_repo_path"]))
    posts_dir = os.path.join(site_repo, config["posts_dir"])
    if not os.path.exists(posts_dir):
        os.makedirs(posts_dir)

    out_path = os.path.join(posts_dir, date_str + ".md")
    with open(out_path, "w") as f:
        f.write(poem)

    state["status"] = "PUBLISHED"
    with open(state_path_for(date_str), "w") as f:
        json.dump(state, f, indent=2, sort_keys=True)

    print("Published to:", out_path)

date_str = today_date_str()
state = load_or_init_state(date_str)

# Test output with print statements
# print("Today's state file: %s" % state_path_for(date_str))
# print("Status: %s" % state.get("status"))
# print("Attempts: %s" % state.get("attempts"))
# ok, reason = safety_check("This is a test poem.")
# print("Safety check test: %s (%s)" % (ok, reason))

if state["status"] == "PENDING":
    print("Attempting generation...")

    poem = generate_poem_stub(state["attempts"])
    ok, reason = safety_check(poem)

    print("Generated poem:", poem)
    print("Safety:", ok, reason)

    if ok:
        # Save poem draft and mark READY
        draft_path = os.path.join(base, "drafts", date_str + ".txt")
        with open(draft_path, "w") as f:
            f.write(poem)

        state["status"] = "READY"
        state["attempts"] = state.get("attempts", 0) + 1
        state["ready_path"] = draft_path
        print("Saved READY draft:", draft_path)

    else:
        # Count a failed attempt
        state["attempts"] = state.get("attempts", 0) + 1

        if state["attempts"] >= 3:
            state["status"] = "FAILED"
            state["error"] = "Failed safety checks 3 times. Shutting down until tomorrow."
            print(state["error"])
        else:
            print("Not ready yet. Will try again next run.")

    # Persist state
    with open(state_path_for(date_str), "w") as f:
        json.dump(state, f, indent=2, sort_keys=True)

else:
    print("No generation needed. Status:", state["status"])

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "publish":
        publish_today()
    else:
        # existing generation logic runs here
        pass
