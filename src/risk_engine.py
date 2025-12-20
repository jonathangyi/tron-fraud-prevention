def calculate_risk(transaction, user_profile):
    risk = 0

    if transaction["country"] not in user_profile["countries"]:
        risk += 40

    if transaction["merchant"] not in user_profile["merchants"]:
        risk += 25
    else:
        risk -= 15  # trusted merchant bonus

    if transaction["amount"] > user_profile["avg_amount"] * 2.5:
        risk += 20

    if transaction["hour"] not in user_profile["active_hours"]:
        risk += 10

    if transaction["device"] not in user_profile["devices"]:
        risk += 15

    return max(risk, 0)
