import streamlit as st
import pandas as pd
import sys
from pathlib import Path
from dataclasses import dataclass, field

# ── Ajustar PATH para importar backend ──────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
from Back_end.validacion_csv import validar_archivo_csv

# ── Estilos globales compartidos ─────────────────────────────────────────────────
try:
    from config.estilos_comunes import aplicar_estilos_globales
    aplicar_estilos_globales()
except ImportError:
    pass

# ── Colores del sistema de diseño ────────────────────────────────────────────────
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

# ================================================================
# 0. DATACLASS DE ESTADO
# ================================================================
@dataclass
class UploadState:
    csv_valido: bool = False
    df_valido: object = None
    mensajes_validacion: list = field(default_factory=list)
    archivo_cargado: bool = False
    estado_upload: str = "esperando"   # "esperando" | "valido" | "invalido"
    nombre_archivo: str | None = None

if "upload_state" not in st.session_state:
    st.session_state.upload_state = UploadState()

def _s() -> UploadState:
    return st.session_state.upload_state

# ================================================================
# 1. CSS (INCLUYE CORRECCIÓN DE CONTRASTE DEL BOTÓN DESHABILITADO)
# ================================================================
st.markdown(f"""
<style>
    /* ── Fondo blanco global ── */
    .stApp, .main, .block-container,
    [data-testid="stAppViewContainer"],
    [data-testid="stHeader"] {{
        background-color: #ffffff !important;
    }}

    /* ── Texto base — solo elementos de layout, no componentes internos ── */
    .stApp label,
    .stMarkdown, .stText, .stTitle,
    h1, h2, h3, h4, h5, h6, p {{
        color: {COLOR_TEXTO_PRINCIPAL} !important;
    }}

    /* ── Alertas: fondo de color + texto muy oscuro ── */
    div[data-testid="stInfo"] {{
        background-color: #e0f2fe !important;
        border-left: 4px solid {COLOR_PRIMARIO} !important;
    }}
    div[data-testid="stSuccess"] {{
        background-color: #dcfce7 !important;
        border-left: 4px solid #10b981 !important;
    }}
    div[data-testid="stWarning"] {{
        background-color: #fef3c7 !important;
        border-left: 4px solid #f59e0b !important;
    }}
    div[data-testid="stError"] {{
        background-color: #fee2e2 !important;
        border-left: 4px solid #ef4444 !important;
    }}
    div[data-testid="stInfo"] *,
    div[data-testid="stSuccess"] *,
    div[data-testid="stWarning"] *,
    div[data-testid="stError"] * {{
        color: #0f172a !important;
    }}

    /* ── Tooltip: fondo CLARO con texto OSCURO
           Se evita fondo oscuro para no pelear con el CSS global de texto.
           Contraste garantizado sin selector wars. ── */
    div[data-baseweb="tooltip"] {{
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        padding: 10px 14px !important;
        font-size: 13px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;
        z-index: 9999 !important;
        max-width: 320px !important;
    }}
    /* Forzar blanco con !important Y especificidad alta
       declarando el color en el propio contenedor y en cada hijo */
    div[data-baseweb="tooltip"],
    div[data-baseweb="tooltip"] div,
    div[data-baseweb="tooltip"] p,
    div[data-baseweb="tooltip"] span,
    div[data-baseweb="tooltip"] small,
    div[data-baseweb="tooltip"] li,
    div[data-baseweb="tooltip"] ul {{
        color: #ffffff !important;
        background-color: transparent !important;
    }}

    /* ── Toast: fondo claro, texto oscuro ── */
    div[data-testid="stToast"] {{
        background-color: #f8fafc !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.12) !important;
    }}
    div[data-testid="stToast"],
    div[data-testid="stToast"] div,
    div[data-testid="stToast"] p,
    div[data-testid="stToast"] span {{
        color: #0f172a !important;
    }}

    /* ── Separador de secciones ── */
    hr.section-divider {{
        border: none;
        border-top: 2px solid #e2e8f0;
        margin: 2rem 0;
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

    /* ── Tabla de ejemplo con scroll ── */
    .scrollable-table-container {{
        position: relative;
        overflow-x: auto;
        white-space: nowrap;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        background: {COLOR_FONDO_TARJETA};
    }}
    .scrollable-table-container::after {{
        content: "";
        position: absolute;
        inset: 0;
        z-index: 10;
        cursor: default;
    }}

    /* ── Uploader contenedor ── */
    [data-testid="stFileUploader"] {{
        background-color: {COLOR_FONDO_TARJETA} !important;
        border: 2px solid #d1d5db !important;
        border-radius: 12px !important;
        padding: 1.5rem !important;
        transition: border-color 0.2s;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }}
    [data-testid="stFileUploader"]:hover {{
        border-color: {COLOR_PRIMARIO} !important;
    }}
    [data-testid="stFileUploader"] > label {{
        color: {COLOR_TEXTO_PRINCIPAL} !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
    }}

    /* ── Zona de drop interna ── */
    [data-testid="stFileUploaderDropzone"] {{
        background-color: #f8fafc !important;
        border: 2px dashed #cbd5e1 !important;
        border-radius: 8px !important;
        transition: background-color 0.2s, border-color 0.2s;
    }}
    [data-testid="stFileUploaderDropzone"]:hover {{
        background-color: #eff6ff !important;
        border-color: {COLOR_PRIMARIO} !important;
    }}
    [data-testid="stFileUploaderDropzoneInstructions"] span {{
        color: {COLOR_TEXTO_PRINCIPAL} !important;
        font-weight: 500 !important;
    }}
    [data-testid="stFileUploaderDropzoneInstructions"] small {{
        color: {COLOR_TEXTO_SECUNDARIO} !important;
    }}
    [data-testid="stFileUploaderDropzone"] svg {{
        fill: {COLOR_PRIMARIO} !important;
    }}
    [data-testid="stFileUploaderDropzone"] button {{
        background-color: {COLOR_PRIMARIO} !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
    }}

    /* ── Archivo cargado dentro del uploader ── */
    [data-testid="stFileUploaderFileName"],
    [data-testid="stFileUploaderFileName"] * {{
        color: {COLOR_TEXTO_PRINCIPAL} !important;
        opacity: 1 !important;
    }}

    /* ── Chip nombre de archivo (debajo del uploader) ── */
    .file-status {{
        background-color: #eff6ff;
        border: 1px solid #bfdbfe;
        border-radius: 8px;
        padding: 10px 16px;
        margin: 8px 0 0 0;
        color: #1d4ed8 !important;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 8px;
    }}

    /* ── Botón Procesar ── */
    .stButton > button {{
        border-radius: 12px !important;
        padding: 0.6rem 1.2rem !important;
        font-weight: bold !important;
        width: 100%;
        transition: background-color 0.2s, transform 0.1s;
    }}
    .stButton > button:not([disabled]) {{
        background-color: {COLOR_PRIMARIO} !important;
        color: #ffffff !important;
        border: none !important;
        box-shadow: 0 2px 8px rgba(37, 99, 235, 0.25) !important;
    }}
    .stButton > button:not([disabled]):hover {{
        background-color: #1d4ed8 !important;
        transform: scale(1.02);
    }}
    
    /* ── NUEVO: Estilos específicos para el botón deshabilitado ── */
    .stButton > button:disabled {{
        background-color: #f1f5f9 !important;  /* Gris muy claro */
        color: #64748b !important;            /* Gris oscuro (viene de tus constantes) */
        border: 1px solid #e2e8f0 !important; /* Borde sutil */
        cursor: not-allowed !important;       /* Icono de no permitido */
        opacity: 1 !important;                /* Sin transparencia extra */
    }}
</style>
""", unsafe_allow_html=True)

