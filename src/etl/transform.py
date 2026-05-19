import re

def info_df(dataframe, search=None, sample_n=5):
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

    print("Informacion sobre el dataframe:")
    dataframe.info()
    print("-" * 100)

    print("La descripcion del dataframe de strings:")
    display(round(dataframe.describe(include=[object, "category"]).T),2)
    print("-" * 100)

    print("La descripcion del dataframe numérico:")
    display(round(dataframe.describe(exclude=[object, "category"]).T),2)
    print("-" * 100)

    print(f"La forma del dataframe es:\n{dataframe.shape[0]} filas\n{dataframe.shape[1]} columnas")
    print("-" * 100)

    if search:
        search_str = str(search).strip().lower()
        cols_match = [c for c in dataframe.columns if search_str in c.lower()]
        print(f"Columnas que contienen '{search}': {cols_match if cols_match else 'ninguna'}")

        mask = dataframe.apply(lambda col: col.astype(str).str.contains(search_str, case=False, na=False))
        rows_match = dataframe[mask.any(axis=1)]
        print(f"Filas con '{search}': {rows_match.shape[0]} encontrada(s)")
        if not rows_match.empty:
            display(rows_match.head(sample_n))
        else:
            print("No se encontraron filas con ese criterio.")
        print("-" * 100)

    print("Muestra del dataframe:")
    display(dataframe.sample(min(sample_n, len(dataframe))))


def analisis_columnas (dataframe):
    """
    Realiza un inventario detallado de cada columna del DataFrame para detectar 
    inconsistencias, nulos y la diversidad de los datos.

    Puntos clave de inspección:
    --------------------------
    1. Valores únicos: Identifica errores tipográficos (ej. "sALES eXECUTIVE") y 
       categorías redundantes.
    2. Duplicados: Cuenta registros repetidos dentro de cada columna (útil para IDs).
    3. Nulos: Cuantifica la ausencia de datos por columna (guía para la imputación).
    4. Tipo de dato: Verifica que la naturaleza del dato (float, int, object) coincida 
       con su contenido real.
    """
    for columna in dataframe:
        print(f"Columna: {columna}\n {"-" * 100}")
        print(f"Valores unicos: {dataframe[columna].unique()}\n {"-" * 100}")
        print(f"Valores duplicados: {dataframe[columna].duplicated().sum()}\n {"-" * 100}")
        print(f"Valores nulos: {dataframe[columna].isna().sum()}\n {"-" * 100}")
        print(f"El tipo de dato: {dataframe[columna].dtype}\n {"-" * 100}")


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