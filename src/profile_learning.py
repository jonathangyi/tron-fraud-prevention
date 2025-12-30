def learn_from_transaction(transaction, profile):
    merchant = transaction["merchant"]
    device = transaction["device"]
    amount = transaction["amount"]
    country = transaction["country"]

    # Update merchant count
    profile["merchant_counts"][merchant] = (
        profile["merchant_counts"].get(merchant, 0) + 1
    )

    # Auto-authorize merchant after 3 approvals
    if (
        profile["merchant_counts"][merchant] >= 3
        and merchant not in profile["authorized_merchants"]
    ):
        profile["authorized_merchants"].append(merchant)

    # Update device trust
    profile["device_counts"][device] = (
        profile["device_counts"].get(device, 0) + 1
    )

    # Update rolling average spending (simple smoothing)
    profile["avg_amount"] = int((profile["avg_amount"] * 0.8) + (amount * 0.2))

    # Learn country only after approval
    if country not in profile["countries"]:
        profile["countries"].append(country)

    return profile
