def decide_action(risk_score):
    if risk_score < 30:
        return "APPROVE"
    elif risk_score < 60:
        return "REQUIRE OTP"
    else:
        return "BLOCK"
