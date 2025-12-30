import streamlit as st
import pandas as pd

from src.risk_engine import calculate_risk
from src.decision_engine import decide_action
from src.otp_service import send_otp
from src.profile_store import load_profile, save_profile
from src.profile_learning import learn_from_transaction

st.set_page_config(page_title="Tron Fraud Prevention", layout="centered")

st.title("💳 Tron – Self-Learning Fraud Prevention System")

# =====================
# LOAD DATA & PROFILE
# =====================
df = pd.read_csv("data/transactions.csv")
profile = load_profile()

user_profile = {
    "merchants": profile["authorized_merchants"],
    "countries": profile["countries"],
    "avg_amount": profile["avg_amount"],
    "active_hours": range(7, 23),
    "devices": list(profile["device_counts"].keys()) if profile["device_counts"] else ["Mobile", "Laptop", "POS"]
}

# =====================
# SIDEBAR – LEARNED PROFILE (READ ONLY)
# =====================
st.sidebar.header("📘 Learned User Profile")

st.sidebar.subheader("Trusted Merchants")
st.sidebar.write(profile["authorized_merchants"])

st.sidebar.subheader("Known Countries")
st.sidebar.write(profile["countries"])

st.sidebar.subheader("Average Spending")
st.sidebar.write(f"{profile['avg_amount']}")

st.sidebar.subheader("Known Devices")
st.sidebar.write(list(profile["device_counts"].keys()))

# =====================
# TRANSACTION SELECTION
# =====================
st.subheader("Simulated Incoming Transaction")

tx_id = st.selectbox(
    "Select Transaction ID",
    df["transaction_id"]
)

transaction = df[df["transaction_id"] == tx_id].iloc[0].to_dict()

st.write("### Transaction Details")
st.json(transaction)

# =====================
# FRAUD DECISION
# =====================
if st.button("Process Transaction"):
    risk = calculate_risk(transaction, user_profile)
    decision = decide_action(risk)

    st.write(f"### Risk Score: `{risk}`")

    # AUTO APPROVE
    if decision == "APPROVE":
        st.success("Transaction Approved ✅")
        profile = learn_from_transaction(transaction, profile)
        save_profile(profile)

    # OTP FLOW
    elif decision == "OTP":
        st.warning("OTP Verification Required ⚠️")
        otp = send_otp()
        user_otp = st.text_input("Enter OTP")

        if user_otp:
            if user_otp == str(otp):
                st.success("OTP Verified. Transaction Approved ✅")
                profile = learn_from_transaction(transaction, profile)
                save_profile(profile)
            else:
                st.error("Invalid OTP. Transaction Blocked ❌")

    # BLOCK
    else:
        st.error("Transaction Blocked ❌ (High Risk)")
