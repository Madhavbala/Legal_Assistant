EN_PROMPT = """
Analyze this IP clause and return ONLY JSON.

Clause:
{clause}

JSON:
{
  "ownership": "assigned | licensed | unclear",
  "exclusivity": "exclusive | non-exclusive | unclear",
  "favor": "one-sided | balanced",
  "risk_reason": "short explanation",
  "suggested_fix": "safer wording"
}
"""
