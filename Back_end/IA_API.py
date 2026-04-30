"""
Módulo de conexión con la API de Gemini para Shadow-Score Académico.
=====================================================================
CORRECCIÓN v2:
  - No usa st.secrets (Streamlit lo intercepta y busca en rutas incorrectas).
  - No depende de __file__ para navegar hacia la raíz del proyecto,
    porque el contexto de importación puede desplazar parent.parent.
  - Usa _encontrar_raiz_proyecto() que sube por el árbol de directorios
    hasta encontrar la carpeta .streamlit/, lo que es robusto sin importar
    desde dónde Streamlit re-importe el módulo.
  - Fallback adicional: si la búsqueda por árbol falla, intenta con
    pathlib.Path.cwd() que en Streamlit apunta a la raíz del proyecto.

FUNCIONES:
  - generar_plan_gemini(prompt) -> str
    Envía cualquier prompt (escenarios, plan de mejora, etc.) a Gemini Flash
    y devuelve la respuesta generada.
"""

import toml
import google.generativeai as genai
import streamlit as st
from pathlib import Path


# ── Constante: nombre del directorio que marca la raíz del proyecto ──────────
_MARKER = ".streamlit"


def _encontrar_raiz_proyecto() -> Path:
    """
    Sube por el árbol de directorios desde la ubicación de este archivo
    hasta encontrar una carpeta que contenga '.streamlit/'.
    Si no lo encuentra por __file__, prueba con Path.cwd() (directorio de
    trabajo actual, que Streamlit fija en la raíz del proyecto al arrancar).

    Returns:
        Path al directorio raíz del proyecto (el que contiene .streamlit/).

    Raises:
        FileNotFoundError si no puede localizar la raíz por ninguna vía.
    """
    # Estrategia 1: subir desde la ubicación de este módulo
    candidato = Path(__file__).resolve().parent
    for _ in range(6):  # máximo 6 niveles hacia arriba
        if (candidato / _MARKER).is_dir():
            return candidato
        candidato = candidato.parent

    # Estrategia 2: usar el directorio de trabajo actual (cwd)
    candidato_cwd = Path.cwd()
    if (candidato_cwd / _MARKER).is_dir():
        return candidato_cwd

    # Estrategia 3: subir desde cwd también
    candidato = candidato_cwd
    for _ in range(4):
        candidato = candidato.parent
        if (candidato / _MARKER).is_dir():
            return candidato

    raise FileNotFoundError(
        f"No se encontró la carpeta '{_MARKER}/' subiendo desde:\n"
        f"  __file__ → {Path(__file__).resolve()}\n"
        f"  cwd      → {Path.cwd()}\n"
        "Verifica que '.streamlit/secrets.toml' existe en la raíz del proyecto."
    )


def _cargar_api_key() -> str:
    """
    Localiza secrets.toml y extrae GEMINI_API_KEY.
    Usa lectura directa con toml, sin pasar por st.secrets.

    Returns:
        String con la API key.

    Raises:
        FileNotFoundError si secrets.toml no existe.
        ValueError si la clave no está definida en el archivo.
    """
    raiz = _encontrar_raiz_proyecto()
    ruta_secrets = raiz / _MARKER / "secrets.toml"

    if not ruta_secrets.exists():
        raise FileNotFoundError(
            f"No se encontró secrets.toml en:\n  {ruta_secrets}\n"
            f"Raíz del proyecto detectada: {raiz}"
        )

    with open(ruta_secrets, "r", encoding="utf-8") as f:
        config = toml.load(f)

    api_key = config.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(
            "La clave 'GEMINI_API_KEY' no está definida o está vacía en secrets.toml.\n"
            f"Archivo leído: {ruta_secrets}"
        )

    return api_key


def generar_plan_gemini(prompt: str) -> str:
    """
    Envía un prompt a Gemini Flash y devuelve el texto generado.

    Pensada para ser usada con cualquier prompt bien formado, como:
      - Escenarios de mejora (prompt corto, 150 palabras)
      - Plan de acción para el informe PDF (prompt extenso, 500‑700 palabras)

    Args:
        prompt: Texto completo del prompt a enviar al modelo.

    Returns:
        Texto de la respuesta generada, o mensaje de error amigable.
    """
    try:
        api_key = _cargar_api_key()
        genai.configure(api_key=api_key)

        model    = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        return response.text

    except FileNotFoundError as e:
        st.error(f"⚠️ Archivo de configuración no encontrado:\n\n{e}")
        return (
            "No se pudo generar el análisis: falta el archivo `secrets.toml`. "
            "Verifica que existe en `.streamlit/secrets.toml` dentro de la raíz del proyecto."
        )

    except ValueError as e:
        st.error(f"⚠️ Clave de API no configurada:\n\n{e}")
        return (
            "No se pudo generar el análisis: la clave `GEMINI_API_KEY` "
            "no está definida en `secrets.toml`."
        )

    except Exception as e:
        st.error(f"⚠️ Error al conectar con Gemini:\n\n{e}")
        return (
            "No se pudo generar el análisis en este momento. "
            "Por favor, inténtalo de nuevo o comprueba tu conexión a Internet."
        )