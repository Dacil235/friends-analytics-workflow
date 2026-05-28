import time
import pandas as pd

from tqdm import tqdm
from langdetect import detect, LangDetectException
from deep_translator import GoogleTranslator


def detect_language(text: str) -> str | None:
    """
    Detecta el idioma de un texto.
    Devuelve el código de idioma o None si falla.
    """
    if not isinstance(text, str) or not text.strip():
        return None

    try:
        return detect(text)
    except LangDetectException:
        return None


def translate_texts(
    texts: list[str],
    translator
) -> list[str]:
    """
    Traduce una lista de textos usando el traductor proporcionado.
    """
    translated = []

    for text in texts:
        try:
            result = translator.translate(text)
            translated.append(result if result else text)

        except Exception:
            translated.append(text)

    return translated


def translate_dataframe(
    df: pd.DataFrame,
    columns: list[str],
    source_lang: str = "en",
    target_lang: str = "es",
    batch_size: int = 100,
    sleep_sec: float = 0.5,
    only_if_lang: str | None = "en",
    overwrite: bool = True,
    suffix: str = "_translated",
    translator=None,
    verbose: bool = True
) -> pd.DataFrame:
    """
    Traduce columnas de un DataFrame de forma genérica.

    Parámetros
    ----------
    df : pd.DataFrame
        DataFrame original.

    columns : list[str]
        Columnas a traducir.

    source_lang : str
        Idioma origen.

    target_lang : str
        Idioma destino.

    batch_size : int
        Cantidad de filas por lote.

    sleep_sec : float
        Pausa entre lotes.

    only_if_lang : str | None
        Solo traduce si detecta este idioma.
        Si es None, traduce todo.

    overwrite : bool
        Si True, sobrescribe columnas originales.

    suffix : str
        Sufijo para nuevas columnas si overwrite=False.

    translator :
        Traductor personalizado.
        Si None usa GoogleTranslator.

    verbose : bool
        Mostrar logs.

    Retorna
    -------
    pd.DataFrame
    """

    df = df.copy()

    # Verificar columnas
    missing_cols = [c for c in columns if c not in df.columns]

    if missing_cols:
        raise ValueError(f"Columnas no encontradas: {missing_cols}")

    # Traductor por defecto
    if translator is None:
        translator = GoogleTranslator(
            source=source_lang,
            target=target_lang
        )

    # Crear columnas nuevas si no overwrite
    if not overwrite:
        for col in columns:
            new_col = f"{col}{suffix}"
            df[new_col] = df[col]

    total_rows = len(df)

    for col in columns:

        target_col = col if overwrite else f"{col}{suffix}"

        if verbose:
            print(f"\nTraduciendo columna: {col}")

        # Detectar qué filas necesitan traducción
        indices_to_translate = []

        for idx, value in df[target_col].items():

            text = str(value)

            if only_if_lang is None:
                indices_to_translate.append(idx)

            else:
                detected = detect_language(text)

                if detected == only_if_lang:
                    indices_to_translate.append(idx)

        if verbose:
            print(
                f"  → {len(indices_to_translate)} "
                f"filas para traducir "
                f"de {total_rows}"
            )

        # Procesar en batches
        for start in tqdm(
            range(0, len(indices_to_translate), batch_size),
            desc=f"Traduciendo {col}",
            disable=not verbose
        ):

            batch_idx = indices_to_translate[start:start + batch_size]

            texts = [
                str(df.at[i, target_col])
                for i in batch_idx
            ]

            translated = translate_texts(
                texts=texts,
                translator=translator
            )

            for i, t in zip(batch_idx, translated):
                df.at[i, target_col] = t

            time.sleep(sleep_sec)

    return df