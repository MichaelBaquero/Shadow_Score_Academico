"""Estilos globales compartidos para todas las páginas del proyecto.

Este módulo exporta la función aplicar_estilos_globales() que inyecta
CSS de presentación para Streamlit sin lógica ejecutable adicional.
"""

import streamlit as st

def aplicar_estilos_globales():
    st.markdown("""
    <style>
        /* Ocultar completamente la sidebar */
        [data-testid="stSidebar"] {
            display: none;
        }
        [data-testid="stSidebarCollapsedControl"] {
            display: none;
        }
        .main > div {
            padding-left: 2rem;
            padding-right: 2rem;
        }

        /* Centrar el título h1 */
        h1 {
            text-align: center;
        }

        /* ===== TARJETAS MÁS GRANDES ===== */
        .stPageLink button {
            background-color: #ffffff;
            border-radius: 28px;
            padding: 2rem 1rem;
            min-height: 350px;          /* Altura mínima aumentada */
            box-shadow: 0 20px 30px -12px rgba(0, 0, 0, 0.15);
            text-align: center;
            transition: transform 0.2s, box-shadow 0.2s;
            border: 1px solid #e2e8f0;
            width: 100%;
            white-space: normal;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;      /* Centra verticalmente el contenido */
            background-color: white;
            color: #1e293b;
        }
        .stPageLink button:hover {
            transform: translateY(-6px);
            box-shadow: 0 25px 35px -12px rgba(0, 0, 0, 0.2);
            border-color: #94a3b8;
        }
        /* Agrandar el texto/emoji dentro del botón */
        .stPageLink button p {
            font-size: 2.5rem !important;   /* Emoji y texto más grandes */
            font-weight: 600 !important;
            margin: 0 0 0.75rem 0 !important;
            line-height: 1.2 !important;
        }
        /* Ajuste para el subtítulo debajo del botón */
        .card-subtitle {
            text-align: center;
            margin-top: 1rem;
            font-size: 1rem;
            color: #475569;
            font-weight: 500;
        }
        /* Separador decorativo */
        hr {
            margin-top: 2rem;
            margin-bottom: 2rem;
        }
    </style>
    """, unsafe_allow_html=True)