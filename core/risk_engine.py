def calculate_ip_risk(llm_result):
    """
    Calculate IP risk score and level consistently.
    Score is 0–100, risk level is Low/Medium/High
    """
    score = 0

    # Assign weights
    ownership_weight = 50
    exclusivity_weight = 30
    favor_weight = 20

    # Calculate score based on LLM results
    ownership = llm_result.get("ownership", "").lower()
    exclusivity = llm_result.get("exclusivity", "").lower()
    favor = llm_result.get("favor", "").lower()

    if ownership == "assigned":
        score += ownership_weight
    if exclusivity == "exclusive":
        score += exclusivity_weight
    if favor == "one-sided":
        score += favor_weight

    # Ensure score is 0–100
    score = min(max(score, 0), 100)

    # Determine risk level consistently
    if score >= 60:
        risk_level = "High"
    elif score >= 30:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    return risk_level, score
