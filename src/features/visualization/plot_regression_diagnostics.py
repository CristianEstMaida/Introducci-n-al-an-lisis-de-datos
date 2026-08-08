# src/visualization/plot_regression_diagnostics.py
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
import statsmodels.api as sm

def generar_graficos_diagnostico(path_input, dir_output):
    if not os.path.exists(path_input):
        print(f"[ERROR] No se encontró el archivo final en {path_input}")
        return

    # Levantamos tu dataset final con los ingresos ya deflactados
    df = pd.read_pickle(path_input)

    # Filtrar datos válidos para la regresión (ej: personas con ingresos reales positivos)
    # Reemplaza 'Variable_X' por tu regresor real (ej: 'ano4', 'edad', 'educacion', etc.)
    df_model = df[(df["ingreso_real"] > 0) & (df["ano4"].notna())].copy()
    
    if df_model.empty:
        print("[ALERTA] No hay registros suficientes para ajustar el modelo.")
        return

    X = df_model["ano4"]  # Ejemplo usando el año cronológico
    y = df_model["ingreso_real"]

    # Ajustamos el modelo lineal (Añadiendo la constante para el intercepto)
    X_con_constante = sm.add_constant(X)
    modelo = sm.OLS(y, X_con_constante).fit()

    valores_ajustados = modelo.predict(X_con_constante)
    residuos = modelo.resid

    # Asegurar que exista la carpeta de salida para los gráficos
    os.makedirs(dir_output, exist_ok=True)

    print("Generando gráficos de diagnóstico estadístico...")

    # 1. Gráfico de Regresión Lineal
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(X, y, color='blue', alpha=0.3, label='Datos Observados')
    ax.plot(X, valores_ajustados, color='red', linewidth=2, 
            label=f'Línea de Regresión (R² = {modelo.rsquared:.3f})')
    ax.set_title('Gráfico de Regresión Lineal (Evolución de Ingresos)')
    ax.set_xlabel('Año')
    ax.set_ylabel('Ingreso Real')
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig(os.path.join(dir_output, '01_grafico_regresion.png'))
    plt.close()

    # 2. Gráfico Q-Q de Residuos (Evaluación de Normalidad)
    fig, ax = plt.subplots(figsize=(8, 5))
    stats.probplot(residuos, dist="norm", plot=ax)
    ax.set_title('Gráfico Q-Q de Residuos')
    ax.set_xlabel('Cuantiles Teóricos')
    ax.set_ylabel('Cuantiles de los Residuos')
    ax.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig(os.path.join(dir_output, '02_qq_plot_residuos.png'))
    plt.close()

    # 3. Gráfico de Homocedasticidad (Residuos vs. Valores Ajustados)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(valores_ajustados, residuos, color='purple', alpha=0.3)
    ax.axhline(y=0, color='red', linestyle='--', linewidth=1.5)
    ax.set_title('Gráfico de Homocedasticidad (Residuos vs. Predichos)')
    ax.set_xlabel('Valores Ajustados (Predichos)')
    ax.set_ylabel('Residuos')
    ax.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig(os.path.join(dir_output, '03_homocedasticidad_residuos.png'))
    plt.close()

    print(f"-> Éxito: Gráficos guardados en la carpeta '{dir_output}/'")

if __name__ == "__main__":
    archivo_final = "data/processed/serie_individual_final.pkl"
    carpeta_reportes = "data/outputs/graficos_diagnostico"
    generar_graficos_diagnostico(archivo_final, carpeta_reportes)