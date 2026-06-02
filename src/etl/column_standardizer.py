import re
import pandas as pd

def normalize_column(col: str) -> str:
    col = col.strip().lower() # Elimina espacial y convierte a minúsculas
    col = re.sub(r"[^\w\s]", "", col) # Quita todo lo que no sea letras 
    col = re.sub(r"\s+", "_", col) # Reemplazar espacios por guiones bajos
    return col

CANONICAL_MAP_EN = {
    "author": "author",
    "actoractriz": "personaje",
    "author_name": "personaje",
    "author": "personaje",
    "autor": "personaje",

    "descripcion" : "description",
    "descripción" : "description",
    "detalle" : "detail",
    "escenario" : "stage",
    "episode": "episode_number",
    "episodio" : "episode_number",
    "episode_number": "numero_episodio",
    "evento" : "event",
    "frase": "quote",
    "numero_escenas_est" : "est_num_scenes",
    "porcentaje_escenas_real" : "%_scenes",
    "quote": "quote",
    "scene": "escena",
    "season": "season",
    "season_number": "season",
    "speaker": "personaje",
    "season": "temporada",
    "temporada": "season",    
    "titulo_episodio": "episode_title",
    "quote_order": "quote_order",
    "quote_ordered": "quote_order",
    "text" : "texto",
    "tipo" : "type",
    "utterance": "orden_intervencion"
}

CANONICAL_MAP_ES = {
    "author": "author",
    "actoractriz": "personaje",
    "author_name": "personaje",
    "author": "personaje",
    "autor": "personaje",
    "cancion" : "song",
    "cita": "quote",
    "descripcion" : "description",
    "descripción" : "description",
    "detalle" : "detail",
    "escenario" : "stage",
    "episode": "episode_number",
    "episodio" : "episode_number",
    "episode_number": "numero_episodio",
    "evento" : "event",
    "frase": "quote",
    "numero_escenas_est" : "est_num_scenes",
    "porcentaje_escenas_real" : "%_scenes",
    "quote": "quote",
    "scene": "escena",
    "season": "season",
    "season_number": "season",
    "speaker": "personaje",
    "season": "temporada",
    "temporada": "season",    
    "titulo_episodio": "episode_title",
    "quote_order": "quote_order",
    "quote_ordered": "quote_order",
    "text" : "texto",
    "tipo" : "type",
    "utterance": "orden_intervencion"
}


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    original = df.columns.tolist()
    normalized = [normalize_column(c) for c in original]
    final = [CANONICAL_MAP_EN.get(c, c) for c in normalized]
    return df.rename(columns=dict(zip(original, final)))
