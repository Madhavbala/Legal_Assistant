# core/llm_engine.py

import os
import json
from groq import Groq

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def analyze_clause_with_llm(clause_text: str, lang: str) -> dict:
    """
    Sends a clause to LLM and returns structured risk analysis as dict.
    Always returns a dict (never raw JSON string).
    """

    prompt = f"""
You are a legal risk analyst.

Analyze the following contract clause and return ONLY valid JSON
with the following keys:

ownership
exclusivity
favor
risk_reason
suggested_fix

Clause:
\"\"\"
{clause_text}
\"\"\"
"""

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": "Return only valid JSON. No markdown."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )

        raw = response.choices[0].message.content.strip()

        # Parse JSON safely
        data = json.loads(raw)

        # Ensure required keys exist
        return {
            "ownership": data.get("ownership", "unknown"),
            "exclusivity": data.get("exclusivity", "unknown"),
            "favor": data.get("favor", "neutral"),
            "risk_reason": data.get("risk_reason", "Not explained."),
            "suggested_fix": data.get("suggested_fix", "No fix suggested."),
        }

    except Exception as e:
        # LLM failure fallback
        return {
            "ownership": "unknown",
            "exclusivity": "unknown",
            "favor": "unknown",
            "risk_reason": f"LLM error: {str(e)}",
            "suggested_fix": "Retry analysis or review clause manually.",
        }
