"""
Shadow-Score Académico - Página de Resultados del Estudiante (v14 - Gráfico 6 meses con hover)
=========================================================================================
"""

import streamlit as st
import sys
from pathlib import Path
import plotly.graph_objects as go
from datetime import datetime

# ── Configurar rutas ──────────────────────────────────────────────────────────
FRONT_END = Path(__file__).parent.parent
sys.path.insert(0, str(FRONT_END))
ROOT = FRONT_END.parent
sys.path.insert(0, str(ROOT))

# ── Importaciones ─────────────────────────────────────────────────────────────
from Back_end.modelo        import ejecutar_modelo
from Back_end.IA_prompts    import generar_prompt_escenarios
from Back_end.IA_API        import generar_plan_mistral, NvidiaAPIError
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

# ── Claves de dominio ──────────────────────────────────────────────────────────
DOMAIN_KEYS = [
    "ss_run_id",
    "ss_perfil",
    "ss_cargas",
    "ss_promedio",
    "ss_resultados",
    "ss_escenarios",
    "ss_escenarios_ok",
]

# ============================================================
# 1. CSS GLOBAL CON ALERTAS, TOOLTIP Y BOTONES CORREGIDOS
# ============================================================
st.markdown(f"""
<style>
    /* ── Fondo y texto base ── */
    .stApp, .main, .block-container,
    [data-testid="stAppViewContainer"],
    [data-testid="stHeader"] {{
        background-color: #f8fafc !important;
    }}
    
    /* Texto normal (NO afecta alertas) */
    .stApp label,
    .stMarkdown:not(.stAlert),
    .stText:not(.stAlert),
    .stTitle,
    h1, h2, h3, h4, h5, h6,
    p:not(.stAlert),
    span:not([data-baseweb]):not(.stAlert) {{
        color: {COLOR_TEXTO_PRINCIPAL} !important;
    }}

    /* ── ALERTAS (con contraste corregido) ── */
    div[data-testid="stInfo"] {{
        background-color: #e0f2fe !important;
        color: #0f172a !important;
        border-left: 4px solid #2563eb !important;
    }}
    div[data-testid="stInfo"] * {{
        color: #0f172a !important;
    }}

    div[data-testid="stSuccess"] {{
        background-color: #dcfce7 !important;
        color: #0f172a !important;
        border-left: 4px solid #10b981 !important;
    }}
    div[data-testid="stSuccess"] * {{
        color: #0f172a !important;
    }}

    div[data-testid="stWarning"] {{
        background-color: #fef3c7 !important;
        color: #0f172a !important;
        border-left: 4px solid #f59e0b !important;
    }}
    div[data-testid="stWarning"] * {{
        color: #0f172a !important;
    }}

    div[data-testid="stError"] {{
        background-color: #fee2e2 !important;
        color: #0f172a !important;
        border-left: 4px solid #ef4444 !important;
    }}
    div[data-testid="stError"] * {{
        color: #0f172a !important;
    }}

    /* ── TOOLTIP (fondo oscuro, texto blanco) ── */
    div[data-baseweb="tooltip"] {{
        background-color: #1e293b !important;
        color: #ffffff !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        padding: 8px 12px !important;
        font-size: 14px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3) !important;
        z-index: 9999 !important;
    }}
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

    /* ── BOTÓN SECUNDARIO "IR AL FORMULARIO" (Contraste corregido) ── */
    .stButton > button[kind="secondary"] {{
        background-color: #ffffff !important;
        color: #1e293b !important;
        border: 2px solid #cbd5e1 !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        padding: 0.5rem 1rem !important;
        transition: all 0.2s ease !important;
    }}
    .stButton > button[kind="secondary"]:hover {{
        background-color: #f1f5f9 !important;
        border-color: #94a3b8 !important;
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
# 3. VERIFICACIÓN DE SESIÓN (CON BOTÓN TIPO SECONDARY)
# ============================================================
if "ss_run_id" not in st.session_state or "ss_perfil" not in st.session_state:
    st.warning(
        "No se han ingresado los datos del perfil. "
        "Por favor completa el formulario primero."
    )
    col_volver, _ = st.columns([1, 3])
    with col_volver:
        if st.button("🔙 Ir al formulario", type="secondary", key="btn_volver"):
            for key in DOMAIN_KEYS:
                st.session_state.pop(key, None)
            st.switch_page("pages/1_estudiante.py")
    st.stop()

perfil = st.session_state["ss_perfil"]
cargas = st.session_state["ss_cargas"]
run_id = st.session_state["ss_run_id"]

# ============================================================
# 4. EJECUTAR MODELO CON VALIDACIÓN POR TOKEN
# ============================================================
resultado_guardado = st.session_state.get("ss_resultados", {})
run_id_guardado = resultado_guardado.get("_run_id")

if run_id_guardado != run_id:
    promedio = st.session_state.get("ss_promedio")
    resultados = ejecutar_modelo(perfil, cargas, promedio)
    resultados["_run_id"] = run_id
    st.session_state["ss_resultados"] = resultados
    st.session_state.pop("ss_escenarios", None)
    st.session_state.pop("ss_escenarios_ok", None)
else:
    resultados = resultado_guardado

shadow_score = resultados["shadow_score"]
fatiga = resultados["fatiga"]
horas_efectivas = resultados["horas_efectivas"]
ppa_estimado = resultados["ppa_estimado"]
coste_horas = resultados["coste_horas"]
coste_ppa = resultados["coste_ppa"]
interpretacion = resultados["interpretacion"]

perfil_con_promedio = perfil.copy()
perfil_con_promedio["promedio_actual"] = st.session_state.get("ss_promedio")
promedio_actual = st.session_state.get("ss_promedio")

# ============================================================
# 5. PRIMERA SECCIÓN: TARJETAS DE INDICADORES
# ============================================================
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
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Fatiga cognitiva</div>
        <div class="metric-value" style="color:#e11d48;">{fatiga * 100:.1f}%</div>
        <div class="metric-subtext">0 % = sin fatiga · 100 % = máxima</div>
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

# ============================================================
# 6. NOTIFICACIONES INTERPRETATIVAS
# ============================================================
if coste_ppa is not None:
    st.info(f"⏳ **Coste de oportunidad:** pierdes aproximadamente **{coste_horas:.1f} horas efectivas** cada semana y tu promedio podría bajar hasta **{coste_ppa:.2f} puntos** respecto al actual.")
else:
    st.info(f"⏳ **Coste de oportunidad:** pierdes aproximadamente **{coste_horas:.1f} horas efectivas** cada semana.")

if promedio_actual is not None:
    if promedio_actual > ppa_estimado:
        st.success(f"📈 Tu promedio actual (**{promedio_actual:.2f}**) está **por encima** del estimado por el modelo ({ppa_estimado:.2f}). ¡Sigue así! Tus hábitos de estudio están dando resultados positivos.")
    elif promedio_actual < ppa_estimado:
        st.warning(f"📉 Tu promedio actual (**{promedio_actual:.2f}**) está **por debajo** del estimado ({ppa_estimado:.2f}). Puede que estés enfrentando dificultades adicionales. Revisa los escenarios de mejora más abajo.")
    else:
        st.info(f"📊 Tu promedio actual (**{promedio_actual:.2f}**) coincide exactamente con el estimado por el modelo ({ppa_estimado:.2f}).")

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

if fatiga > 0.6:
    st.warning(f"🧠 **Fatiga alta ({fatiga * 100:.1f}%):** Más del 60 % de tu esfuerzo de estudio se diluye. Reducir la carga total o usar técnicas de gestión del tiempo puede ayudar.")
elif fatiga > 0.3:
    st.info(f"🧠 **Fatiga moderada ({fatiga * 100:.1f}%):** Aún tienes margen de mejora. Pequeños cambios en la organización pueden marcar diferencia.")

if cargas["horas_estudio"] > 0:
    proporcion_efectiva = horas_efectivas / cargas["horas_estudio"]
    if proporcion_efectiva < 0.5:
        st.warning(f"📚 Solo el **{proporcion_efectiva:.0%}** de tus horas de estudio son realmente productivas. Revisar tu entorno y técnicas de estudio podría aumentar este porcentaje.")
    elif proporcion_efectiva >= 0.8:
        st.success("📚 ¡Excelente! Más del 80 % de tu tiempo de estudio es efectivo. Mantén tus hábitos actuales.")

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# ============================================================
# 7. SEGUNDA SECCIÓN: GAUGE + GRÁFICO 6 MESES CON HOVER
# ============================================================

# ── Gauge (siempre se muestra) ──
col_gauge, col_grafico = st.columns([1, 1.2], gap="large")

with col_gauge:
    st.subheader("Nivel de fatiga")
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=fatiga * 100.0,
        number={"suffix": " %", "font": {"size": 48}},
        domain={"x": [0, 1], "y": [0, 1]},
        title={"text": "Fatiga cognitiva", "font": {"size": 18}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#1e293b", "tickfont": {"color": "#1e293b"}},
            "bar": {"color": "#0f172a", "thickness": 0.15},
            "bgcolor": "white",
            "borderwidth": 2, "bordercolor": "#cbd5e1",
            "steps": [
                {"range": [0, 30], "color": "#10b981"},
                {"range": [30, 60], "color": "#f59e0b"},
                {"range": [60, 100], "color": "#e11d48"},
            ],
            "threshold": {"line": {"color": "#0f172a", "width": 4}, "thickness": 0.8, "value": 80},
        },
    ))
    fig_gauge.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20), paper_bgcolor="rgba(0,0,0,0)", font={"color": "#1e293b", "family": "sans-serif"})
    st.plotly_chart(fig_gauge, width='stretch', config={"displayModeBar": False})

# ── Gráfico de líneas (solo si hay promedio ingresado) ──
with col_grafico:
    st.subheader("Proyección a 6 meses")

    if promedio_actual is None:
        st.info(
            "ℹ️ Este gráfico de proyección a 6 meses requiere tu **promedio ponderado actual**. "
            "No fue ingresado en el formulario, por lo que no es posible simular la evolución de tu nota. "
            "Puedes volver al formulario y añadir ese dato para ver la simulación."
        )
    else:
        # Datos del gráfico
        meses = ["Mes 1", "Mes 2", "Mes 3", "Mes 4", "Mes 5", "Mes 6"]
        inicio = promedio_actual                     # PUNTO DE PARTIDA REAL

        # ── LÍNEA ROJA: Fatiga acumulada sin intervención ──
        # La fatiga se acumula exponencialmente cada mes
        factor_fatiga = fatiga * 0.8  # Normalizar (fatiga es 0-1)
        caida_base = 0.08  # Caída base mensual
        
        valores_actual = [round(inicio, 2)]  # Comienza con el promedio del estudiante
        fatiga_acumulada = 0
        for mes in range(1, 6):
            # La fatiga se acumula: cada mes suma más impacto
            fatiga_acumulada += factor_fatiga * 0.15
            # Caída = base + fatiga acumulada (efecto multiplicativo)
            caida_mes = caida_base + (fatiga_acumulada * 0.2)
            nuevo_valor = valores_actual[-1] - caida_mes
            valores_actual.append(round(max(nuevo_valor, 0.0), 2))

        # ── LÍNEA VERDE: Con control de fatiga y recuperación ──
        # Se controla la fatiga y permite recuperación gradual
        tasa_recuperacion_base = 0.06  # Recuperación base mensual
        mejora_por_control = (1 - fatiga * 0.5)  # Mayor control con menor fatiga
        
        valores_mejora = [round(inicio, 2)]  # Comienza con el promedio del estudiante
        for mes in range(1, 6):
            # Recuperación que mejora con el paso del tiempo (mejor control de fatiga)
            recuperacion_mes = tasa_recuperacion_base * mejora_por_control * (1 + (mes * 0.08))
            nuevo_valor = valores_mejora[-1] + recuperacion_mes
            valores_mejora.append(round(min(nuevo_valor, 5.0), 2))

        fig_lineas = go.Figure()
        fig_lineas.add_trace(go.Scatter(
            x=meses,
            y=valores_actual,
            mode='lines+markers',
            name='Con fatiga acumulada (sin intervención)',
            line=dict(color='#dc2626', width=3),
            marker=dict(size=8, color='#dc2626', symbol='circle'),
            hovertemplate="<b>%{x}</b><br>Promedio: %{y:.2f}<extra></extra>"
        ))
        fig_lineas.add_trace(go.Scatter(
            x=meses,
            y=valores_mejora,
            mode='lines+markers',
            name='Con control de fatiga (intervención)',
            line=dict(color='#16a34a', width=3),
            marker=dict(size=8, color='#16a34a', symbol='diamond'),
            hovertemplate="<b>%{x}</b><br>Promedio: %{y:.2f}<extra></extra>"
        ))

        fig_lineas.update_layout(
            title=dict(
                text="Proyección a 6 meses: Impacto de la fatiga acumulada vs controlada",
                font=dict(color="#1e293b", size=14)
            ),
            xaxis=dict(
                title=dict(
                    text="Período (meses)",
                    font=dict(color="#1e293b", size=12)
                ),
                tickfont=dict(color="#1e293b", size=11),
                gridcolor="#e2e8f0",
                showgrid=True,
                type='category'
            ),
            yaxis=dict(
                title=dict(
                    text="Promedio estimado (0-5)",
                    font=dict(color="#1e293b", size=12)
                ),
                tickfont=dict(color="#1e293b", size=11),
                range=[0, 5.5],
                gridcolor="#e2e8f0"
            ),
            legend=dict(
                orientation="h",
                x=0.5,
                y=1.12,
                xanchor="center",
                yanchor="top",
                bgcolor="rgba(255, 255, 255, 0.8)",
                bordercolor="#cbd5e1",
                borderwidth=1,
                font=dict(color="#1e293b", size=11)
            ),
            hovermode='x unified',
            height=380,
            margin=dict(l=50, r=20, t=100, b=50),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(245, 248, 252, 0.5)",
            font=dict(color="#1e293b", family="sans-serif")
        )

        st.plotly_chart(
            fig_lineas,
            width='stretch',
            config={
                'displayModeBar': False,
                'scrollZoom': False,
                'doubleClick': False,
                'staticPlot': False
            }
        )

# ============================================================
# 8. PROPUESTAS DE MEJORA PERSONALIZADAS
# ============================================================
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
st.subheader("📋 Propuestas de mejora personalizadas")

if "ss_escenarios" not in st.session_state or not st.session_state.get("ss_escenarios_ok", False):
    with st.spinner("🧠 Generando propuestas de mejora personalizadas..."):
        try:
            prompt_esc = generar_prompt_escenarios(perfil_con_promedio, cargas, resultados)
            texto_escenarios = generar_plan_mistral(prompt_esc)
            st.session_state["ss_escenarios"] = texto_escenarios
            st.session_state["ss_escenarios_ok"] = True
        except NvidiaAPIError as e:
            st.error(f"⚠️ {e}")
            texto_escenarios = "No se pudieron generar las propuestas de mejora en este momento. Intenta de nuevo más tarde."
        except Exception as e:
            st.error(f"⚠️ Error inesperado:\n\n{e}")
            texto_escenarios = "No se pudieron generar las propuestas de mejora en este momento. Intenta de nuevo más tarde."
else:
    texto_escenarios = st.session_state["ss_escenarios"]

st.markdown(texto_escenarios)

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)