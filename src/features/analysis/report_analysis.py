# src/analysis/report_analysis.py
import os
import pandas as pd


def generar_resumen_humano(path_tasas, path_ingresos, path_txt_out):
    """
    Levanta las metricas tecnicas procesadas y las traduce a un reporte
    redactado en lenguaje natural legible para cualquier usuario.
    """
    df_tasas = pd.read_pickle(path_tasas)
    df_ingresos = pd.read_pickle(path_ingresos)

    # Filtramos hitos temporales clave para el analisis temporal
    primer_periodo = df_tasas["ano4"].min()
    ultimo_periodo = df_tasas["ano4"].max()

    # Mapeo de nombres para consistencia de lectura
    mapa_aglom = {33: "Gran Buenos Aires (GBA)", 5: "Gran Mendoza"}

    with open(path_txt_out, "w") as f:
        f.write("=========================================================\n")
        f.write("      REPORTE DE EVOLUCION SOCIOECONOMICA (2016-2025)     \n")
        f.write("=========================================================\n\n")

        f.write("1. MERCADO LABORAL (EMPLEO Y DESOCUPACION)\n")
        f.write("---------------------------------------------------------\n")

        for aglom_id, aglom_nom in mapa_aglom.items():
            t_inicial = df_tasas[
                (df_tasas["ano4"] == primer_periodo)
                & (df_tasas["aglomerado"] == aglom_id)
            ]["tasa_desocupacion"].mean()
            t_final = df_tasas[
                (df_tasas["ano4"] == ultimo_periodo)
                & (df_tasas["aglomerado"] == aglom_id)
            ]["tasa_desocupacion"].mean()

            brecha = t_final - t_inicial
            comportamiento = "subio" if brecha > 0 else "bajo"

            f.write(f"* En el {aglom_nom}:\n")
            f.write(
                f"  - Al inicio del periodo ({primer_periodo}), la desocupacion afectaba al {round(t_inicial, 1)}% de la poblacion activa.\n"
            )
            f.write(
                f"  - Al cierre del periodo ({ultimo_periodo}), la desocupacion se ubico en el {round(t_final, 1)}%.\n"
            )
            f.write(
                f"  - En terminos netos, el desempleo {comportamiento} un {round(abs(brecha), 1)}% a lo largo de la decada.\n\n"
            )

        f.write("2. EVOLUCION DEL PODER ADQUISITIVO (INGRESOS REALES)\n")
        f.write("---------------------------------------------------------\n")
        f.write(
            "Nota: Los ingresos han sido corregidos por inflacion y estan expresados\n"
        )
        f.write(
            "en pesos constantes con poder de compra homogeneo de 2025.\n\n"
        )

        for aglom_id, aglom_nom in mapa_aglom.items():
            ing_inicial = df_ingresos[
                (df_ingresos["ano4"] == primer_periodo)
                & (df_ingresos["aglomerado"] == aglom_id)
            ]["ingreso_mediano_pond"].values[0]
            ing_final = df_ingresos[
                (df_ingresos["ano4"] == ultimo_periodo)
                & (df_ingresos["aglomerado"] == aglom_id)
            ]["ingreso_mediano_pond"].values[0]

            # Calculo de variacion porcentual del salario real
            var_porcentual = ((ing_final - ing_inicial) / ing_inicial) * 100
            impacto = "una recuperacion" if var_porcentual > 0 else "una perdida"

            f.write(f"* Analisis de ingresos en {aglom_nom}:\n")
            f.write(
                f"  - La mitad de los trabajadores ganaba menos de ${round(ing_inicial):,} (pesos de 2025) en {primer_periodo}.\n"
            )
            f.write(
                f"  - Para el ano {ultimo_periodo}, la mitad de los trabajadores ganaba menos de ${round(ing_final):,}.\n"
            )
            f.write(
                f"  - Esto representa {impacto} del {round(abs(var_porcentual), 1)}% del poder de compra real de la gente.\n\n"
            )

        f.write("=========================================================\n")
        f.write("                    FIN DEL REPORTE                      \n")
        f.write("=========================================================\n")


if __name__ == "__main__":
    tasas_in = "data/processed/tasas_mercado_trabajo_analysis.pkl"
    ingresos_in = "data/processed/evolucion_ingresos_analysis.pkl"

    # Guardamos el reporte final de texto en la carpeta de reportes
    os.makedirs("reports", exist_ok=True)
    reporte_out = "reports/reporte_humano.txt"

    if not os.path.exists(tasas_in) or not os.path.exists(ingresos_in):
        print(
            "[ERROR] Faltan los archivos de analisis. Correra primero stats_analysis.py"
        )
    else:
        print("Traduciendo metricas duras a lenguaje natural...")
        generar_resumen_humano(tasas_in, ingresos_in, reporte_out)
        print(f"-> Reporte generado con exito en: {reporte_out}")