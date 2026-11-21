import json
import logging
from typing import Dict, Any, Optional
import google.generativeai as genai
from app.core.config import settings

logger = logging.getLogger(__name__)

if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)


EXTRACTION_PROMPT = """You are an AI document categorization and metadata extraction system for the Islamic University of Technology (IUT).
Analyze the following official notice text and return ONLY a valid JSON object matching the schema below.

JSON Schema:
{
  "title": "Clear concise title of the notice",
  "category": "Academic" | "Administrative & Financial" | "Residential & Campus Life" | "Opportunities & Events" | "Emergency & Holidays",
  "subCategory": "Course Registration" | "Exam Routine" | "Fee Notice" | "Hall Notice" | "Scholarship" | "General Circular",
  "department": "All" or specific like "CSE", "EEE", "CEE", "MPE", "BTM",
  "targetAudience": {
    "programs": ["B.Sc.", "M.Sc.", "H.D."],
    "batches": ["2022", "2023", "2024", "2025"],
    "halls": ["All"]
  },
  "sender": {
    "office": "e.g. Office of the Registrar, Head of CSE, Comptroller Office, Provost",
    "signatory": "Name of the person signing if mentioned, else null",
    "rawSignatureDetected": false
  },
  "publishedDate": "YYYY-MM-DD or null",
  "deadlines": [
    {
      "title": "Short description of the deadline",
      "dueDate": "YYYY-MM-DDTHH:MM:SSZ",
      "actionRequired": "What the student needs to do"
    }
  ],
  "confidenceScore": 0.0 to 1.0
}

Notice Text:
\"\"\"{text}\"\"\"
"""


class GeminiExtractor:
    def __init__(self):
        self.model_name = settings.GEMINI_MODEL

    async def extract_structured_metadata(self, text: str) -> Dict[str, Any]:
        """Send extracted OCR/PDF text to Gemini to obtain structured classification."""
        if not settings.GEMINI_API_KEY:
            # Fallback stub for local testing without an API key
            logger.warning("GEMINI_API_KEY not configured. Using heuristic fallback.")
            return self._heuristic_fallback(text)

        try:
            model = genai.GenerativeModel(self.model_name)
            prompt = EXTRACTION_PROMPT.format(text=text[:8000])
            response = await model.generate_content_async(prompt)
            raw_response = response.text.strip()

            # Clean markdown codeblocks if returned
            if raw_response.startswith("```json"):
                raw_response = raw_response[7:-3].strip()
            elif raw_response.startswith("```"):
                raw_response = raw_response[3:-3].strip()

            data = json.loads(raw_response)
            return data
        except Exception as e:
            logger.error(f"Error calling Gemini API: {e}")
            return self._heuristic_fallback(text)

    def _heuristic_fallback(self, text: str) -> Dict[str, Any]:
        """Simple rule-based fallback when offline or API unavailable."""
        first_line = text.split("\n")[0][:100] if text else "Untitled Notice"
        category = "Academic"
        if "fee" in text.lower() or "payment" in text.lower():
            category = "Administrative & Financial"
        elif "hall" in text.lower() or "mess" in text.lower():
            category = "Residential & Campus Life"

        return {
            "title": first_line,
            "category": category,
            "subCategory": "General Circular",
            "department": "All",
            "targetAudience": {"programs": ["All"], "batches": ["All"], "halls": ["All"]},
            "sender": {"office": "University Administration", "signatory": None, "rawSignatureDetected": False},
            "publishedDate": None,
            "deadlines": [],
            "confidenceScore": 0.70
        }


gemini_extractor = GeminiExtractor()
