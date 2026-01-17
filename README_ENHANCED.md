# 💳 Tron – Self-Learning Fraud Prevention System

> **Real-time fraud detection with adaptive behavioral profiling**

A hackathon prototype demonstrating intelligent fraud prevention through machine learning and behavioral analysis. The system learns from each transaction to continuously improve its accuracy.

## 🎯 Key Features

### ✨ Core Capabilities
- **Real-time Risk Scoring**: Multi-factor risk assessment in milliseconds
- **Adaptive Learning**: System improves with each approved transaction
- **Three-Tier Decisions**: Auto-approve, OTP verification, or block
- **Behavioral Profiling**: Learns user patterns for merchants, amounts, locations, devices
- **Performance Analytics**: Track accuracy, precision, recall, and F1 scores

### 📊 Short-Term Enhancements (v2.0)
1. **Fraud-Labeled Dataset**: 25 transactions with ground truth labels
2. **Risk Visualization**: Interactive breakdown of risk factors
3. **Transaction History**: Complete audit trail with performance metrics
4. **Learning Dashboard**: Visual tracking of system improvement over time

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd Tron

# Install dependencies
pip install -r requirements.txt

# Create storage directory
mkdir storage
```

### Run Enhanced Streamlit App (Recommended)

```bash
streamlit run streamlit_app_enhanced.py
```

The app will open in your browser with:
- Interactive transaction processing
- Real-time risk visualization
- Performance metrics dashboard
- Learning progress tracking

### Run Enhanced CLI Version

```bash
python app_enhanced.py
```

Processes all transactions sequentially with detailed console output.

## 📁 Project Structure

```
Tron/
├── data/
│   ├── transactions.csv              # Original test data
│   └── transactions_enhanced.csv     # Enhanced data with fraud labels
├── src/
│   ├── risk_engine.py               # Risk calculation with breakdown
│   ├── decision_engine.py           # Three-tier decision logic
│   ├── otp_service.py              # OTP generation & verification
│   ├── profile_store.py            # User profile persistence
│   ├── profile_learning.py         # Adaptive learning algorithms
│   └── transaction_history.py      # History tracking & metrics
├── storage/
│   ├── user_profile.json           # Learned user profile (auto-generated)
│   └── transaction_history.json    # Transaction log (auto-generated)
├── app.py                          # Original CLI application
├── app_enhanced.py                 # Enhanced CLI with metrics
├── streamlit_app.py               # Original Streamlit app
├── streamlit_app_enhanced.py      # Enhanced Streamlit app (USE THIS)
└── requirements.txt
```

## 🎮 How It Works

### Risk Scoring Algorithm

Each transaction is scored across 5 dimensions:

| Factor | Risk Points | Trigger Condition |
|--------|-------------|-------------------|
| 🌍 Country | +40 | Transaction from unfamiliar country |
| 🏪 Merchant | +25 / -15 | Unknown merchant (+) or trusted merchant (-) |
| 💰 Amount | +20 | Amount > 2.5x user average |
| ⏰ Time | +10 | Transaction outside active hours (7am-11pm) |
| 📱 Device | +15 | Unrecognized device |

### Decision Logic

```
Risk Score < 30  → ✅ AUTO-APPROVE
Risk Score 30-60 → ⚠️  OTP VERIFICATION
Risk Score ≥ 60  → ❌ BLOCK
```

### Adaptive Learning

Approved transactions teach the system:
- **Merchant Trust**: Auto-authorize after 3 successful transactions
- **Spending Patterns**: Rolling average with 80/20 smoothing
- **Device Recognition**: Track and trust frequently used devices
- **Location Learning**: Add countries from approved transactions

## 📊 Performance Metrics

The system tracks comprehensive performance metrics:

- **Accuracy**: Overall correctness (TP + TN) / Total
- **Precision**: Of blocked transactions, % actually fraud
- **Recall**: Of all fraud, % successfully caught
- **F1 Score**: Harmonic mean of precision and recall

### Confusion Matrix

|                | Predicted Legit | Predicted Fraud |
|----------------|----------------|-----------------|
| Actually Legit | True Negative  | False Positive  |
| Actually Fraud | False Negative | True Positive   |

## 🎨 Enhanced Streamlit Features

### 1. Process Transaction Tab
- Select any transaction to analyze
- View detailed risk factor breakdown
- Interactive bar chart of risk components
- Real-time decision with explanations
- OTP verification flow

### 2. Performance Metrics Tab
- Key metrics: Accuracy, Precision, Recall, F1
- Confusion matrix visualization
- Gauge chart for overall performance
- Fraud detection summary

### 3. Transaction History Tab
- Complete audit trail of all processed transactions
- Color-coded outcomes (green=approved, red=blocked)
- Downloadable CSV export
- Quick filtering and search

### 4. Learning Progress Tab
- Risk score trend over time
- Decision distribution pie chart
- Merchant trust growth bar chart
- System improvement metrics
- Learning insights summary

## 🧪 Test Dataset

The enhanced dataset includes 25 transactions:
- **16 legitimate** transactions (is_fraud=0)
- **9 fraudulent** transactions (is_fraud=1)

Fraud types represented:
- Foreign suspicious transactions
- High-risk merchants (casinos, crypto)
- Unusual timing patterns
- Extremely high amounts
- New device + foreign country combinations

## 🔄 System Controls

### Reset Profile
Clears learned behavior and returns to initial state. Useful for:
- Testing system learning from scratch
- Comparing performance before/after training
- Demonstrating adaptive capabilities

### Clear History
Removes transaction history and metrics. Use when:
- Starting a fresh demo
- Testing specific scenarios
- Resetting performance counters

## 📈 Demo Flow Suggestions

### For Investors/Judges:
1. **Show Initial State**: Process first few transactions, show many require OTP
2. **Demonstrate Learning**: Continue processing, show system approves trusted merchants
3. **Highlight Metrics**: Display improving accuracy and decreasing false positives
4. **Show Fraud Detection**: Process known fraud transactions, show successful blocks

### For Technical Audience:
1. **Explain Risk Algorithm**: Walk through risk factor breakdown
2. **Show Adaptive Learning**: Demonstrate merchant authorization threshold
3. **Display Performance**: Review confusion matrix and F1 scores
4. **Discuss Improvements**: Talk about ML models, velocity checks, graph analysis

## 🚀 Next Steps (Medium Term)

### Planned Enhancements:
- [ ] Replace rule-based system with ML model (Random Forest/XGBoost)
- [ ] Add velocity checking (transactions per hour/day)
- [ ] Implement proper authentication and multi-user support
- [ ] Add database layer (PostgreSQL) with encryption
- [ ] Create REST API for payment system integration
- [ ] Add dispute/feedback mechanism for false positives
- [ ] Implement A/B testing framework

### Long-Term Vision:
- [ ] Anomaly detection using isolation forests
- [ ] Graph-based fraud detection (merchant-device-location networks)
- [ ] Real-time streaming with Kafka for high throughput
- [ ] Explainable AI features for regulatory compliance
- [ ] Mobile app for transaction approval/rejection

## 🛠️ Tech Stack

- **Python 3.8+**: Core language
- **Pandas**: Data manipulation
- **Streamlit**: Interactive web interface
- **Plotly**: Interactive visualizations
- **JSON**: Profile and history storage

## 📝 Notes

- System stores data in `storage/` directory (auto-created)
- Profile and history persist between runs
- OTP codes are displayed in console/UI (for demo only)
- All timestamps are in ISO format
- Maximum 100 transactions kept in history (rolling window)

## 🤝 Contributing

This is a hackathon prototype. For production use, consider:
- Secure credential storage (AWS KMS, HashiCorp Vault)
- Real SMS/email OTP delivery
- Database with proper indexing and backup
- Rate limiting and DDoS protection
- Comprehensive error handling and logging
- Unit tests and integration tests
- CI/CD pipeline

## 📄 License

MIT License - feel free to use for educational purposes

## 🎉 Acknowledgments

Built with ❤️ for demonstrating adaptive fraud prevention systems.

---

**Pro Tip**: Start with `streamlit run streamlit_app_enhanced.py` for the best demo experience!
