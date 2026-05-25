import re
import pandas as pd

def normalize_column(col: str) -> str:
    col = col.strip().lower() # Elimina espacial y convierte a minúsculas
    col = re.sub(r"[^\w\s]", "", col) # Quita todo lo que no sea letras 
    col = re.sub(r"\s+", "_", col) # Reemplazar espacios por guiones bajos
    return col

CANONICAL_MAP = {
    "author": "author",
    "actoractriz": "actor",
    "author_name": "author",
    "autor": "author",
    "quote": "quote",
    "frase": "quote",
    "cita": "quote",
    "season": "season",
    "temporada": "season",
    "season_number": "season",
    "episode": "episode_number",
    "episode_number": "episode_number",
    "episode_title": "episode_title",
    "titulo_episodio": "episode_title",
    "quote_order": "quote_order",
    "quote_ordered": "quote_order",
    "descripción" : "description",
    "personaje" : "author",
    "episodio" : "episode_number",
    "descripcion" : "description",
    "escenario" : "stage",
    "tipo" : "type",
    "porcentaje_escenas_real" : "%_scenes",
    "numero_escenas_est" : "est_num_scenes",
    "cancion" : "song",
    "evento" : "event",
    "detalle" : "detail"
}

def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    original = df.columns.tolist()
    normalized = [normalize_column(c) for c in original]
    final = [CANONICAL_MAP.get(c, c) for c in normalized]
    return df.rename(columns=dict(zip(original, final)))
