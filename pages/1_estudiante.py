"""
Shadow-Score Académico - Página del Estudiante (v5 - namespace separation)
==========================================================================
ARQUITECTURA DE SESSION_STATE:
  - Claves _w_*  → propiedad exclusiva de Streamlit (widgets).
                   Nunca se borran manualmente; Streamlit las gestiona.
  - Claves ss_*  → propiedad exclusiva de la aplicación (dominio).
                   Son snapshots inmutables tomados al pulsar el botón.

FLUJO:
  1. Si no existe ss_run_id → sesión nueva → limpiar solo ss_*.
  2. El usuario rellena el formulario; los _w_* se actualizan en tiempo real.
  3. Al pulsar "Calcular":
       a. Leer _w_* para validar (valores actuales del formulario).
       b. Si válido → nuevo ss_run_id + snapshots ss_perfil/ss_cargas/ss_promedio.
       c. Borrar ss_resultados y ss_escenarios (forzar recálculo en resultados).
       d. Redirigir a resultados.
  4. Al volver desde resultados → limpiar solo ss_* → _w_* intactos.
"""

import uuid
import sys
from pathlib import Path
import streamlit as st

# Agregar Front_End al path para importar config
sys.path.insert(0, str(Path(__file__).parent.parent))

# ── Importaciones del proyecto ──────────────────────────────────────────────
try:
    from config.estilos_comunes import aplicar_estilos_globales
    from config.colores import (
        COLOR_PRIMARIO,
        COLOR_BOTON_VERDE,
        COLOR_BOTON_VERDE_HOVER,
    )
    aplicar_estilos_globales()
except ImportError:
    # Fallback si se ejecuta fuera del proyecto completo
    COLOR_PRIMARIO         = "#2563eb"
    COLOR_BOTON_VERDE      = "#16a34a"
    COLOR_BOTON_VERDE_HOVER = "#15803d"

# ── Claves de dominio (las únicas que la app puede borrar manualmente) ───────
DOMAIN_KEYS = [
    "ss_run_id",
    "ss_perfil",
    "ss_cargas",
    "ss_promedio",
    "ss_resultados",
    "ss_escenarios",
]

# ============================================================
# 0. LIMPIEZA INICIAL — solo claves de dominio, nunca _w_*
#    Se ejecuta únicamente en sesiones nuevas (sin ss_run_id).
# ============================================================
if "ss_run_id" not in st.session_state:
    for key in DOMAIN_KEYS:
        st.session_state.pop(key, None)

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
        color: #1e293b !important;
    }}
    .stApp label,
    .stMarkdown,
    .stText,
    .stTitle,
    h1, h2, h3, h4, h5, h6,
    p,
    span:not([data-baseweb]) {{
        color: #1e293b !important;
    }}

    /* ── Inputs ── */
    div[data-baseweb="select"] > div,
    .stNumberInput input[type="number"] {{
        background-color: #dbeafe !important;
        border-radius: 8px !important;
        color: #1e293b !important;
        border: 2px solid #3b82f6 !important;
    }}
    div[data-baseweb="select"] > div {{
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
    }}
    div[data-baseweb="select"] > div * {{
        color: #1e293b !important;
        font-weight: 500 !important;
    }}
    div[data-baseweb="select"] input,
    div[data-baseweb="select"] [role="combobox"] {{
        color: #1e293b !important;
        font-weight: 500 !important;
    }}

    /* ── Dropdown (popover) ── */
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

    /* ── Overlay transparente (evita fondo oscuro en dropdowns) ── */
    div[data-baseweb="layer"] > div,
    #stPortal > div {{
        background-color: transparent !important;
        color-scheme: light !important;
        backdrop-filter: none !important;
    }}

    /* ── Alineación vertical de labels en inputs numéricos ── */
    .carga-semanal .stNumberInput label {{
        min-height: 3.2em !important;
        display: flex !important;
        align-items: flex-end !important;
        line-height: 1.4 !important;
        white-space: normal !important;
        word-wrap: break-word !important;
    }}

    /* ── Botón principal ── */
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
    .profile-emoji {{
        font-size: 5rem;
        background-color: #e2e8f0;
        padding: 0.75rem;
        border-radius: 60px;
        display: inline-block;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
    }}

    /* ── Toast ── */
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

    /* ── Info sobre los namespaces (debug, opcional) ── */
    .namespace-note {{
        font-size: 0.75rem;
        color: #94a3b8;
        margin-top: 0.25rem;
    }}
