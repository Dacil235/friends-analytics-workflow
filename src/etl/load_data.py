import pandas as pd
from pathlib import Path
import logging

# Configuración básica del logger
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def load_friends_data_raw(base_path="../data_raw"):
    """
    Carga todos los CSV del proyecto Friends y devuelve un diccionario
    con los DataFrames listos para usar.

    Args:
        base_path (str): Ruta a la carpeta donde están los CSV.

    Returns:
        dict: Diccionario con los DataFrames cargados.
    """

    base = Path(base_path)

    if not base.exists():
        raise FileNotFoundError(f"La carpeta no existe: {base.resolve()}")

    logging.info(f"Cargando datasets desde: {base.resolve()}")

    files = {
        "bodas_divorcios": "bodas_divorcios_ross.csv",
        "cameos": "cameos_friends_completo.csv",
        "emotions": "friends_emotions.csv",
        "epiv3": "friends_episodes.csv",
        "escenarios": "friends_escenarios.csv",
        "info": "friends_info.csv",
        "quotes": "friends_quotes.csv",
        "friends": "friends.csv",
        "songs": "phoebe_buffay_songs.csv",
        "pato_pollito": "apariciones_detalladas_pato_y_pollito.csv"
    }

    data = {}

    for key, filename in files.items():
        file_path = base / filename

        if not file_path.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {file_path.resolve()}")

        logging.info(f"→ Cargando {filename}...")

        # Configuraciones especiales
        if key == "epiv3":
            df = pd.read_csv(file_path, encoding="latin-1")
        elif key == "pato_pollito":
            df = pd.read_csv(file_path, sep=";", encoding="latin-1")
        else:
            df = pd.read_csv(file_path)

        data[key] = df

    logging.info("Todos los datasets fueron cargados correctamente.")
    return data
