"""
Módulo de conexión con la API de NVIDIA (Mistral) para Shadow-Score Académico.
================================================================================
- Sin reintentos.
- Cualquier error externo (timeout, HTTP 5xx, red) lanza NvidiaAPIError
  con un mensaje genérico.
"""

import toml
import requests
import streamlit as st
from pathlib import Path

# ── Constante: nombre del directorio que marca la raíz del proyecto ──────────
_MARKER = ".streamlit"

# Configuración de la API de NVIDIA
INVOKE_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
MODEL_NAME = "mistralai/mistral-medium-3.5-128b"   # Verifica vigencia
STREAM = False


class NvidiaAPIError(Exception):
    """Excepción para fallos de conexión con NVIDIA."""


def _encontrar_raiz_proyecto() -> Path:
    """Localiza la raíz del proyecto (contiene .streamlit/)."""
    candidato = Path(__file__).resolve().parent
    for _ in range(6):
        if (candidato / _MARKER).is_dir():
            return candidato
        candidato = candidato.parent

    candidato_cwd = Path.cwd()
    if (candidato_cwd / _MARKER).is_dir():
        return candidato_cwd

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
    """Lee la API key desde .streamlit/secrets.toml."""
    raiz = _encontrar_raiz_proyecto()
    ruta_secrets = raiz / _MARKER / "secrets.toml"

    if not ruta_secrets.exists():
        raise FileNotFoundError(
            f"No se encontró secrets.toml en:\n  {ruta_secrets}\n"
            f"Raíz del proyecto detectada: {raiz}"
        )

    with open(ruta_secrets, "r", encoding="utf-8") as f:
        config = toml.load(f)

    api_key = config.get("NVIDIA_API_KEY")
    if not api_key:
        raise ValueError(
            "La clave 'NVIDIA_API_KEY' no está definida o está vacía en secrets.toml.\n"
            f"Archivo leído: {ruta_secrets}"
        )
    return api_key


def generar_plan_mistral(prompt: str) -> str:
    """
    Envía un prompt al modelo Mistral vía NVIDIA (un solo intento).

    Cualquier fallo (timeout, error HTTP, red) genera NvidiaAPIError
    con el mensaje: "No se ha logrado conectar con el servidor externo de NVIDIA."

    Args:
        prompt: Texto completo del prompt.

    Returns:
        Respuesta generada.

    Raises:
        NvidiaAPIError: siempre que falle la comunicación con NVIDIA.
        FileNotFoundError: si falta secrets.toml.
        ValueError: si falta la API key.
    """
    api_key = _cargar_api_key()

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }

    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 16384,
        "temperature": 0.70,
        "top_p": 1.00,
        "stream": STREAM
    }

    try:
        response = requests.post(INVOKE_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()  # lanza HTTPError para códigos 4xx/5xx
        data = response.json()
        return data["choices"][0]["message"]["content"]

    except Exception as e:
        # Cualquier error (timeout, ConnectionError, HTTPError, etc.)
        # se convierte en un único mensaje para el usuario.
        raise NvidiaAPIError(
            "No se ha logrado conectar con el servidor externo de NVIDIA."
        ) from e