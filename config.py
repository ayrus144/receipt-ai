# LLM model name (ollama)
OCR_LLM_MODEL = "qwen3.5:2b"
VISION_LLM_MODEL = "qwen3.5:2b"

# Prompts for the LLM models for OCR and Vision based extractors
OCR_LLM_PROMPT = f"""
You are a receipt parsing system.

Extract the following fields from the receipt text:

- company
- invoice_number
- date (invoice date)
- total

Return ONLY valid JSON in this schema:

{{
  "company": {{"value": string|null, "confidence": float between 0-1}},
  "invoice_number": {{"value": string|null, "confidence": float between 0-1}},
  "date": {{"value": string|null, "confidence": float between 0-1}},
  "total": {{"value": string|null, "confidence": float between 0-1}}
}}

Rules:
- follow the valid JSON schema mentioned above
- Only use provided text and don't hallucinate

TEXT:
"""

VISION_LLM_PROMPT = f"""
You are a receipt understanding system.

Extract:
- company
- invoice_number
- date (invoice date)
- total

Return ONLY JSON in this schema:

{{
  "company": {{"value": string|null, "confidence": float between 0-1}},
  "invoice_number": {{"value": string|null, "confidence": float between 0-1}},
  "date": {{"value": string|null, "confidence": float between 0-1}},
  "total": {{"value": string|null, "confidence": float between 0-1}}
}}

Rules:
- follow the valid JSON schema mentioned above
"""