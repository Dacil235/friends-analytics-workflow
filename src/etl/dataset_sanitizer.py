import re
import pandas as pd
from pathlib import Path

def has_formatting_anomalies(cell_text):
    """
    Evaluates a single cell text string generically to detect formatting anomalies or 
    structural corruptions. 
    
    Returns:
        bool: True if any structural anomaly, unclosed bracket, wrapping curly bracket,
              or raw text-shifting newline is found.
    """
    if pd.isna(cell_text):
        return False
    
    text_string = str(cell_text).strip()
    
    # -------------------------------------------------------------------------
    # 1. TEXT-SHIFTING / CORRUPTED DATA CONTROL (e.g., "Bladder Control" case)
    # If the cell contains raw newlines, it indicates a line split error 
    # inherited from an incorrectly formatted or parsed CSV row.
    # -------------------------------------------------------------------------
    if "\n" in text_string or "\r" in text_string:
        return True

    # Flatten spaces to evaluate formatting syntax rules safely
    text = text_string.replace("\n", " ").replace("\r", " ").strip()
    
    # 2. PURE ACTION RECORDS: Entire cell text block is an action wrapped in <...>
    # (Catches: "<they hug and kiss...>" and "<Amy gets pissed...>")
    if text.startswith("<") and text.endswith(">"):
        return True

    # 3. BRACKETS WRAPPERS: Entire quote incorrectly wrapped inside curly brackets
    # (Catches: "{Y'know, sometimes...}" and "{Oh, all right!}")
    if (text.startswith("{") and text.endswith("}")) or (text.startswith('"{') and text.endswith('}"')):
        return True

    # 4. EMBEDDED CHARACTERS: Character name + action verb at the very beginning of the cell
    # (Catches: "<Joey looks> Oh!" or "<Chandler is startled> Sorry")
    if re.match(r"^<[A-Z][a-z]+(?:\s+[a-z]+)+>", text):
        return True
        
    # 5. FAIL-SAFE SYMBOL COUNT: Verification for unclosed or orphan tags
    if text.count("<") != text.count(">") or text.count("{") != text.count("}"):
        return True

    return False

def export_data_anomalies(path_in, path_out, target_columns, chunksize=50000):
    """
    Parses the input dataset in blocks, applies the anomaly filter dynamically across
    a user-provided list of columns, and exports flagged records to a tracking CSV.
    
    Returns:
        pd.DataFrame: A DataFrame containing all flagged invalid records.
    """
    anomalies = []

    # Automatically convert a single column string into a list if necessary
    if isinstance(target_columns, str):
        target_columns = [target_columns]

    # Stream processing via chunks to optimize memory allocation
    for chunk in pd.read_csv(
        path_in,
        chunksize=chunksize,
        on_bad_lines="skip",     # ← ignora filas corruptas
        quoting=3,               # ← ignora comillas mal formadas
        engine="python"          # ← parser más tolerante
    ):
        # Generate a boolean mask aligned with the chunk's real index to prevent IndexingErrors
        mask = pd.Series([False] * len(chunk), index=chunk.index)

        # Iterates dynamically over the specified columns
        for col in target_columns:
            if col in chunk.columns:
                mask |= chunk[col].apply(has_formatting_anomalies)

        if mask.any():
            chunk_errors = chunk[mask].copy()
            
            # Map the exact spreadsheet row number (Pandas Index + 2 for headers offset)
            chunk_errors['Original_Row_Index'] = chunk_errors.index + 2
            anomalies.append(chunk_errors)

    if anomalies:
        df_anomalies = pd.concat(anomalies)
        
        # Enforce 'Original_Row_Index' as the primary tracking column at the front
        ordered_columns = ['Original_Row_Index'] + [
            col for col in df_anomalies.columns if col != 'Original_Row_Index'
        ]
        df_anomalies = df_anomalies[ordered_columns]
        
        df_anomalies.to_csv(path_out, index=False)
        print(f"[SUCCESS] Data analysis complete. {len(df_anomalies)} anomalies exported to: {path_out}")
        return df_anomalies
    else:
        print("[INFO] No data anomalies were found in the specified target columns.")
        return pd.DataFrame()


def sanitize_dataset_by_index(path_in, path_anomalies, path_out, chunksize=50000):
    """
    Removes invalid records from the source dataset using tracked row index numbers.
    This index-based lookup completely bypasses internal parsing text conflicts.
    
    Returns:
        bool: True if the sanitization process completes successfully.
    """
    try:
        df_anomalies = pd.read_csv(path_anomalies)
    except FileNotFoundError:
        raise FileNotFoundError(f"[ERROR] Anomalies tracking file not found at: {path_anomalies}")
    except Exception as e:
        raise RuntimeError(f"[ERROR] Failed to read anomalies file: {e}")

    if df_anomalies.empty:
        print("[INFO] Anomalies file is empty. Sanitization skipped.")
        return False

    # Extract target rows to drop. Subtract 2 to restore Pandas native 0-indexed position.
    rows_to_remove = set(df_anomalies['Original_Row_Index'] - 2)
    clean_chunks = []
    
    try:
        for chunk in pd.read_csv(path_in, chunksize=chunksize):
            # Highly optimized O(1) hash-set lookup to filter out target rows seamlessly
            chunk_clean = chunk[~chunk.index.isin(rows_to_remove)]
            clean_chunks.append(chunk_clean)
    except FileNotFoundError:
        raise FileNotFoundError(f"[ERROR] Source dataset file not found at: {path_in}")
    except Exception as e:
        raise RuntimeError(f"[ERROR] Error processing source dataset: {e}")

    # Concatenate and stream out the final clean dataset
    try:
        df_final = pd.concat(clean_chunks)
        df_final.to_csv(path_out, index=False)
        print(f"[SUCCESS] Dataset sanitization complete. Clean file saved at: {path_out}")
    except Exception as e:
        raise RuntimeError(f"[ERROR] Failed to write sanitized dataset: {e}")

    return True