from dotenv import load_dotenv
load_dotenv()

from ai_analyzer import analyze_wine_label

# Replace with your test image path
test_image = "static/uploads/wine3.jpg"

try:
    result = analyze_wine_label(test_image)
    print("✅ OCR + AI analysis complete!")
    for k, v in result.items():
        if k == 'raw_response':
            print(f"\n--- Raw AI response ---\n{v}")
        else:
            print(f"{k}: {v}")
except Exception as e:
    print(f"❌ Error: {e}")