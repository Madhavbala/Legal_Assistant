def calculate_ip_risk(llm_result: dict) -> tuple[str, int]:
    """
    Calculate IP risk score (0-100) and level (Low/Medium/High).
    Returns: (risk_level, score)
    """
    score = 0
    
    # Extract LLM analysis
    ownership = llm_result.get("ownership", "").lower()
    exclusivity = llm_result.get("exclusivity", "").lower()
    favor = llm_result.get("favor", "").lower()
    
    # Risk weights
    if "assigned" in ownership:
        score += 40  # High risk
    elif "licensed" in ownership:
        score += 20  # Medium risk
    
    if "exclusive" in exclusivity:
        score += 30  # High exclusivity risk
    
    if "one-sided" in favor:
        score += 25  # Unbalanced terms
    
    # Cap at 100
    score = min(score, 100)
    
    # Risk level
    if score >= 60:
        risk_level = "High"
    elif score >= 30:
        risk_level = "Medium"
    else:
        risk_level = "Low"
    
    return risk_level, score
