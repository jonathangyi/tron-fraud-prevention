import pandas as pd
import time
from src.risk_engine import calculate_risk, get_risk_explanation
from src.decision_engine import decide_action
from src.profile_store import load_profile, save_profile, reset_profile
from src.profile_learning import learn_from_transaction
from src.transaction_history import save_transaction, get_performance_metrics, clear_history

def print_header():
    print("\n" + "=" * 80)
    print("💳 TRON FRAUD PREVENTION SYSTEM - BATCH PROCESSING")
    print("=" * 80)

def print_progress_bar(iteration, total, prefix='', suffix='', length=50):
    """Print a progress bar"""
    percent = (iteration / total)
    filled_length = int(length * percent)
    bar = '█' * filled_length + '-' * (length - filled_length)
    print(f'\r{prefix} |{bar}| {percent:.1%} {suffix}', end='', flush=True)
    if iteration == total:
        print()

def process_all_transactions(csv_file="data/transactions_large.csv", show_details=False):
    """Process all transactions in batch"""
    
    print_header()
    
    # Load data
    try:
        df = pd.read_csv(csv_file)
        print(f"\n📊 Loaded {len(df)} transactions from {csv_file}")
    except FileNotFoundError:
        print(f"\n❌ Error: Could not find {csv_file}")
        print("   Using enhanced dataset instead...")
        df = pd.read_csv("data/transactions_enhanced.csv")
        print(f"\n📊 Loaded {len(df)} transactions from data/transactions_enhanced.csv")
    
    # Show dataset stats
    print(f"\n📈 Dataset Statistics:")
    print(f"   • Total Transactions: {len(df)}")
    print(f"   • Legitimate: {(df['is_fraud'] == 0).sum()}")
    print(f"   • Fraudulent: {(df['is_fraud'] == 1).sum()}")
    print(f"   • Unknown: {df['is_fraud'].isna().sum()}")
    
    # Ask if should reset
    reset = input("\n🔄 Reset profile and history? (y/n): ").lower().strip()
    if reset == 'y':
        reset_profile()
        clear_history()
        print("✅ System reset complete")
    
    # Load profile
    profile = load_profile()
    
    print(f"\n🚀 Starting batch processing...")
    print(f"   • Show details: {'Yes' if show_details else 'No'}")
    print(f"   • Learning enabled: Yes")
    
    input("\n⏸️  Press Enter to start processing...")
    
    # Processing
    print("\n" + "=" * 80)
    print("PROCESSING TRANSACTIONS")
    print("=" * 80)
    
    start_time = time.time()
    results = []
    
    for idx, (_, row) in enumerate(df.iterrows()):
        transaction = row.to_dict()
        
        # Create user profile
        user_profile = {
            "countries": profile["countries"],
            "merchants": profile.get("authorized_merchants", []),
            "avg_amount": profile.get("avg_amount", 50),
            "active_hours": range(7, 23),
            "devices": list(profile.get("device_counts", {}).keys()) if profile.get("device_counts") else ["Mobile", "Laptop", "POS"]
        }
        
        # Calculate risk
        risk, risk_breakdown = calculate_risk(transaction, user_profile)
        decision = decide_action(risk)
        
        # Handle OTP automatically
        if decision == "OTP":
            if transaction.get('is_fraud') == 0:
                outcome = "APPROVED"
                otp_passed = True
            else:
                outcome = "BLOCKED"
                otp_passed = False
            otp_used = True
        elif decision == "APPROVE":
            outcome = "APPROVED"
            otp_used = False
            otp_passed = False
        else:
            outcome = "BLOCKED"
            otp_used = False
            otp_passed = False
        
        # Learn from approved
        if outcome == "APPROVED":
            profile = learn_from_transaction(transaction, profile)
            save_profile(profile)
        
        # Save to history
        save_transaction(transaction, risk, decision, otp_used, otp_passed)
        
        # Track results
        results.append({
            'tx_id': transaction['transaction_id'],
            'merchant': transaction['merchant'],
            'amount': transaction['amount'],
            'risk': risk,
            'decision': decision,
            'outcome': outcome,
            'is_fraud': transaction.get('is_fraud')
        })
        
        # Show progress
        if show_details and idx % 10 == 0:
            print(f"\n[{idx+1}/{len(df)}] {transaction['merchant']}: Risk={risk}, Decision={outcome}")
        else:
            print_progress_bar(idx + 1, len(df), prefix='Progress:', suffix='Complete')
    
    elapsed_time = time.time() - start_time
    
    # Results summary
    print("\n\n" + "=" * 80)
    print("PROCESSING COMPLETE")
    print("=" * 80)
    
    results_df = pd.DataFrame(results)
    
    print(f"\n⏱️  Processing Time: {elapsed_time:.2f} seconds")
    print(f"⚡ Processing Speed: {len(df)/elapsed_time:.1f} transactions/second")
    
    print(f"\n📊 Transaction Summary:")
    print(f"   • Total Processed: {len(results_df)}")
    print(f"   • Approved: {(results_df['outcome'] == 'APPROVED').sum()} ({(results_df['outcome'] == 'APPROVED').sum()/len(results_df)*100:.1f}%)")
    print(f"   • Blocked: {(results_df['outcome'] == 'BLOCKED').sum()} ({(results_df['outcome'] == 'BLOCKED').sum()/len(results_df)*100:.1f}%)")
    print(f"   • OTP Required: {(results_df['decision'] == 'OTP').sum()} ({(results_df['decision'] == 'OTP').sum()/len(results_df)*100:.1f}%)")
    print(f"   • Average Risk: {results_df['risk'].mean():.1f}")
    
    # Performance metrics
    print("\n" + "=" * 80)
    print("SYSTEM PERFORMANCE METRICS")
    print("=" * 80)
    
    metrics = get_performance_metrics()
    if metrics:
        print(f"\n✅ Accuracy:  {metrics['accuracy']:.1%}")
        print(f"🎯 Precision: {metrics['precision']:.1%}")
        print(f"🔍 Recall:    {metrics['recall']:.1%}")
        print(f"📈 F1 Score:  {metrics['f1_score']:.1%}")
        
        print(f"\n📊 Confusion Matrix:")
        print(f"   True Positives:  {metrics['true_positives']:3d} (Fraud correctly blocked)")
        print(f"   True Negatives:  {metrics['true_negatives']:3d} (Legit correctly approved)")
        print(f"   False Positives: {metrics['false_positives']:3d} (Legit incorrectly blocked)")
        print(f"   False Negatives: {metrics['false_negatives']:3d} (Fraud incorrectly approved)")
        
        print(f"\n🎯 Detection Results:")
        print(f"   • Fraud Caught: {metrics['fraud_caught']} out of {metrics['fraud_caught'] + metrics['fraud_missed']}")
        print(f"   • Fraud Missed: {metrics['fraud_missed']}")
        print(f"   • False Alarms: {metrics['legitimate_blocked']}")
        
        # Calculate business impact
        avg_fraud_amount = results_df[results_df['is_fraud'] == 1]['amount'].mean()
        fraud_prevented = metrics['fraud_caught'] * avg_fraud_amount
        
        print(f"\n💰 Business Impact:")
        print(f"   • Average Fraud Amount: ${avg_fraud_amount:.2f}")
        print(f"   • Total Fraud Prevented: ${fraud_prevented:,.2f}")
        print(f"   • Fraud Prevention Rate: {metrics['recall']:.1%}")
    else:
        print("\n⚠️  No labeled transactions to calculate metrics")
    
    # Profile growth
    print("\n" + "=" * 80)
    print("LEARNED PROFILE")
    print("=" * 80)
    
    print(f"\n📚 Profile Statistics:")
    print(f"   • Trusted Merchants: {len(profile.get('authorized_merchants', []))}")
    print(f"   • Known Countries: {len(profile.get('countries', []))}")
    print(f"   • Registered Devices: {len(profile.get('device_counts', {}))}")
    print(f"   • Average Spending: ${profile.get('avg_amount', 0)}")
    
    if profile.get('authorized_merchants'):
        print(f"\n✅ Trusted Merchants:")
        for merchant in profile['authorized_merchants'][:10]:
            count = profile.get('merchant_counts', {}).get(merchant, 0)
            print(f"   • {merchant} ({count} transactions)")
        if len(profile['authorized_merchants']) > 10:
            print(f"   ... and {len(profile['authorized_merchants']) - 10} more")
    
    # Risk analysis
    print("\n" + "=" * 80)
    print("RISK ANALYSIS")
    print("=" * 80)
    
    print(f"\n📊 Risk Score Distribution:")
    print(f"   • Low Risk (0-39):    {(results_df['risk'] < 40).sum()} transactions")
    print(f"   • Medium Risk (40-69): {((results_df['risk'] >= 40) & (results_df['risk'] < 70)).sum()} transactions")
    print(f"   • High Risk (70+):     {(results_df['risk'] >= 70).sum()} transactions")
    
    # Show top risky transactions
    print(f"\n🔴 Top 5 Highest Risk Transactions:")
    top_risky = results_df.nlargest(5, 'risk')
    for _, tx in top_risky.iterrows():
        fraud_label = "FRAUD" if tx['is_fraud'] == 1 else "LEGIT" if tx['is_fraud'] == 0 else "UNKNOWN"
        print(f"   • TX#{tx['tx_id']}: {tx['merchant']} - ${tx['amount']} - Risk: {tx['risk']} - {tx['outcome']} ({fraud_label})")
    
    # Learning effectiveness
    if len(results_df) >= 20:
        print("\n" + "=" * 80)
        print("LEARNING EFFECTIVENESS")
        print("=" * 80)
        
        first_20 = results_df.head(20)
        last_20 = results_df.tail(20)
        
        improvement = first_20['risk'].mean() - last_20['risk'].mean()
        
        print(f"\n📈 System Improvement:")
        print(f"   • First 20 transactions - Avg Risk: {first_20['risk'].mean():.1f}")
        print(f"   • Last 20 transactions  - Avg Risk: {last_20['risk'].mean():.1f}")
        print(f"   • Improvement: {improvement:+.1f} points")
        
        if improvement > 0:
            print(f"\n🎉 System learned successfully! Risk scores decreased by {improvement:.1f} points")
        elif improvement < -5:
            print(f"\n⚠️  Risk scores increased - encountering more fraud or unusual patterns")
        else:
            print(f"\n📊 Risk scores are stable")
    
    print("\n" + "=" * 80)
    print("🎉 BATCH PROCESSING COMPLETE!")
    print("=" * 80)
    print("\n💡 Next Steps:")
    print("   • Run 'streamlit run streamlit_app_batch.py' for visual analysis")
    print("   • Check 'storage/transaction_history.json' for detailed logs")
    print("   • Review 'storage/user_profile.json' to see learned profile")
    print("\n")

if __name__ == "__main__":
    import sys
    
    # Check for arguments
    csv_file = "data/transactions_large.csv"
    show_details = False
    
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    if len(sys.argv) > 2 and sys.argv[2] == "--details":
        show_details = True
    
    try:
        process_all_transactions(csv_file, show_details)
    except KeyboardInterrupt:
        print("\n\n⏹️  Processing interrupted by user.")
        print("Partial results have been saved.")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
