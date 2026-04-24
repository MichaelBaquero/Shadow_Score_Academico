"""
Shadow-Score Académico - Frontend Principal
Versión: 1.1.1 - Corrección en mensaje de PPA y mejoras visuales.
"""

import streamlit as st
import sys
from pathlib import Path

# =========================================================
# CONFIGURACIÓN DE RUTAS PARA IMPORTACIÓN DEL BACKEND
# =========================================================
current_file = Path(__file__).resolve()
frontend_dir = current_file.parent
project_root = frontend_dir.parent

if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from Back_end.modelo import ejecutar_modelo
except ImportError as e:
    st.error(f"Error crítico: No se pudo cargar el módulo del modelo matemático.\n\nDetalles: {e}")
    st.info(f"Ruta del proyecto: {project_root}")
    back_end_path = project_root / 'Back_end'
    if back_end_path.exists():
        contenido = list(back_end_path.glob('*'))
        st.info(f"Contenido de Back_end/: {[f.name for f in contenido]}")
    else:
        st.error(f"La carpeta Back_end no existe en {project_root}")
    st.stop()

# =========================================================
# CONFIGURACIÓN DE PÁGINA
# =========================================================
st.set_page_config(
    page_title="Shadow-Score Académico",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo mínimo en escala de grises
st.markdown("""
<style>
    .stApp {
        background-color: #fafafa;
    }
    .main .block-container {
        padding-top: 2rem;
    }
    h1, h2, h3 {
        color: #2c3e50;
    }
    .stButton > button {
        background-color: #4a4a4a;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }
    .stButton > button:hover {
        background-color: #2c2c2c;
    }
    .stError {
        background-color: #fee;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# FUNCIONES AUXILIARES
# =========================================================
def validar_campos_obligatorios(perfil, cargas):
    errores = []
    if not perfil.get('genero'):
        errores.append("Género es obligatorio.")
    if perfil.get('estrato') is None:
        errores.append("Estrato es obligatorio.")
    if not perfil.get('composicion_hogar'):
        errores.append("Composición del hogar es obligatoria.")
    if cargas.get('horas_domesticas') is None or cargas['horas_domesticas'] < 0:
        errores.append("Horas domésticas debe ser un número ≥ 0.")
    if cargas.get('horas_trabajo') is None or cargas['horas_trabajo'] < 0:
        errores.append("Horas de trabajo deben ser un número ≥ 0.")
    if cargas.get('horas_estudio') is None or cargas['horas_estudio'] < 0:
        errores.append("Horas de estudio deben ser un número ≥ 0.")
    total_horas = (cargas.get('horas_domesticas', 0) + 
                   cargas.get('horas_trabajo', 0) + 
                   cargas.get('horas_estudio', 0))
    if total_horas > 168:
        errores.append(f"La suma de horas ({total_horas}) excede 168 (total semanal).")
    return len(errores) == 0, errores

def mostrar_metrica_con_flecha(label, value, delta_value, unidad, es_bueno_si_positivo=True):
    if delta_value > 0:
        flecha = "↑"
        color = "green" if es_bueno_si_positivo else "red"
        texto = f"{flecha} {delta_value:.1f} {unidad}"
    elif delta_value < 0:
        flecha = "↓"
        color = "red" if es_bueno_si_positivo else "green"
        texto = f"{flecha} {abs(delta_value):.1f} {unidad}"
    else:
        texto = "Sin cambio"
        color = "gray"
    st.metric(label, value)
    st.markdown(f"<span style='color:{color}; font-weight:bold;'>{texto}</span>", 
                unsafe_allow_html=True)

def generar_plan_accion_ia(perfil, cargas, resultados):
    raise NotImplementedError("La integración con IA aún no está implementada.")

# =========================================================
# INTERFAZ PRINCIPAL
# =========================================================
def main():
    st.title("📊 Shadow-Score Académico")
    st.markdown("""
    **Reflexiona sobre la distribución de tu tiempo desde una perspectiva de género.**  
    Esta herramienta te ayuda a visualizar cómo las responsabilidades domésticas y laborales 
    pueden afectar tu rendimiento académico, y te ofrece un plan de acción personalizado.
    """)
    st.divider()

    with st.sidebar:
        st.header("📝 Tus Datos")
        st.subheader("👤 Perfil")
        col1, col2 = st.columns(2)
        with col1:
            genero = st.selectbox("Género *", ["Femenino", "Masculino"], index=None, placeholder="Selecciona una opción")
            estrato = st.selectbox("Estrato socioeconómico *", list(range(1,7)), index=None, placeholder="Elige tu estrato")
        with col2:
            composicion_hogar = st.selectbox("Composición del hogar *", 
                                            ["Vive solo/a", "Con familia", "Con pareja", "Residencia universitaria", "Otros"],
                                            index=None, placeholder="Selecciona...")
            dependientes = st.number_input("Personas a cargo", 0, 10, 0, 1)
        st.divider()
        st.subheader("⏱️ Carga Semanal *")
        horas_domesticas = st.number_input("Horas en tareas domésticas y de cuidado", 0.0, 168.0, 0.0, 1.0)
        horas_trabajo = st.number_input("Horas de trabajo remunerado", 0.0, 168.0, 0.0, 1.0)
        horas_estudio = st.number_input("Horas de estudio declaradas", 0.0, 168.0, 0.0, 1.0)
        st.divider()
        st.subheader("📚 Dato Académico Opcional")
        promedio_actual = st.number_input("Promedio ponderado actual (0.0 - 5.0)", 0.0, 5.0, None, 0.1)
        calcular_clicked = st.button("🔍 Calcular mi Shadow-Score", type="primary", use_container_width=True)

    if calcular_clicked:
        perfil = {'genero': genero, 'estrato': estrato, 'composicion_hogar': composicion_hogar, 'dependientes': dependientes}
        cargas = {'horas_domesticas': horas_domesticas, 'horas_trabajo': horas_trabajo, 'horas_estudio': horas_estudio}
        es_valido, errores = validar_campos_obligatorios(perfil, cargas)
        if not es_valido:
            for error in errores:
                st.error(f"❌ {error}")
        else:
            try:
                resultados = ejecutar_modelo(perfil, cargas, promedio_actual)
                st.session_state['perfil'] = perfil
                st.session_state['cargas'] = cargas
                st.session_state['resultados'] = resultados
                st.success("✅ Cálculo completado. Revisa tus indicadores abajo.")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    mostrar_metrica_con_flecha("Shadow-Score", f"{resultados['shadow_score']:.0f} / 100",
                                               -resultados['shadow_score'], "puntos", es_bueno_si_positivo=True)
                with col2:
                    st.metric("Fatiga Cognitiva", f"{resultados['fatiga']:.1%}")
                with col3:
                    coste = resultados['coste_horas']
                    mostrar_metrica_con_flecha("Horas Efectivas de Estudio", f"{resultados['horas_efectivas']:.1f} h",
                                               -coste, "h", es_bueno_si_positivo=True)
                
                with st.expander("📈 Ver más detalles"):
                    st.write(f"**Carga total semanal (doméstica + laboral):** {resultados['carga_total']:.1f} horas")
                    st.write(f"**Promedio estimado según condiciones:** {resultados['ppa_estimado']:.2f}")
                    if resultados['coste_ppa'] is not None:
                        afectacion = resultados['coste_ppa']
                        if afectacion > 0:
                            st.markdown(f"**✅ Tu promedio está <span style='color:green;'>↑ {afectacion:.2f} puntos por encima</span> del esperado. ¡Excelente!**", unsafe_allow_html=True)
                        elif afectacion < 0:
                            st.markdown(f"**⚠️ Posible afectación en tu promedio: <span style='color:red;'>↓ {abs(afectacion):.2f} puntos por debajo</span> del esperado.**", unsafe_allow_html=True)
                        else:
                            st.write("**Tu promedio coincide exactamente con el estimado.**")
                    else:
                        st.write("**Promedio actual no ingresado.** No se calcula diferencia.")
                
                st.markdown("---")
                st.subheader("🤔 Momento de reflexión")
                st.markdown("> *¿Qué cambiaría si pudieras redistribuir tus tareas domésticas?*")
                st.markdown("> *¿Conoces los apoyos que ofrece tu universidad (guardería, becas, tutorías)?*")
            except Exception as e:
                st.error(f"Ocurrió un error inesperado: {e}")

    if 'resultados' in st.session_state:
        st.divider()
        st.subheader("🤖 Plan de Acción Personalizado con IA")
        if st.button("✨ Generar plan de acción", type="secondary"):
            with st.spinner("Consultando a Gemini..."):
                try:
                    plan = generar_plan_accion_ia(st.session_state['perfil'], st.session_state['cargas'], st.session_state['resultados'])
                    st.markdown(plan)
                except NotImplementedError:
                    st.warning("🚧 La integración con IA estará disponible próximamente.")
                except Exception as e:
                    st.error(f"No se pudo generar el plan: {e}")
    else:
        st.info("👆 Completa el formulario y calcula tu Shadow-Score para recibir un plan personalizado.")

if __name__ == "__main__":
    main()