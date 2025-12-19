import pandas as pd
from src.risk_engine import calculate_risk
from src.decision_engine import decide_action

# Simulated user profile
user_profile = {
    "countries": ["TH"],
    "merchants": ["Amazon", "Starbucks", "Netflix", "LocalMart"],
    "avg_amount": 20,
    "active_hours": range(7, 23)
}

df = pd.read_csv("data/transactions.csv")

for _, row in df.iterrows():
    transaction = row.to_dict()
    risk = calculate_risk(transaction, user_profile)
    decision = decide_action(risk)

    print(f"Transaction {transaction['transaction_id']} | "
          f"Merchant: {transaction['merchant']} | "
          f"Risk Score: {risk} | Decision: {decision}")
