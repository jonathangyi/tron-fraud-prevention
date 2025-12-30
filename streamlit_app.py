import streamlit as st # type: ignore
from src.risk_engine import calculate_risk
from src.decision_engine import decide_action
from src.otp_service import send_otp
from src.profile_store import load_profile, save_profile

st.set_page_config(page_title="Tron Fraud Prevention", layout="centered")

st.title("💳 Tron – Real-Time Fraud Prevention")

profile = load_profile()

st.sidebar.header("User Profile")

authorized_merchants = st.sidebar.multiselect(
    "Authorized Merchants",
    ["Amazon", "Starbucks", "Netflix", "LocalMart", "Apple", "Google"],
    default=profile["authorized_merchants"]
)

countries = st.sidebar.multiselect(
    "Allowed Countries",
    ["TH", "US", "SG", "JP", "PH"],
    default=profile["countries"]
)

avg_amount = st.sidebar.slider(
    "Average Spending Amount",
    10, 500, profile["avg_amount"]
)

if st.sidebar.button("Save Profile"):
    save_profile({
        "authorized_merchants": authorized_merchants,
        "countries": countries,
        "avg_amount": avg_amount
    })
    st.sidebar.success("Profile saved")

user_profile = {
    "merchants": authorized_merchants,
    "countries": countries,
    "avg_amount": avg_amount,
    "active_hours": range(7, 23),
    "devices": ["Mobile", "Laptop", "POS"]
}

# =====================
# TRANSACTION INPUT
# =====================
st.subheader("New Transaction")

merchant = st.text_input("Merchant Name")
amount = st.number_input("Amount", min_value=1)
country = st.selectbox("Country", ["TH", "US", "SG", "JP", "PH"])
hour = st.slider("Transaction Hour", 0, 23, 12)
device = st.selectbox("Device", ["Mobile", "Laptop", "POS", "Unknown"])
platform = st.selectbox("Platform", ["App", "Web", "POS"])

transaction = {
    "merchant": merchant,
    "amount": amount,
    "country": country,
    "hour": hour,
    "device": device,
    "platform": platform
}

# =====================
# FRAUD DECISION
# =====================
if st.button("Submit Transaction"):
    risk = calculate_risk(transaction, user_profile)
    decision = decide_action(risk)

    st.write(f"### Risk Score: `{risk}`")

    if decision == "APPROVE":
        st.success("Transaction Approved ✅")

    elif decision == "OTP":
        st.warning("OTP Verification Required ⚠️")
        otp = send_otp()
        user_otp = st.text_input("Enter OTP")

        if user_otp:
            if user_otp == str(otp):
                st.success("OTP Verified. Transaction Approved ✅")
            else:
                st.error("Invalid OTP. Transaction Blocked ❌")

    else:
        st.error("Transaction Blocked ❌ (High Risk)")
