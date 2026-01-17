def decide_action(risk_score):
    """
    Make decision based on risk score with balanced thresholds
    
    Returns:
        - "APPROVE": Low risk, auto-approve
        - "OTP": Medium risk, require OTP verification
        - "BLOCK": High risk, block transaction
    """
    if risk_score < 40:  # Increased from 30 - more lenient for auto-approve
        return "APPROVE"
    elif risk_score < 70:  # Increased from 60 - medium risk for OTP
        return "OTP"
    else:
        return "BLOCK"
