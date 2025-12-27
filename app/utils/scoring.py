# app/utils/scoring.py

def scoring_instructions() -> str:
    return """
Score based on:
- Clarity of intent
- Trust & credibility
- Positioning strength
- Conversion readiness

Use realistic benchmarks:
9–10: Exceptional
7–8.5: Strong but improvable
5–6.5: Average
Below 5: Weak

Return:
- numeric score (one decimal)
- short reasoning
"""
