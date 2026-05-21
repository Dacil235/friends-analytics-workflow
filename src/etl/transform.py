import re

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
    