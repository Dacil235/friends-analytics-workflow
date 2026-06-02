import deep_translator
import pandas as pd
from deep_translator import GoogleTranslator
from tqdm import tqdm
import time
import os

def translate_csv_fast(input_path, output_path):
    print(f"Leyendo {input_path}...")
    df = pd.read_csv(input_path)
    
    translator = GoogleTranslator(source='en', target='es')
    
    # Listas finales para el DataFrame
    lista_quotes_es = []
    lista_titulos_es = []
    
    # Tamaño del bloque (batch)
    batch_size = 50
    total_filas = len(df)
    
    print(f"Iniciando traducción súper rápida de {total_filas} líneas en bloques de {batch_size}...")
    
    # Procesamos en bloques con barra de progreso
    for i in tqdm(range(0, total_filas, batch_size)):
        batch = df.iloc[i:i+batch_size]
        
        # Unimos las citas del bloque usando un separador único " ||| "
        textos_quotes = [str(r) for r in batch['text']]
        pack_quotes = " ||| ".join(textos_quotes)
        
        # Unimos los títulos del bloque
        textos_titulos = [str(r) for r in batch['scene']]
        pack_titulos = " ||| ".join(textos_titulos)
        
        try:
            # Traducimos todo el paquete de citas de una sola vez
            trans_pack_quotes = translator.translate(pack_quotes)
            res_quotes = trans_pack_quotes.split(" ||| ")
            
            # Traducimos todo el paquete de títulos de una sola vez
            trans_pack_titulos = translator.translate(pack_titulos)
            res_titulos = trans_pack_titulos.split(" ||| ")
            
            # Si por error de la API el tamaño no cuadra, rellenamos con los originales
            if len(res_quotes) == len(batch):
                lista_quotes_es.extend(res_quotes)
            else:
                lista_quotes_es.extend(textos_quotes)
                
            if len(res_titulos) == len(batch):
                lista_titulos_es.extend(res_titulos)
            else:
                lista_titulos_es.extend(textos_titulos)
                
            # Una pausa muy pequeña por cortesía con la API
            time.sleep(0.5)
            
        except Exception as e:
            print(f"\nError en bloque {i}-{i+batch_size}: {e}. Manteniendo originales en este bloque.")
            lista_quotes_es.extend(textos_quotes)
            lista_titulos_es.extend(textos_titulos)
            time.sleep(2)

    # Asegurar que las listas midan exactamente lo mismo que el DataFrame
    df['text'] = lista_quotes_es[:total_filas]
    df['scene'] = lista_titulos_es[:total_filas]
    
    # Renombrar columnas
    df.columns = ['autor', 'numero_episodio', 'titulo_episodio', 'cita', 'orden_cita', 'temporada']
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"\n¡Proceso ultra rápido completado! Guardado en: {output_path}")

if __name__ == "__main__":
    INPUT_FILE = 'data_translated/friends.csv'
    OUTPUT_FILE = 'data_translated/friends_tr.csv'
    translate_csv_fast(INPUT_FILE, OUTPUT_FILE)
