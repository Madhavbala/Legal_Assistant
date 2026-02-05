import json
import os
from datetime import datetime

AUDIT_FILE = "data/audit_logs.json"

def log_audit(results: list, language: str = "unknown"):
    """Log analysis results safely."""
    os.makedirs("data", exist_ok=True)
    
    audit_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "language": language,
        "total_clauses": len(results),
        "avg_risk": sum(r.get("score", 0) for r in results) / len(results),
        "clauses": [{"risk": r.get("risk", "N/A"), "score": r.get("score", 0)} for r in results]
    }
    
    # SAFE JSON loading with empty file handling
    data = []
    if os.path.exists(AUDIT_FILE):
        try:
            with open(AUDIT_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:  # Only load if not empty
                    data = json.loads(content)
                else:
                    data = []
        except (json.JSONDecodeError, ValueError):
            data = []  # Corrupted file → start fresh
    
    # Append new entry
    data.append(audit_entry)
    
    # FIXED: json.dump(data, f, indent=2, ensure_ascii=False)
    with open(AUDIT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
