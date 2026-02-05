EN_PROMPT = """
Analyze this IP clause and return ONLY JSON.

Clause:
{clause}

JSON:
{{
  "ownership": "assigned | licensed | unclear",
  "exclusivity": "exclusive | non-exclusive | unclear",
  "favor": "one-sided | balanced",
  "risk_reason": "short simple explanation",
  "suggested_fix": "safer wording"
}}
"""

HI_PROMPT = """
इस बौद्धिक संपदा (IP) क्लॉज का विश्लेषण करें और केवल JSON लौटाएं।

क्लॉज:
{clause}

JSON:
{{
  "ownership": "assigned | licensed | unclear",
  "exclusivity": "exclusive | non-exclusive | unclear",
  "favor": "one-sided | balanced",
  "risk_reason": "सरल हिंदी में कारण",
  "suggested_fix": "सुरक्षित वैकल्पिक शब्द"
}}
"""