# ================================================================
# 2. CABECERA
# ================================================================
st.markdown(f"""
<div class="custom-header">
    <div class="project-title">📊 Shadow-Score Académico</div>
    <div class="role-badge">
        <span>🛡️</span> Administrador
    </div>
</div>
""", unsafe_allow_html=True)

# ================================================================
# 3. TABLA DE EJEMPLO (solo visual, scroll habilitado)
# ================================================================
st.markdown("### 📋 Vista previa del formato de datos esperado")

datos_ejemplo = {
    "IDEstudiante":         ["20123456", "20123457", "20123458", "20123459"],
    "Género":               ["Femenino", "Masculino", "Femenino", "Masculino"],
    "Estrato":              [3, 2, 5, 4],
    "ComposiciónHogar":     ["Con familia", "Vive solo/a", "Residencia universitaria", "Con pareja"],
    "PersonasDependientes": [2, 0, 0, 1],
    "CargaDomestica":       [10, 5, 2, 8],
    "CargaLaboral":         [0, 15, 8, 20],
    "CargaAcademica":       [25, 20, 30, 18],
    "PromedioActual":       [3.8, 3.5, 4.2, 3.1],
}
df_ejemplo = pd.DataFrame(datos_ejemplo)

with st.container():
    st.markdown('<div class="scrollable-table-container">', unsafe_allow_html=True)
    st.dataframe(
        df_ejemplo,
        use_container_width=False,
        hide_index=True,
        column_config={
            "IDEstudiante":   "ID Estudiante",
            "CargaDomestica": st.column_config.NumberColumn("Carga Doméstica (h)"),
            "CargaLaboral":   st.column_config.NumberColumn("Carga Laboral (h)"),
            "CargaAcademica": st.column_config.NumberColumn("Carga Académica (h)"),
            "PromedioActual": st.column_config.NumberColumn("Promedio Actual", format="%.1f"),
        },
    )
    st.markdown('</div>', unsafe_allow_html=True)

