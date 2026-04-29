"""
Shadow-Score Académico - Página de Resultados del Estudiante
=============================================================
Muestra los indicadores calculados por el modelo matemático,
un espacio para el gráfico gauge y los escenarios de mejora,
y un botón para generar un informe PDF (próximamente).

Autor: [Tu nombre o equipo]
Fecha: 2026-04-29
"""

import streamlit as st
import sys
from pathlib import Path

# ------------------------------------------------------------
# 0. Configurar rutas para importar Back_end y config
# ------------------------------------------------------------
FRONT_END = Path(__file__).parent.parent
sys.path.insert(0, str(FRONT_END))

ROOT = FRONT_END.parent
sys.path.insert(0, str(ROOT))

from Back_end.modelo import ejecutar_modelo
from config.estilos_comunes import aplicar_estilos_globales
from config.colores import (
    COLOR_PRIMARIO,
    COLOR_BOTON_VERDE,
    COLOR_BOTON_VERDE_HOVER,
    COLOR_FONDO_TARJETA,
    COLOR_TEXTO_PRINCIPAL,
    COLOR_TEXTO_SECUNDARIO,
)

# ------------------------------------------------------------
# 1. Estilos base de la aplicación
# ------------------------------------------------------------
aplicar_estilos_globales()

# ------------------------------------------------------------
# 2. CSS personalizado para esta página (tarjetas y layout)
# ------------------------------------------------------------
st.markdown(f"""
<style>
    .stApp, .main, .block-container, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {{
        background-color: #f8fafc !important;
        color: {COLOR_TEXTO_PRINCIPAL} !important;
    }}
    .stApp label, .stMarkdown, .stText, .stTitle, h1, h2, h3, h4, h5, h6, p, span:not([data-baseweb]) {{
        color: {COLOR_TEXTO_PRINCIPAL} !important;
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

    .metric-card {{
        background-color: {COLOR_FONDO_TARJETA};
        border-radius: 16px;
        padding: 1.2rem 1.5rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        text-align: center;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }}
    .metric-value {{
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0.5rem 0;
        line-height: 1.2;
    }}
    .metric-label {{
        font-size: 1rem;
        color: {COLOR_TEXTO_SECUNDARIO};
        margin-bottom: 0.5rem;
    }}
    .metric-subtext {{
        font-size: 0.85rem;
        color: #64748b;
    }}

    .section-divider {{
        border-top: 2px solid #e2e8f0;
        margin: 2rem 0 1.5rem 0;
    }}

    .placeholder-box {{
        background-color: #f1f5f9;
        border: 2px dashed #94a3b8;
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        color: #475569;
        min-height: 250px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }}
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------
# 3. Cabecera común
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
# 4. Verificación de sesión (datos del formulario)
# ------------------------------------------------------------
if "perfil" not in st.session_state or "cargas" not in st.session_state:
    st.warning("No se han ingresado los datos del perfil. Por favor completa el formulario primero.")
    col_volver, _ = st.columns([1, 3])
    with col_volver:
        if st.button("🔙 Ir al formulario"):
            st.switch_page("pages/1_estudiante.py")
    st.stop()

perfil = st.session_state.perfil
cargas = st.session_state.cargas

# ------------------------------------------------------------
# 5. Ejecutar el modelo matemático (solo una vez por sesión)
# ------------------------------------------------------------
if "resultados" not in st.session_state:
    promedio_actual = st.session_state.get("promedio_actual", None)
    resultados = ejecutar_modelo(perfil, cargas, promedio_actual)
    st.session_state.resultados = resultados
else:
    resultados = st.session_state.resultados

# Desempaquetamos para facilitar el acceso
shadow_score    = resultados["shadow_score"]
fatiga          = resultados["fatiga"]
horas_efectivas = resultados["horas_efectivas"]
ppa_estimado    = resultados["ppa_estimado"]
coste_horas     = resultados["coste_horas"]
coste_ppa       = resultados["coste_ppa"]
interpretacion  = resultados["interpretacion"]

# ------------------------------------------------------------
# 6. PRIMERA SECCIÓN: indicadores principales (tarjetas)
# ------------------------------------------------------------
st.markdown("### Tus indicadores")
st.markdown("Resultados del análisis de carga semanal y su posible impacto académico.")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Shadow‑Score</div>
        <div class="metric-value" style="color:{COLOR_PRIMARIO}">{shadow_score:.1f}%</div>
        <div class="metric-subtext">{interpretacion}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    # Mostrar fatiga de 0 a 100 como porcentaje
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Fatiga cognitiva</div>
        <div class="metric-value" style="color:#e11d48;">{fatiga*100:.1f}%</div>
        <div class="metric-subtext">0% = sin fatiga, 100% = máxima</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Horas efectivas / sem.</div>
        <div class="metric-value" style="color:#2563eb;">{horas_efectivas:.1f}</div>
        <div class="metric-subtext">de {cargas['horas_estudio']:.1f} declaradas</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    ppa_texto = f"{ppa_estimado:.2f}" if ppa_estimado is not None else "—"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">PPA estimado (0‑5)</div>
        <div class="metric-value" style="color:#10b981;">{ppa_texto}</div>
        <div class="metric-subtext">promedio proyectado</div>
    </div>
    """, unsafe_allow_html=True)

