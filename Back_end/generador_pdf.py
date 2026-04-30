"""
Generador del informe PDF para Shadow‑Score Académico.
Utiliza fpdf2 para maquetar el documento.
"""

from fpdf import FPDF
from pathlib import Path
from datetime import datetime


def generar_pdf_informe(perfil: dict, resultados: dict, texto_plan: str) -> bytes:
    """
    Construye un PDF con el plan de mejora personalizado.

    Args:
        perfil:      Datos del estudiante.
        resultados:  Diccionario con los indicadores del modelo.
        texto_plan:  Texto del plan de acción generado por la IA.

    Returns:
        Bytes del archivo PDF listos para descargar.
    """
    pdf = FPDF()
    pdf.add_page()

    # ── Configuración de fuentes ──
    # Usamos fuentes estándar (no requiere archivos externos)
    pdf.set_auto_page_break(auto=True, margin=15)

    # ── Encabezado ──
    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 12, "Shadow-Score Académico", ln=True, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, "Informe de Plan de Mejora Personalizado", ln=True, align="C")
    pdf.cell(0, 6, f"Generado el {datetime.now().strftime('%d/%m/%Y')}", ln=True, align="C")
    pdf.ln(8)

    # ── Datos del estudiante ──
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Datos del estudiante", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 5, f"Género: {perfil['genero']}", ln=True)
    pdf.cell(0, 5, f"Estrato: {perfil['estrato']}", ln=True)
    pdf.cell(0, 5, f"Composición del hogar: {perfil['composicion_hogar']}", ln=True)
    pdf.cell(0, 5, f"Personas a cargo: {perfil['dependientes']}", ln=True)
    horas_dom = perfil.get('horas_domesticas', 0)
    horas_trab = perfil.get('horas_trabajo', 0)
    horas_est = perfil.get('horas_estudio', 0)
    pdf.cell(0, 5, f"Horas domésticas/sem: {horas_dom}", ln=True)
    pdf.cell(0, 5, f"Horas trabajo remunerado/sem: {horas_trab}", ln=True)
    pdf.cell(0, 5, f"Horas estudio declaradas/sem: {horas_est}", ln=True)
    prom = perfil.get('promedio_actual')
    if prom:
        pdf.cell(0, 5, f"Promedio actual: {prom:.2f}", ln=True)
    pdf.ln(5)

    # ── Indicadores del modelo ──
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Indicadores Shadow-Score", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 5, f"Shadow-Score: {resultados['shadow_score']:.1f}% ({resultados['interpretacion']})", ln=True)
    pdf.cell(0, 5, f"Fatiga cognitiva: {resultados['fatiga']*100:.1f}%", ln=True)
    pdf.cell(0, 5, f"Horas efectivas: {resultados['horas_efectivas']:.1f} h/sem", ln=True)
    pdf.cell(0, 5, f"PPA estimado: {resultados['ppa_estimado']}", ln=True)
    pdf.ln(8)

    # ── Plan de mejora (texto de la IA) ──
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Plan de Mejora Personalizado", ln=True)
    pdf.ln(3)
    pdf.set_font("Helvetica", "", 10)

    # Insertamos el texto línea por línea respetando saltos de línea
    for linea in texto_plan.split("\n"):
        # Si la línea empieza con "**" asumimos es un título de sección
        if linea.startswith("**") and linea.endswith("**"):
            # Pequeño título en negrita
            pdf.set_font("Helvetica", "B", 11)
            titulo = linea.strip("*")
            pdf.cell(0, 6, titulo, ln=True)
            pdf.set_font("Helvetica", "", 10)
        else:
            pdf.multi_cell(0, 5, linea)
        pdf.ln(1)

    # ── Pie de página ──
    pdf.ln(10)
    pdf.set_font("Helvetica", "I", 8)
    pdf.cell(0, 5, "Este informe fue generado con la herramienta Shadow-Score Académico v3.1", ln=True, align="C")
    pdf.cell(0, 5, "Resultados basados en un modelo matemático. Interpretación con fines educativos.", ln=True, align="C")

    # Devolvemos el PDF como bytes
    return pdf.output()