import json
import os
from datetime import datetime

HISTORY_PATH = "storage/transaction_history.json"

def load_history():
    """Load transaction processing history"""
    if not os.path.exists(HISTORY_PATH):
        return []
    
    try:
        with open(HISTORY_PATH, "r") as f:
            return json.load(f)
    except:
        return []

def save_transaction(transaction, risk_score, decision, otp_used=False, otp_passed=False):
    """Save a processed transaction to history"""
    history = load_history()
    
    record = {
        "timestamp": datetime.now().isoformat(),
        "transaction_id": transaction.get("transaction_id"),
        "merchant": transaction.get("merchant"),
        "amount": transaction.get("amount"),
        "country": transaction.get("country"),
        "hour": transaction.get("hour"),
        "device": transaction.get("device"),
        "is_fraud": transaction.get("is_fraud", None),
        "fraud_type": transaction.get("fraud_type", ""),
        "risk_score": risk_score,
        "decision": decision,
        "otp_used": otp_used,
        "otp_passed": otp_passed,
        "final_outcome": decision if decision != "OTP" else ("APPROVED" if otp_passed else "BLOCKED")
    }
    
    history.append(record)
    
    # Keep only last 100 transactions to avoid file bloat
    if len(history) > 100:
        history = history[-100:]
    
    os.makedirs(os.path.dirname(HISTORY_PATH), exist_ok=True)
    with open(HISTORY_PATH, "w") as f:
        json.dump(history, f, indent=2)
    
    return record

def get_performance_metrics():
    """Calculate system performance metrics"""
    history = load_history()
    
    if not history:
        return None
    
    # Filter transactions with known fraud labels
    labeled = [h for h in history if h.get("is_fraud") is not None]
    
    if not labeled:
        return None
    
    # Calculate metrics
    true_positives = sum(1 for h in labeled if h["is_fraud"] == 1 and h["final_outcome"] == "BLOCKED")
    true_negatives = sum(1 for h in labeled if h["is_fraud"] == 0 and h["final_outcome"] == "APPROVED")
    false_positives = sum(1 for h in labeled if h["is_fraud"] == 0 and h["final_outcome"] == "BLOCKED")
    false_negatives = sum(1 for h in labeled if h["is_fraud"] == 1 and h["final_outcome"] == "APPROVED")
    
    total = len(labeled)
    accuracy = (true_positives + true_negatives) / total if total > 0 else 0
    
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    return {
        "total_transactions": total,
        "true_positives": true_positives,
        "true_negatives": true_negatives,
        "false_positives": false_positives,
        "false_negatives": false_negatives,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1_score": f1_score,
        "fraud_caught": true_positives,
        "fraud_missed": false_negatives,
        "legitimate_blocked": false_positives
    }

def clear_history():
    """Clear transaction history"""
    if os.path.exists(HISTORY_PATH):
        os.remove(HISTORY_PATH)
