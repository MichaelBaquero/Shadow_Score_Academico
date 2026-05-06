"""
Shadow-Score Académico - Página de Inicio (Home)
Versión con tarjetas personalizadas, redirección funcional y carrusel con indicadores.
"""

import os
import sys
from pathlib import Path
import streamlit as st
import json

# Agregar Front_End al path para importar config
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.estilos_comunes import aplicar_estilos_globales
from config.frases import FRASES
from config.tarjetas import TARJETA_ESTUDIANTE, TARJETA_ADMIN
from config.colores import COLOR_FONDO_CARRUSEL

# =========================================================
# CONFIGURACIÓN DE LA PÁGINA
# =========================================================
st.set_page_config(
    page_title="Shadow-Score Académico",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Aplicar estilos globales (sidebar oculta, tarjetas, etc.)
aplicar_estilos_globales()

# =========================================================
# ENCABEZADO PRINCIPAL
# =========================================================
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

# =========================================================
# FUNCIÓN PARA GENERAR TARJETAS CLICKEABLES
# =========================================================
def render_tarjeta(archivo_pagina, emoji, titulo, subtitulo, color_fondo=None, nombre_pagina=None):
    """
    Genera el HTML de una tarjeta interactiva con efecto hover.
    La redirección se realiza a través del atributo 'href' que se le pasa.
    """
    bg_color = color_fondo if color_fondo else "#ffffff"
    target_url = nombre_pagina if nombre_pagina else "#"
    
    html = f"""
    <a style="text-decoration: none; display: block;" href="{target_url}">
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

# =========================================================
# TARJETAS DE ROL (ESTUDIANTE / ADMINISTRATIVO)
# =========================================================
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown(
        render_tarjeta(
            TARJETA_ESTUDIANTE["ruta"],
            TARJETA_ESTUDIANTE["emoji"],
            TARJETA_ESTUDIANTE["titulo"],
            TARJETA_ESTUDIANTE["subtitulo"],
            TARJETA_ESTUDIANTE.get("color_fondo"),
            'estudiante'
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
            TARJETA_ADMIN.get("color_fondo"),
            'administrativo'
        ),
        unsafe_allow_html=True
    )

st.markdown("---")

# =========================================================
# CARRUSEL DE FRASES CON INDICADORES
# =========================================================

frases_json = json.dumps(FRASES)

carousel_html = f"""
<style>
    .carousel-container {{
        background: {COLOR_FONDO_CARRUSEL};
        border-radius: 28px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-top: 1rem;
        padding: 1.5rem;
    }}
    .frase-texto {{
        text-align: center;
        font-size: 1.15rem;
        font-weight: 500;
        color: #1e293b;
        line-height: 1.5;
        min-height: 80px;
        transition: opacity 0.6s ease-in-out;
        opacity: 1;
    }}
    .frase-texto.fade-out {{
        opacity: 0;
    }}
    .dots-container {{
        display: flex;
        justify-content: center;
        gap: 8px;
        margin-top: 20px;
    }}
    .dot {{
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background-color: #cbd5e1;
        transition: background-color 0.3s ease;
    }}
    .dot.active {{
        background-color: #3b82f6;
    }}
</style>

<div class="carousel-container">
    <div id="frase-texto" class="frase-texto">{FRASES[0]}</div>
    <div class="dots-container" id="dots-container"></div>
</div>

<script>
    const frases = {frases_json};
    let currentIndex = 0;
    const intervalTime = 10000; // 10 segundos
    let isTransitioning = false;

    const fraseDiv = document.getElementById('frase-texto');
    const dotsContainer = document.getElementById('dots-container');

    // Crear los puntos (sin eventos de clic)
    frases.forEach((_, idx) => {{
        const dot = document.createElement('div');
        dot.classList.add('dot');
        if (idx === currentIndex) dot.classList.add('active');
        dotsContainer.appendChild(dot);
    }});

    function updateActiveDot() {{
        const dots = document.querySelectorAll('.dot');
        dots.forEach((dot, idx) => {{
            if (idx === currentIndex) dot.classList.add('active');
            else dot.classList.remove('active');
        }});
    }}

    function setFrase(index) {{
        if (isTransitioning) return;
        isTransitioning = true;
        fraseDiv.classList.add('fade-out');
        setTimeout(() => {{
            currentIndex = index;
            fraseDiv.innerHTML = frases[currentIndex];
            updateActiveDot();
            fraseDiv.classList.remove('fade-out');
            setTimeout(() => {{ isTransitioning = false; }}, 100);
        }}, 300);
    }}

    function nextFrase() {{
        const nextIndex = (currentIndex + 1) % frases.length;
        setFrase(nextIndex);
    }}

    setInterval(nextFrase, intervalTime);
</script>
"""

st.html(carousel_html)

# =========================================================
# PIE DE PÁGINA (CRÉDITOS Y FUENTES)
# =========================================================
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
