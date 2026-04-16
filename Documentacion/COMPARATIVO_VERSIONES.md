# Comparativa de versiones: Shadow-Score Académico

Este documento resume las diferencias clave entre las tres versiones del proyecto **Shadow-Score Académico**, desarrolladas entre marzo y abril de 2026. La evolución refleja la incorporación de retroalimentación, la ampliación del modelo matemático y la integración de inteligencia artificial para generar recomendaciones personalizadas.

## Cuadro comparativo

| **Característica** | **Versión 1 (Informe inicial)** | **Versión 2 (Multifactorial)** | **Versión 3 (Con asistente IA)** |
|-------------------|--------------------------------|-------------------------------|----------------------------------|
| **Objetivo general** | Estimar el efecto de la carga doméstica en el rendimiento académico y visualizar el beneficio de una distribución equitativa de tareas. | Integrar un modelo multifactorial que incluya carga doméstica, laboral, composición del hogar y contexto, con enfoque de autorreflexión. | Igual que la versión 2, pero además generar planes de acción personalizados mediante IA para convertir la reflexión en acción. |
| **Modelo matemático** | Básico: carga doméstica → fatiga sigmoidea (con ajuste por género y estrato) → horas efectivas → promedio estimado → Shadow-Score. | Multifactorial: añade **trabajo remunerado**, **composición del hogar**, **dependientes** y **percepción subjetiva**. Fórmulas ampliadas. | Mismo modelo multifactorial de la versión 2, más **cálculo explícito del coste de oportunidad** (horas perdidas y diferencia de promedio). |
| **Variables de entrada** | Género, estrato, horas domésticas (desglose), horas de estudio, promedio actual, dependientes. | Añade: composición del hogar (categórica), trabajo remunerado (sí/no + horas). | Igual que versión 2. |
| **Simulación de escenarios** | Corresponsabilidad con reducción fija (40%) de carga doméstica. Comparación lado a lado (gemelos digitales). | Corresponsabilidad + **apoyo institucional** (reducción de fatiga). Porcentaje de reducción ajustable. | Igual que versión 2. |
| **Asistente IA** | No incluye. | No incluye. | **Sí**: Integración con API externa (OpenAI GPT-4o mini o Gemini Flash). Genera planes de acción personalizados basados en perfil y coste de oportunidad. |
| **Interfaz de usuario** | Formulario básico, medidores (batería), gráfico de radar, barras, st.progress. | Similar, pero con énfasis en **autorreflexión** y elementos contextuales (DANE, ODS). | Igual que versión 2, más **botón específico** para generar plan IA con spinner y manejo de errores. |
| **Tecnologías clave** | Streamlit, Pandas, NumPy, Plotly, Streamlit-extras. | Las mismas. | Las mismas + **OpenAI/Gemini API**, requests/httpx, manejo de secretos (.streamlit/secrets.toml). |
| **Estructura de proyecto** | `src/modelo.py`, `utils.py`, `graficos.py`, `app.py`, `assets/`. | No se detalla, pero similar. | Añade `ia_prompts.py` para plantillas de prompting. |
| **Cronograma (semanas)** | 12 semanas (con dedicación parcial). | 9 semanas (más compacto). | 10 semanas (incluye integración IA en semana 5). |
| **Énfasis principal** | Visibilizar la pobreza de tiempo y la penalización académica por carga doméstica. | Reconocer la **multifactorialidad** del fenómeno (trabajo, hogar, contexto). | **Transformar la reflexión en acción** mediante recomendaciones concretas generadas por IA. |
| **Privacidad y datos** | No almacenar datos personales sin consentimiento. Posible futura base de datos anónima. | Mismo enfoque. | Mismo enfoque. Además, la llamada a API no almacena datos. |
| **Despliegue** | Streamlit Cloud. | Streamlit Cloud. | Streamlit Cloud. |
| **Ampliaciones futuras** | API REST, modelos ML, recomendaciones, dashboard. | API REST, almacenamiento anónimo, recomendaciones, dashboard institucional. | Las mismas, más la posibilidad de desactivar IA si no hay presupuesto. |

## Resumen evolutivo

- **Versión 1** – Prueba de concepto centrada en la carga doméstica como principal factor de penalización. Útil para demostrar el impacto básico del trabajo no remunerado.
- **Versión 2** – Incorpora la complejidad real del estudiantado (trabajo remunerado, composición del hogar, dependientes). Modelo más robusto y realista, e introduce apoyos institucionales.
- **Versión 3** – Salto cualitativo hacia la acción. La IA no solo diagnostica, sino que recomienda estrategias personalizadas de redistribución, gestión del tiempo y recursos externos. Convierte la herramienta en un agente de cambio activo.

La versión actual recomendada para producción es la **Versión 3**, por su capacidad de generar valor añadido mediante inteligencia artificial, manteniendo la robustez del modelo multifactorial.