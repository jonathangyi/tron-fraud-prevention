# 🎨 Tron System Architecture & Flow

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     TRON FRAUD PREVENTION SYSTEM                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────┐
│   Transaction   │  
│     Input       │  → User makes a purchase
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                        RISK ENGINE                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Country    │  │   Merchant   │  │    Amount    │          │
│  │   Analysis   │  │   Analysis   │  │   Analysis   │          │
│  │   +0 to +40  │  │  -15 to +25  │  │   +0 to +20  │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│  ┌──────────────┐  ┌──────────────┐                            │
│  │     Time     │  │    Device    │                            │
│  │   Analysis   │  │   Analysis   │                            │
│  │   +0 to +10  │  │   +0 to +15  │                            │
│  └──────────────┘  └──────────────┘                            │
│                                                                  │
│  Total Risk Score: 0-100                                        │
└──────────────────────────┬───────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DECISION ENGINE                             │
│                                                                  │
│  ┌─────────────┐      ┌─────────────┐      ┌─────────────┐    │
│  │ Risk < 30   │      │ Risk 30-60  │      │ Risk ≥ 60   │    │
│  │             │      │             │      │             │    │
│  │  🟢 APPROVE │      │  🟡 OTP     │      │  🔴 BLOCK   │    │
│  │             │      │             │      │             │    │
│  └──────┬──────┘      └──────┬──────┘      └──────┬──────┘    │
└─────────┼─────────────────────┼─────────────────────┼───────────┘
          │                     │                     │
          ▼                     ▼                     ▼
┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
│  ✅ APPROVED    │   │  ⚠️ OTP CHECK   │   │  ❌ BLOCKED     │
│                 │   │                 │   │                 │
│  • Allow TX     │   │  • Send OTP     │   │  • Decline TX   │
│  • Learn        │   │  • Verify       │   │  • Log event    │
│  • Update       │   │  • If pass:     │   │  • No learning  │
│    profile      │   │    → Learn      │   │                 │
└────────┬────────┘   └────────┬────────┘   └─────────────────┘
         │                     │
         │                     │
         ▼                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                      LEARNING ENGINE                             │
│                                                                  │
│  📚 Updates User Profile:                                        │
│     • Add merchant to trusted list (after 3 approvals)          │
│     • Update average spending amount                            │
│     • Register new device                                       │
│     • Learn new countries                                       │
│                                                                  │
│  💾 Saves to: storage/user_profile.json                         │
└────────┬────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    TRANSACTION HISTORY                           │
│                                                                  │
│  📜 Logs every transaction:                                      │
│     • Risk score & breakdown                                    │
│     • Decision made                                             │
│     • Final outcome                                             │
│     • Whether it was fraud                                      │
│                                                                  │
│  💾 Saves to: storage/transaction_history.json                  │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagram

```
┌──────────────┐
│ Transaction  │
│   Arrives    │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────┐
│ Load User Profile                    │
│ • Trusted merchants                  │
│ • Known countries                    │
│ • Average spending                   │
│ • Registered devices                 │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│ Calculate Risk Score                 │
│                                      │
│ Compare transaction vs profile:      │
│ • Is merchant trusted? (-15)         │
│ • Is country known? (+40 if not)    │
│ • Is amount normal? (+20 if high)   │
│ • Is time usual? (+10 if not)       │
│ • Is device known? (+15 if not)     │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│ Make Decision                        │
│                                      │
│ Risk < 30:  Auto-approve ✅          │
│ Risk 30-60: Request OTP ⚠️           │
│ Risk ≥ 60:  Block ❌                 │
└──────┬───────────────────────────────┘
       │
       ├─────────────────┬─────────────────┐
       ▼                 ▼                 ▼
┌─────────────┐  ┌──────────────┐  ┌─────────────┐
│  APPROVED   │  │  OTP NEEDED  │  │   BLOCKED   │
└──────┬──────┘  └──────┬───────┘  └─────────────┘
       │                 │
       │          ┌──────┴──────┐
       │          ▼             ▼
       │    ┌─────────┐   ┌─────────┐
       │    │ OTP OK  │   │ OTP FAIL│
       │    └────┬────┘   └─────────┘
       │         │
       └─────────┴─────────────────────────┐
                                           │
                                           ▼
                              ┌────────────────────────┐
                              │  LEARN FROM APPROVAL   │
                              │                        │
                              │ • Count merchant use   │
                              │ • Update avg spending  │
                              │ • Register device      │
                              │ • Learn country        │
                              └────────┬───────────────┘
                                       │
                                       ▼
                              ┌────────────────────────┐
                              │  SAVE PROFILE          │
                              │  SAVE HISTORY          │
                              └────────────────────────┘
```

## Learning Progression Example

