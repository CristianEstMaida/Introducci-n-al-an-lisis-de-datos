# src/features/transform_income.py
import os
import pandas as pd


def aplicar_deflacion_ingresos(path_input, path_output):
    """
    Levanta la serie consolidada, sanitiza la columna p21 forzando tipo numerico
    y multiplica los ingresos nominales por el factor de ajuste por inflacion.
    """
    if not os.path.exists(path_input):
        print(f"[ERROR] No se encontro el archivo consolidado en {path_input}")
        return

    # Cargamos el dataframe binario indexado
    df = pd.read_pickle(path_input)

    # DICCIONARIO DE FACTORES DE DEFLACION (Ajuste por IPC del INDEC)
    # COEFICIENTES CORREGIDOS: Factores de escala reales de conversion de poder de compra
    # factores_inflacion = {
    #     2016: 5.68,   
    #     2017: 3.91,   
    #     2018: 2.51,   
    #     2019: 1.59,   
    #     2020: 1.22,   
    #     2021: 0.81,   
    #     2022: 0.42,   
    #     2023: 0.20,   
    #     2024: 0.07,   
    #     2025: 1.00,   
    # }
    # factores_inflacion = {
    #     2016: 166.6,
    #     2017: 132.4,
    #     2018: 101.2,
    #     2019: 68.5,
    #     2020: 48.1,
    #     2021: 32.3,
    #     2022: 18.7,
    #     2023: 7.9,
    #     2024: 1.4,
    #     2025: 1.0,
    # }
    factores_inflacion = {
        2016: 107.1,
        2017: 85.8,
        2018: 58.2,
        2019: 27.8,
        2020: 19.1,
        2021: 14.2,
        2022: 7.8,
        2023: 3.0,
        2024: 1.4,
        2025: 1.0,
    }

    print("Sanitizando columna de ingresos (p21)...")
    # errors='coerce' transforma cualquier string invalido (como espacios vacios) en NaN
    df["p21"] = pd.to_numeric(df["p21"], errors="coerce")

    # Los valores faltantes u outliers de texto los normalizamos a 0 o -9 para mantener logica INDEC
    df["p21"] = df["p21"].fillna(0)

    print("Aplicando ingenieria de caracteristicas: calculo de ingresos reales...")

    # Creamos la columna nueva mapeando el ano4 con nuestro diccionario de coeficientes
    df["factor_ajuste"] = df["ano4"].map(factores_inflacion)

    # Calculamos el ingreso real de la ocupacion principal
    df["ingreso_real"] = df["p21"] * df["factor_ajuste"]
    df.loc[df["p21"] <= 0, "ingreso_real"] = df["p21"]

    # Guardamos el dataset procesado final
    df.to_pickle(path_output)
    print(f"-> Transformacion completada con exito.")
    print(f"Dataset definitivo guardado en: {path_output}")


if __name__ == "__main__":
    archivo_entrada = "data/processed/serie_individual_consolidada.pkl"
    archivo_salida = "data/processed/serie_individual_final.pkl"
    aplicar_deflacion_ingresos(archivo_entrada, archivo_salida)