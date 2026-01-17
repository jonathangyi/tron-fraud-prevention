"""
Demo Automation Script
Perfect for presentations - shows the system in action with commentary
"""

import pandas as pd
import time
from src.risk_engine import calculate_risk, get_risk_explanation
from src.decision_engine import decide_action
from src.profile_store import reset_profile, load_profile, save_profile
from src.profile_learning import learn_from_transaction

def slow_print(text, delay=0.03):
    """Print text with a typewriter effect"""
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()

def demo_transaction(transaction, profile, step_num, total_steps):
    """Process and display a single transaction with commentary"""
    
    user_profile = {
        "countries": profile["countries"],
        "merchants": profile["authorized_merchants"],
        "avg_amount": profile["avg_amount"],
        "active_hours": range(7, 23),
        "devices": list(profile["device_counts"].keys()) if profile["device_counts"] else ["Mobile", "Laptop", "POS"]
    }
    
    print("\n" + "=" * 80)
    slow_print(f"📍 Transaction {step_num}/{total_steps}: {transaction['merchant']}", delay=0.02)
    print("=" * 80)
    
    # Show transaction details
    print(f"\n💳 Transaction Details:")
    print(f"   • Amount: ${transaction['amount']}")
    print(f"   • Country: {transaction['country']}")
    print(f"   • Device: {transaction['device']}")
    print(f"   • Time: {transaction['hour']}:00")
    
    # Show fraud label if it's a fraud demo
    if transaction.get('is_fraud') == 1:
        print(f"   🚨 [System doesn't know yet: This IS fraud - {transaction.get('fraud_type')}]")
    elif transaction.get('is_fraud') == 0:
        print(f"   ✅ [System doesn't know yet: This is legitimate]")
    
    time.sleep(0.5)
    
    # Calculate risk
    print(f"\n🔍 Analyzing...")
    time.sleep(0.3)
    
    risk, risk_breakdown = calculate_risk(transaction, user_profile)
    
    # Show risk score
    if risk < 30:
        risk_emoji = "🟢"
        risk_level = "LOW RISK"
    elif risk < 60:
        risk_emoji = "🟡"
        risk_level = "MEDIUM RISK"
    else:
        risk_emoji = "🔴"
        risk_level = "HIGH RISK"
    
    print(f"\n{risk_emoji} Risk Score: {risk}/100 ({risk_level})")
    
    # Show risk breakdown
    explanations = get_risk_explanation(risk_breakdown)
    if explanations:
        print(f"\n📊 Risk Factors:")
        for exp in explanations:
            print(f"   {exp}")
            time.sleep(0.2)
    
    time.sleep(0.3)
    
    # Make decision
    decision = decide_action(risk)
    
    print(f"\n⚖️  Decision: ", end='')
    time.sleep(0.3)
    
    if decision == "APPROVE":
        slow_print("✅ APPROVED", delay=0.05)
        print("   Transaction is within normal behavior patterns.")
        profile = learn_from_transaction(transaction, profile)
        save_profile(profile)
        print("   📚 System learned from this approval")
        outcome = "APPROVED"
        
    elif decision == "OTP":
        slow_print("⚠️  OTP REQUIRED", delay=0.05)
        print("   Additional verification needed for medium-risk transaction.")
        
        # Simulate OTP for demo
        if transaction.get('is_fraud') == 0:
            print("   🔐 [User would enter correct OTP]")
            print("   ✅ OTP Verified - Transaction Approved")
            profile = learn_from_transaction(transaction, profile)
            save_profile(profile)
            print("   📚 System learned from this approval")
            outcome = "APPROVED"
        else:
            print("   🔐 [Fraudster fails OTP or times out]")
            print("   ❌ OTP Failed - Transaction Blocked")
            outcome = "BLOCKED"
        
    else:
        slow_print("❌ BLOCKED", delay=0.05)
        print("   Transaction exceeds acceptable risk threshold.")
        outcome = "BLOCKED"
    
    time.sleep(0.5)
    
    # Show outcome vs reality
    if transaction.get('is_fraud') is not None:
        is_correct = (transaction['is_fraud'] == 1 and outcome == "BLOCKED") or \
                    (transaction['is_fraud'] == 0 and outcome == "APPROVED")
        
        if is_correct:
            print(f"\n   ✅ CORRECT: ", end='')
            if transaction['is_fraud'] == 1:
                print("Successfully blocked fraud!")
            else:
                print("Legitimate transaction approved!")
        else:
            print(f"\n   ❌ INCORRECT: ", end='')
            if transaction['is_fraud'] == 1:
                print("Fraud slipped through (False Negative)")
            else:
                print("Legitimate transaction blocked (False Positive)")
    
    # Show profile growth
    if len(profile['authorized_merchants']) > 0 or len(profile['device_counts']) > 0:
        print(f"\n📚 Current Profile:")
        print(f"   • Trusted Merchants: {len(profile['authorized_merchants'])}")
        print(f"   • Known Devices: {len(profile['device_counts'])}")
        print(f"   • Avg Spending: ${profile['avg_amount']}")
    
    return profile, outcome

