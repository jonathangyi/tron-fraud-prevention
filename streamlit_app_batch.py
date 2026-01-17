import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time

from src.risk_engine import calculate_risk, get_risk_explanation
from src.decision_engine import decide_action
from src.profile_store import load_profile, save_profile, reset_profile
from src.profile_learning import learn_from_transaction
from src.transaction_history import (
    save_transaction, 
    load_history, 
    get_performance_metrics,
    clear_history
)

st.set_page_config(
    page_title="Tron Fraud Prevention - Batch Processing", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .big-number {
        font-size: 48px;
        font-weight: bold;
        text-align: center;
    }
    .stProgress > div > div > div > div {
        background-color: #00cc00;
    }
    </style>
""", unsafe_allow_html=True)

st.title("💳 Tron – Batch Fraud Prevention System")
st.markdown("**Process all transactions at once with real-time adaptive learning**")

# =====================
# SIDEBAR
# =====================
st.sidebar.header("🎛️ System Controls")

# Dataset selection
dataset_option = st.sidebar.selectbox(
    "Select Dataset",
    ["Small (25 transactions)", "Medium (50 transactions)", "Large (150 transactions)"]
)

if dataset_option == "Small (25 transactions)":
    csv_file = "data/transactions_enhanced.csv"
elif dataset_option == "Medium (50 transactions)":
    csv_file = "data/transactions_enhanced.csv"  # Will use first 50
else:
    csv_file = "data/transactions_large.csv"

# Load data
try:
    df_all = pd.read_csv(csv_file)
    if dataset_option == "Medium (50 transactions)":
        df_all = df_all.head(50)
except:
    st.error(f"Could not load {csv_file}. Using enhanced dataset.")
    df_all = pd.read_csv("data/transactions_enhanced.csv")

st.sidebar.metric("Total Transactions", len(df_all))
st.sidebar.metric("Fraudulent", df_all['is_fraud'].sum())
st.sidebar.metric("Legitimate", len(df_all) - df_all['is_fraud'].sum())

st.sidebar.markdown("---")

if st.sidebar.button("🔄 Reset System", help="Clear profile and history"):
    reset_profile()
    clear_history()
    st.rerun()

st.sidebar.markdown("---")

# Load current state
profile = load_profile()
history = load_history()

st.sidebar.header("📊 Current Status")
st.sidebar.metric("Processed Transactions", len(history))
st.sidebar.metric("Trusted Merchants", len(profile.get("authorized_merchants", [])))
st.sidebar.metric("Known Devices", len(profile.get("device_counts", {})))

# =====================
# MAIN CONTENT
# =====================

tab1, tab2, tab3, tab4 = st.tabs([
    "🚀 Batch Processing",
    "📊 Performance Dashboard", 
    "📜 Transaction Details",
    "📈 Learning Analytics"
])

# =====================
# TAB 1: BATCH PROCESSING
# =====================
with tab1:
    st.header("Batch Transaction Processing")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### How It Works
        1. Click **"Process All Transactions"** below
        2. System processes each transaction in sequence
        3. Learns from approved transactions in real-time
        4. Displays results and metrics when complete
        
        **Note:** OTP challenges are automatically handled:
        - Legitimate transactions → OTP passes
        - Fraudulent transactions → OTP fails
        """)
    
    with col2:
        st.markdown("### Quick Stats")
        st.info(f"**{len(df_all)}** transactions ready to process")
        if len(history) > 0:
            st.warning(f"**{len(history)}** already processed")
        else:
            st.success("System is reset and ready!")
    
    st.markdown("---")
    
    # Processing controls
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("🚀 Process All Transactions", type="primary", use_container_width=True):
            st.session_state.processing_started = True
    
    with col2:
        show_details = st.checkbox("Show detailed progress", value=False)
    
    with col3:
        auto_learn = st.checkbox("Enable learning", value=True, help="Learn from approved transactions")
    
    # Batch Processing Logic
    if st.session_state.get('processing_started'):
        st.markdown("---")
        st.subheader("🔄 Processing Transactions...")
        
        # Create containers for live updates
        progress_bar = st.progress(0)
        status_text = st.empty()
        metrics_container = st.container()
        
        # Metrics tracking
        results = []
        start_time = time.time()
        
        # Load profile
        profile = load_profile()
        
        for idx, (_, row) in enumerate(df_all.iterrows()):
            transaction = row.to_dict()
            
            # Create user profile for risk calculation
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
            
            # Handle OTP decisions automatically
            if decision == "OTP":
                # Legitimate transactions pass OTP, fraud fails
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
            else:  # BLOCK
                outcome = "BLOCKED"
                otp_used = False
                otp_passed = False
            
            # Learn from approved transactions
            if outcome == "APPROVED" and auto_learn:
                profile = learn_from_transaction(transaction, profile)
                save_profile(profile)
            
            # Save to history
            save_transaction(transaction, risk, decision, otp_used, otp_passed)
            
            # Track results
            results.append({
                'transaction_id': transaction['transaction_id'],
                'merchant': transaction['merchant'],
                'amount': transaction['amount'],
                'risk': risk,
                'decision': decision,
                'outcome': outcome,
                'is_fraud': transaction.get('is_fraud'),
                'risk_breakdown': risk_breakdown
            })
            
            # Update progress
            progress = (idx + 1) / len(df_all)
            progress_bar.progress(progress)
            status_text.text(f"Processing transaction {idx + 1}/{len(df_all)}: {transaction['merchant']} (${transaction['amount']})")
            
            # Show detailed progress if enabled
            if show_details and idx % 10 == 0:
                with metrics_container:
                    temp_metrics = get_performance_metrics()
                    if temp_metrics:
                        col1, col2, col3, col4 = st.columns(4)
                        col1.metric("Accuracy", f"{temp_metrics['accuracy']:.1%}")
                        col2.metric("Fraud Caught", temp_metrics['fraud_caught'])
                        col3.metric("Fraud Missed", temp_metrics['fraud_missed'])
                        col4.metric("False Alarms", temp_metrics['legitimate_blocked'])
        
        # Processing complete
        elapsed_time = time.time() - start_time
        progress_bar.progress(100)
        status_text.text(f"✅ Processing complete! {len(df_all)} transactions in {elapsed_time:.2f} seconds")
        
        st.success(f"🎉 Successfully processed {len(df_all)} transactions in {elapsed_time:.2f} seconds!")
        
        # Show final results
        st.markdown("---")
        st.subheader("📊 Processing Results")
        
        results_df = pd.DataFrame(results)
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        total_approved = (results_df['outcome'] == 'APPROVED').sum()
        total_blocked = (results_df['outcome'] == 'BLOCKED').sum()
        total_otp = (results_df['decision'] == 'OTP').sum()
        avg_risk = results_df['risk'].mean()
        
        col1.metric("Approved", total_approved, f"{total_approved/len(results_df)*100:.1f}%")
        col2.metric("Blocked", total_blocked, f"{total_blocked/len(results_df)*100:.1f}%")
        col3.metric("OTP Required", total_otp, f"{total_otp/len(results_df)*100:.1f}%")
        col4.metric("Avg Risk Score", f"{avg_risk:.1f}")
        col5.metric("Processing Speed", f"{len(results_df)/elapsed_time:.1f} tx/sec")
        
        # Show performance metrics
        metrics = get_performance_metrics()
        if metrics:
            st.markdown("### 🎯 System Performance")
            
            col1, col2, col3, col4 = st.columns(4)
            
            col1.metric("Accuracy", f"{metrics['accuracy']:.1%}")
            col2.metric("Precision", f"{metrics['precision']:.1%}")
            col3.metric("Recall", f"{metrics['recall']:.1%}")
            col4.metric("F1 Score", f"{metrics['f1_score']:.1%}")
            
            st.markdown("---")
            
            col1, col2, col3 = st.columns(3)
            
            col1.metric("✅ Fraud Caught", metrics['fraud_caught'], 
                       f"out of {metrics['fraud_caught'] + metrics['fraud_missed']}")
            col2.metric("⚠️ Fraud Missed", metrics['fraud_missed'],
                       delta=f"-{metrics['fraud_missed']}", delta_color="inverse")
            col3.metric("🚫 False Alarms", metrics['legitimate_blocked'],
                       delta=f"-{metrics['legitimate_blocked']}", delta_color="inverse")
        
        st.session_state.processing_started = False
        
        # Rerun to update other tabs
        time.sleep(1)
        st.rerun()

