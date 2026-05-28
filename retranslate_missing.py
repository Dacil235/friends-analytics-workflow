"""
retranslate_missing.py
----------------------
Revisa un CSV ya traducido, detecta las filas que siguen en inglés
(usando langdetect) y las retraduce usando Google Translate (gratis).

Requisitos:
    pip install pandas langdetect deep-translator tqdm

Uso:
    python retranslate_missing.py
"""

import os
import time
import pandas as pd
from tqdm import tqdm
from langdetect import detect, LangDetectException
from deep_translator import GoogleTranslator

# ── CONFIGURACIÓN ──────────────────────────────────────────────────────────────
os.chdir(os.path.dirname(os.path.abspath(__file__)))

INPUT_FILE  = "data_translated/friends_t1.csv"   # CSV con la traducción incompleta
OUTPUT_FILE = "data_translated/friends_t2.csv"  # CSV resultante

# Columnas que deben estar en español
COLUMNS_TO_TRANSLATE = ["text"]  # ← ajusta a tus nombres reales

BATCH_SIZE = 50    # textos por llamada a Google Translate
SLEEP_SEC  = 0.5   # pausa entre llamadas para no saturar
# ──────────────────────────────────────────────────────────────────────────────

translator = GoogleTranslator(source="en", target="es")


def is_english(text: str) -> bool:
    """Devuelve True si el texto parece estar en inglés."""
    if not isinstance(text, str) or text.strip() == "":
        return False
    try:
        return detect(text) == "en"
    except LangDetectException:
        return False


def row_needs_translation(row) -> bool:
    """True si CUALQUIERA de las columnas objetivo sigue en inglés."""
    return any(is_english(str(row[col])) for col in COLUMNS_TO_TRANSLATE if col in row.index)


def translate_batch(texts: list[str]) -> list[str]:
    """
    Traduce una lista de textos del inglés al español usando Google Translate.
    Devuelve la lista traducida en el mismo orden.
    """
    translated = []
    for text in texts:
        try:
            result = translator.translate(text)
            translated.append(result if result else text)
        except Exception:
            translated.append(text)  # si falla, conserva el original
    return translated


def retranslate_csv(input_path: str, output_path: str):
    print(f"Leyendo {input_path}...")
    df = pd.read_csv(input_path)

    # Verifica que las columnas existen
    missing_cols = [c for c in COLUMNS_TO_TRANSLATE if c not in df.columns]
    if missing_cols:
        print(f"ERROR: columnas no encontradas en el CSV: {missing_cols}")
        print(f"Columnas disponibles: {df.columns.tolist()}")
        return

    print("Detectando filas en inglés...")
    mask = df.apply(row_needs_translation, axis=1)
    indices_en = df[mask].index.tolist()

    print(f"  → {len(indices_en)} filas necesitan retraducción de {len(df)} totales.")

    if not indices_en:
        print("¡Todo ya está traducido! No hay nada que hacer.")
        df.to_csv(output_path, index=False)
        return

    # Procesa en batches
    for batch_start in tqdm(range(0, len(indices_en), BATCH_SIZE), desc="Retraduciendo"):
        batch_idx = indices_en[batch_start: batch_start + BATCH_SIZE]

        for col in COLUMNS_TO_TRANSLATE:
            if col not in df.columns:
                continue

            # Solo retraduce las celdas de esta columna que están en inglés
            col_mask = [is_english(str(df.at[i, col])) for i in batch_idx]
            to_translate_idx = [idx for idx, eng in zip(batch_idx, col_mask) if eng]

            if not to_translate_idx:
                continue

            texts = [str(df.at[i, col]) for i in to_translate_idx]
            translated = translate_batch(texts)
            for i, t in zip(to_translate_idx, translated):
                df.at[i, col] = t

        time.sleep(SLEEP_SEC)

    print(f"\nGuardando resultado en {output_path}...")
    df.to_csv(output_path, index=False)
    print("✅ ¡Listo!")


if __name__ == "__main__":
    retranslate_csv(INPUT_FILE, OUTPUT_FILE)