"""
Shadow-Score Académico - Página del Estudiante
=============================================
Formulario de captura de perfil y carga semanal del estudiante.

CORRECCIONES DE CACHE (v2):
- Se eliminan los `key=` de todos los widgets del formulario para evitar
  que Streamlit vincule los controles al session_state y reutilice valores
  residuales de sesiones anteriores.
- Los valores se leen desde las variables locales del widget (retorno de
  st.selectbox / st.number_input) y se guardan manualmente en session_state
  solo al momento de presionar el botón, garantizando datos frescos.
- Se limpia el estado de resultados previos (`resultados`, `promedio_actual`)
  antes de redirigir para forzar recálculo limpio en la página de resultados.
"""

import streamlit as st
import sys
from pathlib import Path

from config.estilos_comunes import aplicar_estilos_globales
from config.colores import (
    COLOR_PRIMARIO,
    COLOR_BOTON_VERDE,
    COLOR_BOTON_VERDE_HOVER,
)

aplicar_estilos_globales()

# ------------------------------------------------------------
# 1. Estilos CSS personalizados
# ------------------------------------------------------------
st.markdown(f"""
<style>
    .stApp, .main, .block-container, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {{
        background-color: #f8fafc !important;
        color: #1e293b !important;
    }}
    .stApp label, .stMarkdown, .stText, .stTitle, h1, h2, h3, h4, h5, h6, p, span:not([data-baseweb]) {{
        color: #1e293b !important;
    }}

    div[data-baseweb="select"] > div,
    .stNumberInput input[type="number"] {{
        background-color: #dbeafe !important;
        border-radius: 8px !important;
        color: #1e293b !important;
    }}
    div[data-baseweb="select"] > div * {{
        color: #1e293b !important;
    }}

    div[data-baseweb="popover"] {{
        background-color: #1e293b !important;
        border: 1px solid #475569 !important;
        border-radius: 8px !important;
        color: #f1f5f9 !important;
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.4) !important;
    }}
    div[data-baseweb="popover"] div[role="listbox"] {{
        background-color: #1e293b !important;
        padding: 4px 0 !important;
    }}
    div[data-baseweb="popover"] div[role="option"] {{
        background-color: #1e293b !important;
        color: #f1f5f9 !important;
        padding: 8px 12px !important;
        cursor: pointer !important;
    }}
    div[data-baseweb="popover"] div[role="option"]:hover {{
        background-color: #334155 !important;
    }}
    div[data-baseweb="popover"] * {{
        color: #f1f5f9 !important;
    }}

    div[data-baseweb="layer"] > div, #stPortal > div {{
        background-color: transparent !important;
        color-scheme: light !important;
        backdrop-filter: none !important;
    }}

    .carga-semanal .stNumberInput label {{
        min-height: 3.2em !important;
        display: flex !important;
        align-items: flex-end !important;
        line-height: 1.4 !important;
        white-space: normal !important;
        word-wrap: break-word !important;
    }}

    .stButton > button {{
        background-color: {COLOR_BOTON_VERDE} !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 12px !important;
        padding: 0.6rem 1.2rem !important;
        border: none !important;
    }}
    .stButton > button:hover {{
        background-color: {COLOR_BOTON_VERDE_HOVER} !important;
        transform: scale(1.02);
    }}

    .custom-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 2rem;
        border-bottom: 2px solid #cbd5e1;
        padding-bottom: 1rem;
    }}
    .project-title {{
        font-size: 2.2rem !important;
        font-weight: 700;
        color: {COLOR_PRIMARIO} !important;
        margin: 0;
    }}
    .role-badge {{
        background-color: {COLOR_PRIMARIO};
        color: white !important;
        padding: 0.5rem 1.2rem;
        border-radius: 48px;
        font-size: 1.2rem !important;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 10px;
    }}
    .role-badge span {{
        font-size: 1.4rem;
    }}
    .profile-emoji {{
        font-size: 5rem;
        background-color: #e2e8f0;
        padding: 0.75rem;
        border-radius: 60px;
        display: inline-block;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
    }}

    div[data-testid="stToast"] {{
        background-color: white !important;
        color: #1e293b !important;
        border: 1px solid #e2e8f0 !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
        border-radius: 8px !important;
        padding: 12px 16px !important;
        animation: fadeInDown 0.5s ease-out !important;
    }}
    div[data-testid="stToast"] * {{
        color: #1e293b !important;
    }}
    @keyframes fadeInDown {{
        from {{ opacity: 0; transform: translateY(-20px); }}
        to   {{ opacity: 1; transform: translateY(0); }}
    }}
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------
# 2. JavaScript de respaldo
# ------------------------------------------------------------
st.markdown("""
<script>
new MutationObserver(() => {
    document.querySelectorAll('div[data-baseweb="popover"]').forEach(pop => {
        pop.style.backgroundColor = '#1e293b';
        pop.style.color = '#f1f5f9';
        pop.style.border = '1px solid #475569';
        const listbox = pop.querySelector('div[role="listbox"]');
        if (listbox) listbox.style.backgroundColor = '#1e293b';
        pop.querySelectorAll('div[role="option"]').forEach(opt => {
            opt.style.backgroundColor = '#1e293b';
            opt.style.color = '#f1f5f9';
        });
    });
    document.querySelectorAll('div[data-baseweb="layer"] > div').forEach(overlay => {
        overlay.style.backgroundColor = 'transparent';
        overlay.style.colorScheme = 'light';
    });
    const portal = document.getElementById('stPortal');
    if (portal && portal.firstElementChild) {
        portal.firstElementChild.style.backgroundColor = 'transparent';
        portal.firstElementChild.style.colorScheme = 'light';
    }
    document.querySelectorAll('div[data-testid="stToast"]').forEach(toast => {
        toast.style.backgroundColor = 'white';
        toast.style.color = '#1e293b';
        toast.style.border = '1px solid #e2e8f0';
        toast.style.boxShadow = '0 4px 12px rgba(0,0,0,0.1)';
    });
}).observe(document.body, { childList: true, subtree: true });
</script>
""", unsafe_allow_html=True)

# ------------------------------------------------------------
# 3. Cabecera visual
# ------------------------------------------------------------
st.markdown(f"""
<div class="custom-header">
    <div class="project-title">📊 Shadow-Score Académico</div>
    <div class="role-badge">
        <span>🎓</span> Soy estudiante
    </div>
</div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------
# 4. Formulario de perfil del estudiante
#
# CORRECCIÓN CLAVE: ningún widget usa key= para evitar que
# Streamlit los enlace al session_state y reutilice valores
# residuales de ejecuciones anteriores. Los valores se capturan
# desde las variables locales y se persisten manualmente solo
# al pulsar el botón.
# ------------------------------------------------------------
st.markdown("### Perfil del estudiante")

with st.container():
    col_icon, col_fields = st.columns([1, 4], gap="medium")
    with col_icon:
        st.markdown('<div class="profile-emoji">🧑‍🎓</div>', unsafe_allow_html=True)
    with col_fields:
        col1, col2 = st.columns(2)
        with col1:
            genero = st.selectbox(
                "Género *",
                ["Femenino", "Masculino"],
                index=None,
                placeholder="Selecciona una opción",
                # Sin key= para evitar cache de session_state
            )
            estrato = st.selectbox(
                "Estrato socioeconómico *",
                list(range(1, 7)),
                index=None,
                placeholder="Elige tu estrato",
                # Sin key= para evitar cache de session_state
            )
        with col2:
            composicion_hogar = st.selectbox(
                "Composición del hogar *",
                ["Vive solo/a", "Con familia", "Con pareja", "Residencia universitaria", "Otros"],
                index=None,
                placeholder="Selecciona...",
                # Sin key= para evitar cache de session_state
            )
            dependientes = st.number_input(
                "Personas a cargo",
                min_value=0,
                max_value=10,
                value=0,
                step=1,
                # Sin key= para evitar cache de session_state
            )

# ------------------------------------------------------------
# 5. Carga semanal
# ------------------------------------------------------------
st.markdown('<div class="carga-semanal">', unsafe_allow_html=True)
st.markdown("### ⏱️ Carga semanal")

col_c1, col_c2, col_c3 = st.columns(3)
with col_c1:
    horas_domesticas = st.number_input(
        "Horas en tareas domésticas/cuidado",
        min_value=0.0,
        max_value=168.0,
        value=0.0,
        step=1.0,
        # Sin key= para evitar cache de session_state
    )
with col_c2:
    horas_trabajo = st.number_input(
        "Horas de trabajo remunerado",
        min_value=0.0,
        max_value=168.0,
        value=0.0,
        step=1.0,
        # Sin key= para evitar cache de session_state
    )
with col_c3:
    horas_estudio = st.number_input(
        "Horas de estudio declaradas",
        min_value=0.0,
        max_value=168.0,
        value=0.0,
        step=1.0,
        # Sin key= para evitar cache de session_state
    )
st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------------------------------------
# 5.1 Promedio académico actual (opcional)
# ------------------------------------------------------------
st.markdown("### 📊 Promedio académico (opcional)")
promedio_actual = st.number_input(
    "Promedio ponderado actual (0.0 – 5.0)",
    min_value=0.0,
    max_value=5.0,
    value=None,
    step=0.1,
    placeholder="Ejemplo: 3.8",
    # Sin key= para evitar cache de session_state
)
st.caption("Si proporcionas tu promedio actual, el modelo estimará la posible pérdida de puntos (coste de oportunidad).")

# ------------------------------------------------------------
# 6. Botón, validación, almacenamiento y redirección
# ------------------------------------------------------------
if st.button("🔍 Calcular mi Shadow-Score", type="primary", use_container_width=False):
    errores = []

    if not genero:
        errores.append("Género es obligatorio.")
    if estrato is None:
        errores.append("Estrato es obligatorio.")
    if not composicion_hogar:
        errores.append("Composición del hogar es obligatoria.")

    total_horas = horas_domesticas + horas_trabajo + horas_estudio
    if total_horas <= 0:
        errores.append("Debe ingresar al menos una hora en alguna categoría.")
    elif total_horas > 168:
        errores.append(f"La suma de horas ({total_horas:.0f}) excede 168 horas semanales.")

    if errores:
        for err in errores:
            st.toast(err, icon="❌", duration=10)
    else:
        # ----------------------------------------------------------
        # CORRECCIÓN: limpiar cualquier resultado previo antes de
        # guardar los nuevos datos, para forzar recálculo limpio
        # en la página de resultados y evitar mostrar resultados
        # de una sesión anterior.
        # ----------------------------------------------------------
        for clave_residual in ["resultados", "perfil", "cargas", "promedio_actual"]:
            st.session_state.pop(clave_residual, None)

        # Guardar datos frescos capturados desde los widgets locales
        st.session_state.perfil = {
            "genero":            genero,
            "estrato":           estrato,
            "composicion_hogar": composicion_hogar,
            "dependientes":      dependientes,
        }
        st.session_state.cargas = {
            "horas_domesticas": horas_domesticas,
            "horas_trabajo":    horas_trabajo,
            "horas_estudio":    horas_estudio,
        }
        # None si el usuario dejó el campo vacío (value=None por defecto)
        st.session_state.promedio_actual = promedio_actual

        st.switch_page("pages/3_resultados_estudiantes.py")