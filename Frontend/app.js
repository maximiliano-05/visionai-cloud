const imageInput = document.getElementById("imageInput");
const previewImage = document.getElementById("previewImage");

imageInput.addEventListener("change", () => {
    const file = imageInput.files[0];

    if (file) {
        previewImage.src = URL.createObjectURL(file);
        previewImage.style.display = "block";
    }
});

function renderResult(data) {
    if (data.error) {
        return `<div class="error">${data.error}</div>`;
    }

    return `
        <div class="ai-card">
            <h3>Análisis inteligente de imagen</h3>

            <div class="info-row">
                <span class="label">Descripción generada por IA</span>
                <span>${data.descripcion_es}</span>
            </div>

            <div class="info-row">
                <span class="label">Descripción original en inglés</span>
                <span>${data.descripcion_ia}</span>
            </div>

            <div class="info-row">
                <span class="label">Categoría detectada por IA</span>
                <span>${data.tipo_imagen}</span>
            </div>

            <div class="info-row">
                <span class="label">Confianza de clasificación</span>
                <span>${data.confianza_categoria}%</span>
            </div>

            <div class="info-row">
                <span class="label">Uso sugerido</span>
                <span>${data.uso_sugerido}</span>
            </div>

            <div class="info-row">
                <span class="label">Texto alternativo</span>
                <span>${data.alt_text}</span>
            </div>

            <div class="info-row">
                <span class="label">Análisis combinado</span>
                <span>${data.analisis_combinado}</span>
            </div>

            <div class="info-row">
                <span class="label">Resolución</span>
                <span>${data.width} x ${data.height}px</span>
            </div>

            <div class="info-row">
                <span class="label">Formato</span>
                <span>${data.formato}</span>
            </div>

            <div class="info-row">
                <span class="label">Fecha de análisis</span>
                <span>${data.created_at}</span>
            </div>
        </div>
    `;
}

function renderHistory(data) {
    if (!data.length) {
        return "<p>No hay análisis guardados todavía.</p>";
    }

    return data.map((item, index) => `
        <div class="ai-card history-card">
            <h3>Análisis ${index + 1}: ${item.tipo_imagen}</h3>

            <p><strong>Descripción:</strong> ${item.descripcion_es}</p>
            <p><strong>Descripción original:</strong> ${item.descripcion_ia}</p>
            <p><strong>Confianza:</strong> ${item.confianza_categoria}%</p>
            <p><strong>Uso sugerido:</strong> ${item.uso_sugerido}</p>
            <p><strong>Resolución:</strong> ${item.width} x ${item.height}px</p>
            <p><strong>Formato:</strong> ${item.formato}</p>
            <p><strong>Fecha:</strong> ${item.created_at}</p>
        </div>
    `).join("");
}

async function sendImage() {
    const result = document.getElementById("result");

    if (!imageInput.files.length) {
        result.innerHTML = `<div class="error">Selecciona una imagen primero.</div>`;
        return;
    }

    const formData = new FormData();
    formData.append("file", imageInput.files[0]);

    result.innerHTML = `<div class="loading">Analizando con IA y traduciendo resultado... puede tardar unos segundos.</div>`;

    try {
        const response = await fetch("/predict", {
            method: "POST",
            body: formData
        });

        const data = await response.json();
        result.innerHTML = renderResult(data);

    } catch (error) {
        result.innerHTML = `<div class="error">Error al conectar con la API.</div>`;
    }
}

async function loadHistory() {
    const history = document.getElementById("history");

    try {
        const response = await fetch("/history");
        const data = await response.json();

        history.innerHTML = renderHistory(data);

    } catch (error) {
        history.innerHTML = `<div class="error">Error al cargar historial.</div>`;
    }
}