import json
import os
from datetime import datetime

AUDIT_FILE = os.path.join("data", "audit_logs.json")

def log_audit(results, language="unknown"):
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
            "risk": r.get("risk"),
            "score": r.get("score")
        })

    if os.path.exists(AUDIT_FILE):
        with open(AUDIT_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    data.append(audit_entry)

    with open(AUDIT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
