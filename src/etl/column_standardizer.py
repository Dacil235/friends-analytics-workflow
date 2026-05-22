"""

column_standardizer.py
 
Versión optimizada:

- NO carga modelos dentro del módulo

- Recibe translator y semantic_unifier como parámetros

- Mucho más rápido en notebooks y ETLs

"""
 
import re

import pandas as pd
 
 
# ============================================================

# 1. Normalización básica

# ============================================================
 
def normalize_column(col: str) -> str:

    """Convierte una columna a snake_case y minúsculas."""

    col = col.strip()

    col = col.lower()

    col = re.sub(r"[^\w\s]", "", col)      # quitar caracteres raros

    col = re.sub(r"\s+", "_", col)         # espacios → _

    return col
 
 
# ============================================================

# 2. IA HuggingFace (recibe modelos desde fuera)

# ============================================================
 
def ai_translate(col: str, translator) -> str:

    """Traduce una columna usando el modelo ya cargado."""

    prompt = (

        f"Traduce este nombre de columna al inglés y conviértelo a snake_case. "

        f"Devuelve solo una cadena válida:\n{col}"

    )

    result = translator(prompt, max_length=64)[0]["generated_text"]

    return result.strip().strip("'").strip('"')
 
 
def ai_unify(col: str, semantic_unifier) -> str:

    """Unifica semánticamente una columna usando el modelo ya cargado."""

    prompt = (

        f"Unifica este nombre de columna a un estándar semántico. "

        f"Ejemplo: season_number, temporada → season. "

        f"Devuelve solo una cadena válida:\n{col}"

    )

    result = semantic_unifier(prompt, max_length=64)[0]["generated_text"]

    return result.strip().strip("'").strip('"')
 
 
# ============================================================

# 3. Pipeline principal

# ============================================================
 
def standardize_columns_with_global_dict(

    df: pd.DataFrame,

    translator,

    semantic_unifier,

    global_dict: dict

) -> pd.DataFrame:

    """

    Pipeline completo:

    - Normaliza columnas

    - Consulta diccionario global

    - IA para columnas nuevas

    - Actualiza diccionario global

    - Renombra DataFrame

    """
 
    original_cols = df.columns.tolist()

    normalized = [normalize_column(c) for c in original_cols]
 
    final_cols = []
 
    for col in normalized:

        if col in global_dict:

            final_cols.append(global_dict[col])

        else:

            translated = ai_translate(col, translator)

            unified = ai_unify(translated, semantic_unifier)
 
            final_cols.append(unified)

            global_dict[col] = unified  # aprendizaje incremental
 
    rename_map = dict(zip(original_cols, final_cols))

    return df.rename(columns=rename_map), global_dict

 