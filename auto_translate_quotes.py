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
    OUTPUT_FILE = 'data_translated/friends_quotes_tr.csv'
    
    # Si quieres hacer primero un test rápido, puedes cambiar limit=None por limit=10
    translate_csv(INPUT_FILE, OUTPUT_FILE, limit=None)

