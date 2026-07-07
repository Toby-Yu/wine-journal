import os
import json
from PIL import Image
import pytesseract
import ollama

# ----- Tesseract path (configurable via environment variable) -----
# If TESSERACT_CMD is set, use it; otherwise rely on system PATH.
tesseract_cmd = os.getenv('TESSERACT_CMD')
if tesseract_cmd:
    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

# Original model (slower but reliable)
FAST_MODEL = "llama3.2:3b"

def analyze_wine_label(image_path):
    """
    Extract wine info from label photo using OCR + local Ollama model.
    Returns a dict with structured fields.
    """
    # ----- OCR -----
    try:
        img = Image.open(image_path)
        extracted_text = pytesseract.image_to_string(img).strip()
    except Exception as e:
        return {
            "wine_name": "",
            "producer": "",
            "vintage": "",
            "region": "",
            "country": "",
            "grape_variety": "",
            "other_details": f"OCR failed: {e}",
            "confidence": 0.0,
            "raw_response": ""
        }

    if not extracted_text:
        return {
            "wine_name": "",
            "producer": "",
            "vintage": "",
            "region": "",
            "country": "",
            "grape_variety": "",
            "other_details": "No text found in image.",
            "confidence": 0.0,
            "raw_response": ""
        }

    # ----- AI Structuring via Ollama (original model) -----
    prompt = (
        "You are a wine data parser. Given raw OCR text from a wine label, output ONLY a valid JSON object – no code, no explanation.\n"
        f"Raw text:\n{extracted_text}\n\n"
        "Fill these fields as best you can:\n"
        "{\n"
        '  "wine_name": "...",\n'
        '  "producer": "...",\n'
        '  "vintage": "...",\n'
        '  "region": "...",\n'
        '  "country": "...",\n'
        '  "grape_variety": "...",\n'
        '  "other_details": "...",\n'
        '  "confidence": 0.0\n'
        "}\n"
        "Important for confidence:\n"
        "- If the raw text contains clear, complete wine label info, set confidence between 0.7 and 0.9.\n"
        "- If the text is garbled, only partial, or looks like random noise, set confidence between 0.2 and 0.4.\n"
        "- Never use 0.0 unless absolutely no useful info is extractable.\n"
        "Return just the JSON, no other text."
    )

    try:
        response = ollama.chat(
            model=FAST_MODEL,          # original model
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0.0}
        )
        raw = response["message"]["content"].strip()
    except Exception as e:
        return {
            "wine_name": "",
            "producer": "",
            "vintage": "",
            "region": "",
            "country": "",
            "grape_variety": "",
            "other_details": f"AI structuring failed (Ollama error): {e}. Raw OCR text:\n{extracted_text}",
            "confidence": 0.0,
            "raw_response": extracted_text
        }

    # Robust JSON extraction
    start = raw.find('{')
    end = raw.rfind('}')
    if start != -1 and end != -1:
        json_str = raw[start:end+1]
    else:
        json_str = raw

    try:
        parsed = json.loads(json_str)
    except json.JSONDecodeError:
        return {
            "wine_name": "",
            "producer": "",
            "vintage": "",
            "region": "",
            "country": "",
            "grape_variety": "",
            "other_details": f"Failed to parse JSON. Raw AI output:\n{raw}",
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
        "other_details": str(parsed.get("other_details", "")),
        "confidence": float(parsed.get("confidence", 0.0)),
        "raw_response": raw
    }