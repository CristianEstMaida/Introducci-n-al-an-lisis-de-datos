# src/visualization/plots_visualization.py
import os
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def generar_grafico_tasas(path_tasas, output_dir):
    """
    Genera graficos de lineas temporales para comparar las tasas de actividad,
    empleo y desocupacion entre los dos aglomerados seleccionados.
    """
    df_tasas = pd.read_pickle(path_tasas)

    # Creamos una variable de linea temporal combinando ano y trimestre
    df_tasas["periodo"] = (
        df_tasas["ano4"].astype(str) + "T" + df_tasas["trimestre"].astype(str)
    )

    # Mapeo de nombres de aglomerados para mejorar la estetica de las leyendas
    mapa_aglom = {33: "GBA", 5: "Gran Mendoza"}
    df_tasas["Aglomerado"] = df_tasas["aglomerado"].map(mapa_aglom)

    tasas = ["tasa_actividad", "tasa_empleo", "tasa_desocupacion"]
    titulos = [
        "Evolucion de la Tasa de Actividad",
        "Evolucion de la Tasa de Empleo",
        "Evolucion de la Tasa de Desocupacion",
    ]

    sns.set_theme(style="whitegrid")

    for tasa, titulo in zip(tasas, titulos):
        plt.figure(figsize=(12, 5))
        sns.lineplot(
            data=df_tasas,
            x="periodo",
            y=tasa,
            hue="Aglomerado",
            marker="o",
            linewidth=2,
            palette="Set1",
        )

        plt.title(titulo, fontsize=14, fontweight="bold", pad=15)
        plt.xlabel("Periodo (Ano y Trimestre)", fontsize=11, labelpad=10)
        plt.ylabel("Porcentaje (%)", fontsize=11, labelpad=10)
        plt.xticks(rotation=45, ha="right", fontsize=9)
        plt.tight_layout()

        # Guardado sistematico en alta definicion para impresion en PDF
        nombre_archivo = f"evolucion_{tasa}.png"
        plt.savefig(os.path.join(output_dir, nombre_archivo), dpi=300)
        plt.close()
        print(f"-> Grafico exportado con exito: {nombre_archivo}")


def generar_boxplot_multivariado(path_final, output_dir):
    """
    Genera un diagrama de caja (boxplot) cruzando Ingresos Reales,
    Sexo y Nivel Educativo para analizar segmentacion socioeconomica.
    """
    df = pd.read_pickle(path_final)

    # Filtramos para el ultimo ano disponible con ingresos validos declarados
    ultimo_ano = df["ano4"].max()
    df_filtrado = df[
        (df["ano4"] == ultimo_ano) & (df["ingreso_real"] > 0)
    ].copy()

    # Mapeos de variables categoricas segun los manuales del INDEC
    df_filtrado["Sexo"] = df_filtrado["ch04"].map({1: "Varon", 2: "Mujer"})
    df_filtrado["Educacion"] = df_filtrado["nivel_ed"].map(
        {
            1: "Primaria Inc",
            2: "Primaria Comp",
            3: "Secundaria Inc",
            4: "Secundaria Comp",
            5: "Superior Inc",
            6: "Superior Comp",
            7: "Sin Instruccion",
        }
    )

    # Limpiamos nulos que puedan surgir de codificaciones inconsistentes
    df_filtrado = df_filtrado.dropna(subset=["Sexo", "Educacion"])

    plt.figure(figsize=(14, 7))
    sns.boxplot(
        data=df_filtrado,
        x="Educacion",
        y="ingreso_real",
        hue="Sexo",
        palette="pastel",
        order=[
            "Sin Instruccion",
            "Primaria Inc",
            "Primaria Comp",
            "Secundaria Inc",
            "Secundaria Comp",
            "Superior Inc",
            "Superior Comp",
        ],
    )

    plt.title(
        f"Distribucion de Ingresos Reales por Nivel Educativo y Sexo ({ultimo_ano})",
        fontsize=14,
        fontweight="bold",
        pad=15,
    )
    plt.xlabel("Nivel Educativo Maximo Alcanzado", fontsize=11, labelpad=10)
    plt.ylabel("Ingreso Real (Pesos Constantes)", fontsize=11, labelpad=10)
    plt.xticks(rotation=30, ha="right", fontsize=10)
    plt.yscale("log")  # Escala logaritmica para manejar la dispersion de outliers
    plt.tight_layout()

    nombre_archivo = "boxplot_ingresos_multivariado.png"
    plt.savefig(os.path.join(output_dir, nombre_archivo), dpi=300)
    plt.close()
    print(f"-> Grafico exportado con exito: {nombre_archivo}")


if __name__ == "__main__":
    # Definicion de rutas del pipeline
    tasas_input = "data/processed/tasas_mercado_trabajo_analysis.pkl"
    final_input = "data/processed/serie_individual_final.pkl"
    figures_dir = "reports/figures"

    os.makedirs(figures_dir, exist_ok=True)

    print("Iniciando generacion sistematica de graficos para el informe...")
    generar_grafico_tasas(tasas_input, figures_dir)
    generar_boxplot_multivariado(final_input, figures_dir)
    print(f"\n-> Proceso terminado. Archivos png listos en: {figures_dir}/")
