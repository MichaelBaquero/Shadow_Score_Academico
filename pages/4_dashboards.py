# 4_Dashboards.py
# Módulo administrativo: panel de dashboards con 4 gráficos + tabla de datos.
# ----------------------------------------------------------------------------
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import sys
from pathlib import Path

# ── Agregar rutas para imports ──
sys.path.insert(0, str(Path(__file__).parent.parent))

# ── Configuración de página ──
st.set_page_config(page_title="Shadow-Score · Admin", layout="wide")

# ── Estilos globales compartidos ──
try:
    from config.estilos_comunes import aplicar_estilos_globales
    aplicar_estilos_globales()
except ImportError:
    pass

# ── Colores del sistema de diseño ──
try:
    from config.colores import (
        COLOR_PRIMARIO,
        COLOR_FONDO_TARJETA,
        COLOR_TEXTO_PRINCIPAL,
        COLOR_TEXTO_SECUNDARIO,
    )
except ImportError:
    COLOR_PRIMARIO         = "#2563eb"
    COLOR_FONDO_TARJETA    = "#ffffff"
    COLOR_TEXTO_PRINCIPAL  = "#1e293b"
    COLOR_TEXTO_SECUNDARIO = "#64748b"

COLOR_NEGRO = "#000000"

# ================================================================
# CSS DEFINITIVO (Tarjeta con gráfico integrado)
# ================================================================
st.markdown(f"""
<style>
    .stApp, .main, .block-container,
    [data-testid="stAppViewContainer"],
    [data-testid="stHeader"] {{
        background-color: #ffffff !important;
        color: {COLOR_TEXTO_PRINCIPAL} !important;
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
        color: #ffffff !important;
        padding: 0.5rem 1.2rem;
        border-radius: 48px;
        font-size: 1.2rem !important;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 10px;
    }}
    .role-badge span {{ font-size: 1.4rem; color: #ffffff !important; }}

    .metric-card {{
        background-color: {COLOR_FONDO_TARJETA};
        border-radius: 16px;
        padding: 1.2rem 1.5rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        text-align: center;
        height: 100%;
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

    /* ══ TARJETA DE GRÁFICO DEFINITIVA ══ */
    .chart-card {{
        background: {COLOR_FONDO_TARJETA};
        border-radius: 12px;
        border: 1px solid #dde1e6;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        padding: 0.8rem;
    }}

    .chart-title {{
        text-align: center;
        font-size: 1rem;
        font-weight: 700;
        color: {COLOR_NEGRO};
        margin-bottom: 0.5rem;
    }}
</style>
""", unsafe_allow_html=True)

