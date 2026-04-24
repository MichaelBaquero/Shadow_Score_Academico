import os
import streamlit as st
from config.estilos_comunes import aplicar_estilos_globales
from config.frases import FRASES
from config.tarjetas import TARJETA_ESTUDIANTE, TARJETA_ADMIN
from config.colores import COLOR_FONDO_CARRUSEL
import json

st.set_page_config(
    page_title="Shadow-Score Académico",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

aplicar_estilos_globales()

st.title("📊 Shadow-Score Académico")
st.markdown(
    """
    <p style="font-size:1.2rem; color:#2c3e50; text-align:center; margin-bottom:2rem;">
    Calcula el impacto de la carga doméstica y laboral en tu rendimiento académico.<br>
    Reflexiona, simula escenarios de corresponsabilidad y recibe planes de acción personalizados.
    </p>
    """,
    unsafe_allow_html=True
)

# Función para generar una tarjeta clickeable
def render_tarjeta(archivo_pagina, emoji, titulo, subtitulo, color_fondo=None):
    # Construir la URL de Streamlit a partir del archivo en pages/
    # Ejemplo: "pages/1. estudiante.py" -> "/1_estudiante"
    nombre_base = archivo_pagina.replace("pages/", "").replace(".py", "")
    # Reemplazar espacios por guiones bajos (Streamlit lo hace así)
    url = "/" + nombre_base.replace(" ", "_")
    # Además, si el nombre comienza con número y punto, lo deja tal cual (ej: "1_estudiante")
    
    bg_color = color_fondo if color_fondo else "#ffffff"
    
    html = f"""
    <a href="{url}" style="text-decoration: none; display: block;">
        <div style="
            background-color: {bg_color};
            border-radius: 32px;
            padding: 2rem 1rem;
            min-height: 400px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            cursor: pointer;
            box-shadow: 0 20px 30px -12px rgba(0, 0, 0, 0.15);
            transition: transform 0.2s, box-shadow 0.2s;
            border: 1px solid #e2e8f0;
            margin-bottom: 1rem;
        "
        onmouseover="this.style.transform='translateY(-6px)'; this.style.boxShadow='0 25px 35px -12px rgba(0,0,0,0.2)';"
        onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 20px 30px -12px rgba(0,0,0,0.15)';">
            <div style="font-size: 5rem; margin-bottom: 1rem;">{emoji}</div>
            <div style="font-size: 2rem; font-weight: 700; margin-bottom: 0.75rem; color: #1e293b;">{titulo}</div>
            <div style="font-size: 1rem; color: #475569; max-width: 80%;">{subtitulo}</div>
        </div>
    </a>
    """
    return html

col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown(
        render_tarjeta(
            TARJETA_ESTUDIANTE["ruta"],
            TARJETA_ESTUDIANTE["emoji"],
            TARJETA_ESTUDIANTE["titulo"],
            TARJETA_ESTUDIANTE["subtitulo"],
            TARJETA_ESTUDIANTE.get("color_fondo")
        ),
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        render_tarjeta(
            TARJETA_ADMIN["ruta"],
            TARJETA_ADMIN["emoji"],
            TARJETA_ADMIN["titulo"],
            TARJETA_ADMIN["subtitulo"],
            TARJETA_ADMIN.get("color_fondo")
        ),
        unsafe_allow_html=True
    )

st.markdown("---")

# --- Carrusel de frases (con HTML y JS, usando FRASES con <strong>) ---
# Construir el array de frases en formato JSON para JavaScript
import json
frases_json = json.dumps(FRASES)

carousel_html = f"""
<div id="frase-carousel" style="
    background: {COLOR_FONDO_CARRUSEL};
    border-radius: 28px;
    padding: 2rem 1.5rem;
    text-align: center;
    font-size: 1.15rem;
    font-weight: 500;
    color: #1e293b;
    border-left: 6px solid #3b82f6;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    margin-top: 1rem;
">
    <div style="font-size: 1rem; color: #3b82f6; margin-bottom: 0.75rem;">✨ Reflexión del momento ✨</div>
    <div id="frase-texto" style="line-height: 1.5;">{FRASES[0]}</div>
</div>

<script>
    const frases = {frases_json};
    let index = 0;
    const intervalo = 10000; // 10 segundos

    function cambiarFrase() {{
        index = (index + 1) % frases.length;
        document.getElementById("frase-texto").innerHTML = frases[index];
    }}
    setInterval(cambiarFrase, intervalo);
</script>
"""

st.components.v1.html(carousel_html, height=180)
st.caption("🔄 Las frases cambian automáticamente cada 10 segundos.")

# --- Footer ---
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #6c757d; font-size: 0.8rem;">
    Basado en datos del DANE, ENUT, ODS 5 y estudios colombianos sobre fatiga académica y corresponsabilidad.<br>
    Shadow-Score Académico v3.0 - Transformando la reflexión en acción.
    </div>
    """,
    unsafe_allow_html=True
)