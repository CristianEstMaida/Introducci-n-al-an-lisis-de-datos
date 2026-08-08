# src/analysis/stats_analysis.py
import os
import numpy as np
import pandas as pd


def calcular_tasas_mercado_trabajo(df):
    """
    Calcula las tasas de Actividad, Empleo y Desocupacion agrupadas
    por ano, trimestre y aglomerado de forma vectorizada y optimizada.
    """
    # Vectorizacion: Operaciones booleanas de alta performance
    df["pob_total"] = df["pondera"]
    df["pob_ocupada"] = (df["estado"] == 1) * df["pondera"]
    df["pob_desocupada"] = (df["estado"] == 2) * df["pondera"]
    df["pea"] = df["pob_ocupada"] + df["pob_desocupada"]

    # Agrupamos eficientemente
    grouped = (
        df.groupby(["ano4", "trimestre", "aglomerado"])
        .agg(
            total_pob=("pob_total", "sum"),
            total_pea=("pea", "sum"),
            total_ocup=("pob_ocupada", "sum"),
            total_desocup=("pob_desocupada", "sum"),
        )
        .reset_index()
    )

    # Fórmulas oficiales de la catedra
    grouped["tasa_actividad"] = (grouped["total_pea"] / grouped["total_pob"]) * 100
    grouped["tasa_empleo"] = (grouped["total_ocup"] / grouped["total_pob"]) * 100
    grouped["tasa_desocupacion"] = (
        grouped["total_desocup"] / grouped["total_pea"]
    ) * 100

    return grouped


def _percentil_ponderado(valores, pesos, q):
    """
    Calculo matematico exacto para cuantiles ponderados basados en pesos de expansion.
    """
    idx = np.argsort(valores)
    valores_ordenados = valores[idx]
    pesos_ordenados = pesos[idx]

    cum_pesos = np.cumsum(pesos_ordenados) - 0.5 * pesos_ordenados
    cum_pesos /= np.sum(pesos_ordenados)

    return np.interp(q, cum_pesos, valores_ordenados)


def calcular_metricas_ingreso(df):
    """
    Calcula las medidas de tendencia central y posicion para el ingreso real
    aplicando de forma estricta los ponderadores de expansion poblacional.
    """
    # Filtramos la no respuesta y valores distorsivos
    df_validos = df[df["ingreso_real"] > 0].copy()

    resultados = []

    # Iteramos por los grupos para aplicar las funciones vectorizadas de numpy
    for (ano, aglomerado), grupo in df_validos.groupby(["ano4", "aglomerado"]):
        valores = grupo["ingreso_real"].to_numpy()
        pesos = grupo["pondera"].to_numpy()

        # Media ponderada: Suma(X * Pondera) / Suma(Pondera)
        media_p = np.average(valores, weights=pesos)

        # Percentiles ponderados
        q1_p = _percentil_ponderado(valores, pesos, 0.25)
        mediana_p = _percentil_ponderado(valores, pesos, 0.50)
        q3_p = _percentil_ponderado(valores, pesos, 0.75)

        resultados.append(
            {
                "ano4": ano,
                "aglomerado": aglomerado,
                "ingreso_medio_pond": round(media_p, 2),
                "ingreso_mediano_pond": round(mediana_p, 2),
                "q1_pond": round(q1_p, 2),
                "q3_pond": round(q3_p, 2),
            }
        )

    return pd.DataFrame(resultados)


if __name__ == "__main__":
    path_input = "data/processed/serie_individual_final.pkl"

    if not os.path.exists(path_input):
        print(f"[ERROR] No se encontro el archivo final en {path_input}")
    else:
        df_serie = pd.read_pickle(path_input)

        print("Calculando tasas del mercado de trabajo (Vectorizado)...")
        df_tasas = calcular_tasas_mercado_trabajo(df_serie)
        print(df_tasas.head(10))

        print("\nCalculando evolucion de ingresos reales ponderados...")
        df_ingresos = calcular_metricas_ingreso(df_serie)
        print(df_ingresos.head(10))

        os.makedirs("data/processed", exist_ok=True)
        df_tasas.to_pickle("data/processed/tasas_mercado_trabajo_analysis.pkl")
        df_ingresos.to_pickle("data/processed/evolucion_ingresos_analysis.pkl")
        print("\n-> Metricas calculadas y almacenadas con exito.")