# ================================================================
# CABECERA
# ================================================================
st.markdown(f"""
<div class="custom-header">
    <div class="project-title">📊 Shadow-Score Académico</div>
    <div class="role-badge">
        <span>🛡️</span> Administrador
    </div>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# CARGA DE DATOS REALES PROCESADOS
# ════════════════════════════════════════════════════════════════
if "df_resultados" not in st.session_state or st.session_state.df_resultados is None:
    st.warning("No hay datos procesados. Por favor carga y procesa un archivo CSV desde la página de Administración.")
    st.page_link("pages/2_Administrativo.py", label="Ir a Administración", icon="⬅️")
    st.stop()

df = st.session_state.df_resultados.copy()

# Función para categorizar el Shadow-Score
def categorizar(score):
    if score <= 20:
        return "Baja"
    elif score <= 40:
        return "Moderada"
    elif score <= 60:
        return "Significativa"
    elif score <= 80:
        return "Alta"
    else:
        return "Extrema"

df["categoria"] = df["shadow_score"].apply(categorizar)

# ════════════════════════════════════════════════════════════════
# TARJETAS DE RESUMEN (con datos reales)
# ════════════════════════════════════════════════════════════════
col1, col2, col3 = st.columns(3)

with col1:
    total = len(df)
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">🎓 Estudiantes analizados</div>
        <div class="metric-value" style="color:{COLOR_PRIMARIO}">{total}</div>
        <div class="metric-subtext">Registros procesados</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    shadow_mean = df["shadow_score"].mean()
    # Moda (valor más frecuente), si hay empate se toma el primero
    cat = df["categoria"].mode()
    if not cat.empty:
        cat_str = cat[0]
    else:
        cat_str = "—"
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">📈 Shadow‑Score medio</div>
        <div class="metric-value" style="color:#f59e0b;">{shadow_mean:.1f}%</div>
        <div class="metric-subtext">Categoría "{cat_str}"</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    # fatiga es un valor entre 0 y 1, lo convertimos a porcentaje
    fatiga_mean = df["fatiga"].mean() * 100
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">🧠 Fatiga media</div>
        <div class="metric-value" style="color:#e11d48;">{fatiga_mean:.1f}%</div>
        <div class="metric-subtext">0% (sin fatiga) – 100% (máxima)</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# MÉTRICAS INSTITUCIONALES (4 GRÁFICOS EN TARJETAS)
# ════════════════════════════════════════════════════════════════
st.markdown("## 📈 Métricas institucionales")

c1, c2, c3, c4 = st.columns(4)

# ── Gráfico 1: Distribución de Shadow-Score ──
with c1:
    st.markdown('<div class="chart-title">Shadow-Score</div>', unsafe_allow_html=True)
    cat_counts = df["categoria"].value_counts().reindex(
        ["Baja", "Moderada", "Significativa", "Alta", "Extrema"], fill_value=0
    )
    fig1 = go.Figure(data=[go.Bar(
        x=cat_counts.index,
        y=cat_counts.values,
        marker_color=["#10b981", "#f59e0b", "#fbbf24", "#f87171", "#ef4444"],
        text=cat_counts.values,
        textposition='outside',
        textfont=dict(color=COLOR_NEGRO, size=10)
    )])
    fig1.update_layout(
        margin=dict(l=5, r=5, t=5, b=10),
        height=220,
        yaxis=dict(showgrid=False, visible=False, range=[0, max(cat_counts.values) * 1.15]),
        xaxis=dict(tickfont=dict(color=COLOR_NEGRO, size=9)),
        showlegend=False,
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff"
    )
    st.plotly_chart(fig1, width='stretch', config={'displayModeBar': False})

# ── Gráfico 2: Fatiga media (Gauge) ──
with c2:
    st.markdown('<div class="chart-title">Fatiga media</div>', unsafe_allow_html=True)
    fig2 = go.Figure(go.Indicator(
        mode="gauge+number",
        value=fatiga_mean,
        number={"font": {"size": 32, "color": COLOR_NEGRO}},
        domain={"x": [0, 1], "y": [0, 1]},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": COLOR_NEGRO,
                     "tickfont": {"size": 10, "color": COLOR_NEGRO}},
            "bar": {"color": "#2563eb", "thickness": 0.25},
            "steps": [
                {"range": [0, 30], "color": "#10b981"},
                {"range": [30, 60], "color": "#f59e0b"},
                {"range": [60, 100], "color": "#e11d48"},
            ],
        },
    ))
    fig2.update_layout(
        height=220,
        margin=dict(l=15, r=15, t=5, b=10),
        paper_bgcolor="#ffffff",
        font={"color": COLOR_NEGRO, "family": "Arial", "size": 11},
        showlegend=False
    )
    st.plotly_chart(fig2, width='stretch', config={'displayModeBar': False})

# ── Gráfico 3: Brecha de género en Shadow-Score ──
with c3:
    st.markdown('<div class="chart-title">Brecha de género</div>', unsafe_allow_html=True)
    # Asegurar que la columna se llame 'Género' (ya viene del CSV)
    gen_agg = df.groupby("Género")["shadow_score"].mean().reset_index()
    fig3 = px.bar(
        gen_agg, x="Género", y="shadow_score",
        color="Género",
        color_discrete_map={"Femenino": "#f472b6", "Masculino": "#60a5fa"},
        text="shadow_score"
    )
    fig3.update_traces(
        texttemplate="%{y:.1f}",
        textposition='outside',
        textfont=dict(color=COLOR_NEGRO, size=11)
    )
    fig3.update_layout(
        margin=dict(l=5, r=5, t=5, b=10),
        height=220,
        xaxis=dict(showgrid=False, visible=True, tickfont=dict(color=COLOR_NEGRO, size=9)),
        yaxis=dict(showgrid=False, visible=False, range=[0, max(gen_agg['shadow_score']) * 1.15]),
        showlegend=False,
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff"
    )
    st.plotly_chart(fig3, width='stretch', config={'displayModeBar': False})

# ── Gráfico 4: Distribución de horas efectivas ──
with c4:
    st.markdown('<div class="chart-title">Horas efectivas</div>', unsafe_allow_html=True)
    fig4 = go.Figure(data=[go.Histogram(
        x=df["horas_efectivas"],
        marker_color="#2563eb",
        opacity=0.70,
    )])
    fig4.update_layout(
        margin=dict(l=5, r=5, t=5, b=15),
        height=220,
        xaxis=dict(
            showgrid=False,
            title=dict(text="h/semana", font=dict(color=COLOR_NEGRO, size=9)),
            tickfont=dict(color=COLOR_NEGRO, size=9)
        ),
        yaxis=dict(showgrid=False, visible=False),
        showlegend=False,
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff"
    )
    st.plotly_chart(fig4, width='stretch', config={'displayModeBar': False})

# ════════════════════════════════════════════════════════════════
# TABLA DE DATOS COMPLETA
# ════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown("## 📋 Tabla de resultados")

# Seleccionar y renombrar columnas para la visualización
columnas_para_tabla = [
    "IDEstudiante", "Género", "Estrato",
    "CargaDomestica", "CargaLaboral", "CargaAcademica",
    "horas_efectivas", "fatiga", "shadow_score", "categoria"
]
tabla_mostrar = df[columnas_para_tabla].copy()

# Convertir fatiga a porcentaje (viene entre 0-1)
tabla_mostrar["fatiga"] = (tabla_mostrar["fatiga"] * 100).round(1)
tabla_mostrar["shadow_score"] = tabla_mostrar["shadow_score"].round(1)
tabla_mostrar["horas_efectivas"] = tabla_mostrar["horas_efectivas"].round(1)

# Traducir nombres para la vista
tabla_mostrar.columns = [
    "ID Estudiante", "Género", "Estrato",
    "Horas domésticas", "Horas trabajo", "Horas estudio",
    "Horas efectivas", "Fatiga (%)", "Shadow-Score", "Categoría"
]

st.dataframe(
    tabla_mostrar,
    width='stretch',
    column_config={
        "Categoría": st.column_config.TextColumn("Categoría"),
        "Fatiga (%)": st.column_config.NumberColumn(format="%.1f%%"),
        "Shadow-Score": st.column_config.NumberColumn(format="%.1f"),
    },
    height=400
)

st.caption(f"📌 Total registros: {len(df)}. Datos reales procesados desde el archivo CSV.")