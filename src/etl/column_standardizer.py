import re
import pandas as pd

def normalize_column(col: str) -> str:
    col = col.strip().lower()
    col = re.sub(r"[^\w\s]", "", col)
    col = re.sub(r"\s+", "_", col)
    return col

CANONICAL_MAP = {
    "author": "author",
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
}

def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    original = df.columns.tolist()
    normalized = [normalize_column(c) for c in original]
    final = [CANONICAL_MAP.get(c, c) for c in normalized]
    return df.rename(columns=dict(zip(original, final)))
