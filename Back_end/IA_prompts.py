def generar_prompt_escenarios(perfil: dict, cargas: dict, resultados: dict) -> str:
    """
    Construye el prompt para que la IA (Mistral) genere propuestas de mejora
    personalizadas y accionables, basadas en el perfil y resultados del estudiante.
    """
    horas_domesticas = cargas['horas_domesticas']
    horas_trabajo    = cargas['horas_trabajo']
    horas_estudio    = cargas['horas_estudio']

    prompt = f"""Eres un asesor de bienestar universitario especializado en equidad de género y gestión del tiempo.

**Datos del estudiante:**
- Género: {perfil['genero']}
- Estrato: {perfil['estrato']}
- Composición del hogar: {perfil['composicion_hogar']}
- Personas a cargo: {perfil['dependientes']}
- Horas domésticas semanales: {horas_domesticas}
- Horas de trabajo remunerado: {horas_trabajo}
- Horas de estudio declaradas: {horas_estudio}
- Promedio actual: {perfil.get('promedio_actual', 'No ingresado')}

**Resultados del modelo:**
- Fatiga cognitiva: {resultados['fatiga']*100:.1f}%
- Horas efectivas de estudio: {resultados['horas_efectivas']:.1f} h/semana
- Shadow-Score: {resultados['shadow_score']:.1f}%
- PPA estimado: {resultados['ppa_estimado']}

**Instrucciones:**
Redacta un conjunto de propuestas de mejora concretas y accionables, organizadas en las siguientes categorías:

1. **Acciones individuales** (gestión del tiempo, técnicas de estudio, autocuidado)
2. **Acciones en el entorno cercano** (diálogo en el hogar, redistribución de tareas, corresponsabilidad)
3. **Apoyos institucionales** (becas, tutorías, servicios de bienestar universitario)

Cada propuesta debe ser específica, realista y adaptada al perfil del estudiante. Incluye ejemplos prácticos cuando sea posible.

Formato: texto claro, en español, con viñetas. Máximo 250 palabras.
Empieza directamente con las propuestas, sin saludos ni despedidas.
"""
    return prompt