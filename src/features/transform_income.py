# src/features/transform_income.py
import os
import pandas as pd


def aplicar_deflacion_ingresos(path_input, path_output):
    """
    Levanta la serie consolidada y multiplica los ingresos nominales (p21)
    por el factor de ajuste por inflacion correspondiente a cada ano.
    """
    if not os.path.exists(path_input):
        print(f"[ERROR] No se encontro el archivo consolidado en {path_input}")
        return

    # Cargamos el dataframe binario indexado
    df = pd.read_pickle(path_input)

    # DICCIONARIO DE FACTORES DE DEFLACION (Ajuste por IPC del INDEC)
    # Nota: Estos coeficientes multiplican el valor nominal para llevarlo
    # a pesos constantes de poder adquisitivo homogeneo (base fin de serie).
    factores_inflacion = {
        2016: 35.4,
        2017: 28.2,
        2018: 19.1,
        2019: 12.4,
        2020: 8.7,
        2021: 5.8,
        2022: 3.0,
        2023: 1.4,
        2024: 1.1,
        2025: 1.0,  # Ano base
    }

    print("Aplicando ingenieria de caracteristicas: calculo de ingresos reales...")

    # Creamos la columna nueva mapeando el ano4 con nuestro diccionario de coeficientes
    df["factor_ajuste"] = df["ano4"].map(factores_inflacion)

    # Calculamos el ingreso real de la ocupacion principal
    # Si el ingreso es menor o igual a cero (o -9), mantenemos el valor original
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
