"""
Shadow-Score Académico - Página de Resultados del Estudiante (v5 - namespace separation)
=========================================================================================
ARQUITECTURA DE SESSION_STATE (coherente con 1_estudiante.py):
  - Claves _w_*  → propiedad exclusiva de Streamlit (widgets del formulario).
                   Esta página NUNCA las lee ni las modifica.
  - Claves ss_*  → propiedad exclusiva de la aplicación (dominio).
                   Esta página las lee y, en su caso, escribe ss_resultados
                   y ss_escenarios.

TOKEN DE EJECUCIÓN (ss_run_id):
  Cada vez que el usuario pulsa "Calcular", 1_estudiante.py genera un nuevo
  UUID y lo guarda en ss_run_id. Los resultados guardados en ss_resultados
  incluyen el campo interno "_run_id". Si ambos no coinciden, esta página
  descarta el resultado anterior y recalcula con los snapshots actuales.
  Esto garantiza que nunca se muestren resultados obsoletos aunque el usuario
  haya navegado hacia atrás y vuelto a la página de resultados.

LIMPIEZA:
  Al pulsar "Volver al formulario", esta página elimina solo las claves ss_*.
  Los _w_* permanecen intactos → el usuario ve sus últimos valores al regresar.
"""

import streamlit as st
import sys
from pathlib import Path
import plotly.graph_objects as go
from datetime import datetime

# ── Configurar rutas para importar Back_end y config ─────────────────────────
FRONT_END = Path(__file__).parent.parent
sys.path.insert(0, str(FRONT_END))

ROOT = FRONT_END.parent
sys.path.insert(0, str(ROOT))

# ── Importaciones del proyecto ────────────────────────────────────────────────
from Back_end.modelo        import ejecutar_modelo
from Back_end.IA_prompts    import generar_prompt_escenarios
from Back_end.IA_API        import generar_plan_gemini

try:
    from config.estilos_comunes import aplicar_estilos_globales
    from config.colores import (
        COLOR_PRIMARIO,
        COLOR_BOTON_VERDE,
        COLOR_BOTON_VERDE_HOVER,
        COLOR_FONDO_TARJETA,
        COLOR_TEXTO_PRINCIPAL,
        COLOR_TEXTO_SECUNDARIO,
    )
    aplicar_estilos_globales()
except ImportError:
    COLOR_PRIMARIO          = "#2563eb"
    COLOR_BOTON_VERDE       = "#16a34a"
    COLOR_BOTON_VERDE_HOVER = "#15803d"
    COLOR_FONDO_TARJETA     = "#ffffff"
    COLOR_TEXTO_PRINCIPAL   = "#1e293b"
    COLOR_TEXTO_SECUNDARIO  = "#475569"

# ── Claves de dominio (las únicas que esta página puede borrar) ───────────────
DOMAIN_KEYS = [
    "ss_run_id",
    "ss_perfil",
    "ss_cargas",
    "ss_promedio",
    "ss_resultados",
    "ss_escenarios",
]

