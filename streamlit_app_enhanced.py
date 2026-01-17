import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

from src.risk_engine import calculate_risk, get_risk_explanation
from src.decision_engine import decide_action
from src.otp_service import send_otp
from src.profile_store import load_profile, save_profile, reset_profile
from src.profile_learning import learn_from_transaction
from src.transaction_history import (
    save_transaction, 
    load_history, 
    get_performance_metrics,
    clear_history
)

st.set_page_config(
    page_title="Tron Fraud Prevention", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .risk-high { color: #ff4b4b; font-weight: bold; }
    .risk-medium { color: #ffa500; font-weight: bold; }
    .risk-low { color: #00cc00; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.title("💳 Tron – Self-Learning Fraud Prevention System")
st.markdown("**Real-time fraud detection with adaptive behavioral profiling**")

# =====================
# LOAD DATA & PROFILE
# =====================
df = pd.read_csv("data/transactions_enhanced.csv")
profile = load_profile()

user_profile = {
    "merchants": profile["authorized_merchants"],
    "countries": profile["countries"],
    "avg_amount": profile["avg_amount"],
    "active_hours": range(7, 23),
    "devices": list(profile["device_counts"].keys()) if profile["device_counts"] else ["Mobile", "Laptop", "POS"]
}

# Load history
history = load_history()
metrics = get_performance_metrics()

# =====================
# SIDEBAR – PROFILE & CONTROLS
# =====================
st.sidebar.header("🎛️ System Controls")

if st.sidebar.button("🔄 Reset Profile", help="Reset to initial state"):
    reset_profile()
    st.rerun()

if st.sidebar.button("🗑️ Clear History", help="Clear transaction history"):
    clear_history()
    st.rerun()

st.sidebar.markdown("---")

st.sidebar.header("📘 Learned User Profile")

with st.sidebar.expander("✅ Trusted Merchants", expanded=False):
    if profile["authorized_merchants"]:
        for merchant in profile["authorized_merchants"]:
            count = profile["merchant_counts"].get(merchant, 0)
            st.write(f"• {merchant} ({count} transactions)")
    else:
        st.write("*No trusted merchants yet*")

with st.sidebar.expander("🌍 Known Countries", expanded=False):
    st.write(", ".join(profile["countries"]))

with st.sidebar.expander("💰 Average Spending", expanded=False):
    st.metric("Average Amount", f"${profile['avg_amount']}")
    st.caption(f"High risk threshold: ${int(profile['avg_amount'] * 2.5)}")

with st.sidebar.expander("📱 Known Devices", expanded=False):
    if profile["device_counts"]:
        for device, count in profile["device_counts"].items():
            st.write(f"• {device} ({count} uses)")
    else:
        st.write("*No devices registered*")

# =====================
# MAIN TABS
# =====================
tab1, tab2, tab3, tab4 = st.tabs([
    "🔍 Process Transaction", 
    "📊 Performance Metrics",
    "📜 Transaction History",
    "📈 Learning Progress"
])

# =====================
# TAB 1: PROCESS TRANSACTION
# =====================
with tab1:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Select Transaction to Process")
        
        # Transaction selection
        tx_id = st.selectbox(
            "Transaction ID",
            df["transaction_id"],
            format_func=lambda x: f"Transaction #{x}"
        )
        
        transaction = df[df["transaction_id"] == tx_id].iloc[0].to_dict()
        
        # Display transaction details
        st.markdown("### 📋 Transaction Details")
        
        detail_col1, detail_col2 = st.columns(2)
        with detail_col1:
            st.metric("Merchant", transaction["merchant"])
            st.metric("Amount", f"${transaction['amount']}")
            st.metric("Country", transaction["country"])
        
        with detail_col2:
            st.metric("Device", transaction["device"])
            st.metric("Time", f"{transaction['hour']}:00")
            st.metric("Platform", transaction["platform"])
        
        # Show fraud label if available
        if transaction.get("is_fraud") == 1:
            st.error(f"⚠️ **Known Fraud**: {transaction.get('fraud_type', 'Unknown')}")
        elif transaction.get("is_fraud") == 0:
            st.success("✅ **Legitimate Transaction**")
    
    with col2:
        st.subheader("Fraud Detection Analysis")
        
        # Process button
        if st.button("🚀 Process Transaction", type="primary", use_container_width=True):
            # Calculate risk
            risk, risk_breakdown = calculate_risk(transaction, user_profile)
            decision = decide_action(risk)
            
            # Store in session state for OTP flow
            st.session_state.current_risk = risk
            st.session_state.current_decision = decision
            st.session_state.current_breakdown = risk_breakdown
            st.session_state.current_transaction = transaction
            st.session_state.otp_generated = None
            st.session_state.transaction_processed = True
        
        # Display results if transaction was processed
        if st.session_state.get("transaction_processed"):
            risk = st.session_state.current_risk
            decision = st.session_state.current_decision
            breakdown = st.session_state.current_breakdown
            transaction = st.session_state.current_transaction
            
            # Risk score display with color coding
            if risk < 40:
                risk_class = "risk-low"
                risk_emoji = "🟢"
            elif risk < 70:
                risk_class = "risk-medium"
                risk_emoji = "🟡"
            else:
                risk_class = "risk-high"
                risk_emoji = "🔴"
            
            st.markdown(f"### {risk_emoji} Risk Score: <span class='{risk_class}'>{risk}</span>", 
                       unsafe_allow_html=True)
            
            # Risk breakdown visualization
            st.markdown("#### Risk Factor Breakdown")
            breakdown_df = pd.DataFrame([
                {"Factor": "Country", "Score": breakdown["country_risk"]},
                {"Factor": "Merchant", "Score": breakdown["merchant_risk"]},
                {"Factor": "Amount", "Score": breakdown["amount_risk"]},
                {"Factor": "Time", "Score": breakdown["time_risk"]},
                {"Factor": "Device", "Score": breakdown["device_risk"]}
            ])
            
            fig = px.bar(
                breakdown_df, 
                x="Factor", 
                y="Score",
                color="Score",
                color_continuous_scale=["green", "yellow", "red"],
                text="Score"
            )
            fig.update_layout(showlegend=False, height=300)
            st.plotly_chart(fig, use_container_width=True)
            
            # Risk explanations
            explanations = get_risk_explanation(breakdown)
            if explanations:
                st.markdown("#### Risk Factors Detected")
                for exp in explanations:
                    st.write(exp)
            
            st.markdown("---")
            
            # Decision display and handling
            if decision == "APPROVE":
                st.success("✅ **Decision: APPROVED**")
                st.info("Transaction is within normal behavior patterns.")
                
                if st.button("✓ Confirm & Learn", use_container_width=True):
                    profile = learn_from_transaction(transaction, profile)
                    save_profile(profile)
                    save_transaction(transaction, risk, decision)
                    st.success("Profile updated with this transaction!")
                    st.session_state.transaction_processed = False
                    st.rerun()
            
            elif decision == "OTP":
                st.warning("⚠️ **Decision: OTP VERIFICATION REQUIRED**")
                st.info("Transaction requires additional verification.")
                
                # Generate OTP if not already generated
                if st.session_state.get("otp_generated") is None:
                    otp = send_otp()
                    st.session_state.otp_generated = otp
                else:
                    otp = st.session_state.otp_generated
                
                st.code(f"Your OTP: {otp}")
                
                user_otp = st.text_input("Enter OTP to verify:", key="otp_input")
                
                col_otp1, col_otp2 = st.columns(2)
                with col_otp1:
                    if st.button("Verify OTP", use_container_width=True):
                        if user_otp == str(otp):
                            st.success("✅ OTP Verified! Transaction Approved")
                            profile = learn_from_transaction(transaction, profile)
                            save_profile(profile)
                            save_transaction(transaction, risk, decision, 
                                           otp_used=True, otp_passed=True)
                            st.session_state.transaction_processed = False
                            st.rerun()
                        else:
                            st.error("❌ Invalid OTP. Transaction Blocked")
                            save_transaction(transaction, risk, decision, 
                                           otp_used=True, otp_passed=False)
                            st.session_state.transaction_processed = False
                            st.rerun()
                
                with col_otp2:
                    if st.button("Cancel", use_container_width=True):
                        save_transaction(transaction, risk, decision, 
                                       otp_used=False, otp_passed=False)
                        st.session_state.transaction_processed = False
                        st.rerun()
            
            else:  # BLOCK
                st.error("❌ **Decision: BLOCKED**")
                st.warning("Transaction exceeds acceptable risk threshold.")
                
                if st.button("Confirm Block", use_container_width=True):
                    save_transaction(transaction, risk, decision)
                    st.session_state.transaction_processed = False
                    st.rerun()

# =====================
# TAB 2: PERFORMANCE METRICS
# =====================
with tab2:
    st.subheader("📊 System Performance Metrics")
    
    if metrics:
        # Key metrics at the top
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Accuracy",
                f"{metrics['accuracy']:.1%}",
                help="Percentage of correct predictions"
            )
        
        with col2:
            st.metric(
                "Precision",
                f"{metrics['precision']:.1%}",
                help="Of blocked transactions, % that were actually fraud"
            )
        
        with col3:
            st.metric(
                "Recall",
                f"{metrics['recall']:.1%}",
                help="Of all fraud, % that was caught"
            )
        
        with col4:
            st.metric(
                "F1 Score",
                f"{metrics['f1_score']:.1%}",
                help="Harmonic mean of precision and recall"
            )
        
        st.markdown("---")
        
        # Confusion matrix
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("#### Confusion Matrix")
            confusion_data = pd.DataFrame({
                'Predicted Legitimate': [metrics['true_negatives'], metrics['false_negatives']],
                'Predicted Fraud': [metrics['false_positives'], metrics['true_positives']]
            }, index=['Actually Legitimate', 'Actually Fraud'])
            
            st.dataframe(confusion_data, use_container_width=True)
            
            st.markdown(f"""
            **Results Summary:**
            - ✅ Fraud Caught: {metrics['fraud_caught']}
            - ⚠️ Fraud Missed: {metrics['fraud_missed']}
            - 🚫 False Alarms: {metrics['legitimate_blocked']}
            - Total Transactions: {metrics['total_transactions']}
            """)
        
        with col2:
            st.markdown("#### Performance Visualization")
            
            # Create gauge chart for accuracy
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=metrics['accuracy'] * 100,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Overall Accuracy"},
                delta={'reference': 80},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 50], 'color': "lightgray"},
                        {'range': [50, 80], 'color': "gray"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ))
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.info("📊 No metrics available yet. Process some transactions to see performance data!")

