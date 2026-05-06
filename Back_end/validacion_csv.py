"""Validación de archivos CSV para el módulo administrativo.

Este módulo valida que el archivo cargado cumpla la estructura,
los tipos y los valores esperados para el procesamiento ETL.
"""

import pandas as pd
from typing import List, Dict, Optional, Tuple

def validar_archivo_csv(
    archivo,
    columnas_esperadas: Optional[List[str]] = None,
    categorias_validas: Optional[Dict[str, List[str]]] = None,
    margenes_numericos: Optional[Dict[str, Dict[str, float]]] = None,
    max_horas_semanales: float = 168.0,
) -> Tuple[bool, Optional[pd.DataFrame], List[str]]:
    """
    Valida un CSV para el procesamiento administrativo del proyecto.

    Verifica columnas obligatorias, tipos numéricos, rangos, categorías válidas,
    duplicados de ID y suma de horas semanales.

    Retorna (es_valido, df_limpio, mensajes_de_error).
    """
    if columnas_esperadas is None:
        columnas_esperadas = [
            "IDEstudiante", "Género", "Estrato", "ComposiciónHogar",
            "PersonasDependientes", "CargaDomestica", "CargaLaboral",
            "CargaAcademica", "PromedioActual"
        ]

    if categorias_validas is None:
        categorias_validas = {
            "Género": ["Femenino", "Masculino"],
            "ComposiciónHogar": [
                "Vive solo/a", "Con familia", "Con pareja",
                "Residencia universitaria", "Otros"
            ]
        }

    if margenes_numericos is None:
        margenes_numericos = {
            "Estrato":                {"min": 1, "max": 6},
            "PromedioActual":         {"min": 0.0, "max": 5.0},
            "PersonasDependientes":   {"min": 0, "max": 10}
        }

    mensajes = []

    # 1. Leer archivo
    try:
        df = pd.read_csv(archivo)
    except Exception as e:
        mensajes.append(f"Error al leer el archivo CSV: {e}")
        return False, None, mensajes

    # 2. Validar columnas exactas
    faltantes = set(columnas_esperadas) - set(df.columns)
    sobrantes = set(df.columns) - set(columnas_esperadas)
    if faltantes or sobrantes:
        if faltantes:
            mensajes.append(f"Faltan columnas: {', '.join(sorted(faltantes))}")
        if sobrantes:
            mensajes.append(f"Columnas no esperadas: {', '.join(sorted(sobrantes))}")
        return False, None, mensajes

    df = df[columnas_esperadas]
    enteras   = ["IDEstudiante", "Estrato", "PersonasDependientes"]
    flotantes = ["CargaDomestica", "CargaLaboral", "CargaAcademica", "PromedioActual"]
    strings   = ["Género", "ComposiciónHogar"]

    # 3. Validar tipos numéricos (ya NO cortamos aquí)
    for col in enteras:
        temp = pd.to_numeric(df[col], errors='coerce')
        nulas = df[col][temp.isna()].index
        for i in nulas:
            mensajes.append(f"Fila {i+2}: '{col}' no es numérico (valor: {df.at[i, col]})")
        if len(nulas) == 0:
            decimales = (temp % 1) != 0
            filas_no_enteras = df.index[decimales & temp.notna()]
            for i in filas_no_enteras:
                mensajes.append(f"Fila {i+2}: '{col}' debe ser entero, "
                                f"pero se encontró decimal ({df.at[i, col]})")
        df[col] = temp

    for col in flotantes:
        temp = pd.to_numeric(df[col], errors='coerce')
        nulas = df[col][temp.isna()].index
        for i in nulas:
            mensajes.append(f"Fila {i+2}: '{col}' no es numérico (valor: {df.at[i, col]})")
        df[col] = temp

    # 4. Márgenes numéricos (incluso si hay NaN, se ignoran)
    for col, limites in margenes_numericos.items():
        if col not in df.columns:
            continue
        min_val = limites.get("min")
        max_val = limites.get("max")
        # Asegurarse de trabajar con valores no nulos para las comparaciones
        serie = df[col].dropna()
        if min_val is not None:
            fuera = serie[serie < min_val]
            for idx in fuera.index:
                mensajes.append(f"Fila {idx+2}: '{col}' es {df.at[idx, col]}, menor que {min_val}")
        if max_val is not None:
            fuera = serie[serie > max_val]
            for idx in fuera.index:
                mensajes.append(f"Fila {idx+2}: '{col}' es {df.at[idx, col]}, mayor que {max_val}")

    # 5. Suma de horas semanales
    cargas = ["CargaDomestica", "CargaLaboral", "CargaAcademica"]
    # Sumar ignorando NaN (los NaN se convierten en 0 para la suma, o se omite la fila)
    suma = df[cargas].sum(axis=1, min_count=1)  # min_count=1 para que si todo es NaN la suma sea NaN
    exceso = suma[suma > max_horas_semanales]
    for i in exceso.index:
        mensajes.append(f"Fila {i+2}: suma de horas ({suma.at[i]:.1f}) supera "
                        f"el límite de {max_horas_semanales} h")

    # 6. Categorías de strings
    for col, valores_ok in categorias_validas.items():
        if col not in df.columns:
            continue
        col_limpia = df[col].astype(str).str.strip()
        mascara = ~col_limpia.isin(valores_ok)
        filas_inv = df.index[mascara]
        for i in filas_inv:
            mensajes.append(f"Fila {i+2}: '{col}' contiene '{df.at[i, col]}' "
                            f"(valores permitidos: {', '.join(valores_ok)})")

    # 7. Duplicados de ID (ERROR)
    # Solo tiene sentido si la columna ID es numérica y sin NaN
    if df['IDEstudiante'].notna().all():
        duplicados = df[df.duplicated(subset='IDEstudiante', keep=False)]
        if not duplicados.empty:
            for id_dup, grupo in duplicados.groupby('IDEstudiante'):
                filas = grupo.index + 2
                mensajes.append(
                    f"IDEstudiante '{int(id_dup)}' duplicado en filas {', '.join(map(str, filas))}"
                )
    else:
        # Si hay NaN en ID, ya se reportó como error de tipo, no buscamos duplicados
        pass

    # 8. Resultado final
    if mensajes:
        return False, None, mensajes

    # 9. Conversión final a tipos correctos (solo si no hay errores)
    for col in enteras:
        df[col] = df[col].astype(int)
    for col in flotantes:
        df[col] = df[col].astype(float)
    for col in strings:
        df[col] = df[col].astype(str).str.strip()

    return True, df, mensajes