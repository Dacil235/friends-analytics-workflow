import os
import time
import pandas as pd
from pathlib import Path
from tqdm import tqdm
from deep_translator import GoogleTranslator

def generic_translate_dataframe(data_input, target_columns, source_lang='en', target_lang='es', checkpoint_path=None):
    """
    A generic, schema-agnostic function to translate specified columns in a pandas DataFrame or CSV file.
    
    Args:
        data_input (str, Path, or pd.DataFrame): Path to the CSV file or an already loaded pandas DataFrame.
        target_columns (list or str): A single column name or a list of column names to translate.
        source_lang (str): Source language code (default is 'en').
        target_lang (str): Target language code (default is 'es').
        checkpoint_path (str or Path, optional): Path to save a temporary backup CSV during long iterations.
        
    Returns:
        pd.DataFrame: The modified DataFrame with translated target columns.
    """
    # 1. Data Input Validation & Loading
    if isinstance(data_input, (str, Path)):
        print(f"[INFO] Loading dataset from: {data_input}")
        df = pd.read_csv(data_input)
    elif isinstance(data_input, pd.DataFrame):
        df = data_input.copy()
    else:
        raise ValueError("[ERROR] 'data_input' must be a valid file path string, Path object, or pandas DataFrame.")

    # Ensure target_columns is a list even if a single string is passed
    if isinstance(target_columns, str):
        target_columns = [target_columns]

    # Validate that all requested columns actually exist
    missing_cols = [col for col in target_columns if col not in df.columns]
    if missing_cols:
        raise KeyError(f"[ERROR] The following target columns do not exist in the dataset: {missing_cols}")

    # 2. Setup Translator and Data Types
    translator = GoogleTranslator(source=source_lang, target=target_lang)
    
    # Cast target columns to string to handle any mixed types safely
    for col in target_columns:
        df[col] = df[col].astype(str)

    print(f"[INFO] Initializing translation for {len(df)} rows across columns: {target_columns}")

    # 3. Row-by-Row Safe Processing
    total_cells = len(df) * len(target_columns)
    
    with tqdm(total=total_cells, desc="Translating data cells") as pbar:
        for idx, row in df.iterrows():
            for col in target_columns:
                original_text = row[col]
                
                # Skip empty cells or raw 'nan' strings to save API quota and time
                if not original_text or original_text.strip().lower() == 'nan':
                    pbar.update(1)
                    continue
                
                try:
                    # Translate and update the cell directly in-place
                    translated_text = translator.translate(original_text)
                    df.at[idx, col] = translated_text
                    
                except Exception as e:
                    print(f"\n[WARNING] Error on row index {idx}, column '{col}': {e}")
                    print("[INFO] Connection glitch or rate limit reached. Keeping original text for this cell and retrying...")
                    time.sleep(3)  # Cooldown safety pause
                
                pbar.update(1)
            
            # Anti-blocking throttle: subtle sleep every 10 rows
            if idx % 10 == 0:
                time.sleep(0.2)
            
            # Optional Checkpoint: saves progress to disk every 50 rows to protect your data
            if checkpoint_path and idx % 50 == 0 and idx > 0:
                df.to_csv(checkpoint_path, index=False, encoding='utf-8-sig')

    # Clean up checkpoint file if processing finishes flawlessly
    if checkpoint_path and os.path.exists(checkpoint_path):
        try:
            os.remove(checkpoint_path)
        except OSError:
            pass

    print("\n[SUCCESS] Translation process completed successfully.")
    return df


if __name__ == "__main__":
    # EXAMPLE USAGE (Adjust paths and columns as needed)
    INPUT_FILE = 'data_raw/friends_quotes.csv'
    OUTPUT_FILE = 'data_translated/friends_quotes_es.csv'
    
    # You can pass the file path directly and specify any columns you want:
    cols_to_translate = ['quote', 'titulo_episodio']
    
    translated_df = generic_translate_dataframe(
        data_input=INPUT_FILE,
        target_columns=cols_to_translate,
        checkpoint_path='data_translated/temp_backup.csv'
    )
    
    # Save the final result
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    translated_df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')