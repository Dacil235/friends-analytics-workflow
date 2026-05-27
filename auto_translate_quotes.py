import pandas as pd
from deep_translator import GoogleTranslator
from tqdm import tqdm
import time
import os

def translate_csv(input_path, output_path, limit=None):
    # 1. Cargar el archivo
    print(f"Leyendo {input_path}...")
    df = pd.read_csv(input_path)
    
    # Si queremos probar con pocos registros primero
    if limit:
        df = df.head(limit)
    
    # Configuramos el traductor de Deep Translator (usa Google Translate internamente)
    translator = GoogleTranslator(source='en', target='es')
    
    # Listas para almacenar las traducciones
    traducciones_quotes = []
    traducciones_titulos = []
    
    print(f"Iniciando traducción de {len(df)} líneas...")
    
    # 2. Traducir fila por fila con barra de progreso
    for index, row in tqdm(df.iterrows(), total=len(df)):
        original_quote = str(row['quote'])
        original_titulo = str(row['titulo_episodio'])
        
        try:
            # Traducir la cita
            trans_quote = translator.translate(original_quote)
            traducciones_quotes.append(trans_quote)
            
            # Traducir el título del episodio
            trans_titulo = translator.translate(original_titulo)
            traducciones_titulos.append(trans_titulo)
            
            # Pausa mínima para evitar límites (ajustada porque ahora haces 2 peticiones por fila)
            if index % 10 == 0:
                time.sleep(0.3)
                
        except Exception as e:
            print(f"\nError en línea {index}: {e}")
            # Si falla, añadimos el texto original para no desalinear el DataFrame
            traducciones_quotes.append(original_quote)
            traducciones_titulos.append(original_titulo)
            time.sleep(2)

    # 3. Guardar resultados
    # Sobrescribimos las columnas originales con las listas de traducciones obtenidas
    df['quote'] = traducciones_quotes
    df['titulo_episodio'] = traducciones_titulos
    
    # Renombrar columnas según el orden original de tu dataset de Friends
    df.columns = ['autor', 'numero_episodio', 'titulo_episodio', 'cita', 'orden_cita', 'temporada']
    
    # Crear la carpeta de salida si no existe
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Guardar a CSV
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"\n¡Prueba completada! Archivo guardado en: {output_path}")

if __name__ == "__main__":
    INPUT_FILE = 'data_raw/friends_quotes.csv'
    OUTPUT_FILE = 'data_translated/friends_quotes_auto.csv'
    
    # Si quieres hacer primero un test rápido, puedes cambiar limit=None por limit=10
    translate_csv(INPUT_FILE, OUTPUT_FILE, limit=None)

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
        textos_quotes = [str(r) for r in batch['quote']]
        pack_quotes = " ||| ".join(textos_quotes)
        
        # Unimos los títulos del bloque
        textos_titulos = [str(r) for r in batch['titulo_episodio']]
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
    df['quote'] = lista_quotes_es[:total_filas]
    df['titulo_episodio'] = lista_titulos_es[:total_filas]
    
    # Renombrar columnas
    df.columns = ['autor', 'numero_episodio', 'titulo_episodio', 'cita', 'orden_cita', 'temporada']
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"\n¡Proceso ultra rápido completado! Guardado en: {output_path}")

if __name__ == "__main__":
    INPUT_FILE = 'data_raw/friends_quotes.csv'
    OUTPUT_FILE = 'data_translated/friends_quotes_auto.csv'
    translate_csv_fast(INPUT_FILE, OUTPUT_FILE)