# ------------------------------------------------------------
# 7. Notificaciones interpretativas
# ------------------------------------------------------------

# --- Coste de oportunidad ---
if coste_ppa is not None:
    st.info(f"⏳ **Coste de oportunidad:** pierdes aproximadamente **{coste_horas:.1f} horas efectivas** cada semana "
            f"y tu promedio podría bajar hasta **{coste_ppa:.2f} puntos** respecto al actual.")
else:
    st.info(f"⏳ **Coste de oportunidad:** pierdes aproximadamente **{coste_horas:.1f} horas efectivas** cada semana.")

# --- Comparación con el promedio real (si se proporcionó) ---
promedio_actual = st.session_state.get("promedio_actual")
if promedio_actual is not None:
    if promedio_actual > ppa_estimado:
        st.success(f"📈 Tu promedio actual (**{promedio_actual:.2f}**) está **por encima** del estimado por el modelo "
                   f"({ppa_estimado:.2f}). ¡Sigue así! Tus hábitos de estudio están dando resultados positivos.")
    elif promedio_actual < ppa_estimado:
        st.warning(f"📉 Tu promedio actual (**{promedio_actual:.2f}**) está **por debajo** del estimado "
                   f"({ppa_estimado:.2f}). Puede que estés enfrentando dificultades adicionales. "
                   "Revisa los escenarios de mejora más abajo.")
    else:
        st.info(f"📊 Tu promedio actual (**{promedio_actual:.2f}**) coincide exactamente con el estimado por el modelo "
                f"({ppa_estimado:.2f}).")

# --- Interpretación del Shadow-Score ---
if shadow_score <= 20:
    st.success("✅ **Shadow-Score bajo:** Tu carga no académica parece tener poco impacto en tu rendimiento. ¡Sigue así!")
elif shadow_score <= 40:
    st.info("ℹ️ **Shadow-Score moderado:** Algunas tareas podrían estar restando tiempo de estudio de calidad.")
elif shadow_score <= 60:
    st.warning("⚠️ **Shadow-Score significativo:** La fatiga derivada de tus cargas puede estar afectando tu desempeño académico.")
elif shadow_score <= 80:
    st.warning("🔶 **Shadow-Score alto:** Gran parte de tu tiempo efectivo de estudio se está perdiendo. Considera estrategias de redistribución.")
else:
    st.error("🔴 **Shadow-Score extremo:** Tus responsabilidades no académicas están consumiendo prácticamente todo tu potencial de estudio. Busca apoyo institucional.")

# --- Fatiga ---
if fatiga > 0.6:
    st.warning(f"🧠 **Fatiga alta ({fatiga*100:.1f}%):** Más del 60% de tu esfuerzo de estudio se diluye. Reducir la carga total o usar técnicas de gestión del tiempo puede ayudar.")
elif fatiga > 0.3:
    st.info(f"🧠 **Fatiga moderada ({fatiga*100:.1f}%):** Aún tienes margen de mejora. Pequeños cambios en la organización pueden marcar diferencia.")

# --- Horas efectivas ---
if cargas["horas_estudio"] > 0:
    proporcion_efectiva = horas_efectivas / cargas["horas_estudio"]
    if proporcion_efectiva < 0.5:
        st.warning(f"📚 Solo el **{proporcion_efectiva:.0%}** de tus horas de estudio son realmente productivas. Revisar tu entorno y técnicas de estudio podría aumentar este porcentaje.")
    elif proporcion_efectiva >= 0.8:
        st.success("📚 ¡Excelente! Más del 80% de tu tiempo de estudio es efectivo. Mantén tus hábitos actuales.")

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# ------------------------------------------------------------
# 8. SEGUNDA SECCIÓN: gauge (izq) + escenarios (der)
# ------------------------------------------------------------
col_gauge, col_scenarios = st.columns([1, 1.2], gap="large")

with col_gauge:
    st.subheader("Nivel de fatiga")
    st.markdown("""
    <div class="placeholder-box">
        <span style="font-size:3rem;">📊</span>
        <p><strong>Gráfico gauge</strong></p>
        <p>Aquí se mostrará un velocímetro interactivo con la fatiga cognitiva.</p>
    </div>
    """, unsafe_allow_html=True)

with col_scenarios:
    st.subheader("Escenarios de mejora")
    st.markdown("""
    <div class="placeholder-box">
        <span style="font-size:3rem;">✨</span>
        <p><strong>Análisis de escenarios (IA)</strong></p>
        <p>Al cargar la página se generará automáticamente una comparativa de escenarios
        (por ejemplo, reduciendo un 30% las horas domésticas) para mostrar tu potencial mejora.</p>
    </div>
    """, unsafe_allow_html=True)

# ------------------------------------------------------------
# 9. Botón para generar informe PDF (propuesta de mejora)
# ------------------------------------------------------------
st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

col_boton, _ = st.columns([1, 2])
with col_boton:
    if st.button("📄 Generar informe PDF", disabled=True, help="Próximamente disponible"):
        # Aquí se activará la segunda llamada a la IA (propuesta de mejora detallada)
        # y se generará el PDF con todos los resultados.
        pass
    st.caption("El informe incluirá una propuesta de mejora personalizada generada por IA.")