def run_demo():
    """Run the full demo"""
    
    # Header
    print("\n" + "=" * 80)
    slow_print("💳 TRON FRAUD PREVENTION SYSTEM - LIVE DEMO", delay=0.04)
    print("=" * 80)
    slow_print("\n🎯 Demonstrating adaptive learning and fraud detection capabilities\n", delay=0.02)
    
    time.sleep(1)
    
    # Load data
    df = pd.read_csv("data/transactions_enhanced.csv")
    
    # Reset to clean state
    print("🔄 Initializing system with clean profile...")
    profile = reset_profile()
    time.sleep(0.5)
    print("✅ System ready\n")
    
    # Select interesting transactions for demo
    # Mix of legitimate and fraud, showing system learning
    demo_tx_ids = [1, 2, 3, 7, 9, 10, 15, 19, 20, 22]  # Curated sequence
    demo_transactions = df[df['transaction_id'].isin(demo_tx_ids)].sort_values('transaction_id')
    
    total = len(demo_transactions)
    results = []
    
    # Process each transaction
    for idx, (_, row) in enumerate(demo_transactions.iterrows(), 1):
        transaction = row.to_dict()
        profile, outcome = demo_transaction(transaction, profile, idx, total)
        results.append({
            'tx_id': transaction['transaction_id'],
            'is_fraud': transaction.get('is_fraud'),
            'outcome': outcome
        })
        
        if idx < total:
            input("\n⏸️  Press Enter to continue to next transaction...")
    
    # Final summary
    print("\n\n" + "=" * 80)
    slow_print("📊 DEMO SUMMARY", delay=0.04)
    print("=" * 80)
    
    # Calculate demo metrics
    results_df = pd.DataFrame(results)
    results_df = results_df[results_df['is_fraud'].notna()]
    
    if len(results_df) > 0:
        correct = sum((results_df['is_fraud'] == 1) & (results_df['outcome'] == 'BLOCKED')) + \
                 sum((results_df['is_fraud'] == 0) & (results_df['outcome'] == 'APPROVED'))
        
        accuracy = correct / len(results_df)
        
        fraud_caught = sum((results_df['is_fraud'] == 1) & (results_df['outcome'] == 'BLOCKED'))
        fraud_missed = sum((results_df['is_fraud'] == 1) & (results_df['outcome'] == 'APPROVED'))
        false_alarms = sum((results_df['is_fraud'] == 0) & (results_df['outcome'] == 'BLOCKED'))
        
        print(f"\n✅ Accuracy: {accuracy:.1%}")
        print(f"🎯 Fraud Caught: {fraud_caught}/{sum(results_df['is_fraud'] == 1)}")
        print(f"⚠️  Fraud Missed: {fraud_missed}")
        print(f"🚫 False Alarms: {false_alarms}")
    
    print(f"\n📚 Final Learned Profile:")
    print(f"   • Trusted Merchants: {len(profile['authorized_merchants'])}")
    if profile['authorized_merchants']:
        print(f"     → {', '.join(profile['authorized_merchants'][:5])}")
    print(f"   • Known Countries: {', '.join(profile['countries'])}")
    print(f"   • Registered Devices: {len(profile['device_counts'])}")
    print(f"   • Average Spending: ${profile['avg_amount']}")
    
    print("\n" + "=" * 80)
    slow_print("✨ Key Advantages of Adaptive Learning:", delay=0.02)
    print("=" * 80)
    print("1. ✅ Reduces false positives as system learns user behavior")
    print("2. 🎯 Improves fraud detection through pattern recognition")
    print("3. 🚀 Better user experience - fewer unnecessary blocks")
    print("4. 📈 Continuously improves without manual rule updates")
    print("5. 🔒 Maintains security while maximizing convenience")
    
    print("\n" + "=" * 80)
    slow_print("🎉 Demo Complete! Thank you for watching!", delay=0.03)
    print("=" * 80)
    print("\n💡 Next: Try 'streamlit run streamlit_app_enhanced.py' for interactive demo")
    print("💡 Or run 'python compare_systems.py' to see before/after metrics\n")

if __name__ == "__main__":
    try:
        run_demo()
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted. Thank you!")
