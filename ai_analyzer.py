import os
import json
import base64
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise RuntimeError("OPENROUTER_API_KEY not set in .env")

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
MODEL = "z-ai/glm-4.6v"   # GLM‑4.6V vision model

client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url=OPENROUTER_BASE_URL,
    default_headers={
        "HTTP-Referer": "http://localhost:5000",
        "X-Title": "WineJournalDemo"
    }
)

def encode_image(image_path: str) -> str:
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def analyze_wine_label(image_path: str) -> dict:
    """Send a wine label photo to GLM‑4.6V. Returns structured fields + tasting notes + confidence."""
    try:
        b64_img = encode_image(image_path)
    except Exception as e:
        return {
            "wine_name": "", "producer": "", "vintage": "", "region": "",
            "country": "", "grape_variety": "", "tasting_notes": "",
            "other_details": f"Image encoding failed: {e}",
            "confidence": 0.0, "raw_response": ""
        }

    system_prompt = (
        "You are a master sommelier AI that analyses wine label photos. "
        "First, extract all visible text from the label (wine name, producer, vintage, region, etc.). "
        "Then, use your deep knowledge of world wines to fill in any missing fields and to generate an accurate tasting note. "
        "For the tasting note, infer the typical flavour profile (colour, aromas, body, tannins, finish) based on the wine, its region, and grape variety. "
        "If the label is blurry, angled, or partially cropped, infer the most likely wine from recognisable fragments. "
        "Always output a valid JSON object – no code, no explanation."
    )

    user_prompt = (
        "Analyse the wine label in this photo and return a JSON object with exactly these fields:\n"
        "{\n"
        '  "wine_name": "string",\n'
        '  "producer": "string",\n'
        '  "vintage": "string",\n'
        '  "region": "string",\n'
        '  "country": "string",\n'
        '  "grape_variety": "string",\n'
        '  "tasting_notes": "string (a brief, professional tasting note: colour, aromas, palate, finish)",\n'
        '  "other_details": "string (any extra useful info)",\n'
        '  "confidence": 0.0\n'
        "}\n\n"
        "Confidence rules:\n"
        "- Clear label: 0.85 – 0.95\n"
        "- Blurry/partial but identifiable: 0.6 – 0.8\n"
        "- Guessing from fragments: 0.3 – 0.5\n"
        "- No label: 0.0\n\n"
        "Important: The tasting note should be specific to the wine you identified. "
        "Use your knowledge of typical profiles for that grape/region/vintage. "
        "Now, output only the JSON."
    )

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{b64_img}"
                            }
                        }
                    ]
                }
            ],
            temperature=0.0,
            max_tokens=1024
        )
        raw = response.choices[0].message.content.strip()
    except Exception as e:
        return {
            "wine_name": "", "producer": "", "vintage": "", "region": "",
            "country": "", "grape_variety": "", "tasting_notes": "",
            "other_details": f"OpenRouter API call failed: {e}",
            "confidence": 0.0,
            "raw_response": str(e)
        }

    # Parse JSON
    start = raw.find('{')
    end = raw.rfind('}')
    json_str = raw[start:end+1] if start != -1 and end != -1 else raw

    try:
        parsed = json.loads(json_str)
    except json.JSONDecodeError:
        return {
            "wine_name": "", "producer": "", "vintage": "", "region": "",
            "country": "", "grape_variety": "", "tasting_notes": "",
            "other_details": f"Failed to parse JSON. Raw output:\n{raw}",
            "confidence": 0.0,
            "raw_response": raw
        }

    return {
        "wine_name": str(parsed.get("wine_name", "")),
        "producer": str(parsed.get("producer", "")),
        "vintage": str(parsed.get("vintage", "")),
        "region": str(parsed.get("region", "")),
        "country": str(parsed.get("country", "")),
        "grape_variety": str(parsed.get("grape_variety", "")),
        "tasting_notes": str(parsed.get("tasting_notes", "")),
        "other_details": str(parsed.get("other_details", "")),
        "confidence": float(parsed.get("confidence", 0.0)),
        "raw_response": raw
    }