# Comparativa de versiones: Shadow-Score Académico

Este documento resume las diferencias clave entre las versiones del proyecto **Shadow-Score Académico**, desarrolladas entre marzo y abril de 2026. La evolución culmina en la versión 5, que representa la versión final del proyecto con el modelo calibrado, el asistente de IA estabilizado y el módulo administrativo consolidado para análisis institucional.

## Evolución técnica del proyecto

La evolución de Shadow-Score Académico se organizó en ciclos claros de desarrollo. Cada versión incorporó mejoras técnicas concretas, hasta llegar a la versión final, que combina modelo matemático calibrado, IA estable y análisis masivo institucional.

### Versión 1 — Base conceptual
- Implementación inicial del concepto de Shadow-Score: fatiga sigmoidea, horas efectivas de estudio y resultado interpretativo.
- Interfaz básica de Streamlit para ingreso de datos individuales del estudiante.
- Validación simple de rangos en los datos de entrada.
- Enfoque centrado en la carga doméstica como factor de impacto académico.

### Versión 2 — Modelo multifactorial
- Ampliación del modelo matemático con variables adicionales:
  - trabajo remunerado,
  - composición del hogar,
  - dependientes,
  - estrato socioeconómico.
- Ajuste de coeficientes y ponderaciones para reflejar movilidad social y apoyos.
- Gráficos mejorados con Plotly para mostrar distribución de cargas y fatiga.
- Preparación de la estructura para aplicar el mismo modelo en lotes de datos.

### Versión 3 — Asistente de IA
- Integración de un asistente de inteligencia artificial para planes de acción personalizados.
- Generación de prompts y uso de API externa para producir recomendaciones basadas en coste de oportunidad.
- Conservación del modelo matemático de v2, con agregados de costo en horas y PPA.
- Inclusión de un flujo de interacción donde el estudiante recibe sugerencias de redistribución de tiempo.

### Versión 4 — Módulo administrativo
- Desarrollo del panel administrativo con carga masiva de CSV y procesamiento ETL en Pandas.
- Implementación de validación, limpieza, deduplicación e imputación en el flujo de datos.
- Dashboard institucional con indicadores agregados: Shadow-Score, brechas de género, estrato y composición del hogar.
- Separación explícita de la lógica de IA: el rol administrativo no consume modelos externos.
- Almacenamiento de resultados en `st.session_state` para manejo en sesión activa.

### Versión 5 — Versión final del proyecto
- Versión final de producción con modelo calibrado a los datos de la ENUT 2024-2025.
- Ajuste de coeficientes y factores de la fórmula para mejorar robustez e interpretabilidad.
- Asistente IA estabilizado con NVIDIA Mistral Medium 3.5 y clave gestionada por `st.secrets`.
- Consolidación del módulo administrativo: procesamiento masivo confiable, dashboards estabilizados y protección de datos sensibles.
- El proyecto finaliza con una arquitectura modular y lista para despliegue en Streamlit Cloud.

## Resumen técnico
- La versión 5 es la versión final del proyecto.
- Mantiene el modelo multifactorial de v2 y la IA de v3.
- Añade el módulo administrativo de v4 con calibración y consolidación para producción.
- Se entrega como la versión más estable y completa, adecuada para uso individual y análisis institucional.
