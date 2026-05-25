# VisionAI Cloud

VisionAI Cloud es una API de inteligencia artificial como servicio que permite analizar imágenes desde una interfaz web. El sistema recibe una imagen, la procesa mediante modelos de inteligencia artificial y entrega una descripción automática, una categoría probable, una traducción al español y datos técnicos de la imagen.

## Objetivo del proyecto

Desarrollar una solución tecnológica basada en una API propia que consuma modelos de inteligencia artificial para el análisis de imágenes. La aplicación permite que un usuario suba una imagen desde el navegador y reciba un análisis generado automáticamente.

## Funcionalidades principales

- Subida de imágenes desde una interfaz web.
- Análisis automático de imágenes con inteligencia artificial.
- Generación de descripción de imagen mediante IA.
- Clasificación de imagen por categoría.
- Porcentaje de confianza de la clasificación.
- Traducción automática de la descripción al español.
- Generación de texto alternativo para accesibilidad.
- Visualización del resultado en una página web.
- Historial temporal de análisis realizados.
- Documentación automática de la API mediante FastAPI.

## Tecnologías utilizadas

- Python
- FastAPI
- HTML
- CSS
- JavaScript
- Hugging Face Transformers
- PyTorch
- Pillow
- Uvicorn

## Modelos de inteligencia artificial utilizados

### BLIP

Se utiliza el modelo `Salesforce/blip-image-captioning-large` para generar una descripción automática de la imagen.

### CLIP

Se utiliza el modelo `openai/clip-vit-base-patch32` para clasificar la imagen dentro de una categoría probable.

### Modelo de traducción

Se utiliza el modelo `Helsinki-NLP/opus-mt-en-es` para traducir la descripción generada desde inglés a español.

## Endpoints de la API

### GET /

Muestra la interfaz web principal.

### POST /predict

Recibe una imagen y devuelve el análisis generado por inteligencia artificial.

Respuesta esperada:

    {
      "descripcion_ia": "a person standing in a street",
      "descripcion_es": "una persona de pie en una calle",
      "tipo_imagen": "Persona / retrato",
      "confianza_categoria": 85.4,
      "uso_sugerido": "Útil para descripción de escenas con personas, retratos o contenido social.",
      "alt_text": "Imagen descrita automáticamente por IA: una persona de pie en una calle",
      "analisis_combinado": "La IA describe la imagen como...",
      "width": 1080,
      "height": 720,
      "formato": "jpg",
      "created_at": "2026-05-24 20:40:00"
    }

### GET /history

Muestra el historial temporal de análisis realizados durante la ejecución del servidor.

### GET /health

Verifica que la API esté funcionando correctamente.

### GET /docs

Muestra la documentación automática generada por FastAPI.

## Arquitectura en capas

### Capa de presentación

Corresponde a la interfaz web ubicada en la carpeta `Frontend`. Está desarrollada con HTML, CSS y JavaScript. Permite al usuario subir imágenes y visualizar los resultados del análisis.

Archivos principales:

- `Frontend/index.html`
- `Frontend/style.css`
- `Frontend/app.js`

### Capa de lógica de negocio

Corresponde al archivo `main.py`. Esta capa recibe la imagen, valida el formato, procesa la imagen y consume los modelos de inteligencia artificial.

Funciones principales:

- Recepción de imágenes.
- Validación de formatos.
- Generación de descripción con BLIP.
- Clasificación con CLIP.
- Traducción al español.
- Generación de respuesta JSON.

### Capa de datos

El sistema mantiene un historial temporal en memoria durante la ejecución. También utiliza la carpeta `uploads` de forma local para almacenar temporalmente las imágenes procesadas.

## Formatos de imagen soportados

- JPG
- JPEG
- PNG
- WEBP
- BMP
- GIF
- TIFF
- TIF
- JFIF

## Instalación y ejecución local

1. Clonar el repositorio:

    git clone https://github.com/maximiliano-05/visionai-cloud.git

2. Entrar a la carpeta del proyecto:

    cd visionai-cloud

3. Crear un entorno virtual:

    python -m venv venv

4. Activar el entorno virtual en Windows:

    .\venv\Scripts\Activate.ps1

5. Instalar dependencias:

    pip install -r requirements.txt

6. Ejecutar la API:

    python -m uvicorn main:app --reload

7. Abrir en el navegador:

    http://127.0.0.1:8000

## Estructura del proyecto

    visionai-cloud/
    ├── Frontend/
    │   ├── index.html
    │   ├── style.css
    │   └── app.js
    ├── main.py
    ├── requirements.txt
    ├── .gitignore
    └── README.md

## Relación con Cloud Computing

El proyecto está preparado para ser desplegado en una máquina virtual o servicio cloud. La API puede ejecutarse en un servidor en la nube para que sea accesible desde internet.

### IaaS

Se puede utilizar una máquina virtual, por ejemplo AWS EC2, Oracle Cloud VM, Azure VM o Google Compute Engine, para desplegar la API.

### PaaS

Se puede complementar con servicios administrados como Supabase, Amazon RDS, Render, Railway o servicios equivalentes para almacenamiento, base de datos o despliegue.

### SaaS

VisionAI Cloud funciona como una aplicación web accesible desde el navegador, donde el usuario puede consumir el servicio de análisis de imágenes sin instalar software adicional.

## Autor

Maximiliano Avila Morales

## Estado del proyecto

Proyecto en desarrollo para evaluación de Infraestructura TI.
