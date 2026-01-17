def calculate_risk(transaction, user_profile):
    """Calculate risk score with detailed breakdown"""
    risk_breakdown = {
        "country_risk": 0,
        "merchant_risk": 0,
        "amount_risk": 0,
        "time_risk": 0,
        "device_risk": 0
    }
    
    # Country check - reduced from 40 to 25
    if transaction["country"] not in user_profile["countries"]:
        risk_breakdown["country_risk"] = 25
    
    # Merchant check - reduced penalties, increased bonus
    if transaction["merchant"] not in user_profile["merchants"]:
        risk_breakdown["merchant_risk"] = 15  # Reduced from 25
    else:
        risk_breakdown["merchant_risk"] = -20  # Increased from -15 (trusted merchant bonus)
    
    # Amount check - more lenient threshold
    if transaction["amount"] > user_profile["avg_amount"] * 5:  # Changed from 2.5x to 5x
        risk_breakdown["amount_risk"] = 15  # Reduced from 20
    
    # Time check - reduced penalty
    if transaction["hour"] not in user_profile["active_hours"]:
        risk_breakdown["time_risk"] = 5  # Reduced from 10
    
    # Device check - reduced penalty
    if transaction["device"] not in user_profile["devices"]:
        risk_breakdown["device_risk"] = 10  # Reduced from 15
    
    total_risk = sum(risk_breakdown.values())
    
    return max(total_risk, 0), risk_breakdown


def get_risk_explanation(risk_breakdown):
    """Generate human-readable risk explanation"""
    explanations = []
    
    if risk_breakdown["country_risk"] > 0:
        explanations.append(f"🌍 Unfamiliar country (+{risk_breakdown['country_risk']})")
    
    if risk_breakdown["merchant_risk"] > 0:
        explanations.append(f"🏪 Unknown merchant (+{risk_breakdown['merchant_risk']})")
    elif risk_breakdown["merchant_risk"] < 0:
        explanations.append(f"✅ Trusted merchant ({risk_breakdown['merchant_risk']})")
    
    if risk_breakdown["amount_risk"] > 0:
        explanations.append(f"💰 Very high amount (+{risk_breakdown['amount_risk']})")
    
    if risk_breakdown["time_risk"] > 0:
        explanations.append(f"⏰ Unusual time (+{risk_breakdown['time_risk']})")
    
    if risk_breakdown["device_risk"] > 0:
        explanations.append(f"📱 New device (+{risk_breakdown['device_risk']})")
    
    return explanations
