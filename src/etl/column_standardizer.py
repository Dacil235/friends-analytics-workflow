import re
import pandas as pd
import unicodedata

def normalize_column(col: str) -> str:
    col = col.strip().lower()
    col = unicodedata.normalize("NFD", col)           # Descompone: "ó" -> "o" + acento
    col = col.encode("ascii", "ignore").decode("utf-8") # Elimina el acento, deja "o"
    col = re.sub(r"[^\w\s]", "", col)                 # Quita puntuación
    col = re.sub(r"\s+", "_", col)                    # Espacios -> guiones bajos
    return col

CANONICAL_MAP_EN = {
    "author": "character",
    "actoractriz": "actor",
    "author_name": "character",
    "autor": "character",
    "cancion" : "song",
    "cita": "quote",
    "descripcion" : "description",
    "descripción" : "description",
    "detalle" : "detail",
    "detail":"detail",
    "escenario" : "stage",
    "episode": "episode_number",
    "episodio" : "episode_number",
    "episode_number": "episode_number",
    "evento" : "event",
    "frase": "quote",
    "numero_escenas_est" : "est_num_scenes",
    "num_escenas_est" : "est_num_scenes",
    "personaje" : "character",
    "porcentaje_escenas_real" : "%_scenes",
    "quote": "quote",
    "song": "song",
    "scene": "scene",
    "season": "season",
    "season_number": "season",
    "speaker": "character",
    "stage": "stage",
    "temporada": "season",
    "titulo": "episode_title",    
    "titulo_episodio": "episode_title",
    "quote_order": "quote_order",
    "quote_ordered": "quote_order",
    "text" : "text",
    "tipo" : "type",
    "utterance": "utterance"
}

## PENDIENTE A TERMINAR FUNCIÓN INGLÉS / ESPAÑOL. 
CANONICAL_MAP_ES = {
    "author": "personaje",
    "actor": "actor",
    "actoractriz": "actor",
    "author_name": "personaje",
    "autor": "personaje",
    "cancion" : "cancion",
    "character": "personaje",
    "cita": "cita",
    "descripcion" : "descripcion",
    "descripción" : "descripcion",
    "detalle" : "detalle",
    "detail":"detalle",
    "escenario" : "escenario",
    "episode": "numero_episodio",
    "episodio" : "numero_episodio",
    "episode_number": "numero_episodio",
    "evento" : "evento",
    "frase": "cita",
    "numero_escenas_est" : "num_escenas_est",
    "porcentaje_escenas_real" : "%_escenas",
    "quote": "cita",
    "scene": "escena",
    "season": "temporada",
    "season_number": "temporada",
    "speaker": "personaje",
    "song": "cancion",
    "stage": "escenario",
    "temporada": "temporada",    
    "titulo": "titulo_episodio",
    "titulo_episodio": "titulo_episodio",
    "quote_order": "cita",
    "quote_ordered": "cita",
    "text" : "texto",
    "tipo" : "tipo",
    "utterance": "orden_intervencion"
}


def standardize_columns(df: pd.DataFrame, opc: int) -> pd.DataFrame:
    '''Estandariza los nombres de las columnas de un DataFrame.
    Args:
        df (pd.DataFrame): DataFrame a estandarizar.
        opc (int): Opción para seleccionar el mapa canónico (1 para español, 0 para inglés).
    Returns:
        pd.DataFrame: DataFrame con las columnas estandarizadas.'''
        
    original = df.columns.tolist()
    normalized = [normalize_column(c) for c in original]

    if opc == 1:
        final = [CANONICAL_MAP_ES.get(c, c) for c in normalized]
    else:
        final = [CANONICAL_MAP_EN.get(c, c) for c in normalized]

    return df.rename(columns=dict(zip(original, final)))