# =====================
# TAB 3: TRANSACTION HISTORY
# =====================
with tab3:
    st.subheader("📜 Transaction Processing History")
    
    if history:
        # Convert to DataFrame
        history_df = pd.DataFrame(history)
        
        # Format for display
        display_df = history_df[[
            "transaction_id", "merchant", "amount", "country", 
            "risk_score", "decision", "final_outcome", "is_fraud"
        ]].copy()
        
        # Add color coding
        def color_outcome(val):
            if val == "APPROVED":
                return "background-color: #d4edda"
            elif val == "BLOCKED":
                return "background-color: #f8d7da"
            else:
                return ""
        
        styled_df = display_df.style.applymap(
            color_outcome, 
            subset=["final_outcome"]
        )
        
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
        
        # Download button
        csv = history_df.to_csv(index=False)
        st.download_button(
            "📥 Download Full History (CSV)",
            csv,
            "transaction_history.csv",
            "text/csv",
            use_container_width=True
        )
    else:
        st.info("📜 No transaction history yet. Start processing transactions!")

# =====================
# TAB 4: LEARNING PROGRESS
# =====================
with tab4:
    st.subheader("📈 System Learning Progress")
    
    if history:
        history_df = pd.DataFrame(history)
        
        # Risk score over time
        st.markdown("#### Risk Scores Over Time")
        fig = px.line(
            history_df.reset_index(), 
            x='index', 
            y='risk_score',
            markers=True,
            labels={'index': 'Transaction Number', 'risk_score': 'Risk Score'}
        )
        fig.add_hline(y=30, line_dash="dash", line_color="green", 
                     annotation_text="Auto-Approve Threshold")
        fig.add_hline(y=60, line_dash="dash", line_color="red", 
                     annotation_text="Block Threshold")
        st.plotly_chart(fig, use_container_width=True)
        
        # Decision distribution
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Decision Distribution")
            decision_counts = history_df['final_outcome'].value_counts()
            fig = px.pie(
                values=decision_counts.values,
                names=decision_counts.index,
                color=decision_counts.index,
                color_discrete_map={
                    'APPROVED': '#00cc00',
                    'BLOCKED': '#ff4b4b',
                }
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### Merchant Trust Growth")
            merchant_df = pd.DataFrame([
                {"Merchant": m, "Count": c} 
                for m, c in profile["merchant_counts"].items()
            ]).sort_values("Count", ascending=False).head(10)
            
            if not merchant_df.empty:
                fig = px.bar(
                    merchant_df,
                    x="Merchant",
                    y="Count",
                    color="Count",
                    color_continuous_scale="Greens"
                )
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No merchant data yet")
        
        # Learning insights
        st.markdown("#### 🎓 Learning Insights")
        
        insights_col1, insights_col2, insights_col3 = st.columns(3)
        
        with insights_col1:
            st.metric(
                "Trusted Merchants",
                len(profile["authorized_merchants"]),
                help="Merchants with 3+ successful transactions"
            )
        
        with insights_col2:
            st.metric(
                "Known Countries",
                len(profile["countries"]),
                help="Countries seen in approved transactions"
            )
        
        with insights_col3:
            st.metric(
                "Registered Devices",
                len(profile["device_counts"]),
                help="Devices used in approved transactions"
            )
        
        # Average risk score trend
        if len(history_df) >= 5:
            recent_avg = history_df.tail(5)['risk_score'].mean()
            overall_avg = history_df['risk_score'].mean()
            improvement = overall_avg - recent_avg
            
            st.markdown("#### System Improvement")
            st.metric(
                "Recent Risk Score (last 5 transactions)",
                f"{recent_avg:.1f}",
                f"{-improvement:.1f} from overall average",
                delta_color="inverse"
            )
            
            if improvement > 0:
                st.success("🎉 System is learning! Average risk scores are decreasing.")
            elif improvement < 0:
                st.warning("⚠️ Recent transactions show higher risk. System may need adjustment.")
            else:
                st.info("Risk scores are stable.")
    
    else:
        st.info("📈 No learning data yet. Process transactions to see progress!")

# =====================
# FOOTER
# =====================
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: gray;'>
        <p>Tron Fraud Prevention System v2.0 | Built with ❤️ for the hackathon</p>
        <p>Features: Adaptive Learning • Real-time Risk Scoring • Performance Analytics</p>
    </div>
""", unsafe_allow_html=True)
