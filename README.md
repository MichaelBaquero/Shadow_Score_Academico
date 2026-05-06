# Shadow-Score Académico v5

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://tu-app-url.streamlit.app)  
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)  
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Aplicación web interactiva para que estudiantes universitarios reflexionen sobre la distribución de su tiempo (cargas domésticas, laborales y académicas) y visualicen posibles afectaciones en su rendimiento académico con perspectiva de género. Incluye un modelo matemático calibrado con la **ENUT 2024-2025 del DANE**, un asistente de inteligencia artificial (NVIDIA API) que genera planes de acción personalizados y un **módulo administrativo** para procesamiento masivo de datos vía CSV y dashboards institucionales.

## 🚀 Características principales

- **Rol estudiante**  
  - Formulario detallado con validación en tiempo real.  
  - Cálculo de indicadores: fatiga cognitiva, horas efectivas de estudio, Shadow‑Score (cualitativo y numérico), coste de oportunidad.  
  - Gráficos interactivos (Plotly): gauge de fatiga, radar multivariable, métricas.  
  - Simulación de escenario mejorado (redistribución de carga doméstica).  
  - **Asistente IA** (NVIDIA API, modelo Mistral Medium 3.5) que genera planes de acción personalizados basados en el coste de oportunidad.

- **Rol administrativo**  
  - Carga de archivos CSV (un archivo por facultad) con identificadores anónimos.  
  - Flujo ETL completo con **Pandas**: validación, limpieza, transformación y aplicación del modelo matemático a cada registro.  
  - Dashboards interactivos: distribución de Shadow‑Score, brechas de género, fatiga por estrato, horas efectivas de estudio.  
  - Sin IA en este módulo para preservar la confidencialidad de datos sensibles.  
  - Exportación de reportes agregados (CSV/Excel/PDF) – *pendiente en versión actual*.

- **Infraestructura**  
  - Desplegada en **Streamlit Cloud** con integración continua desde GitHub.  
  - Gestión segura de claves API mediante `st.secrets`.  
  - Código modular (back-end, configuración, páginas Streamlit).

## 🧠 Modelo matemático (v5)

Calibrado con la **Encuesta Nacional de Uso del Tiempo (ENUT) 2024-2025 del DANE** y literatura complementaria.

### Variables de entrada
- Género (Femenino / Masculino), estrato (1‑6), composición del hogar, número de dependientes, horas domésticas, horas de trabajo remunerado, horas de estudio, promedio actual (opcional).

### Indicadores calculados
- **Carga total** = horas domésticas + horas trabajo  
- **Fatiga cognitiva** (sigmoide con punto de inflexión en 45h/semana, pendiente modulada por factores de género, estrato y hogar)  
- **Horas efectivas de estudio** = horas estudio × (1 – fatiga)  
- **PPA estimado** (promedio ponderado acumulado) mediante modelo lineal con interacción género×fatiga  
- **Shadow‑Score** (0‑100): combinación de carga total y fatiga, con categorías cualitativas (baja, moderada, significativa, alta, extrema)  
- **Coste de oportunidad** (horas perdidas y diferencia de promedio)

### Factores de ajuste
Los coeficientes de ajuste se derivan de supuestos informados basados en los datos de la ENUT 2024-2025 del DANE, que proporcionan estadísticas nacionales sobre distribución de tiempo por género, estrato socioeconómico y composición del hogar. Estos factores modulan la fatiga cognitiva y el impacto en el rendimiento académico.

- **Género**: α_femenino = 1.40, α_masculino = 1.00 (refleja mayor carga doméstica en mujeres según ENUT)  
- **Estrato**: desde 1.25 (estrato 1) hasta 0.87 (estrato 6) (menor fatiga en estratos altos por mejor acceso a servicios)  
- **Composición del hogar**: desde 0.75 (residencia universitaria) hasta 1.05 (vive con familia) (mayor carga en hogares con dependientes)

> ⚠️ Las métricas del modelo están basadas en supuestos calculados a partir de la ENUT, pero pueden estandarizarse y mejorarse mediante regresión lineal múltiple con datos reales de estudiantes (n ≥ 150). Algunos coeficientes del modelo de PPA están marcados como `[SUPUESTO]` en el código y deben validarse empíricamente para mayor precisión.

## 🤖 Asistente IA (solo estudiante)

- **API**: NVIDIA API, modelo `mistralai/mistral-medium-3.5-128b`  
- **Prompt estructurado** que incluye perfil del usuario, carga detectada, coste de oportunidad y contexto del escenario.  
- **Timeout extendido** (10 minutos) y reintentos automáticos ante errores 5xx.  
- **Disclaimer** informativo sobre la naturaleza generativa de las recomendaciones.

## 📂 Módulo administrativo – Procesamiento masivo

### Formato CSV de entrada
| Columna | Tipo | Descripción |
|---------|------|-------------|
| `id_estudiante` | cadena | Identificador anónimo (hash del código estudiantil) |
| `genero` | Femenino/Masculino | |
| `estrato` | 1‑6 | |
| `composicion_hogar` | Vive solo/a, con familia, con pareja, residencia universitaria, otros | |
| `dependientes` | 0‑10 | Número de personas dependientes |
| `horas_domesticas` | 0‑168 | Horas semanales de carga doméstica |
| `horas_trabajo` | 0‑168 | Horas semanales de trabajo remunerado (0 si no trabaja) |
| `horas_estudio` | 0‑168 | Horas semanales de estudio |
| `promedio_actual` (opcional) | 0.0‑5.0 | Para coste de oportunidad en PPA |

