"""
Modelo matemático para Shadow-Score Académico (v5).

Este módulo contiene la lógica de cálculo del índice de fatiga,
las horas efectivas de estudio, la estimación del PPA y el Shadow-Score.
Los parámetros se han calibrado para la versión final del proyecto,
con base en la ENUT 2024-2025 y literatura complementaria.

Los coeficientes marcados con [SUPUESTO] deben revisarse cuando se
cuente con datos locales suficientes (n ≥ 150) para una regresión.
"""

import math

# =========================================================
# PARÁMETROS DE FATIGA COGNITIVA
# =========================================================
MU = 45.0       # horas/semana — punto de inflexión (media estudiantil ponderada)
KAPPA = 10.0    # pendiente de la curva sigmoide

# =========================================================
# FACTOR ALPHA: AJUSTE POR GÉNERO
# =========================================================
# Razón cargas no remuneradas ENUT: 53.1 / 22.4 = 2.37 → √2.37 ≈ 1.54 → 1.40
ALPHA_GENERO = {
    "Femenino":  1.40,
    "Masculino": 1.00
}

# =========================================================
# FACTOR BETA: AJUSTE POR ESTRATO
# =========================================================
# Basado en acceso a externalización de tareas (ECV 2023)
BETA_ESTRATO = {
    1: 1.25,
    2: 1.18,
    3: 1.08,
    4: 1.00,
    5: 0.93,
    6: 0.87,
}

# =========================================================
# FACTOR GAMMA: AJUSTE POR COMPOSICIÓN DEL HOGAR
# =========================================================
# Ajustado según distribución de carga doméstica por tipo de hogar (ENUT)
GAMMA_HOGAR = {
    "Residencia universitaria": 0.75,
    "Vive solo/a":              0.90,
    "Con familia":              1.05,
    "Con pareja":               0.95,
    "Otros":                    1.00,
}

# =========================================================
# COEFICIENTES DEL PPA ESTIMADO
# =========================================================
BETA_0 = 3.00    # intercepto [SUPUESTO]
BETA_1 = 0.025   # horas efectivas [UdeG 2013, Fazio 2004]
BETA_2 = 0.10    # estrato [EAFIT 2010]
BETA_3 = -0.10   # género femenino [SUPUESTO]
BETA_4 = -0.07   # dependientes [SUPUESTO]
BETA_5 = -0.35   # interacción género × fatiga [SUPUESTO]

# =========================================================
# CONSTANTES GENERALES
# =========================================================
MAX_HORAS_SEMANA = 168.0
MAX_FACTOR       = 1.40


# =========================================================
# FUNCIONES DEL MODELO
# =========================================================

def sigmoide(x: float) -> float:
    """Función logística estándar, protegida contra OverflowError."""
    try:
        return 1.0 / (1.0 + math.exp(-x))
    except OverflowError:
        return 1.0 if x > 0 else 0.0


def calcular_fatiga(
    carga_total: float,
    genero: str,
    estrato: int,
    composicion_hogar: str,
) -> float:
    """
    Calcula el índice de fatiga cognitiva [0, 1].
    El factor combinado (α·β·γ) ajusta la pendiente de la sigmoide,
    no la salida, para evitar saturación artificial.
    """
    alpha = ALPHA_GENERO.get(genero, 1.0)
    beta  = BETA_ESTRATO.get(estrato, 1.0)
    gamma = GAMMA_HOGAR.get(composicion_hogar, 1.0)

    factor = min(alpha * beta * gamma, MAX_FACTOR)
    pendiente_ajustada = KAPPA / factor
    x = (carga_total - MU) / pendiente_ajustada

    return sigmoide(x)


def calcular_horas_efectivas(horas_estudio: float, fatiga: float) -> float:
    """Horas efectivas = horas_estudio × (1 − fatiga)."""
    return horas_estudio * (1.0 - fatiga)


def estimar_ppa(
    horas_efectivas: float,
    estrato: int,
    genero: str,
    dependientes: int,
    fatiga: float,
) -> float:
    """Estima el PPA (0-5) mediante regresión lineal múltiple."""
    gen_binario = 1.0 if genero == "Femenino" else 0.0

    ppa = (
        BETA_0
        + BETA_1 * horas_efectivas
        + BETA_2 * estrato
        + BETA_3 * gen_binario
        + BETA_4 * dependientes
        + BETA_5 * gen_binario * fatiga
    )
    return max(0.0, min(5.0, ppa))


def calcular_shadow_score(carga_total: float, fatiga: float) -> float:
    """
    Shadow-Score [0, 100] como media ponderada de dos componentes:
    - comp_tiempo: proporción de la semana ocupada
    - comp_fatiga: índice de fatiga cognitiva
    Pesos: 50% cada uno.
    """
    comp_tiempo = carga_total / MAX_HORAS_SEMANA
    comp_fatiga = fatiga
    score = 100.0 * (0.5 * comp_tiempo + 0.5 * comp_fatiga)
    return min(100.0, score)


def interpretar_shadow_score(score: float) -> str:
    """Categorización cualitativa del Shadow-Score."""
    if score <= 20:
        return "Baja penalización"
    elif score <= 40:
        return "Penalización moderada"
    elif score <= 60:
        return "Penalización significativa"
    elif score <= 80:
        return "Alta penalización"
    else:
        return "Penalización extrema"


def ejecutar_modelo(
    perfil: dict,
    cargas: dict,
    promedio_actual: float | None = None,
) -> dict:
    """
    Punto de entrada principal. Ejecuta el modelo completo.

    Args:
        perfil: dict con claves genero, estrato, composicion_hogar, dependientes.
        cargas: dict con claves horas_domesticas, horas_trabajo, horas_estudio.
        promedio_actual: PPA real del estudiante (opcional).

    Returns:
        dict con todos los indicadores calculados.
    """
    genero            = perfil["genero"]
    estrato           = perfil["estrato"]
    composicion_hogar = perfil["composicion_hogar"]
    dependientes      = perfil.get("dependientes", 0)

    horas_domesticas = cargas["horas_domesticas"]
    horas_trabajo    = cargas["horas_trabajo"]
    horas_estudio    = cargas["horas_estudio"]

    carga_total     = horas_domesticas + horas_trabajo
    fatiga          = calcular_fatiga(carga_total, genero, estrato, composicion_hogar)
    horas_efectivas = calcular_horas_efectivas(horas_estudio, fatiga)
    ppa_estimado    = estimar_ppa(horas_efectivas, estrato, genero, dependientes, fatiga)
    shadow_score    = calcular_shadow_score(carga_total, fatiga)
    interpretacion  = interpretar_shadow_score(shadow_score)

    coste_horas = horas_estudio - horas_efectivas
    coste_ppa   = (promedio_actual - ppa_estimado) if promedio_actual is not None else None

    comp_tiempo = carga_total / MAX_HORAS_SEMANA
    comp_fatiga = fatiga

    return {
        "carga_total":      carga_total,
        "fatiga":           round(fatiga, 4),
        "horas_efectivas":  round(horas_efectivas, 2),
        "ppa_estimado":     round(ppa_estimado, 2),
        "shadow_score":     round(shadow_score, 2),
        "comp_tiempo":      round(comp_tiempo, 4),
        "comp_fatiga":      round(comp_fatiga, 4),
        "interpretacion":   interpretacion,
        "coste_horas":      round(coste_horas, 2),
        "coste_ppa":        round(coste_ppa, 2) if coste_ppa is not None else None,
    }