# =====================
# TAB 2: PERFORMANCE DASHBOARD
# =====================
with tab2:
    st.header("📊 Performance Dashboard")
    
    metrics = get_performance_metrics()
    
    if metrics and len(history) > 0:
        # Top metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=metrics['accuracy'] * 100,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Accuracy"},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 60], 'color': "lightgray"},
                        {'range': [60, 80], 'color': "gray"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ))
            fig.update_layout(height=250)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=metrics['precision'] * 100,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Precision"},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "green"},
                    'steps': [
                        {'range': [0, 60], 'color': "lightgray"},
                        {'range': [60, 80], 'color': "gray"}
                    ]
                }
            ))
            fig.update_layout(height=250)
            st.plotly_chart(fig, use_container_width=True)
        
        with col3:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=metrics['recall'] * 100,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Recall"},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "orange"},
                    'steps': [
                        {'range': [0, 60], 'color': "lightgray"},
                        {'range': [60, 80], 'color': "gray"}
                    ]
                }
            ))
            fig.update_layout(height=250)
            st.plotly_chart(fig, use_container_width=True)
        
        with col4:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=metrics['f1_score'] * 100,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "F1 Score"},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "purple"},
                    'steps': [
                        {'range': [0, 60], 'color': "lightgray"},
                        {'range': [60, 80], 'color': "gray"}
                    ]
                }
            ))
            fig.update_layout(height=250)
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Confusion Matrix
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### Confusion Matrix")
            
            confusion_data = pd.DataFrame({
                'Predicted Legitimate': [metrics['true_negatives'], metrics['false_negatives']],
                'Predicted Fraud': [metrics['false_positives'], metrics['true_positives']]
            }, index=['Actually Legitimate', 'Actually Fraud'])
            
            st.dataframe(confusion_data, use_container_width=True)
            
            st.markdown(f"""
            **Results Summary:**
            - ✅ Correct Predictions: {metrics['true_positives'] + metrics['true_negatives']}
            - ❌ Incorrect Predictions: {metrics['false_positives'] + metrics['false_negatives']}
            - 🎯 Fraud Detection Rate: {metrics['recall']:.1%}
            - 🎯 Precision Rate: {metrics['precision']:.1%}
            """)
        
        with col2:
            st.markdown("### Performance Breakdown")
            
            breakdown_data = pd.DataFrame({
                'Metric': ['True Positive', 'True Negative', 'False Positive', 'False Negative'],
                'Count': [metrics['true_positives'], metrics['true_negatives'], 
                         metrics['false_positives'], metrics['false_negatives']],
                'Type': ['Correct', 'Correct', 'Error', 'Error']
            })
            
            fig = px.bar(breakdown_data, x='Metric', y='Count', color='Type',
                        color_discrete_map={'Correct': 'green', 'Error': 'red'})
            fig.update_layout(showlegend=True, height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        # Risk distribution
        st.markdown("---")
        st.markdown("### Risk Score Distribution")
        
        history_df = pd.DataFrame(history)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Risk by outcome
            fig = px.box(history_df, x='final_outcome', y='risk_score', 
                        color='final_outcome',
                        color_discrete_map={'APPROVED': 'green', 'BLOCKED': 'red'})
            fig.update_layout(title="Risk Scores by Outcome", height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Risk by fraud label
            labeled = history_df[history_df['is_fraud'].notna()]
            if len(labeled) > 0:
                labeled['fraud_label'] = labeled['is_fraud'].map({0: 'Legitimate', 1: 'Fraud'})
                fig = px.box(labeled, x='fraud_label', y='risk_score', 
                            color='fraud_label',
                            color_discrete_map={'Legitimate': 'blue', 'Fraud': 'orange'})
                fig.update_layout(title="Risk Scores: Fraud vs Legitimate", height=400)
                st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.info("📊 No data yet. Process transactions to see performance metrics!")

# =====================
# TAB 3: TRANSACTION DETAILS
# =====================
with tab3:
    st.header("📜 Transaction History")
    
    if len(history) > 0:
        history_df = pd.DataFrame(history)
        
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            outcome_filter = st.multiselect(
                "Filter by Outcome",
                options=history_df['final_outcome'].unique(),
                default=history_df['final_outcome'].unique()
            )
        
        with col2:
            if 'is_fraud' in history_df.columns:
                fraud_filter = st.multiselect(
                    "Filter by Type",
                    options=['Legitimate', 'Fraud', 'Unknown'],
                    default=['Legitimate', 'Fraud', 'Unknown']
                )
        
        with col3:
            risk_range = st.slider(
                "Risk Score Range",
                0, 100, (0, 100)
            )
        
        # Apply filters
        filtered_df = history_df[history_df['final_outcome'].isin(outcome_filter)]
        filtered_df = filtered_df[(filtered_df['risk_score'] >= risk_range[0]) & 
                                 (filtered_df['risk_score'] <= risk_range[1])]
        
        # Display table
        display_df = filtered_df[[
            "transaction_id", "merchant", "amount", "country", 
            "risk_score", "decision", "final_outcome", "is_fraud"
        ]].copy()
        
        display_df['is_fraud'] = display_df['is_fraud'].map({0: 'Legit', 1: 'Fraud', None: 'Unknown'})
        
        st.dataframe(display_df, use_container_width=True, hide_index=True, height=400)
        
        # Summary stats
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        
        col1.metric("Total Shown", len(filtered_df))
        col2.metric("Approved", (filtered_df['final_outcome'] == 'APPROVED').sum())
        col3.metric("Blocked", (filtered_df['final_outcome'] == 'BLOCKED').sum())
        col4.metric("Avg Risk", f"{filtered_df['risk_score'].mean():.1f}")
        
        # Download button
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            "📥 Download Filtered Data (CSV)",
            csv,
            "filtered_transactions.csv",
            "text/csv",
            use_container_width=True
        )
    
    else:
        st.info("📜 No transaction history yet. Process transactions first!")

# =====================
# TAB 4: LEARNING ANALYTICS
# =====================
with tab4:
    st.header("📈 Learning Analytics")
    
    if len(history) > 0:
        history_df = pd.DataFrame(history)
        
        # Risk trend over time
        st.markdown("### Risk Score Trend Over Time")
        
        history_df['transaction_number'] = range(1, len(history_df) + 1)
        
        fig = px.line(history_df, x='transaction_number', y='risk_score',
                     title="How Risk Scores Change as System Learns")
        fig.add_hline(y=40, line_dash="dash", line_color="green", 
                     annotation_text="Auto-Approve Threshold (40)")
        fig.add_hline(y=70, line_dash="dash", line_color="red", 
                     annotation_text="Block Threshold (70)")
        
        # Add rolling average
        history_df['risk_rolling'] = history_df['risk_score'].rolling(window=10, min_periods=1).mean()
        fig.add_trace(go.Scatter(x=history_df['transaction_number'], 
                                y=history_df['risk_rolling'],
                                name='Rolling Average (10 tx)',
                                line=dict(color='orange', width=3)))
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Decision distribution over time
        st.markdown("---")
        st.markdown("### Decision Distribution Evolution")
        
        # Split into chunks
        chunk_size = max(10, len(history_df) // 5)
        chunks = [history_df[i:i+chunk_size] for i in range(0, len(history_df), chunk_size)]
        
        chunk_stats = []
        for i, chunk in enumerate(chunks):
            chunk_stats.append({
                'Chunk': f"{i*chunk_size+1}-{min((i+1)*chunk_size, len(history_df))}",
                'Approved': (chunk['final_outcome'] == 'APPROVED').sum(),
                'Blocked': (chunk['final_outcome'] == 'BLOCKED').sum()
            })
        
        chunk_df = pd.DataFrame(chunk_stats)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Approved', x=chunk_df['Chunk'], y=chunk_df['Approved'], 
                            marker_color='green'))
        fig.add_trace(go.Bar(name='Blocked', x=chunk_df['Chunk'], y=chunk_df['Blocked'],
                            marker_color='red'))
        fig.update_layout(barmode='stack', title="Decisions Over Time (by batch)")
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Profile growth
        st.markdown("---")
        st.markdown("### Profile Growth")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Trusted Merchants",
                len(profile.get("authorized_merchants", [])),
                help="Merchants with 3+ successful transactions"
            )
            if profile.get("authorized_merchants"):
                with st.expander("View Trusted Merchants"):
                    for merchant in profile["authorized_merchants"]:
                        count = profile.get("merchant_counts", {}).get(merchant, 0)
                        st.write(f"• {merchant} ({count} transactions)")
        
        with col2:
            st.metric(
                "Known Countries",
                len(profile.get("countries", [])),
                help="Countries seen in approved transactions"
            )
            if profile.get("countries"):
                with st.expander("View Countries"):
                    st.write(", ".join(profile["countries"]))
        
        with col3:
            st.metric(
                "Registered Devices",
                len(profile.get("device_counts", {})),
                help="Devices used in approved transactions"
            )
            if profile.get("device_counts"):
                with st.expander("View Devices"):
                    for device, count in profile["device_counts"].items():
                        st.write(f"• {device} ({count} uses)")
        
        # Learning effectiveness
        if len(history_df) >= 20:
            st.markdown("---")
            st.markdown("### Learning Effectiveness")
            
            first_20 = history_df.head(20)
            last_20 = history_df.tail(20)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**First 20 Transactions**")
                st.metric("Avg Risk Score", f"{first_20['risk_score'].mean():.1f}")
                st.metric("Auto-Approved", (first_20['risk_score'] < 30).sum())
            
            with col2:
                st.markdown("**Last 20 Transactions**")
                improvement = first_20['risk_score'].mean() - last_20['risk_score'].mean()
                st.metric("Avg Risk Score", f"{last_20['risk_score'].mean():.1f}",
                         delta=f"{-improvement:.1f}", delta_color="inverse")
                st.metric("Auto-Approved", (last_20['risk_score'] < 30).sum(),
                         delta=f"+{(last_20['risk_score'] < 30).sum() - (first_20['risk_score'] < 30).sum()}")
            
            if improvement > 0:
                st.success(f"🎉 System improved! Risk scores decreased by {improvement:.1f} points on average")
            elif improvement < -5:
                st.warning("⚠️ Risk scores increasing - system may be encountering more fraud")
            else:
                st.info("📊 Risk scores are stable")
    
    else:
        st.info("📈 No data yet. Process transactions to see learning analytics!")

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: gray;'>
        <p>Tron Fraud Prevention System - Batch Processing Edition</p>
        <p>Processes hundreds of transactions with real-time adaptive learning</p>
    </div>
""", unsafe_allow_html=True)
