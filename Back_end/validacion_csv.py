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
    Valida un CSV con la estructura requerida por Shadow-Score Académico.

    Ahora los valores permitidos coinciden exactamente con el formulario
    del estudiante (Género: solo Femenino/Masculino, ComposiciónHogar incluye Otros,
    PersonasDependientes entre 0 y 10).

    Retorna (es_valido, DataFrame_depurado, lista_de_mensajes).
    """
    # ── Valores por defecto alineados con el frontend ────────────────
    if columnas_esperadas is None:
        columnas_esperadas = [
            "IDEstudiante", "Género", "Estrato", "ComposiciónHogar",
            "PersonasDependientes", "CargaDomestica", "CargaLaboral",
            "CargaAcademica", "PromedioActual"
        ]

    if categorias_validas is None:
        categorias_validas = {
            "Género": ["Femenino", "Masculino"],                     # ← ajustado
            "ComposiciónHogar": [
                "Vive solo/a", "Con familia", "Con pareja",
                "Residencia universitaria", "Otros"                  # ← añadido
            ]
        }

    if margenes_numericos is None:
        margenes_numericos = {
            "Estrato":                {"min": 1, "max": 6},
            "PromedioActual":         {"min": 0.0, "max": 5.0},
            "PersonasDependientes":   {"min": 0, "max": 10}         # ← nuevo
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

    # 3. Conjuntos de columnas por tipo
    enteras   = ["IDEstudiante", "Estrato", "PersonasDependientes"]
    flotantes = ["CargaDomestica", "CargaLaboral", "CargaAcademica", "PromedioActual"]
    strings   = ["Género", "ComposiciónHogar"]

    # 4. Validar tipos numéricos
    for col in enteras:
        temp = pd.to_numeric(df[col], errors='coerce')
        nulas = df[col][temp.isna()].index
        for i in nulas:
            mensajes.append(f"Fila {i+2}: '{col}' no es numérico (valor: {df.at[i, col]})")
        if len(nulas) == 0:
            # Verificar que sea entero sin decimal
            decimales = (temp % 1) != 0
            filas_no_enteras = df.index[decimales & temp.notna()]
            for i in filas_no_enteras:
                mensajes.append(
                    f"Fila {i+2}: '{col}' debe ser entero, "
                    f"pero se encontró decimal ({df.at[i, col]})"
                )
        df[col] = temp

    for col in flotantes:
        temp = pd.to_numeric(df[col], errors='coerce')
        nulas = df[col][temp.isna()].index
        for i in nulas:
            mensajes.append(f"Fila {i+2}: '{col}' no es numérico (valor: {df.at[i, col]})")
        df[col] = temp

    if mensajes:   # errores de tipo, no seguir
        return False, None, mensajes

    # 5. Márgenes numéricos
    for col, limites in margenes_numericos.items():
        if col not in df.columns:
            continue
        min_val = limites.get("min")
        max_val = limites.get("max")
        if min_val is not None:
            fuera = df[df[col] < min_val]
            for i in fuera.index:
                mensajes.append(
                    f"Fila {i+2}: '{col}' es {df.at[i, col]}, menor que {min_val}"
                )
        if max_val is not None:
            fuera = df[df[col] > max_val]
            for i in fuera.index:
                mensajes.append(
                    f"Fila {i+2}: '{col}' es {df.at[i, col]}, mayor que {max_val}"
                )

    # 6. Suma de horas semanales
    cargas = ["CargaDomestica", "CargaLaboral", "CargaAcademica"]
    suma = df[cargas].sum(axis=1)
    exceso = df[suma > max_horas_semanales]
    for i in exceso.index:
        mensajes.append(
            f"Fila {i+2}: suma de horas ({suma.at[i]:.1f}) supera "
            f"el límite de {max_horas_semanales} h"
        )

    # 7. Categorías de strings
    for col, valores_ok in categorias_validas.items():
        if col not in df.columns:
            continue
        col_limpia = df[col].astype(str).str.strip()
        mascara = ~col_limpia.isin(valores_ok)
        filas_inv = df.index[mascara]
        for i in filas_inv:
            mensajes.append(
                f"Fila {i+2}: '{col}' contiene '{df.at[i, col]}' "
                f"(valores permitidos: {', '.join(valores_ok)})"
            )

    if mensajes:
        return False, None, mensajes

    # 8. Conversión final a tipos correctos
    for col in enteras:
        df[col] = df[col].astype(int)
    for col in flotantes:
        df[col] = df[col].astype(float)
    for col in strings:
        df[col] = df[col].astype(str).str.strip()

    return True, df, mensajes