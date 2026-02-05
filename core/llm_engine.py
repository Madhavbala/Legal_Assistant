import os
import json
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def analyze_clause_with_llm(clause_text: str, lang: str) -> dict:
    prompt = f"""
Analyze the following contract clause and return ONLY valid JSON.

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

        data = json.loads(response.choices[0].message.content.strip())

        return {
            "ownership": data.get("ownership", "unknown"),
            "exclusivity": data.get("exclusivity", "unknown"),
            "favor": data.get("favor", "neutral"),
            "risk_reason": data.get("risk_reason", "Not explained."),
            "suggested_fix": data.get("suggested_fix", "No fix suggested."),
        }

    except Exception as e:
        return {
            "ownership": "unknown",
            "exclusivity": "unknown",
            "favor": "unknown",
            "risk_reason": f"LLM error: {str(e)}",
            "suggested_fix": "Manual review required.",
        }
