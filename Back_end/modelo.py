"""
Modelo matemático para Shadow-Score Académico.
Parámetros calibrados con base en la ENUT 2024-2025 del DANE.
"""

import math

# =========================================================
# PARÁMETROS BASADOS EN LA ENUT
# =========================================================

# Fatiga cognitiva
MU = 50.0           # horas de carga total (punto medio)
KAPPA = 12.0        # pendiente (suavidad)

# Factores de ajuste
ALPHA_GENERO = {
    'Femenino': 1.2,
    'Masculino': 1.0
}

BETA_ESTRATO = {
    1: 1.20,
    2: 1.15,
    3: 1.10,
    4: 1.00,
    5: 0.95,
    6: 0.90
}

GAMMA_HOGAR = {
    'Vive solo/a': 0.85,
    'Con familia': 1.00,
    'Con pareja': 1.10,
    'Residencia universitaria': 0.90,
    'Otros': 1.00
}

# Coeficientes del PPA (sin cambios)
BETA_0 = 2.8
BETA_1 = 0.03
BETA_2 = 0.12
BETA_3 = -0.15
BETA_4 = -0.08
BETA_5 = -0.5

MAX_CARGA = 168.0
MAX_FACTOR = 1.4     # evita saturación total


def sigmoide(x: float) -> float:
    try:
        return 1.0 / (1.0 + math.exp(-x))
    except OverflowError:
        return 1.0 if x > 0 else 0.0


def calcular_fatiga(carga_total: float, genero: str, estrato: int, composicion_hogar: str) -> float:
    x = (carga_total - MU) / KAPPA
    sigma = sigmoide(x)
    
    alpha = ALPHA_GENERO.get(genero, 1.0)
    beta = BETA_ESTRATO.get(estrato, 1.0)
    gamma = GAMMA_HOGAR.get(composicion_hogar, 1.0)
    
    factor = alpha * beta * gamma
    factor = min(factor, MAX_FACTOR)
    
    fatiga = sigma * factor
    return min(1.0, fatiga)


def calcular_horas_efectivas(horas_estudio: float, fatiga: float) -> float:
    return horas_estudio * (1.0 - fatiga)


def estimar_ppa(horas_efectivas: float, estrato: int, genero: str, dependientes: int, fatiga: float) -> float:
    gen_binario = 1.0 if genero == 'Femenino' else 0.0
    ppa = (BETA_0 +
           BETA_1 * horas_efectivas +
           BETA_2 * estrato +
           BETA_3 * gen_binario +
           BETA_4 * dependientes +
           BETA_5 * gen_binario * fatiga)
    return max(0.0, min(5.0, ppa))


def calcular_shadow_score(carga_total: float, fatiga: float) -> float:
    score = (carga_total / MAX_CARGA) * 100.0 * fatiga
    return min(100.0, score)


def interpretar_shadow_score(score: float) -> str:
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


def ejecutar_modelo(perfil: dict, cargas: dict, promedio_actual: float = None) -> dict:
    genero = perfil['genero']
    estrato = perfil['estrato']
    composicion_hogar = perfil['composicion_hogar']
    dependientes = perfil.get('dependientes', 0)
    
    horas_domesticas = cargas['horas_domesticas']
    horas_trabajo = cargas['horas_trabajo']
    horas_estudio = cargas['horas_estudio']
    
    carga_total = horas_domesticas + horas_trabajo
    fatiga = calcular_fatiga(carga_total, genero, estrato, composicion_hogar)
    horas_efectivas = calcular_horas_efectivas(horas_estudio, fatiga)
    ppa_estimado = estimar_ppa(horas_efectivas, estrato, genero, dependientes, fatiga)
    shadow_score = calcular_shadow_score(carga_total, fatiga)
    interpretacion = interpretar_shadow_score(shadow_score)
    
    coste_horas = horas_estudio - horas_efectivas
    coste_ppa = (promedio_actual - ppa_estimado) if promedio_actual is not None else None
    
    return {
        'carga_total': carga_total,
        'fatiga': fatiga,
        'horas_efectivas': horas_efectivas,
        'ppa_estimado': ppa_estimado,
        'shadow_score': shadow_score,
        'interpretacion': interpretacion,
        'coste_horas': coste_horas,
        'coste_ppa': coste_ppa
    }