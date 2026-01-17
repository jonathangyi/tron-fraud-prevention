import json
import os

PROFILE_PATH = "storage/user_profile.json"

def load_profile():
    if not os.path.exists(PROFILE_PATH):
        default_profile = {
            "authorized_merchants": ["Amazon", "Starbucks", "Netflix"],  # Start with some common merchants
            "countries": ["TH"],
            "avg_amount": 200,  # Increased from 50 to be more realistic
            "merchant_counts": {
                "Amazon": 3,
                "Starbucks": 3,
                "Netflix": 3
            },
            "device_counts": {
                "Mobile": 5,
                "Laptop": 3,
                "POS": 2
            }
        }
        # Ensure storage directory exists
        os.makedirs(os.path.dirname(PROFILE_PATH), exist_ok=True)
        save_profile(default_profile)
        return default_profile

    with open(PROFILE_PATH, "r") as f:
        profile = json.load(f)
        
        # Ensure all required fields exist
        if "merchant_counts" not in profile:
            profile["merchant_counts"] = {}
        if "device_counts" not in profile:
            profile["device_counts"] = {}
        
        return profile

def save_profile(profile):
    os.makedirs(os.path.dirname(PROFILE_PATH), exist_ok=True)
    with open(PROFILE_PATH, "w") as f:
        json.dump(profile, f, indent=2)

def reset_profile():
    """Reset profile to default state with some pre-learned data"""
    default_profile = {
        "authorized_merchants": ["Amazon", "Starbucks", "Netflix"],
        "countries": ["TH"],
        "avg_amount": 200,
        "merchant_counts": {
            "Amazon": 3,
            "Starbucks": 3,
            "Netflix": 3
        },
        "device_counts": {
            "Mobile": 5,
            "Laptop": 3,
            "POS": 2
        }
    }
    save_profile(default_profile)
    return default_profile
