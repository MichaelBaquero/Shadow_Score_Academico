"""
Módulo de prompts para el asistente IA de Shadow-Score Académico.
Contiene las funciones que construyen los textos que se envían a Gemini
para los escenarios de mejora y, más adelante, para los planes detallados.
"""

def generar_prompt_escenarios(perfil: dict, cargas: dict, resultados: dict) -> str:
    """
    Construye el prompt para que la IA genere un análisis de escenarios
    comparando la situación actual con una posible mejora (corresponsabilidad).
    """
    horas_domesticas = cargas['horas_domesticas']
    horas_trabajo    = cargas['horas_trabajo']
    horas_estudio    = cargas['horas_estudio']

    # Escenario mejorado: reducir un 40% las horas domésticas
    reduccion = 0.4
    nuevas_domesticas = horas_domesticas * (1 - reduccion)

    prompt = f"""Eres un asesor de bienestar universitario especializado en equidad de género.
Tienes los datos de un estudiante universitario colombiano que ha usado la herramienta 
Shadow-Score Académico v3.1.

**Contexto:**
El modelo matemático estima que la carga no académica (trabajo doméstico + laboral) 
genera fatiga cognitiva y reduce las horas efectivas de estudio, impactando el promedio.
El Shadow-Score (0-100) indica la penalización global (50% tiempo ocupado + 50% fatiga).

**Perfil actual del estudiante:**
- Género: {perfil['genero']}
- Estrato: {perfil['estrato']}
- Composición del hogar: {perfil['composicion_hogar']}
- Personas a cargo: {perfil['dependientes']}
- Horas domésticas semanales: {horas_domesticas}
- Horas de trabajo remunerado: {horas_trabajo}
- Horas de estudio declaradas: {horas_estudio}
- Promedio actual (si aplica): {perfil.get('promedio_actual', 'No ingresado')}

**Resultados del modelo (situación actual):**
- Fatiga cognitiva: {resultados['fatiga']*100:.1f}%
- Horas efectivas de estudio: {resultados['horas_efectivas']:.1f} horas/semana
- Shadow-Score: {resultados['shadow_score']:.1f}% ({resultados['interpretacion']})
- PPA estimado: {resultados['ppa_estimado']}

**Escenario de mejora:**
Suponiendo una redistribución de tareas domésticas (por ejemplo, corresponsabilidad) 
que reduzca en un {reduccion*100:.0f}% las horas domésticas del estudiante 
(nuevas horas domésticas: {nuevas_domesticas:.1f}), 
describe de forma breve pero concreta:

1. Cómo cambiarían los indicadores (fatiga, horas efectivas, Shadow-Score, PPA) 
   de manera cualitativa y cuantitativa.
2. Los beneficios potenciales en el rendimiento académico y bienestar.
3. Recomendaciones para lograr ese cambio (apoyos institucionales, diálogo en el hogar, etc.).

Formato: texto claro, en español, con viñetas si es necesario. Máximo 150 palabras.
Empieza directamente con el análisis, sin saludos ni despedidas.
"""
    return prompt

def generar_prompt_plan_mejora(perfil: dict, cargas: dict, resultados: dict) -> str:
    """
    Construye el prompt para un plan de acción personalizado extenso,
    que será usado como contenido principal del informe PDF.
    """
    horas_domesticas = cargas['horas_domesticas']
    horas_trabajo    = cargas['horas_trabajo']
    horas_estudio    = cargas['horas_estudio']
    shadow_score     = resultados['shadow_score']
    fatiga           = resultados['fatiga']
    horas_efectivas  = resultados['horas_efectivas']
    ppa_estimado     = resultados['ppa_estimado']
    interpretacion   = resultados['interpretacion']

    # ── Datos adicionales del perfil para enriquecer el plan ──
    genero             = perfil['genero']
    estrato            = perfil['estrato']
    composicion_hogar  = perfil['composicion_hogar']
    dependientes       = perfil['dependientes']
    promedio_actual    = perfil.get('promedio_actual', None)

    prompt = f"""Eres un orientador académico y de bienestar universitario especializado en equidad de género 
y gestión del tiempo. Debes redactar un plan de mejora personalizado para un estudiante 
colombiano que ha utilizado la herramienta Shadow‑Score Académico v3.1.

**Datos del estudiante:**
- Género: {genero}
- Estrato socioeconómico: {estrato}
- Composición del hogar: {composicion_hogar}
- Personas a cargo: {dependientes}
- Horas semanales de trabajo doméstico: {horas_domesticas}
- Horas semanales de trabajo remunerado: {horas_trabajo}
- Horas de estudio declaradas: {horas_estudio}
- Promedio académico actual (si fue ingresado): {promedio_actual if promedio_actual else 'No reportado'}

**Resultados actuales del modelo Shadow‑Score:**
- Shadow‑Score general: {shadow_score:.1f}% ({interpretacion})
- Fatiga cognitiva: {fatiga*100:.1f}%
- Horas efectivas reales de estudio: {horas_efectivas:.1f} h/semana (de {horas_estudio} declaradas)
- PPA estimado (promedio proyectado): {ppa_estimado}

**Instrucciones para el plan de mejora:**
Redacta un documento claro, empático y motivador en español, con los siguientes apartados:

1. **Diagnóstico personalizado**: Explica, en un párrafo, cómo las cargas actuales están afectando 
   el rendimiento académico y el bienestar, usando los indicadores del Shadow‑Score. 
   Menciona el impacto diferencial según género y situación familiar si es pertinente.

2. **Metas realistas**: Define de 2 a 3 metas concretas de mejora para las próximas 8 semanas, 
   por ejemplo: aumentar horas efectivas de estudio, reducir la fatiga percibida, 
   o proteger un mínimo de horas de sueño/ocio. Incluye metas cuantitativas si es posible.

3. **Estrategias y acciones concretas**: Propón al menos 4 acciones específicas divididas en:
   - **Acciones individuales** (gestión del tiempo, técnicas de estudio, autocuidado).
   - **Acciones en el entorno cercano** (diálogo en el hogar, redistribución de tareas, 
     corresponsabilidad).
   - **Apoyos institucionales** (becas, tutorías, servicios de bienestar universitario, 
     grupos de apoyo) que el estudiante puede buscar.

4. **Escenario de corresponsabilidad**: Simula cómo mejorarían los indicadores si se lograra 
   reducir las horas domésticas en un 40% gracias a una mejor distribución en el hogar. 
   Presenta, en lenguaje sencillo, los cambios estimados en fatiga, horas efectivas y PPA, 
   y destaca los beneficios en el rendimiento y la calidad de vida.

5. **Mensaje motivador final**: Cierra con un mensaje de aliento, reforzando la capacidad 
   de agencia del estudiante y recordándole que pequeños cambios sostenidos pueden generar 
   grandes diferencias.

**Formato de salida**:
- El texto debe estar estructurado con títulos de sección claros (puedes usar “**Diagnóstico**”, 
  “**Metas realistas**”, etc.) y párrafos breves.
- Longitud: entre 500 y 700 palabras.
- Tono: profesional pero cercano, libre de juicios de valor sobre las decisiones del estudiante.
- No incluyas saludos ni despedidas (el documento será insertado directamente en un PDF). 
- Asegúrate de que todas las recomendaciones sean accionables y adaptadas al perfil presentado.
"""
    return prompt