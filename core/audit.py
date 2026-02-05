import json
import os
from datetime import datetime

# Relative path for audit logs
AUDIT_FILE = os.path.join("data", "audit_logs.json")

def log_audit(results, language="unknown"):
    """
    Automatically append audit entry.
    No manual save required.
    """

    # Ensure the 'data' folder exists
    os.makedirs("data", exist_ok=True)

    audit_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "language": language,
        "total_clauses": len(results),
        "clauses": []
    }

    for r in results:
        audit_entry["clauses"].append({
            "clause": r["clause"],
            "ownership": r["analysis"].get("ownership"),
            "exclusivity": r["analysis"].get("exclusivity"),
            "risk": r["risk"],
            "score": r["score"]
        })

    # Load existing audits
    if os.path.exists(AUDIT_FILE):
        with open(AUDIT_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    # Append new audit
    data.append(audit_entry)

    # Save back (APPEND STYLE)
    with open(AUDIT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
