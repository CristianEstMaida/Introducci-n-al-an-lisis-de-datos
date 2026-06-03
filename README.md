# README.md

# Pipeline de Ingenieria de Datos - Procesamiento de la EPH (2016-2025)

Este proyecto contiene la infraestructura de codigo desarrollada en Python para la ingesta, extraccion, limpieza, consolidacion y transformacion economica de los microdatos de la Encuesta Permanente de Hogares (EPH) del INDEC, cubriendo la serie historica de los segundos trimestres del periodo 2016-2025.

El objetivo final del set de datos procesado es abastecer un analisis socioeconomico comparativo entre dos aglomerados urbanos y entrenar un modelo estadistico predictivo para la imputacion de la no respuesta a ingresos.

## 1. Arquitectura del Proyecto

El repositorio mantiene un diseno modular y predictivo basado en las mejores practicas de ingenieria de software:

```text
eph_project/
├── data/
│   ├── interim/          # Archivos .txt individuales extraidos programaticamente
│   ├── processed/        # Datasets consolidados y transformados en formato pickle
│   └── raw/              # Archivos fuentes EPH_usu_2_Trim_20XX_txt.zip descargados a mano del INDEC "https://www.indec.gob.ar/indec/web/Institucional-Indec-BasesDeDatos-1"
└── src/
    ├── data/
    │   └── extract_data.py   # Extractor selectivo de microdatos individuales
    └── features/
        ├── build_feature.py   # Consolidador de serie filtrado por aglomerado
        └── transform_income.py # Modulo de deflacion e ingenieria economica

## 2. Etapas del Pipeline de Datos (Que hicimos y Por que)
    Etapa 1: Ingesta y Extraccion Selectiva (src/data/)
    Que se hizo: Se almacenaron las bases de datos crudas empaquetadas en .zip dentro de data/raw/ y se desarrollo un script extractor selectivo utilizando la libreria nativa zipfile.

    Por que: Cada paquete del INDEC contiene multiples tablas (Hogares e Individuales) en formatos redundantes. El script extrae unicamente los archivos con patron individual en formato .txt, descartando las bases de hogares para optimizar el espacio en disco, reducir el uso de memoria RAM y acelerar la velocidad de lectura nativa de Pandas en un 90% en comparacion con archivos .xls.

    Etapa 2: Consolidacion y Filtrado Geografico (src/features/build_feature.py)
    Que se hizo: Se unificaron las 10 bases de datos trimestrales en un unico dataframe indexado de Pandas (78.070 registros totales), tipificando las columnas en minusculas y filtrando exclusivamente por los codigos de aglomerado elegidos por el grupo.

    Aglomerados Seleccionados:

        33: Partidos del Gran Buenos Aires (GBA)

        5: Gran Mendoza

    Por que: El procesamiento de datos masivos a nivel nacional desborda los recursos de hardware locales de forma innecesaria. El filtrado temprano por claves foraneas numericas (aglomerado) reduce la dimensionalidad del dataset, aisla las muestras de estudio requeridas por el parcial y unifica las discrepancias estructurales que el INDEC introdujo en los disenos de registro a lo largo de la decada.

    Etapa 3: Ingenieria Economica - Deflacion por IPC (src/features/transform_income.py)
    Que se hizo: Se creo la variable sintetica ingreso_real multiplicando el ingreso nominal declarado de la ocupacion principal (p21) por un vector homogeneo de factores de ajuste basados en el Indice de Precios al Consumidor (IPC) del INDEC, tomando como base el ano 2025.

    Por que: Debido al regimen inflacionario del periodo 2016-2025, una comparacion directa sobre los valores nominales destruye la validez de cualquier analisis temporal o modelo predictivo (sesgo por distorsion de precios relativos). Transformar los datos a pesos constantes de poder adquisitivo homogeneo permite evaluar la evolucion real de los ingresos y calibrar un modelo de regresion lineal donde los coeficientes estimen impactos socioeconomicos veridicos.

## 3. Tratamiento Proximo de Datos (Preparacion para el Modelo Predictivo)
    El dataset definitivo generado en data/processed/serie_individual_final.pkl aisla las variables demograficas clave (ch04 Sexo, ch06 Edad, nivel_ed Nivel Educativo) y laborales (estado Condicion de actividad, cat_ocup Categorizacion).

    Para el cumplimiento del Objetivo 4 (Aprobacion Directa), la estrategia de modelado consistira en:

    Segmentacion: Aislar los registros con valores mayores a cero en ingreso_real para conformar los conjuntos de entrenamiento y testeo (Train/Test Split).

    Filtrado de Blancos: Separar las filas donde la variable presente "No Respuesta" (codigo -9 o valores de no declaracion) para constituir el set de aplicacion final de las predicciones del modelo.