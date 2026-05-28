import os
import time
import pandas as pd
from pathlib import Path
from tqdm import tqdm
from deep_translator import GoogleTranslator

def translate_dataframe(data_input, target_columns, source_lang='en', target_lang='es', checkpoint_path=None):
    """
    Traduce de manera genérica las columnas especificadas de un DataFrame o archivo CSV.
    
    Args:
        data_input (str, Path o pd.DataFrame): Ruta del archivo CSV o un DataFrame de Pandas ya cargado.
        target_columns (list o str): Columna o lista de columnas que se desean traducir.
        source_lang (str): Idioma de origen (por defecto 'en').
        target_lang (str): Idioma de destino (por defecto 'es').
        checkpoint_path (str o Path, opcional): Ruta para guardar un archivo temporal de respaldo.
        
    Returns:
        pd.DataFrame: El DataFrame con las columnas seleccionadas traducidas.
    """
    # 1. Validación y Carga de Datos
    if isinstance(data_input, (str, Path)):
        print(f"[INFO] Cargando archivo desde: {data_input}")
        df = pd.read_csv(data_input)
    elif isinstance(data_input, pd.DataFrame):
        df = data_input.copy()
    else:
        raise ValueError("[ERROR] 'data_input' debe ser una ruta de archivo válida o un DataFrame de Pandas.")

    # Asegurar que target_columns sea una lista
    if isinstance(target_columns, str):
        target_columns = [target_columns]

    # Verificar que las columnas existan en el DataFrame
    missing_cols = [col for col in target_columns if col not in df.columns]
    if missing_cols:
        raise KeyError(f"[ERROR] Las siguientes columnas no existen en el dataset: {missing_cols}")

    # 2. Configuración del Traductor
    translator = GoogleTranslator(source=source_lang, target=target_lang)
    
    # Convertir columnas a tipo string para evitar errores con valores numéricos/nulos
    for col in target_columns:
        df[col] = df[col].astype(str)

    print(f"[INFO] Iniciando traducción de {len(df)} filas para las columnas: {target_columns}")

    # 3. Procesamiento Fila por Fila (Seguro y Genérico)
    # Total de celdas a traducir para el cálculo preciso del progreso
    total_cells = len(df) * len(target_columns)
    
    with tqdm(total=total_cells, desc="Traduciendo celdas") as pbar:
        for idx, row in df.iterrows():
            for col in target_columns:
                original_text = row[col]
                
                # Evitar llamadas innecesarias a la API si la celda está vacía o es "nan"
                if not original_text or original_text.strip().lower() == 'nan':
                    pbar.update(1)
                    continue
                
                try:
                    # Traducir y actualizar directamente la celda del DataFrame
                    translated_text = translator.translate(original_text)
                    df.at[idx, col] = translated_text
                    
                except Exception as e:
                    print(f"\n[ERROR] Error en fila {idx}, columna '{col}': {e}")
                    print("[INFO] Conservando texto original para esta celda. Reintentando conexión...")
                    time.sleep(3)  # Pausa de seguridad por si es un bloqueo por límite de peticiones
                
                pbar.update(1)
            
            # Pausa sutil cada 10 filas para respetar los límites de la API de Google
            if idx % 10 == 0:
                time.sleep(0.2)
            
            # Guardar un backup en disco cada 50 filas si se especificó un checkpoint
            if checkpoint_path and idx % 50 == 0 and idx > 0:
                df.to_csv(checkpoint_path, index=False, encoding='utf-8-sig')

    # Eliminar el archivo de checkpoint temporal si todo terminó con éxito
    if checkpoint_path and os.path.exists(checkpoint_path):
        try:
            os.remove(checkpoint_path)
        except OSError:
            pass

    print("\n[SUCCESS] Proceso de traducción finalizado.")
    return df