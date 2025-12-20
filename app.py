import pandas as pd
from src.risk_engine import calculate_risk
from src.decision_engine import decide_action
from src.otp_service import send_otp, verify_otp

# Simulated user profile
user_profile = {
    "countries": ["TH"],
    "merchants": ["Amazon", "Starbucks", "Netflix", "LocalMart"],
    "avg_amount": 30,
    "active_hours": range(7, 23),
    "devices": ["Mobile", "Laptop", "POS"]
}


df = pd.read_csv("data/transactions.csv")


for _, row in df.iterrows():
    transaction = row.to_dict()
    risk = calculate_risk(transaction, user_profile)
    decision = decide_action(risk)

    print("\n" + "-" * 60)
    print(f"Transaction ID: {transaction['transaction_id']}")
    print(f"Merchant: {transaction['merchant']}")
    print(f"Country: {transaction['country']}")
    print(f"Amount: {transaction['amount']}")
    print(f"Risk Score: {risk}")

    if decision == "APPROVE":
        print("Decision: APPROVED ✅")

    elif decision == "OTP":
        print("Decision: OTP REQUIRED ⚠️")
        otp = send_otp()
        if verify_otp(otp):
            print("OTP verified. Transaction APPROVED ✅")
        else:
            print("OTP failed. Transaction BLOCKED ❌")

    else:
        print("Decision: BLOCKED ❌ (High Risk)")
