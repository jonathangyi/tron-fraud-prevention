import json
import os

PROFILE_PATH = "storage/user_profile.json"

def load_profile():
    if not os.path.exists(PROFILE_PATH):
        return {
            "authorized_merchants": [],
            "countries": ["TH"],
            "avg_amount": 50
        }

    with open(PROFILE_PATH, "r") as f:
        return json.load(f)

def save_profile(profile):
    with open(PROFILE_PATH, "w") as f:
        json.dump(profile, f, indent=2)
