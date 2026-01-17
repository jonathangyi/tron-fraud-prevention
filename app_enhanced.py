import pandas as pd
from src.risk_engine import calculate_risk, get_risk_explanation
from src.decision_engine import decide_action
from src.otp_service import send_otp, verify_otp
from src.profile_store import load_profile, save_profile
from src.profile_learning import learn_from_transaction
from src.transaction_history import save_transaction, get_performance_metrics

# Load enhanced data
df = pd.read_csv("data/transactions_enhanced.csv")

# Load user profile
profile = load_profile()
user_profile = {
    "countries": profile["countries"],
    "merchants": profile["authorized_merchants"],
    "avg_amount": profile["avg_amount"],
    "active_hours": range(7, 23),
    "devices": list(profile["device_counts"].keys()) if profile["device_counts"] else ["Mobile", "Laptop", "POS"]
}

print("=" * 70)
print("💳 TRON FRAUD PREVENTION SYSTEM - Enhanced Edition")
print("=" * 70)
print(f"\n📊 Processing {len(df)} transactions...\n")

# Process all transactions
for idx, row in df.iterrows():
    transaction = row.to_dict()
    risk, risk_breakdown = calculate_risk(transaction, user_profile)
    decision = decide_action(risk)

    print("\n" + "-" * 70)
    print(f"Transaction #{transaction['transaction_id']} | {transaction['merchant']}")
    print("-" * 70)
    
    # Transaction details
    print(f"💰 Amount: ${transaction['amount']}")
    print(f"🌍 Country: {transaction['country']}")
    print(f"⏰ Time: {transaction['hour']}:00")
    print(f"📱 Device: {transaction['device']}")
    
    # Show fraud label if available
    if transaction.get('is_fraud') == 1:
        print(f"⚠️  KNOWN FRAUD: {transaction.get('fraud_type', 'Unknown')}")
    elif transaction.get('is_fraud') == 0:
        print(f"✅ LEGITIMATE TRANSACTION")
    
    # Risk score with color coding
    if risk < 30:
        risk_emoji = "🟢"
        risk_level = "LOW"
    elif risk < 60:
        risk_emoji = "🟡"
        risk_level = "MEDIUM"
    else:
        risk_emoji = "🔴"
        risk_level = "HIGH"
    
    print(f"\n{risk_emoji} Risk Score: {risk} ({risk_level})")
    
    # Risk breakdown
    print("\n📊 Risk Factor Breakdown:")
    for factor, score in risk_breakdown.items():
        if score != 0:
            print(f"   • {factor.replace('_', ' ').title()}: {score:+d}")
    
    # Risk explanation
    explanations = get_risk_explanation(risk_breakdown)
    if explanations:
        print("\n🔍 Risk Factors:")
        for exp in explanations:
            print(f"   {exp}")

    # Decision handling
    print(f"\n{'='*70}")
    
    if decision == "APPROVE":
        print("✅ Decision: APPROVED")
        profile = learn_from_transaction(transaction, profile)
        save_profile(profile)
        save_transaction(transaction, risk, decision)
        print("📚 Profile updated from this transaction")

    elif decision == "OTP":
        print("⚠️  Decision: OTP VERIFICATION REQUIRED")
        otp = send_otp()
        if verify_otp(otp):
            print("✅ OTP verified. Transaction APPROVED")
            profile = learn_from_transaction(transaction, profile)
            save_profile(profile)
            save_transaction(transaction, risk, decision, otp_used=True, otp_passed=True)
            print("📚 Profile updated from this transaction")
        else:
            print("❌ OTP failed. Transaction BLOCKED")
            save_transaction(transaction, risk, decision, otp_used=True, otp_passed=False)

    else:
        print("❌ Decision: BLOCKED (High Risk)")
        save_transaction(transaction, risk, decision)
    
    # Update profile for next iteration
    user_profile = {
        "countries": profile["countries"],
        "merchants": profile["authorized_merchants"],
        "avg_amount": profile["avg_amount"],
        "active_hours": range(7, 23),
        "devices": list(profile["device_counts"].keys()) if profile["device_counts"] else ["Mobile", "Laptop", "POS"]
    }

# Final summary
print("\n" + "=" * 70)
print("📊 SYSTEM PERFORMANCE SUMMARY")
print("=" * 70)

metrics = get_performance_metrics()
if metrics:
    print(f"\n✅ Accuracy: {metrics['accuracy']:.1%}")
    print(f"🎯 Precision: {metrics['precision']:.1%}")
    print(f"🔍 Recall: {metrics['recall']:.1%}")
    print(f"📈 F1 Score: {metrics['f1_score']:.1%}")
    print(f"\n📊 Results:")
    print(f"   • Fraud Caught: {metrics['fraud_caught']}")
    print(f"   • Fraud Missed: {metrics['fraud_missed']}")
    print(f"   • False Alarms: {metrics['legitimate_blocked']}")
    print(f"   • Total Transactions: {metrics['total_transactions']}")
else:
    print("\n⚠️  No labeled transactions to calculate metrics")

print(f"\n📚 Learned Profile:")
print(f"   • Trusted Merchants: {len(profile['authorized_merchants'])}")
print(f"   • Known Countries: {len(profile['countries'])}")
print(f"   • Average Amount: ${profile['avg_amount']}")
print(f"   • Registered Devices: {len(profile['device_counts'])}")

print("\n" + "=" * 70)
print("🎉 Processing complete! Use streamlit_app_enhanced.py for visual analysis")
print("=" * 70)
