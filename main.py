from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image, ImageOps
from datetime import datetime
from transformers import (
    BlipProcessor,
    BlipForConditionalGeneration,
    CLIPProcessor,
    CLIPModel,
    MarianMTModel,
    MarianTokenizer
)
from pathlib import Path
import torch
import uuid
import re

app = FastAPI(title="VisionAI Cloud API")

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_FOLDER = BASE_DIR / "uploads"
FRONTEND_FOLDER = BASE_DIR / "Frontend"

UPLOAD_FOLDER.mkdir(exist_ok=True)

history_data = []

ALLOWED_EXTENSIONS = [
    "jpg", "jpeg", "png", "webp", "bmp", "gif", "tiff", "tif", "jfif"
]

BLIP_MODEL_NAME = "Salesforce/blip-image-captioning-large"
CLIP_MODEL_NAME = "openai/clip-vit-base-patch32"
TRANSLATION_MODEL_NAME = "Helsinki-NLP/opus-mt-en-es"

print("Cargando modelo BLIP para descripción...")
blip_processor = BlipProcessor.from_pretrained(BLIP_MODEL_NAME)
blip_model = BlipForConditionalGeneration.from_pretrained(BLIP_MODEL_NAME)

print("Cargando modelo CLIP para clasificación...")
clip_processor = CLIPProcessor.from_pretrained(CLIP_MODEL_NAME)
clip_model = CLIPModel.from_pretrained(CLIP_MODEL_NAME)

print("Cargando modelo de traducción inglés-español...")
translator_tokenizer = MarianTokenizer.from_pretrained(TRANSLATION_MODEL_NAME)
translator_model = MarianMTModel.from_pretrained(TRANSLATION_MODEL_NAME)

if FRONTEND_FOLDER.exists():
    app.mount("/frontend", StaticFiles(directory=str(FRONTEND_FOLDER)), name="frontend")


CATEGORIES = [
    {
        "prompt": "a photo of a person or people",
        "tipo": "Persona / retrato",
        "uso": "Útil para descripción de escenas con personas, retratos o contenido social."
    },
    {
        "prompt": "a photo of an anime character, cartoon character or illustration",
        "tipo": "Ilustración / personaje",
        "uso": "Útil para describir personajes, dibujos, contenido animado o referencias artísticas."
    },
    {
        "prompt": "a photo of a car, vehicle, motorcycle, bus or truck",
        "tipo": "Vehículo / transporte",
        "uso": "Útil para análisis de autos, transporte, movilidad o escenas urbanas."
    },
    {
        "prompt": "a photo of an animal, dog, cat, bird or pet",
        "tipo": "Animal",
        "uso": "Útil para clasificación de mascotas, animales o contenido educativo."
    },
    {
        "prompt": "a photo of food, meal, pizza, burger, cake or drink",
        "tipo": "Comida",
        "uso": "Útil para menús, restaurantes, delivery o análisis gastronómico."
    },
    {
        "prompt": "a photo of a landscape, beach, mountain, forest or desert",
        "tipo": "Paisaje / naturaleza",
        "uso": "Útil para describir paisajes, naturaleza, viajes o lugares turísticos."
    },
    {
        "prompt": "a photo of a city, street, building, room or house",
        "tipo": "Espacio / arquitectura",
        "uso": "Útil para analizar espacios, edificios, habitaciones o escenas urbanas."
    },
    {
        "prompt": "a photo of an object, product, tool or device",
        "tipo": "Objeto / producto",
        "uso": "Útil para describir productos, objetos, herramientas o elementos visuales."
    },
    {
        "prompt": "a video game screenshot or digital game scene",
        "tipo": "Videojuego / escena digital",
        "uso": "Útil para analizar capturas de videojuegos, escenas 3D o contenido digital."
    }
]


def clean_caption(caption: str):
    caption = caption.strip()

    words = caption.split()
    cleaned_words = []

    for word in words:
        if not cleaned_words or cleaned_words[-1].lower() != word.lower():
            cleaned_words.append(word)

    cleaned = " ".join(cleaned_words)

    cleaned = re.sub(r"\b(\w+)\s+and\s+\1\b", r"\1", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\b(\w+)\s+with\s+\1\b", r"\1", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\b(\w+)\s+in\s+\1\b", r"\1", cleaned, flags=re.IGNORECASE)

    return cleaned


