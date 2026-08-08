# src/features/inspect_data.py
import os
import pandas as pd


def inspeccionar_dataset(path_pickle):
    """
    Levanta el DataFrame consolidado final y muestra su estructura,
    las primeras filas y estadisticas de control de los ingresos reales.
    """
    if not os.path.exists(path_pickle):
        print(f"[ERROR] No se encontro el archivo en {path_pickle}")
        return

    # Levantamos el DataFrame desde el archivo binario pickle
    df = pd.read_pickle(path_pickle)

    print("\n================ INFO GENERAL DEL DATAFRAME ================")
    print(f"Cantidad total de registros (filas): {df.shape[0]}")
    print(f"Cantidad de variables (columnas): {df.shape[1]}")
    print("\nColumnas presentes:")
    print(list(df.columns))
    print("=============================================================")

    print("\n================ PRIMERAS 5 FILAS ORDENADAS ================")
    # pd.set_option ayuda a que no se corte el texto en la consola de Git Bash
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 1000)
    print(df.head())
    print("=============================================================")

    print("\n========== CONTROL DE INGRESOS REALES POR AGLOMERADO ==========")
    # Filtramos los que si declararon ingresos para ver estadisticas reales
    df_con_ingreso = df[df["ingreso_real"] > 0]
    resumen = (
        df_con_ingreso.groupby("aglomerado")["ingreso_real"]
        .describe()
        .round(2)
    )
    print(resumen)
    print("=============================================================")


if __name__ == "__main__":
    archivo_final = "data/processed/serie_individual_final.pkl"
    inspeccionar_dataset(archivo_final)
