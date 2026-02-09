import io
import requests
from fastapi import FastAPI, HTTPException
from PIL import Image
import pytesseract
import fitz  # PyMuPDF

# Tell Python where Tesseract is installed (Windows)
pytesseract.pytesseract.tesseract_cmd = r"C:\Users\sahana.jp\Tesseract-OCR\tesseract.exe"

app = FastAPI()

@app.post("/ocr")
async def ocr_endpoint(payload: dict):
    file_url = payload.get("file_url")
    file_type = payload.get("file_type", "").lower()

    if not file_url:
        raise HTTPException(status_code=400, detail="file_url is required")

    try:
        response = requests.get(
    file_url,
    headers={"User-Agent": "Mozilla/5.0"},
    timeout=30
)

        response.raise_for_status()
        file_bytes = response.content

        extracted_text = ""

        if "image" in file_type:
            image = Image.open(io.BytesIO(file_bytes))
            extracted_text = pytesseract.image_to_string(image)

        elif "pdf" in file_type:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            for page in doc:
                extracted_text += page.get_text()

        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")

        return {"text": extracted_text.strip()}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
