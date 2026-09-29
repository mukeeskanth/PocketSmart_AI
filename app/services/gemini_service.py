import json
import base64
import mimetypes
import google.generativeai as genai
from app.config import settings

def configured():
    return bool(settings.gemini_api_key and
                settings.gemini_api_key != "your_gemini_api_key_here")

def generate_json(prompt, image_path=None):
    if not configured():
        raise RuntimeError("Gemini API key is not configured.")
    genai.configure(api_key=settings.gemini_api_key)
    model = genai.GenerativeModel(settings.gemini_model)
    content = [prompt]
    if image_path:
        mime = mimetypes.guess_type(image_path)[0] or "image/jpeg"
        with open(image_path, "rb") as f:
            data = base64.b64encode(f.read()).decode("utf-8")
        content.append({"mime_type": mime, "data": data})
    response = model.generate_content(content)
    raw = (getattr(response, "text", "") or "").strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)