# ============================================================
# 1. CSS GLOBAL
# ============================================================
st.markdown(f"""
<style>
    /* ── Fondo y texto base ── */
    .stApp,
    .main,
    .block-container,
    [data-testid="stAppViewContainer"],
    [data-testid="stHeader"] {{
        background-color: #f8fafc !important;
        color: {COLOR_TEXTO_PRINCIPAL} !important;
    }}
    .stApp label,
    .stMarkdown,
    .stText,
    .stTitle,
    h1, h2, h3, h4, h5, h6,
    p,
    span:not([data-baseweb]) {{
        color: {COLOR_TEXTO_PRINCIPAL} !important;
    }}

    /* ── Botón principal (activo) ── */
    .stButton > button {{
        background-color: {COLOR_BOTON_VERDE} !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 12px !important;
        padding: 0.6rem 1.2rem !important;
        border: none !important;
        transition: background-color 0.2s ease, transform 0.15s ease;
    }}
    .stButton > button:hover {{
        background-color: {COLOR_BOTON_VERDE_HOVER} !important;
        transform: scale(1.02);
    }}

    /* ── Botón deshabilitado para Generar PDF (fondo gris) ── */
    .stButton > button:disabled {{
        background-color: #9ca3af !important;  /* Gris medio */
        color: white !important;
        border: 1px solid #6b7280 !important;
        box-shadow: none !important;
        cursor: not-allowed !important;
        opacity: 1 !important;
        font-weight: bold !important;
        border-radius: 12px !important;
    }}
    .stButton > button:disabled:hover {{
        transform: none !important;
        background-color: #9ca3af !important;
    }}

    /* ── Tooltip personalizado (Solución a "fondo negro, letra negra") ── */
    /* Forzamos fondo oscuro y texto blanco para alto contraste */
    div[data-baseweb="tooltip"] {{
        background-color: #1e293b !important;  /* Gris muy oscuro */
        color: #ffffff !important;             /* Blanco puro */
        border-radius: 8px !important;
        font-size: 14px !important;
        padding: 10px 14px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3) !important;
        border: 1px solid #334155 !important;
        z-index: 9999 !important;
    }}
    /* Asegurar que cualquier texto dentro del tooltip sea blanco */
    div[data-baseweb="tooltip"] * {{
        color: #ffffff !important;
    }}

    /* ── Cabecera ── */
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

    /* ── Tarjetas de métricas ── */
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
        border: 1px solid #e2e8f0;
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
        font-weight: 600;
    }}
    .metric-subtext {{
        font-size: 0.85rem;
        color: #64748b;
    }}

    /* ── Divisor de sección ── */
    .section-divider {{
        border: none;
        border-top: 2px solid #e2e8f0;
        margin: 2rem 0 1.5rem 0;
    }}

    /* ── Badge del run_id (debug, sutil) ── */
    .run-badge {{
        font-size: 0.7rem;
        color: #94a3b8;
        background: #f1f5f9;
        border-radius: 4px;
        padding: 2px 6px;
        font-family: monospace;
    }}
</style>
""", unsafe_allow_html=True)