def translate_to_spanish(text: str):
    try:
        inputs = translator_tokenizer(
            text,
            return_tensors="pt",
            padding=True,
            truncation=True
        )

        with torch.no_grad():
            translated = translator_model.generate(
                **inputs,
                max_new_tokens=80,
                num_beams=4,
                early_stopping=True
            )

        spanish_text = translator_tokenizer.decode(
            translated[0],
            skip_special_tokens=True
        )

        return spanish_text

    except Exception:
        return "No se pudo traducir automáticamente."


def generate_caption(image_rgb):
    inputs = blip_processor(image_rgb, return_tensors="pt")

    with torch.no_grad():
        output = blip_model.generate(
            **inputs,
            max_new_tokens=45,
            num_beams=5,
            no_repeat_ngram_size=2,
            repetition_penalty=1.5,
            early_stopping=True
        )

    caption = blip_processor.decode(output[0], skip_special_tokens=True)
    caption = clean_caption(caption)

    return caption


def classify_image(image_rgb):
    prompts = [category["prompt"] for category in CATEGORIES]

    inputs = clip_processor(
        text=prompts,
        images=image_rgb,
        return_tensors="pt",
        padding=True
    )

    with torch.no_grad():
        outputs = clip_model(**inputs)
        probs = outputs.logits_per_image.softmax(dim=1)[0]

    best_index = int(torch.argmax(probs).item())
    confidence = round(float(probs[best_index]) * 100, 2)

    selected_category = CATEGORIES[best_index]

    return {
        "tipo": selected_category["tipo"],
        "uso": selected_category["uso"],
        "confianza": confidence
    }


@app.get("/")
def home():
    index_path = FRONTEND_FOLDER / "index.html"

    if index_path.exists():
        return FileResponse(index_path)

    return {
        "mensaje": "Frontend no encontrado. Crea la carpeta Frontend con index.html, style.css y app.js."
    }


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    file_extension = file.filename.split(".")[-1].lower()

    if file_extension not in ALLOWED_EXTENSIONS:
        return {
            "error": "Formato no permitido. Usa jpg, jpeg, png, webp, bmp, gif, tiff, tif o jfif."
        }

    new_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = UPLOAD_FOLDER / new_filename

    image_bytes = await file.read()

    with open(file_path, "wb") as image_file:
        image_file.write(image_bytes)

    try:
        image = Image.open(file_path)

        try:
            image.seek(0)
        except EOFError:
            pass

        image = ImageOps.exif_transpose(image)

        width, height = image.size
        image_rgb = image.convert("RGB")

    except Exception:
        return {
            "error": "No se pudo leer la imagen. Prueba con otro archivo o formato."
        }

    descripcion_ia = generate_caption(image_rgb)
    descripcion_es = translate_to_spanish(descripcion_ia)

    categoria = classify_image(image_rgb)

    tipo_imagen = categoria["tipo"]
    uso_sugerido = categoria["uso"]
    confianza_categoria = categoria["confianza"]

    alt_text = f"Imagen descrita automáticamente por IA: {descripcion_es}"

    analisis_combinado = (
        f"La IA describe la imagen como: '{descripcion_es}'. "
        f"La categoría más probable es '{tipo_imagen}' con una confianza de {confianza_categoria}%."
    )

    prediction = {
        "descripcion_ia": descripcion_ia,
        "descripcion_es": descripcion_es,
        "tipo_imagen": tipo_imagen,
        "confianza_categoria": confianza_categoria,
        "uso_sugerido": uso_sugerido,
        "alt_text": alt_text,
        "analisis_combinado": analisis_combinado,
        "width": width,
        "height": height,
        "formato": file_extension,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    history_data.append(prediction)

    return prediction


@app.get("/history")
def history():
    return history_data


@app.get("/health")
def health():
    return {
        "status": "ok",
        "message": "VisionAI Cloud API funcionando correctamente",
        "modelo_descripcion": BLIP_MODEL_NAME,
        "modelo_clasificacion": CLIP_MODEL_NAME,
        "modelo_traduccion": TRANSLATION_MODEL_NAME,
        "formatos_soportados": ALLOWED_EXTENSIONS
    }