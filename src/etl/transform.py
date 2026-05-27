import re
import pandas as pd
from pathlib import Path

def info_df(dataframe, sample_n=5):
    """
    Genera un informe técnico del DataFrame: separa estadísticas por tipo de dato (str vs num),
    muestra dimensiones y permite buscar términos específicos en columnas y filas.

    Parámetros:
    -----------
    dataframe : pandas.DataFrame
        El conjunto de datos a analizar.
    search : str, opcional (default=None)
        Término de búsqueda para localizar columnas por nombre o filas por contenido 
        específico. Ignora mayúsculas/minúsculas.
    sample_n : int, opcional (default=5)
        Número de filas a mostrar en las previsualizaciones y muestras aleatorias.

    """

    print("\n" + "="*80)
    print("INFORME TÉCNICO DEL DATAFRAME")
    print("="*80)


     # Validación inicial
    if dataframe is None:
        print("❌ Error: El DataFrame es None.")
        return
    
    if not hasattr(dataframe, "shape"):
        print("❌ Error: El objeto proporcionado no es un DataFrame válido.")
        return

    if dataframe.empty:
        print("⚠️ El DataFrame está vacío. No hay datos que analizar.")
        return
    
  # Dimensiones
    print("\n🔹 Dimensiones:")
    print(f"- Filas: {dataframe.shape[0]}")
    print(f"- Columnas: {dataframe.shape[1]}")

    # Info general
    print("\n🔹 Info general:")
    try:
        dataframe.info()
    except Exception as e:
        print(f"❌ Error al mostrar dataframe.info(): {e}")

    # Nulos
    print("\n🔹 Nulos:")
    try:
        print(f"{dataframe.isna().sum()/dataframe.shape[0]*100}")
    except Exception as e:
        print(f"❌ Error al calcular nulos: {e}")

    # Duplicados
    print("\n🔹 Duplicados:")
    try:
        print(f"Total duplicados: {dataframe.duplicated().sum()}")
    except Exception as e:
        print(f"❌ Error al calcular duplicados: {e}")

    # Descriptivo cualitativo
    print("\n🔹 Descriptivo variables cualitativas:")
    try:
        qual_cols = dataframe.select_dtypes(include=['object', 'category'])
        if qual_cols.shape[1] > 0:
            display(qual_cols.describe().T)
        else:
            print("No hay variables cualitativas.")
    except Exception as e:
        print(f"❌ Error en descriptivo cualitativo: {e}")

    # Descriptivo cuantitativo
    print("\n🔹 Descriptivo variables cuantitativas:")
    try:
        num_cols = dataframe.select_dtypes(include='number')
        if num_cols.shape[1] > 0:
            display(num_cols.describe().T.round(2))
        else:
            print("No hay variables numéricas.")
    except Exception as e:
        print(f"❌ Error en descriptivo cuantitativo: {e}")

    print("\n🔹 Muestra del dataframe:")
    display(dataframe.sample(min(sample_n, len(dataframe))))


#función patrón regex para transformar los nombres de las columnas 
def transformar_nombre(nombre):
    """
    Normaliza nombres de columnas de CamelCase o PascalCase a snake_case 
    utilizando expresiones regulares.

    Transforma: 'MonthlyIncome' -> 'monthly_income'
    
    Proceso:
    1. Localiza posiciones entre caracteres donde sigue una mayúscula (sin ser el inicio).
    2. Inserta un guion bajo (_) en dichas posiciones.
    3. Convierte toda la cadena resultante a minúsculas.
    """
    # Agrega un guión bajo antes de cada mayúscula y lo pasa a minúsculas
    # El '(?<=[a-z])' busca una mayúscula que tenga una minúscula detrás
    nuevo_nombre = re.sub(r'(?<!^)(?=[A-Z])', '_', nombre).lower()
    return nuevo_nombre

#Funciones para la limpieza de datos:

def min_datos (df):
    ''' Función para poner en minúsculas y quitar espacios por guiones bajos en columnas df
    Devuelve el df.columns'''
    
    df.columns = df.columns.str.lower()
    df.columns = df.columns.str.replace(" ","_")

    return df.columns

def dato_a_int(valor):
    ''' Función que pasa valores float a int, si es  False, None o texto devuelve el mismo valor'''

    try:
        # Convertimos a float y luego a int para quitar el .0
        return int(float(valor))
    except (ValueError, TypeError):
        return valor
    
def nulos_false_int(df):
    '''Función que le recibe una columna y rellena los nulos por "False" y aplica la función dato_a_int
    Devuelve el df modificado'''
    df = df.fillna("False")
    df= df.apply(dato_a_int)
    
    return df

#Funciones para el análisis de los datos

def detectar_outliers_iqr(df, columna):
    '''Función que calcula los quartiles para calcular el IQR y sacar los límites y el número de outliers
    Devuelve el limite superior, limite inferior y la cantidad de outliers'''
    q1 = df[columna].quantile(0.25)
    q3 = df[columna].quantile(0.75)
    iqr = q3 - q1
    limite_superior = q3 + 1.5 * iqr
    limite_inferior = q1 - 1.5 * iqr
    
    #hago la máscara y digo que me saque un df con los outliers, luego le hago un len y devuelvo la cantidad de ellos.
    outliers = df[(df[columna] > limite_superior) | (df[columna] < limite_inferior)] 
    return limite_superior, limite_inferior, len(outliers)


