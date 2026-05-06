"""
Módulo de conexión con la API de NVIDIA (Mistral) para Shadow-Score Académico.
================================================================================
- Compatible con ejecución local y Streamlit Cloud.
- Timeout configurable para prompts largos (hasta 10 minutos).
- Reintentos automáticos para errores transitorios (5xx).
- Cualquier error externo lanza NvidiaAPIError con mensaje amigable.
"""

import toml
import requests
import time
from pathlib import Path
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ── Constante: nombre del directorio que marca la raíz del proyecto ──────────
_MARKER = ".streamlit"

# ── Configuración de la API de NVIDIA ────────────────────────────────────────
INVOKE_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
MODEL_NAME = "mistralai/mistral-medium-3.5-128b"
STREAM = False

# ── Configuración de timeout (en segundos) ───────────────────────────────────
CONNECT_TIMEOUT = 60
READ_TIMEOUT = 600

class NvidiaAPIError(Exception):
    """Excepción personalizada para fallos de conexión con NVIDIA."""
    pass

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
    """
    Lee la API key priorizando st.secrets (local y nube),
    con fallback a lectura directa de secrets.toml para entornos sin Streamlit.
    """
    # ── Intento 1: st.secrets (funciona en local y Streamlit Cloud) ──────────
    try:
        import streamlit as st
        api_key = st.secrets.get("NVIDIA_API_KEY")
        if api_key:
            return api_key
    except Exception:
        pass

    # ── Intento 2: lectura directa del archivo (fallback local) ──────────────
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
            "La clave 'NVIDIA_API_KEY' no está definida o está vacía.\n"
            f"Archivo leído: {ruta_secrets}"
        )
    return api_key

def generar_plan_mistral(prompt: str) -> str:
    """
    Envía un prompt al modelo Mistral vía NVIDIA con timeout extendido.

    Args:
        prompt: Texto completo del prompt.

    Returns:
        Respuesta generada.

    Raises:
        NvidiaAPIError: siempre que falle la comunicación con NVIDIA.
        FileNotFoundError: si falta secrets.toml y no hay st.secrets.
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

    # ── Configuración de reintentos (solo para errores 5xx) ──────────────────
    session = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["POST"]
    )
    session.mount("https://", HTTPAdapter(max_retries=retries))

    print(f"📤 Enviando prompt de {len(prompt)} caracteres...")
    start = time.time()

    try:
        response = session.post(
            INVOKE_URL,
            headers=headers,
            json=payload,
            timeout=(CONNECT_TIMEOUT, READ_TIMEOUT)
        )
        response.raise_for_status()
        elapsed = time.time() - start
        print(f"✅ Respuesta recibida en {elapsed:.1f} segundos")

        data = response.json()
        return data["choices"][0]["message"]["content"]

    except requests.exceptions.Timeout:
        elapsed = time.time() - start
        print(f"⏰ Timeout después de {elapsed:.1f} segundos")
        raise NvidiaAPIError(
            f"La API de NVIDIA tardó más de {READ_TIMEOUT} segundos en responder. "
            "Inténtalo de nuevo más tarde. Si el problema persiste, usa una VPN "
            "o cambia de red."
        )

    except requests.exceptions.ConnectionError as e:
        print(f"❌ Error de conexión: {e}")
        raise NvidiaAPIError(
            "No se pudo establecer conexión con el servidor externo de NVIDIA. "
            "Verifica tu conexión a Internet e intenta de nuevo."
        )

    except requests.exceptions.HTTPError as e:
        print(f"❌ Error HTTP: {e}")
        if e.response.status_code == 401:
            raise NvidiaAPIError(
                "Autenticación fallida con NVIDIA. Verifica que tu API key sea válida "
                "y esté correctamente configurada."
            )
        else:
            raise NvidiaAPIError(
                f"El servidor de NVIDIA respondió con un error ({e.response.status_code}). "
                "Inténtalo de nuevo más tarde."
            )

    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        raise NvidiaAPIError(
            "No se ha logrado conectar con el servidor externo de NVIDIA. "
            "Si estás en una red corporativa, prueba con una VPN."
        ) from e