</style>
""", unsafe_allow_html=True)

# ── JS: forzar estilos de popover que Streamlit inyecta fuera del shadow DOM ─
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
# 3. FORMULARIO
#    Todos los widgets usan key="_w_*" para que Streamlit los
#    gestione de forma independiente a las claves de dominio ss_*.
# ============================================================
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
                key="_w_genero",           # ← namespace _w_
            )
            estrato = st.selectbox(
                "Estrato socioeconómico *",
                list(range(1, 7)),
                index=None,
                placeholder="Elige tu estrato",
                key="_w_estrato",
            )

        with col2:
            composicion_hogar = st.selectbox(
                "Composición del hogar *",
                ["Vive solo/a", "Con familia", "Con pareja",
                 "Residencia universitaria", "Otros"],
                index=None,
                placeholder="Selecciona...",
                key="_w_composicion",
            )
            dependientes = st.number_input(
                "Personas a cargo",
                min_value=0, max_value=10, value=0, step=1,
                key="_w_dependientes",
            )

st.markdown("### ⏱️ Carga semanal")
col_c1, col_c2, col_c3 = st.columns(3)

with col_c1:
    horas_domesticas = st.number_input(
        "Horas en tareas domésticas/cuidado",
        min_value=0.0, max_value=168.0, value=0.0, step=1.0,
        key="_w_domesticas",
    )
with col_c2:
    horas_trabajo = st.number_input(
        "Horas de trabajo remunerado",
        min_value=0.0, max_value=168.0, value=0.0, step=1.0,
        key="_w_trabajo",
    )
with col_c3:
    horas_estudio = st.number_input(
        "Horas de estudio declaradas",
        min_value=0.0, max_value=168.0, value=0.0, step=1.0,
        key="_w_estudio",
    )

st.markdown("### 📊 Promedio académico (opcional)")
promedio_actual = st.number_input(
    "Promedio ponderado actual (0.0 – 5.0)",
    min_value=0.0, max_value=5.0,
    value=None, step=0.1,
    placeholder="Ejemplo: 3.8",
    key="_w_promedio",
)
st.caption(
    "Si proporcionas tu promedio actual, el modelo estimará "
    "la posible pérdida de puntos (coste de oportunidad)."
)

# ============================================================
# 4. BOTÓN — VALIDACIÓN Y ESCRITURA EN ss_*
# ============================================================
if st.button("🔍 Calcular mi Shadow-Score", type="primary", width='content'):

    # 4a. Leer los valores actuales del formulario desde session_state por su _w_key.
    #     Esto es equivalente a las variables locales definidas arriba, pero explícito
    #     y seguro: refleja exactamente lo que Streamlit tiene guardado en este instante.
    g   = st.session_state.get("_w_genero")
    e   = st.session_state.get("_w_estrato")
    c   = st.session_state.get("_w_composicion")
    dep = st.session_state.get("_w_dependientes", 0)
    hd  = st.session_state.get("_w_domesticas", 0.0)
    ht  = st.session_state.get("_w_trabajo",    0.0)
    he  = st.session_state.get("_w_estudio",    0.0)
    pm  = st.session_state.get("_w_promedio")

    # 4b. Validación sobre los valores reales del formulario
    errores = []
    if not g:
        errores.append("Género es obligatorio.")
    if e is None:
        errores.append("Estrato es obligatorio.")
    if not c:
        errores.append("Composición del hogar es obligatoria.")

    total_horas = hd + ht + he
    if total_horas <= 0:
        errores.append("Debe ingresar al menos una hora en alguna categoría.")
    elif total_horas > 168:
        errores.append(
            f"La suma de horas ({total_horas:.0f}) excede las 168 horas semanales."
        )

    if errores:
        # Mostrar errores sin tocar ninguna clave (ni _w_* ni ss_*)
        for err in errores:
            st.toast(err, icon="❌", duration=10)

    else:
        # 4c. Limpiar SOLO resultados anteriores — los widgets _w_* no se tocan
        st.session_state.pop("ss_resultados", None)
        st.session_state.pop("ss_escenarios", None)

        # 4d. Generar token de ejecución.
        #     La página de resultados compara este ID con el que acompañó
        #     el último cálculo guardado; si no coinciden, recalcula.
        st.session_state["ss_run_id"] = str(uuid.uuid4())

        # 4e. Guardar snapshots de dominio con los datos del formulario actual
        st.session_state["ss_perfil"] = {
            "genero":            g,
            "estrato":           e,
            "composicion_hogar": c,
            "dependientes":      dep,
        }
        st.session_state["ss_cargas"] = {
            "horas_domesticas": hd,
            "horas_trabajo":    ht,
            "horas_estudio":    he,
        }
        st.session_state["ss_promedio"] = pm

        # 4f. Navegar a la página de resultados
        st.switch_page("pages/3_resultados_estudiantes.py")