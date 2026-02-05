def calculate_ip_risk(llm_result: dict):
    score = 0

    if llm_result.get("ownership", "").lower() == "assigned":
        score += 50
    if llm_result.get("exclusivity", "").lower() == "exclusive":
        score += 30
    if llm_result.get("favor", "").lower() == "one-sided":
        score += 20

    score = min(score, 100)

    if score >= 60:
        return "High", score
    if score >= 30:
        return "Medium", score
    return "Low", score
