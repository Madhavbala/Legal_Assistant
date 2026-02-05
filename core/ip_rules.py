def is_ip_clause(clause: str) -> bool:
    clause_lower = clause.lower()
    keywords = ["intellectual property", "ownership", "exclusive", "assign",
                "no rights to reuse", "no rights to modify", "license", "patent", "copyright"]
    return any(k in clause_lower for k in keywords)

def infer_ip_meaning(clause: str) -> dict:
    clause_lower = clause.lower()
    ownership = "Unknown"
    exclusivity = "Unknown"
    
    if "client" in clause_lower:
        ownership = "Client"
    elif "service provider" in clause_lower or "provider" in clause_lower:
        ownership = "Service Provider"

    if "exclusive" in clause_lower:
        exclusivity = "Exclusive"
    elif "non-exclusive" in clause_lower:
        exclusivity = "Non-Exclusive"

    return {
        "ownership": ownership,
        "exclusivity": exclusivity,
        "risk_reason": "The clause is risky because it is overly broad and can create IP disputes.",
        "suggested_fix": "Define IP ownership clearly and include carve-outs for background IP."
    }
