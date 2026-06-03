# src/data/extract_data.py
import os
import zipfile


def extraer_individuales_desde_cero(dir_raw, dir_interim):
    """
    Limpia el directorio intermedio y extrae unicamente las bases
    individuales de personas desde los archivos zip validos.
    """
    # Validacion de infraestructura basica
    if not os.path.exists(dir_raw):
        print(
            f"[ERROR] No existe la carpeta {dir_raw}. Move los .zip ahi adentro."
        )
        return

    if not os.path.exists(dir_interim):
        os.makedirs(dir_interim)

    # Listar los archivos zip reales descargados a mano
    archivos_zip = [f for f in os.listdir(dir_raw) if f.endswith(".zip")]

    if not archivos_zip:
        print(f"[ALERTA] No se encontraron archivos .zip en {dir_raw}")
        return

    print(
        f"Se detectaron {len(archivos_zip)} archivos para procesar en {dir_raw}"
    )
    print("Iniciando extraccion selectiva de bases individuales...")

    for archivo in archivos_zip:
        path_zip = os.path.join(dir_raw, archivo)

        try:
            with zipfile.ZipFile(path_zip, "r") as zip_ref:
                contenido = zip_ref.namelist()

                # Filtrar el archivo de microdatos individuales de personas
                target_txt = [
                    f
                    for f in contenido
                    if "individual" in f.lower() and f.endswith(".txt")
                ]

                if target_txt:
                    archivo_origen = target_txt[0]

                    # Estandarizamos el nombre final del archivo de datos intermedio
                    # Ejemplo: EPH_tot_2trim_16.zip -> usu_individual_2trim_16.txt
                    sufijo = archivo.replace("EPH_tot_", "").replace(
                        ".zip", ""
                    )
                    nuevo_nombre = f"usu_individual_{sufijo}.txt"
                    path_destino = os.path.join(dir_interim, nuevo_nombre)

                    # Extraccion limpia por chunks de bytes
                    with zip_ref.open(archivo_origen) as f_src, open(
                        path_destino, "wb"
                    ) as f_dst:
                        f_dst.write(f_src.read())

                    print(f"-> Procesado con exito: {nuevo_nombre}")
                else:
                    print(
                        f"[AVISO] El archivo {archivo} no contiene una base de personas."
                    )

        except zipfile.BadZipFile:
            print(
                f"[CRITICO] El archivo {archivo} esta corrupto o no es un ZIP valido. Volvelo a bajar a mano."
            )
        except Exception as e:
            print(f"[ERROR] Fallo inesperado en {archivo}: {e}")


if __name__ == "__main__":
    # Definicion de rutas relativas desde la raiz del proyecto
    extraer_individuales_desde_cero("data/raw", "data/interim")