# ============================================================
# 2. CABECERA
# ============================================================
st.markdown(f"""
<div class="custom-header">
    <div class="project-title">📊 Shadow-Score Académico</div>
    <div class="role-badge">
        <span>🎓</span> Soy estudiante
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# 3. VERIFICACIÓN DE SESIÓN
#    Solo se comprueba ss_run_id y ss_perfil (claves de dominio).
#    Si no existen, el usuario llegó sin pasar por el formulario.
# ============================================================
if "ss_run_id" not in st.session_state or "ss_perfil" not in st.session_state:
    st.warning(
        "No se han ingresado los datos del perfil. "
        "Por favor completa el formulario primero."
    )
    col_volver, _ = st.columns([1, 3])
    with col_volver:
        if st.button("🔙 Ir al formulario"):
            # Limpieza quirúrgica: solo claves de dominio ss_*
            # Los _w_* se preservan → el usuario verá sus últimos valores
            for key in DOMAIN_KEYS:
                st.session_state.pop(key, None)
            st.switch_page("pages/1_estudiante.py")
    st.stop()

# ── Recuperar datos de dominio ────────────────────────────────────────────────
perfil  = st.session_state["ss_perfil"]
cargas  = st.session_state["ss_cargas"]
run_id  = st.session_state["ss_run_id"]

# ============================================================
# 4. EJECUTAR MODELO CON VALIDACIÓN POR TOKEN
#
#    El resultado guardado incluye el campo interno "_run_id".
#    Si no coincide con el ss_run_id actual, el resultado es de
#    una ejecución anterior y debe descartarse → recalcular.
#    Esto protege contra datos obsoletos aunque el usuario
#    navegue hacia atrás y vuelva a esta página sin reenviar.
# ============================================================
resultado_guardado  = st.session_state.get("ss_resultados", {})
run_id_guardado     = resultado_guardado.get("_run_id")

if run_id_guardado != run_id:
    # El resultado no corresponde a este envío de formulario → recalcular
    promedio = st.session_state.get("ss_promedio")
    resultados = ejecutar_modelo(perfil, cargas, promedio)

    # Sellar el resultado con el token de ejecución actual
    resultados["_run_id"] = run_id

    # Persistir en dominio y forzar regeneración de la IA
    st.session_state["ss_resultados"] = resultados
    st.session_state.pop("ss_escenarios", None)
else:
    # El resultado ya corresponde a este envío → reutilizar sin recalcular
    resultados = resultado_guardado

# ── Desempaquetar indicadores ─────────────────────────────────────────────────
shadow_score    = resultados["shadow_score"]
fatiga          = resultados["fatiga"]
horas_efectivas = resultados["horas_efectivas"]
ppa_estimado    = resultados["ppa_estimado"]
coste_horas     = resultados["coste_horas"]
coste_ppa       = resultados["coste_ppa"]
interpretacion  = resultados["interpretacion"]

# ── Construir perfil_con_promedio sin modificar el snapshot original ──────────
perfil_con_promedio = perfil.copy()
perfil_con_promedio["promedio_actual"] = st.session_state.get("ss_promedio")

promedio_actual = st.session_state.get("ss_promedio")

# ============================================================
# 5. PRIMERA SECCIÓN: TARJETAS DE INDICADORES
# ============================================================
st.markdown("### Tus indicadores")
st.markdown(
    "Resultados del análisis de carga semanal y su posible impacto académico."
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Shadow‑Score</div>
        <div class="metric-value" style="color:{COLOR_PRIMARIO}">
            {shadow_score:.1f}%
        </div>
        <div class="metric-subtext">{interpretacion}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Fatiga cognitiva</div>
        <div class="metric-value" style="color:#e11d48;">
            {fatiga * 100:.1f}%
        </div>
        <div class="metric-subtext">0 % = sin fatiga · 100 % = máxima</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Horas efectivas / sem.</div>
        <div class="metric-value" style="color:#2563eb;">
            {horas_efectivas:.1f}
        </div>
        <div class="metric-subtext">
            de {cargas['horas_estudio']:.1f} declaradas
        </div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    ppa_texto = f"{ppa_estimado:.2f}" if ppa_estimado is not None else "—"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">PPA estimado (0‑5)</div>
        <div class="metric-value" style="color:#10b981;">
            {ppa_texto}
        </div>
        <div class="metric-subtext">promedio proyectado</div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# 6. NOTIFICACIONES INTERPRETATIVAS
# ============================================================

# ── Coste de oportunidad ──────────────────────────────────────────────────────
if coste_ppa is not None:
    st.info(
        f"⏳ **Coste de oportunidad:** pierdes aproximadamente "
        f"**{coste_horas:.1f} horas efectivas** cada semana y tu promedio "
        f"podría bajar hasta **{coste_ppa:.2f} puntos** respecto al actual."
    )
else:
    st.info(
        f"⏳ **Coste de oportunidad:** pierdes aproximadamente "
        f"**{coste_horas:.1f} horas efectivas** cada semana."
    )

# ── Comparación promedio real vs. estimado ────────────────────────────────────
if promedio_actual is not None:
    if promedio_actual > ppa_estimado:
        st.success(
            f"📈 Tu promedio actual (**{promedio_actual:.2f}**) está **por encima** "
            f"del estimado por el modelo ({ppa_estimado:.2f}). "
            "¡Sigue así! Tus hábitos de estudio están dando resultados positivos."
        )
    elif promedio_actual < ppa_estimado:
        st.warning(
            f"📉 Tu promedio actual (**{promedio_actual:.2f}**) está **por debajo** "
            f"del estimado ({ppa_estimado:.2f}). "
            "Puede que estés enfrentando dificultades adicionales. "
            "Revisa los escenarios de mejora más abajo."
        )
    else:
        st.info(
            f"📊 Tu promedio actual (**{promedio_actual:.2f}**) coincide exactamente "
            f"con el estimado por el modelo ({ppa_estimado:.2f})."
        )

# ── Interpretación del Shadow-Score ──────────────────────────────────────────
if shadow_score <= 20:
    st.success(
        "✅ **Shadow-Score bajo:** Tu carga no académica parece tener poco "
        "impacto en tu rendimiento. ¡Sigue así!"
    )
elif shadow_score <= 40:
    st.info(
        "ℹ️ **Shadow-Score moderado:** Algunas tareas podrían estar restando "
        "tiempo de estudio de calidad."
    )
elif shadow_score <= 60:
    st.warning(
        "⚠️ **Shadow-Score significativo:** La fatiga derivada de tus cargas "
        "puede estar afectando tu desempeño académico."
    )
elif shadow_score <= 80:
    st.warning(
        "🔶 **Shadow-Score alto:** Gran parte de tu tiempo efectivo de estudio "
        "se está perdiendo. Considera estrategias de redistribución."
    )
else:
    st.error(
        "🔴 **Shadow-Score extremo:** Tus responsabilidades no académicas están "
        "consumiendo prácticamente todo tu potencial de estudio. "
        "Busca apoyo institucional."
    )

# ── Interpretación de la fatiga ───────────────────────────────────────────────
if fatiga > 0.6:
    st.warning(
        f"🧠 **Fatiga alta ({fatiga * 100:.1f}%):** Más del 60 % de tu esfuerzo "
        "de estudio se diluye. Reducir la carga total o usar técnicas de gestión "
        "del tiempo puede ayudar."
    )
elif fatiga > 0.3:
    st.info(
        f"🧠 **Fatiga moderada ({fatiga * 100:.1f}%):** Aún tienes margen de mejora. "
        "Pequeños cambios en la organización pueden marcar diferencia."
    )

# ── Proporción de horas efectivas ────────────────────────────────────────────
if cargas["horas_estudio"] > 0:
    proporcion_efectiva = horas_efectivas / cargas["horas_estudio"]
    if proporcion_efectiva < 0.5:
        st.warning(
            f"📚 Solo el **{proporcion_efectiva:.0%}** de tus horas de estudio son "
            "realmente productivas. Revisar tu entorno y técnicas de estudio "
            "podría aumentar este porcentaje."
        )
    elif proporcion_efectiva >= 0.8:
        st.success(
            "📚 ¡Excelente! Más del 80 % de tu tiempo de estudio es efectivo. "
            "Mantén tus hábitos actuales."
        )

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# ============================================================
# 7. SEGUNDA SECCIÓN: GAUGE + ESCENARIOS DE MEJORA
# ============================================================
col_gauge, col_scenarios = st.columns([1, 1.2], gap="large")

# ── Gauge de fatiga ───────────────────────────────────────────────────────────
with col_gauge:
    st.subheader("Nivel de fatiga")

    fig = go.Figure(go.Indicator(
        mode   = "gauge+number",
        value  = fatiga * 100.0,
        number = {"suffix": " %", "font": {"size": 48}},
        domain = {"x": [0, 1], "y": [0, 1]},
        title  = {"text": "Fatiga cognitiva", "font": {"size": 18}},
        gauge  = {
            "axis": {
                "range": [0, 100],
                "tickwidth": 1,
                "tickcolor": "#1e293b",
                "tickfont":  {"color": "#1e293b"},
            },
            "bar":         {"color": "#0f172a", "thickness": 0.15},
            "bgcolor":     "white",
            "borderwidth": 2,
            "bordercolor": "#cbd5e1",
            "steps": [
                {"range": [0,   30],  "color": "#10b981"},   # verde
                {"range": [30,  60],  "color": "#f59e0b"},   # ámbar
                {"range": [60, 100],  "color": "#e11d48"},   # rojo
            ],
            "threshold": {
                "line":      {"color": "#0f172a", "width": 4},
                "thickness": 0.8,
                "value":     80,
            },
        },
    ))

    fig.update_layout(
        height       = 300,
        margin       = dict(l=20, r=20, t=50, b=20),
        paper_bgcolor= "rgba(0,0,0,0)",
        font         = {"color": "#1e293b", "family": "sans-serif"},
    )

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# ── Escenarios de mejora generados por IA ────────────────────────────────────
with col_scenarios:
    st.subheader("Escenarios de mejora")

    # Generar solo si no existe ya, o si fue invalidado junto con los resultados
    if "ss_escenarios" not in st.session_state:
        # ------------------------------------------------------------
        # NOTA PARA DESARROLLADORES:
        # El módulo de generación de escenarios con IA (Gemini)
        # está completamente implementado, pero actualmente NO es
        # funcional porque requiere la compra de créditos en la API
        # de Google Generative AI. Al ser un MVP, ese coste no se
        # asume en esta fase.
        #
        # Cuando se disponga de los créditos basta con:
        #   1. Descomentar las líneas de abajo.
        #   2. Borrar el bloque que asigna el mensaje informativo.
        # ------------------------------------------------------------
        with st.spinner("🧠 Preparando análisis de escenarios..."):
            # Llamada real (requiere créditos de API):
            # prompt_esc = generar_prompt_escenarios(
            #     perfil_con_promedio, cargas, resultados
            # )
            # texto_escenarios = generar_plan_gemini(prompt_esc)

            # Mensaje informativo para el usuario:
            texto_escenarios = (
                "> **Funcionalidad no disponible en esta versión**  \n\n"
                "La generación de escenarios de mejora personalizados con "
                "inteligencia artificial está implementada, pero requiere el "
                "uso de créditos en la API de Google Generative AI. Al ser "
                "esta una versión de prueba (MVP), no se ha habilitado su "
                "ejecución para evitar costes adicionales.\n\n"
                "En una futura versión, podrás recibir aquí un análisis "
                "detallado con propuestas concretas para optimizar tu "
                "rendimiento académico."
            )
            st.session_state["ss_escenarios"] = texto_escenarios

    st.markdown(st.session_state["ss_escenarios"])

# ── BOTÓN GENERAR PDF (IMPLEMENTADO PERO INHABILITADO POR FALTA DE CRÉDITOS) ──
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button(
        "📄 Generar informe PDF",
        use_container_width=True,
        disabled=True,   # ← Deshabilitado hasta que se disponga de créditos en Gemini
        help="⚠️ Funcionalidad no disponible en esta versión.\n\n"
             "La generación del informe personalizado con IA está "
             "completamente implementada, pero requiere créditos en la "
             "API de Google Generative AI. Al ser esta una versión de "
             "prueba (MVP), no se ha habilitado su ejecución para evitar "
             "costes adicionales.\n\n"
             "En una futura versión podrás descargar un PDF con tu plan "
             "de mejora detallado."
    ):
        # ================================================================
        # La lógica siguiente está lista, pero NO se ejecutará mientras
        # el botón esté disabled=True.
        # Para activarla basta con quitar esa línea y tener créditos en
        # la API de Gemini.
        # ================================================================
        with st.spinner("Redactando plan de acción con IA..."):
            from Back_end.IA_prompts import generar_prompt_plan_mejora
            from Back_end.IA_API import generar_plan_gemini

            prompt = generar_prompt_plan_mejora(perfil, cargas, resultados)
            texto_plan = generar_plan_gemini(prompt)

        with st.spinner("Creando documento PDF..."):
            from Back_end.generador_pdf import generar_pdf_informe
            from datetime import datetime

            pdf_bytes = generar_pdf_informe(perfil, resultados, texto_plan)

        st.success("Informe generado con éxito. Haz clic abajo para descargarlo.")
        st.download_button(
            label="⬇️ Descargar PDF",
            data=pdf_bytes,
            file_name=f"Plan_Mejora_ShadowScore_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf"
        )