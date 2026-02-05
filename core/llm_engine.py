import os
import json
import streamlit as st
from groq import Groq

def get_groq_client():
    """Safe Groq client initialization."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        st.error("❌ **GROQ_API_KEY not found**. Add to Streamlit Secrets.")
        st.stop()
    
    try:
        return Groq(api_key=api_key)
    except Exception as e:
        st.error(f"❌ Groq init failed: {e}")
        st.stop()

# Lazy init (only when called)
_client = None
def get_client():
    global _client
    if _client is None:
        _client = get_groq_client()
    return _client

def get_prompt(clause_text: str, lang: str) -> str:
    """Bilingual IP analysis prompt."""
    if lang == "hi":
        return f"""इस IP क्लॉज का विश्लेषण करें। केवल JSON दें:

{{"ownership": "assigned|licensed|retained|unclear", 
  "exclusivity": "exclusive|non-exclusive|unclear", 
  "favor": "one-sided|balanced|neutral",
  "risk_reason": "संक्षिप्त कारण",
  "suggested_fix": "बेहतर शब्दावली"}}

क्लॉज: {clause_text[:1000]}"""
    return f"""Analyze IP clause. Return ONLY JSON:

{{"ownership": "assigned|licensed|retained|unclear", 
  "exclusivity": "exclusive|non-exclusive|unclear", 
  "favor": "one-sided|balanced|neutral",
  "risk_reason": "Brief explanation", 
  "suggested_fix": "Safer wording"}}

Clause: {clause_text[:1000]}"""

def analyze_clause_with_llm(clause_text: str, lang: str) -> dict:
    """Analyze with error handling."""
    try:
        client = get_client()
        response = client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[
                {"role": "system", "content": "ONLY valid JSON. No markdown/text."},
                {"role": "user", "content": get_prompt(clause_text, lang)}
            ],
            temperature=0.1,
            max_tokens=300
        )
        
        raw = response.choices[0].message.content.strip()
        return json.loads(raw)
        
    except json.JSONDecodeError:
        return {"ownership": "unclear", "exclusivity": "unclear", "favor": "neutral", 
                "risk_reason": "JSON parse failed", "suggested_fix": "Manual review"}
    except Exception as e:
        return {"ownership": "error", "exclusivity": "error", "favor": "error",
                "risk_reason": f"API error: {str(e)[:100]}", "suggested_fix": "Check API key"}