def process_friends_writers(df_info, output_path="../data_processed/writers.csv"):
    """
    Procesa la columna 'written_by' del dataset de Friends, limpia anomalías
    de texto (nombres pegados, saltos de línea), desglosa los escritores en
    filas individuales con sus respectivos roles y exporta el resultado.

    Args:
        df_info (pd.DataFrame): DataFrame original con la información de los episodios.
        output_path (str): Ruta donde se guardará el archivo CSV procesado.

    Returns:
        pd.DataFrame: DataFrame limpio y normalizado con los escritores.
    """
    rows_escritores = []

    # Recorremos el DataFrame original fila por fila
    for idx, row in df_info.iterrows():
        sea = row['season']
        epi = row['episode']
        texto = str(row['written_by']).strip()
        
        # ==========================================================
        # === PASO DE PRE-LIMPIEZA AGRESIVA (Para evitar nombres pegados) ===
        # ==========================================================
        # A) Separar nombres pegados por falta de espacios/comas (Ej: "Sikowitzmichael" -> "Sikowitz, michael")
        texto = re.sub(r'([a-z])([A-Z])', r'\1, \2', texto)
        
        # B) Separar nombres pegados a la palabra 'teleplay' o 'story' (Ej: "Jungeteleplay" -> "Junge, teleplay")
        texto = re.sub(r'(?i)([a-z])(teleplay\s+by|story\s+by)', r'\1, \2', texto)
        
        # C) Homogeneizar espaciados dobles que rompan las divisiones posteriores
        texto = re.sub(r'\s+', ' ', texto).strip()
        
        # --- CASO A: TIENE CRÉDITOS DIVIDIDOS (Story by / Teleplay by) ---
        if "story by" in texto.lower() or "teleplay by" in texto.lower():
            
            # Usamos expresiones regulares para identificar quién es quién sin importar el orden
            story_match = re.search(r'(?i)story\s+by:\s*([^,]+(?:,\s*[^,]+)*)', texto)
            teleplay_match = re.search(r'(?i)teleplay\s+by:\s*([^,]+(?:,\s*[^,]+)*)', texto)
            
            nombres_story = []
            nombres_teleplay = []
            
            if story_match:
                bloque_story = story_match.group(1)
                bloque_story = re.sub(r'(?i)\s+and\s+|\s+&\s+', ', ', bloque_story)
                nombres_story = [n.strip() for n in bloque_story.split(',') if n.strip()]
                
            if teleplay_match:
                bloque_teleplay = teleplay_match.group(1)
                bloque_teleplay = re.sub(r'(?i)\s+and\s+|\s+&\s+', ', ', bloque_teleplay)
                nombres_teleplay = [n.strip() for n in bloque_teleplay.split(',') if n.strip()]
                
            # Si un nombre quedó suelto AL PRINCIPIO antes de "Teleplay by:"
            if teleplay_match and not story_match:
                antes_teleplay = texto.split(teleplay_match.group(0))[0].strip().rstrip(',')
                if antes_teleplay and "story by" not in antes_teleplay.lower():
                    antes_teleplay = re.sub(r'(?i)\s+and\s+|\s+&\s+', ', ', antes_teleplay)
                    nombres_story = [n.strip() for n in antes_teleplay.split(',') if n.strip()]

            # Guardamos los resultados clasificados asegurando que no se cuelen fragmentos de etiquetas
            for nom in nombres_story:
                if "teleplay" not in nom.lower() and "story" not in nom.lower():
                    rows_escritores.append({"season": sea, "episode": epi, "writer": nom})
            for nom in nombres_teleplay:
                if "teleplay" not in nom.lower() and "story" not in nom.lower():
                    rows_escritores.append({"season": sea, "episode": epi, "writer": nom})

        # --- CASO B: ESCRITORES NORMALES (Sin etiquetas) ---
        else:
            limpio = re.sub(r'(?i)\s+and\s+|\s+&\s+', ', ', texto)
            nombres = [n.strip() for n in limpio.split(',') if n.strip()]
            
            for nom in nombres:
                rows_escritores.append({"season": sea, "episode": epi, "writer": nom})

    # 2. Convertir la lista en el DataFrame final
    df_writers_clean = pd.DataFrame(rows_escritores)

    # ==========================================================
    # === PASO DE RESCATE PARA FILAS ROTAS (Saltos de línea) ===
    # ==========================================================
    # A) Convertir strings vacíos en None para poder eliminarlos con dropna
    df_writers_clean['writer'] = df_writers_clean['writer'].replace(r'^\s*$', None, regex=True)
    df_writers_clean = df_writers_clean.dropna(subset=['writer'])

    # B) Rellenar hacia abajo (ffill) las temporadas y episodios vacíos rotos por el "Enter" original
    df_writers_clean['season'] = df_writers_clean['season'].ffill()
    df_writers_clean['episode'] = df_writers_clean['episode'].ffill()

    # Convertir a enteros nativos para evitar problemas de tipos (.0) en las uniones de BI
    df_writers_clean['season'] = df_writers_clean['season'].astype(int)
    df_writers_clean['episode'] = df_writers_clean['episode'].astype(int)
    # ==========================================================

    # 3. Limpieza estética final de los nombres
    df_writers_clean['writer'] = df_writers_clean['writer'].str.title().str.strip()

    # Eliminamos duplicados absolutos de filas por seguridad
    df_writers_clean = df_writers_clean.drop_duplicates()

    # Filtro de seguridad: Evitar textos basura residuales de menos de 3 caracteres
    df_writers_clean = df_writers_clean[df_writers_clean['writer'].str.len() > 3]

    # 4. Exportar el fichero limpio definitivo asegurando la existencia de la carpeta destino
    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    
    df_writers_clean.to_csv(out_path, index=False, encoding="utf-8")
    print(f"¡Fichero corregido con éxito! Guardado en: {out_path.resolve()} ({len(df_writers_clean)} filas).")
    
    return df_writers_clean