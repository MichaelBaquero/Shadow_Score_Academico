"""
Módulo de transformación ETL para Shadow-Score Académico.
Toma el DataFrame validado (sin errores de formato ni duplicados) y:
  1. Mapea columnas al formato del modelo.
  2. Ejecuta el modelo para cada estudiante.
  3. Agrega los resultados como nuevas columnas.
Retorna el DataFrame enriquecido listo para visualización.
"""

import pandas as pd
from Back_end.modelo import ejecutar_modelo

# Mapeo entre columnas del CSV validado y claves del modelo
MAPEO_PERFIL = {
    "genero":            "Género",
    "estrato":           "Estrato",
    "composicion_hogar": "ComposiciónHogar",
    "dependientes":      "PersonasDependientes",
}

MAPEO_CARGAS = {
    "horas_domesticas": "CargaDomestica",
    "horas_trabajo":    "CargaLaboral",
    "horas_estudio":    "CargaAcademica",
}


def procesar_etl(df_validado: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica el modelo Shadow-Score a todos los registros y devuelve
    el DataFrame original aumentado con las métricas calculadas.
    """
    resultados = []

    for _, fila in df_validado.iterrows():
        # Construir diccionarios esperados por el modelo
        perfil = {
            "genero":             fila[MAPEO_PERFIL["genero"]],
            "estrato":            int(fila[MAPEO_PERFIL["estrato"]]),
            "composicion_hogar":  fila[MAPEO_PERFIL["composicion_hogar"]],
            "dependientes":       int(fila[MAPEO_PERFIL["dependientes"]]),
        }

        cargas = {
            "horas_domesticas": float(fila[MAPEO_CARGAS["horas_domesticas"]]),
            "horas_trabajo":    float(fila[MAPEO_CARGAS["horas_trabajo"]]),
            "horas_estudio":    float(fila[MAPEO_CARGAS["horas_estudio"]]),
        }

        promedio_actual = float(fila["PromedioActual"])

        # Ejecutar modelo
        resultado = ejecutar_modelo(perfil, cargas, promedio_actual)

        # Añadir métricas a una copia de la fila original
        nueva_fila = fila.to_dict()
        nueva_fila.update(resultado)
        resultados.append(nueva_fila)

    df_enriquecido = pd.DataFrame(resultados)

    # Orden lógico de columnas (ID primero, luego perfil, cargas, promedio, métricas)
    columnas_finales = [
        "IDEstudiante", "Género", "Estrato", "ComposiciónHogar",
        "PersonasDependientes", "CargaDomestica", "CargaLaboral",
        "CargaAcademica", "PromedioActual",
        "carga_total", "fatiga", "horas_efectivas", "ppa_estimado",
        "shadow_score", "comp_tiempo", "comp_fatiga", "interpretacion",
        "coste_horas", "coste_ppa"
    ]
    # Solo conservamos las columnas que existen (por si acaso)
    columnas_finales = [c for c in columnas_finales if c in df_enriquecido.columns]
    df_enriquecido = df_enriquecido[columnas_finales]

    return df_enriquecido