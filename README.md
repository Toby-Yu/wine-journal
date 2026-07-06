## Recognition Approach

1. **OCR**: The uploaded label photo is processed by Tesseract OCR to extract raw text.
2. **AI Structuring**: The extracted text is sent to Google Gemma 4 31B (free text model via OpenRouter) with a prompt asking it to parse the text into a structured JSON (wine name, producer, vintage, region, country, grape variety, confidence).
3. **Confidence & Fallback**: If OCR finds no text, or the AI call fails, the entry is created with low confidence and the raw OCR text is stored in "other_details" for manual editing.

## Known Limitations

- OCR accuracy depends heavily on image quality, angle, and lighting. Hand‑written or very stylised labels may not be recognised well.
- The free text model may occasionally hallucinate or misparse the text.
- Tesseract must be installed separately on the system.