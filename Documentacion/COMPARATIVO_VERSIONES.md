# Comparativa de versiones: Shadow-Score Académico

Este documento resume las diferencias clave entre las versiones del proyecto **Shadow-Score Académico**, desarrolladas entre marzo y abril de 2026. La evolución refleja la incorporación de retroalimentación, la ampliación del modelo matemático, la integración de inteligencia artificial y la adición de un módulo administrativo para análisis institucional.

## Cuadro comparativo

| **Característica** | **Versión 1 (Informe inicial)** | **Versión 2 (Multifactorial)** | **Versión 3 (Con asistente IA)** | **Versión 4 (Con módulo administrativo)** |
|-------------------|--------------------------------|-------------------------------|----------------------------------|-------------------------------------------|
| **Objetivo general** | Estimar el efecto de la carga doméstica en el rendimiento académico. | Integrar modelo multifactorial (carga doméstica, laboral, composición del hogar, contexto). | Igual que v2, más planes de acción personalizados con IA. | Igual que v3, más **análisis masivo para la universidad** mediante carga CSV, ETL y dashboards. |
| **Roles de usuario** | Solo estudiante individual. | Solo estudiante individual. | Solo estudiante individual. | **Estudiante** (individual + IA) y **Administrativo** (carga masiva, dashboards, sin IA). |
| **Modelo matemático** | Básico: fatiga sigmoidea → horas efectivas → Shadow-Score. | Multifactorial: añade trabajo remunerado, composición hogar, dependientes, percepción. | Mismo que v2, más **coste de oportunidad** (horas y PPA). | **Mismo modelo que v3** – se aplica idénticamente a estudiantes individuales y a lotes CSV. |
| **Variables de entrada (estudiante)** | Género, estrato, horas domésticas, horas estudio, promedio, dependientes. | Añade composición hogar, trabajo remunerado (sí/no + horas). | Igual que v2. | Igual que v3. |
| **Entrada masiva (administrativo)** | No aplica. | No aplica. | No aplica. | Archivo CSV con misma estructura base + `id_estudiante`. Se procesa por **ETL** (validación, limpieza, transformación) usando Pandas. |
| **Simulación de escenarios** | Corresponsabilidad (reducción fija 40%). | Corresponsabilidad + apoyo institucional (reduce fatiga). | Igual que v2. | Individual (estudiante) y **agregada** (administrativo puede simular reducción de carga doméstica en toda la muestra). |
| **Asistente IA** | No. | No. | **Sí** (OpenAI/Gemini) para planes personalizados del estudiante. | **Sí para estudiante**; **No para administrativo** (por manejo de datos sensibles). |
| **Dashboards / visualización** | Gráficos individuales (radar, barras, gauge). | Ídem. | Ídem. | **Añade dashboards institucionales**: distribución de Shadow-Score, brechas de género, segmentación por estrato, simulación agregada, exportación de reportes. |
| **Procesamiento de datos** | En memoria por sesión. | En memoria por sesión. | En memoria por sesión. | **ETL + estructuras internas (Pandas)**; no se usa base de datos externa. |
| **Tecnologías clave** | Streamlit, Pandas, NumPy, Plotly. | Las mismas. | Las mismas + OpenAI/Gemini API. | Las mismas + **ETL con Pandas**, autenticación para rol administrativo. |
| **Privacidad y seguridad** | No almacenar datos personales. | Ídem. | Ídem. | **Sin IA en rol admin**, anonimización, autenticación, cumplimiento Ley 1581. Los CSV no se conservan. |
| **Despliegue** | Streamlit Cloud. | Streamlit Cloud. | Streamlit Cloud. | Streamlit Cloud. |
| **Énfasis principal** | Visibilizar pobreza de tiempo. | Reconocer multifactorialidad. | Transformar reflexión en acción (IA). | **Dotar a la institución de herramientas de análisis masivo** para la toma de decisiones en equidad y permanencia. |

## Resumen evolutivo

- **Versión 1** – Prueba de concepto centrada en la carga doméstica.
- **Versión 2** – Modelo más realista al incluir trabajo remunerado y composición del hogar.
- **Versión 3** – Salto cualitativo: la IA genera planes de acción personalizados.
- **Versión 4** – Expansión al ámbito institucional: permite a la universidad cargar datos de múltiples estudiantes, procesarlos mediante ETL (mismo modelo), visualizar dashboards agregados y simular políticas de corresponsabilidad a nivel de muestra, **sin exponer datos sensibles a IA externa**.

La **versión 4** es la actualmente en producción, pues cubre tanto la experiencia individual del estudiante (con IA) como las necesidades de análisis institucional de Unicafam.