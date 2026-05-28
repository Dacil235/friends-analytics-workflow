import pandas as pd
import re
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
        "weddings": "weddings_divorces_ross.csv",
        "cameos": "friends_cameos.csv",
        "emotions": "friends_emotions.csv",
        "epiv3": "friends_episodes.csv",
        "sets": "friends_sets.csv",
        "info": "friends_info.csv",
        "quotes": "friends_quotes.csv",
        "friends": "friends.csv",
        "songs": "phoebe_buffay_songs.csv",
        "dac": "duck_and_chicken.csv",
        #"writers": "writers.csv"
    }

    data = {}

    for key, filename in files.items():
        file_path = base / filename

        if not file_path.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {file_path.resolve()}")

        logging.info(f"→ Cargando {filename}...")

        # Configuraciones especiales
        # Dentro de tu bucle for en load_data.py
        try:
            # 1. Intentamos primero con UTF-8 con soporte para firmas de Excel (BOM)
            df = pd.read_csv(file_path, sep=None, engine="python", encoding="utf-8-sig")
        except UnicodeDecodeError:
            # 2. Si falla por problemas de caracteres, lo cargamos con Latin-1
            df = pd.read_csv(file_path, sep=None, engine="python", encoding="latin-1")

        data[key] = df

    logging.info("Todos los datasets fueron cargados correctamente.")
    return data




def load_friends_data_translated(base_path="../data_translated/"):
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
        "weddings": "friends_weddings_divorce_ross.csv",
        "cameos": "friends_cameos.csv",
        "emotions": "friends_emotions.csv",
        "epiv3": "friends_episodes.csv",
        "sets": "friends_sets.csv",
        "info": "friends_info.csv",
        "quotes": "friends_quotes.csv",
        "friends": "friends.csv",
        "songs": "friends_songs.csv",
        "dac": "duck_and_chicken.csv",
        "writers": "writers.csv"
    }

    data = {}

    for key, filename in files.items():
        file_path = base / filename

        if not file_path.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {file_path.resolve()}")

        logging.info(f"→ Cargando {filename}...")

        # Configuraciones especiales
        # Dentro de tu bucle for en load_data.py
        try:
            # 1. Intentamos primero con UTF-8 con soporte para firmas de Excel (BOM)
            df = pd.read_csv(file_path, sep=None, engine="python", encoding="utf-8-sig", 
                 on_bad_lines='skip', quotechar='"')
        except UnicodeDecodeError:
            # 2. Si falla por problemas de caracteres, lo cargamos con Latin-1
            df = pd.read_csv(file_path, sep=None, engine="python", encoding="latin-1", 
                 on_bad_lines='skip', quotechar='"')

        data[key] = df

    logging.info("Todos los datasets fueron cargados correctamente.")
    return data


