"""Entrada principal del proyecto Shadow-Score Académico.

Este módulo configura Streamlit y redirige a la página de inicio.
"""

import sys
import os
from pathlib import Path

# Back_end al path para acceso a modelos
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
st.switch_page("pages/0_home.py")