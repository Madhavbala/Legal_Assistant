import json
import os
from datetime import datetime

AUDIT_FILE = "data/audit_logs.json"

def log_audit(results: list, language: str = "unknown"):
    """Log analysis results."""
    os.makedirs("data", exist_ok=True)
    
    audit_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "language": language,
        "total_clauses": len(results),
        "avg_risk": sum(r["score"] for r in results) / len(results),
        "clauses": [{"risk": r["risk"], "score": r["score"]} for r in results]
    }
    
    # Append to existing logs
    if os.path.exists(AUDIT_FILE):
        with open(AUDIT_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except:
                data = []
    else:
        data = []
    
    data.append(audit_entry)
    with open(AUDIT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, indent=2, ensure_ascii=False)
