# src/features/build_feature.py
import os
import pandas as pd


def consolidar_serie_individual(dir_interim, codigos_aglomerados):
    """
    Levanta los 10 archivos txt de personas, filtra por los aglomerados
    seleccionados por el grupo y estandariza los datos faltantes (-9).
    """
    archivos_txt = [
        f for f in os.listdir(dir_interim) if f.endswith(".txt")
    ]
    dataframes_validos = []

    print(
        f"Procesando e integrando {len(archivos_txt)} bases individuales..."
    )

    for archivo in archivos_txt:
        path_completo = os.path.join(dir_interim, archivo)

        # Forzamos sep=';' debido a la estructura nativa del INDEC
        df = pd.read_csv(path_completo, sep=";", low_memory=False)

        # Estandarizamos columnas a minusculas para evitar inconsistencias de anos
        df.columns = df.columns.str.lower()

        # Filtrado inmediato por los dos aglomerados elegidos por el grupo
        df_filtrado = df[df["aglomerado"].isin(codigos_aglomerados)].copy()

        # Seleccionamos las variables indispensables para el parcial
        columnas_tp = [
            "codusu",
            "ano4",
            "trimestre",
            "aglomerado",
            "ch04",  # Sexo
            "ch06",  # Edad
            "nivel_ed",  # Nivel educativo
            "estado",  # Condicion de actividad
            "cat_ocup",  # Categoria ocupacional
            "p21",  # Ingreso ocupacion principal
            "pondera",  # Factor de expansion
        ]

        # Validamos que el ano tenga todas las columnas
        columnas_existentes = [
            c for c in columnas_tp if c in df_filtrado.columns
        ]
        df_filtrado = df_filtrado[columnas_existentes]

        dataframes_validos.append(df_filtrado)

    # Consolidacion de la serie historica completa
    df_serie = pd.concat(dataframes_validos, ignore_index=True)

    print(
        f"-> Serie consolidada con exito. Registros totales: {len(df_serie)}"
    )
    return df_serie


if __name__ == "__main__":
    # REEMPLAZO CONFIGURADO: 33 = GBA, 5 = Gran Mendoza
    aglomerados_grupo = [33, 5]
    df_final = consolidar_serie_individual(
        "data/interim", aglomerados_grupo
    )

    # Guardamos el dataset procesado intermedio
    os.makedirs("data/processed", exist_ok=True)
    df_final.to_pickle(
        "data/processed/serie_individual_consolidada.pkl"
    )
    print(
        "Dataset guardado en data/processed/serie_individual_consolidada.pkl"
    )