```
Transaction #1: Amazon, $100, TH, Mobile
├─ Profile State: Empty (new user)
├─ Risk Factors:
│  ├─ Unknown merchant: +25
│  ├─ High amount (>$50): +20
│  └─ Total Risk: 45
├─ Decision: OTP REQUIRED ⚠️
├─ User passes OTP ✅
└─ Learning:
   ├─ Merchant count: Amazon = 1
   ├─ Device count: Mobile = 1
   └─ Avg amount: $100

Transaction #2: Amazon, $120, TH, Mobile
├─ Profile State: Amazon(1), Mobile(1), Avg=$100
├─ Risk Factors:
│  ├─ Unknown merchant: +25
│  ├─ Trusted device: 0
│  ├─ Amount okay: 0
│  └─ Total Risk: 25
├─ Decision: APPROVED ✅ (auto)
└─ Learning:
   ├─ Merchant count: Amazon = 2
   ├─ Device count: Mobile = 2
   └─ Avg amount: $104

Transaction #3: Amazon, $110, TH, Mobile
├─ Profile State: Amazon(2), Mobile(2), Avg=$104
├─ Risk Factors:
│  ├─ Unknown merchant: +25
│  ├─ Trusted device: 0
│  └─ Total Risk: 25
├─ Decision: APPROVED ✅ (auto)
└─ Learning:
   ├─ Merchant count: Amazon = 3 → TRUSTED! ✨
   ├─ Device count: Mobile = 3
   └─ Avg amount: $105

Transaction #4: Amazon, $90, TH, Mobile
├─ Profile State: Amazon=TRUSTED, Mobile(3), Avg=$105
├─ Risk Factors:
│  ├─ Trusted merchant: -15 ⭐
│  ├─ Known device: 0
│  ├─ Normal amount: 0
│  └─ Total Risk: 0
├─ Decision: APPROVED ✅ (instant!)
└─ Result: Seamless experience for legitimate user
```

## Performance Metrics Calculation

```
Confusion Matrix:

                    Predicted Legit  |  Predicted Fraud
                    ─────────────────┼─────────────────
Actually Legit  |   True Negative   |  False Positive
                |   (Correct ✅)     |  (Error ❌)
                |                   |
Actually Fraud  |   False Negative  |  True Positive
                |   (Error ❌)       |  (Correct ✅)


Accuracy = (TP + TN) / Total
         = Correct predictions / All predictions

Precision = TP / (TP + FP)
          = Of blocked transactions, % actually fraud

Recall = TP / (TP + FN)
       = Of all fraud, % successfully caught

F1 Score = 2 × (Precision × Recall) / (Precision + Recall)
         = Harmonic mean of precision and recall
```

## File Organization

```
Storage Files:
├─ user_profile.json
│  {
│    "authorized_merchants": ["Amazon", "Starbucks"],
│    "countries": ["TH"],
│    "avg_amount": 105,
│    "merchant_counts": {"Amazon": 4, "Starbucks": 2},
│    "device_counts": {"Mobile": 5, "Laptop": 1}
│  }
│
└─ transaction_history.json
   [
     {
       "timestamp": "2025-01-10T14:30:00",
       "transaction_id": 1,
       "risk_score": 45,
       "decision": "OTP",
       "final_outcome": "APPROVED",
       "is_fraud": 0
     },
     ...
   ]
```

## Risk Score Visualization

```
Risk Breakdown Example:

Country Risk     ████████████████████████████████████████  +40
Merchant Risk    █████████████████████████  +25
Amount Risk      ████████████████████  +20
Time Risk        ██████████  +10
Device Risk      ███████████████  +15
                 ─────────────────────────────────────────
Total Risk Score: 110 (Would be blocked at ≥60)


After Learning:

Country Risk     ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  0 (known)
Merchant Risk    ▓▓▓▓▓▓▓▓▓▓▓▓▓▓  -15 (trusted!)
Amount Risk      ░░░░░░░░░░░░░░░░░░░░  0 (normal)
Time Risk        ░░░░░░░░░░  0 (usual time)
Device Risk      ░░░░░░░░░░░░░░░  0 (known)
                 ─────────────────────────────────────────
Total Risk Score: -15 → 0 (Capped at 0, APPROVED!)
```

## System States

```
┌────────────────────────────────────────────────────────────┐
│                    INITIAL STATE                           │
│  New User / Reset Profile                                  │
│  • No trusted merchants                                    │
│  • Only home country known                                 │
│  • Default average spending                                │
│  • No devices registered                                   │
│                                                            │
│  Result: Most transactions require OTP                     │
└────────────────────────────────────────────────────────────┘
                          │
                          │ Process transactions
                          │ Learn from approvals
                          ▼
┌────────────────────────────────────────────────────────────┐
│                   LEARNING STATE                           │
│  System gathering data                                     │
│  • Building merchant trust (1-2 uses)                      │
│  • Calibrating spending patterns                           │
│  • Recognizing devices                                     │
│                                                            │
│  Result: Mix of approvals, OTPs, blocks                    │
└────────────────────────────────────────────────────────────┘
                          │
                          │ Continued use
                          │ More approvals
                          ▼
┌────────────────────────────────────────────────────────────┐
│                   MATURE STATE                             │
│  System well-trained                                       │
│  • 5+ trusted merchants                                    │
│  • Accurate spending average                               │
│  • Multiple devices known                                  │
│  • Possibly multiple countries                             │
│                                                            │
│  Result: Mostly auto-approvals, rare OTPs, blocks fraud    │
└────────────────────────────────────────────────────────────┘
```

---

This visual guide helps explain the system architecture to non-technical audiences!