### Flujo ETL (sin base de datos)
1. **Extracción**: lectura del CSV con `pd.read_csv()`.  
2. **Validación**: comprobación de columnas, rangos y consistencia.  
3. **Limpieza**: eliminación de duplicados por `id_estudiante`, imputación de valores faltantes no críticos.  
4. **Transformación**: aplicación del modelo matemático a cada fila, generando columnas derivadas (fatiga, horas_efectivas, shadow_score, categoría, coste_horas, coste_ppa).  
5. **Carga**: almacenamiento en memoria (`st.session_state`) durante la sesión.

### Dashboards institucionales (Plotly)
- Resumen general (total estudiantes, Shadow‑Score promedio, distribución por categoría)  
- Distribución de fatiga y cargas  
- Brechas de género (horas domésticas, fatiga, Shadow‑Score, horas efectivas)  
- Segmentación por estrato y composición del hogar  
- Tabla de resultados completa (sin identificadores personales)

## 🛠️ Tecnologías utilizadas

| Tecnología | Uso |
|------------|-----|
| Python 3.10+ | Lenguaje base |
| Streamlit | Interfaz de usuario, gestión de estado, despliegue |
| Pandas | Manejo de datos y procesamiento ETL |
| NumPy | Operaciones matemáticas vectorizadas |
| Plotly | Gráficos interactivos (gauge, radar, barras) |
| NVIDIA API (Mistral Medium 3.5) | Asistente IA para planes de acción |
| Requests | Cliente HTTP para consumir la API |
| Git / GitHub | Control de versiones |
| Streamlit Cloud | Despliegue continuo |

## 📦 Instalación y ejecución local

### Requisitos previos
- Python 3.10 o superior
- Clave de API de NVIDIA (para el asistente IA)

### Pasos
1. Clona el repositorio:
   ```bash
   git clone https://github.com/tu-usuario/shadow-score-academico.git
   cd shadow-score-academico
   ```
2. Crea y activa un entorno virtual:
   ```bash
   python -m venv venv
   # En Windows:
   venv\Scripts\activate
   # En Linux/Mac:
   source venv/bin/activate
   ```
3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
4. Configura las claves API locales:  
   Crea el archivo `.streamlit/secrets.toml` con:
   ```toml
   NVIDIA_API_KEY = "tu-api-key-aqui"
   ```
5. Ejecuta la aplicación:
   ```bash
   streamlit run app.py
   ```

## 🗂️ Estructura del proyecto

```
Proyecto/
├── app.py                          # Punto de entrada principal
├── requirements.txt                # Dependencias de Python
├── Back_end/                       # Lógica de negocio y procesamiento
│   ├── __init__.py
│   ├── IA_API.py                   # Llamadas a la API de IA
│   ├── IA_prompts.py               # Prompts para el asistente IA
│   ├── modelo.py                   # Modelo matemático (fatiga, Shadow-Score)
│   ├── procesamiento_etl.py        # Flujo ETL para CSV
│   └── validacion_csv.py           # Validación de archivos CSV
├── config/                         # Constantes, estilos y configuraciones
│   ├── __init__.py
│   ├── colores.py                  # Definiciones de colores
│   ├── estilos_comunes.py          # Estilos comunes para la UI
│   ├── frases.py                   # Frases y mensajes
│   └── tarjetas.py                 # Configuración de tarjetas
├── pages/                          # Páginas de Streamlit (multipágina)
│   ├── __init__.py
│   ├── 0_home.py                   # Página de inicio
│   ├── 1_estudiante.py             # Formulario y resultados para estudiantes
│   ├── 2_administrativo.py         # Carga de CSV y dashboards
│   ├── 3_resultados_estudiantes.py # Resultados detallados para estudiantes
│   └── 4_dashboards.py             # Dashboards institucionales
├── Documentacion/                  # Documentos y reportes
│   ├── COMPARATIVO_VERSIONES.md
│   ├── Informe_de_proyecto_Shadow_Score.tex
│   └── Docs/                       # Carpeta para imágenes y anexos
└── .streamlit/
    └── secrets.toml                # Claves API (no se sube al repositorio)
```

## 📊 Uso en Streamlit Cloud
- La aplicación está desplegada en Streamlit Cloud y se actualiza automáticamente con cada push a la rama main del repositorio.
- Las claves API se definen en los secrets de la aplicación en la plataforma.

## ⚠️ Limitaciones conocidas
*(Basado en el informe de producción v5 - 6 mayo 2026)*

- **Sin autenticación real** – El módulo administrativo es accesible públicamente sin credenciales.
- **Sin exportación de reportes** – Los dashboards no permiten descargar resultados agregados (CSV/Excel/PDF).
- **Sin persistencia entre sesiones** – Los datos procesados se almacenan solo en `st.session_state` y se pierden al recargar.
- **Género binario** – Solo se contempla Femenino/Masculino (limitación del modelo ENUT).
- **Simulación de corresponsabilidad solo individual** – El dashboard administrativo no incluye simulación agregada.
- **Sin caché de llamadas a la IA** – Cada solicitud al asistente genera una nueva llamada a la API, aunque el perfil sea idéntico.
- **`promedio_actual` no integrado en dashboards** – El coste de oportunidad en PPA se calcula, pero no se visualiza a nivel institucional.
- **Coeficientes supuestos** – Varios coeficientes del modelo de PPA deben ser recalibrados con datos reales.

## 📄 Licencia
Este proyecto se distribuye bajo la licencia MIT. Consulta el archivo LICENSE para más información.

*Inspirado en los datos de la ENUT 2024-2025 del DANE y los Objetivos de Desarrollo Sostenible (ODS 5 – Igualdad de género).*