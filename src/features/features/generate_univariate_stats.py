# src/features/generate_univariate_stats.py
import os
import pandas as pd

def calcular_tasas_mercado_trabajo(df):
    """
    Calcula las tasas básicas del mercado de trabajo por trimestre y aglomerado.
    Estado: 1 = Ocupado, 2 = Desocupado, 3 = Inactivo.
    """
    # Agrupamos por año, trimestre, aglomerado y condición de actividad
    # Usamos siempre la variable 'pondera' para representar a la población real
    pob_estados = (
        df.groupby(["ano4", "trimestre", "aglomerado", "estado"])[
            "pondera"
        ]
        .sum()
        .unstack(fill_value=0)
    )

    # Renombramos columnas para claridad (evitando inconsistencias si falta algún estado)
    pob_estados = pob_estados.rename(
        columns={1: "ocupados", 2: "desocupados", 3: "inactivos"}
    )

    # Población Total del trimestre (en base a la muestra expandida)
    pob_estados["pob_total"] = (
        pob_estados["ocupados"]
        + pob_estados["desocupados"]
        + pob_estados["inactivos"]
    )
    pob_estados["PEA"] = (
        pob_estados["ocupados"] + pob_estados["desocupados"]
    )

    # Cálculo de Tasas (Multiplicado por 100 para porcentaje)
    pob_estados["tasa_actividad"] = (
        pob_estados["PEA"] / pob_estados["pob_total"]
    ) * 100
    pob_estados["tasa_empleo"] = (
        pob_estados["ocupados"] / pob_estados["pob_total"]
    ) * 100
    pob_estados["tasa_desocupacion"] = (
        pob_estados["desocupados"] / pob_estados["PEA"]
    ) * 100

    return pob_estados.reset_index()


def analizar_univariado_ingresos(df):
    """
    Calcula la evolución de medidas de tendencia central y posición
    para los ingresos reales de la ocupación principal (p21 > 0).
    """
    df_ingresos = df[df["ingreso_real"] > 0].copy()

    # Definimos las funciones de agregación para estadística descriptiva
    # Incluye Media, Mediana (p50), y los percentiles de posición (p25 y p75)
    stats_ingresos = (
        df_ingresos.groupby(["ano4", "aglomerado"])["ingreso_real"]
        .agg(
            media="mean",
            p25=lambda x: x.quantile(0.25),
            mediana="median",
            p75=lambda x: x.quantile(0.75),
        )
        .round(2)
    )

    return stats_ingresos.reset_index()


if __name__ == "__main__":
    path_final = "data/processed/serie_individual_final.pkl"

    if not os.path.exists(path_final):
        print(f"[ERROR] No existe el archivo {path_final}.")
        exit()

    df = pd.read_pickle(path_final)

    print("--- 1. CALCULANDO TASAS DEL MERCADO DE TRABAJO (SERIE HISTÓRICA) ---")
    df_tasas = calcular_tasas_mercado_trabajo(df)

    # Resumen univariado histórico de las tasas por aglomerado (Mapeo de códigos)
    # 33 = GBA, 5 = Gran Mendoza
    for aglo_cod, aglo_name in [
        (33, "Gran Buenos Aires"),
        (5, "Gran Mendoza"),
    ]:
        print(f"\n=================== {aglo_name.upper()} ===================")
        df_aglo = df_tasas[df_tasas["aglomerado"] == aglo_cod]

        resumen_tasas = df_aglo[
            ["tasa_actividad", "tasa_empleo", "tasa_desocupacion"]
        ].describe()
        print(resumen_tasas.round(2))

    print("\n--- 2. EVOLUCIÓN HISTÓRICA DE INGRESOS REALES (MÉTRICAS DE POSICIÓN) ---")
    df_ingresos_evolucion = analizar_univariado_ingresos(df)

    # Guardamos los resultados en la carpeta processsed para consumirlos desde los gráficos del informe
    os.makedirs("data/outputs", exist_ok=True)
    df_tasas.to_csv("data/outputs/tasas_mercado_trabajo.csv", index=False)
    df_ingresos_evolucion.to_csv(
        "data/outputs/evolucion_ingresos_univariado.csv", index=False
    )
    print(
        "\nResultados exportados con éxito a 'data/outputs/' en formato CSV para armar las tablas del informe."
    )