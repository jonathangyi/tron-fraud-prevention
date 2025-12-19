def calculate_risk(transaction, user_profile):
    risk = 0

    # Unusual country
    if transaction["country"] not in user_profile["countries"]:
        risk += 40

    # Unusual merchant
    if transaction["merchant"] not in user_profile["merchants"]:
        risk += 30

    # High amount
    if transaction["amount"] > user_profile["avg_amount"] * 3:
        risk += 20

    # Unusual time
    if transaction["hour"] not in user_profile["active_hours"]:
        risk += 10

    return risk