st.caption("💡 *Ejemplo con scroll horizontal. Asegúrate de que tu CSV tenga exactamente estas columnas.*")

st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# ================================================================
# 4. CALLBACK DE VALIDACIÓN
# ================================================================
def validar_archivo_automatico() -> None:
    """
    Callback seguro para st.file_uploader.
    Usa .get() para evitar AttributeError si la clave no existe todavía.
    """
    archivo = st.session_state.get("cargador_csv")
    s = _s()

    if archivo is None:
        s.csv_valido          = False
        s.df_valido           = None
        s.mensajes_validacion = []
        s.archivo_cargado     = False
        s.estado_upload       = "esperando"
        s.nombre_archivo      = None
        return

    s.nombre_archivo = archivo.name

    with st.spinner("🔍 Validando estructura del archivo CSV..."):
        es_valido, df_validado, mensajes = validar_archivo_csv(archivo)

    s.csv_valido          = es_valido
    s.df_valido           = df_validado
    s.mensajes_validacion = mensajes
    s.archivo_cargado     = True

    if es_valido:
        s.estado_upload = "valido"
        st.toast(f"✅ CSV válido — {len(df_validado)} registros listos.", icon="✅", duration=8)
    else:
        s.estado_upload = "invalido"
        if mensajes:
            st.toast(f"❌ {mensajes[0]}", icon="❌", duration=8)

# ================================================================
# 5. SECCIÓN DE CARGA
# ================================================================
st.subheader("📂 Cargar datos reales")

st.file_uploader(
    "Arrastra o selecciona tu archivo CSV",
    type=["csv"],
    key="cargador_csv",
    label_visibility="visible",
    on_change=validar_archivo_automatico,
    help=(
        "El archivo debe cumplir con las siguientes condiciones:\n\n"
        "• Formato: CSV con separador coma (,)\n"
        "• Columnas requeridas (en cualquier orden):\n"
        "  IDEstudiante, Género, Estrato, ComposiciónHogar,\n"
        "  PersonasDependientes, CargaDomestica, CargaLaboral,\n"
        "  CargaAcademica, PromedioActual\n"
        "• Sin columnas extra ni nombres distintos a los indicados\n"
        "• PromedioActual debe estar entre 0.0 y 5.0\n"
        "• No se permiten filas completamente vacías"
    ),
)

if _s().nombre_archivo:
    st.markdown(
        f'<div class="file-status">📄 {_s().nombre_archivo}</div>',
        unsafe_allow_html=True,
    )

# ================================================================
# 6. RESUMEN PERSISTENTE DE VALIDACIÓN
# ================================================================
estado = _s().estado_upload

if estado == "valido":
    st.success(
        f"✅ **{len(_s().df_valido)} registros válidos** cargados correctamente y listos para procesar."
    )
elif estado == "invalido":
    with st.expander("❌ Errores de validación — haz clic para ver el detalle", expanded=True):
        for msg in _s().mensajes_validacion:
            st.error(msg)

# ================================================================
# 7. BOTÓN PROCESAR (SIN HELP, CONTRASTE CORREGIDO)
# ================================================================
_, col_proc, _ = st.columns([3, 2, 3])

with col_proc:
    if estado == "valido":
        # Botón habilitado con contraste correcto (Azul sobre blanco desde el CSS)
        if st.button(
            "⚙️ Procesar",
            use_container_width=True,
            key="btn_procesar"
            # El parámetro 'help' ha sido eliminado (tu petición)
        ):
            with st.spinner("🔄 Procesando datos..."):
                st.success("✅ Procesamiento iniciado (funcionalidad en desarrollo).")
                st.toast("🔄 Procesando… (funcionalidad en desarrollo)", icon="🔄", duration=8)
    else:
        # Botón deshabilitado. El CSS aplica #f1f5f9 con texto #64748b y borde sutil.
        st.button(
            "⚙️ Procesar",
            use_container_width=True,
            disabled=True,
            key="btn_procesar_disabled"
        )