# Wine Journal – AI-Powered Label Recognition Demo

A lightweight Flask app that lets you snap a photo of a wine label, automatically extract structured information using OCR + a local AI model, and build a personal wine journal.

---

## 🚀 How to Run the Demo

### 1. Clone the repository & set up a virtual environment

```bash
git clone https://github.com/Toby-Yu/wine-journal.git
cd wine-journal
python -m venv venv

# Activate the virtual environment
# macOS / Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

### 2. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 3. Install Tesseract OCR (system‑level)
Tesseract is used to extract raw text from wine label images.
Windows
- Download the installer from UB‑Mannheim/tesseract.
- Install it (default path: C:\Program Files\Tesseract-OCR).
- After installation, open a new PowerShell window and run:

## Recognition Approach

1. **OCR**: The uploaded label photo is processed by Tesseract OCR to extract raw text.
2. **AI Structuring**: The extracted text is sent to llama-3.2 3.2b with a prompt asking it to parse the text into a structured JSON (wine name, producer, vintage, region, country, grape variety, confidence).
3. **Confidence & Fallback**: If OCR finds no text, or the AI call fails, the entry is created with low confidence and the raw OCR text is stored in "other_details" for manual editing.

## Known Limitations

- OCR accuracy depends heavily on image quality, angle, and lighting. Hand‑written or very stylised labels may not be recognised well.
- The free text model may occasionally hallucinate or misparse the text.
- Tesseract must be installed separately on the system.