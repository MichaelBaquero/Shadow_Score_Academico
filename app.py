"""
Shadow-Score Académico - Aplicación Principal (app.py)
Punto de entrada que corre todo el localhost y renderiza 0_home.py como página inicial.
Ubicado en Proyecto/ para servir como root de la aplicación.
"""

import sys
import os
from pathlib import Path

# Agregar Front_End al path ANTES de cualquier import
# Esto permite que config/ sea accesible desde todas las páginas
front_end_path = Path(__file__).parent / "Front_End"
sys.path.insert(0, str(front_end_path))

# También agregar Back_end para acceso a modelos
back_end_path = Path(__file__).parent / "Back_end"
sys.path.insert(0, str(back_end_path))

import streamlit as st
from config.estilos_comunes import aplicar_estilos_globales

# =========================================================
# CONFIGURACIÓN DE LA APLICACIÓN
# =========================================================
st.set_page_config(
    page_title="Shadow-Score Académico",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Aplicar estilos globales
aplicar_estilos_globales()

# =========================================================
# NAVEGACIÓN A HOME (Página Inicial)
# =========================================================
st.switch_page("Front_End/pages/0_home.py")