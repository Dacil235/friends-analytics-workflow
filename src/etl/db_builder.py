import os
import pandas as pd
from sqlalchemy import create_engine, text

def get_connection_string(db_name=None, user=None, password=None, host=None, port=None):
    """
    Centraliza la creación de la URL de forma dinámica.
    Resuelve problemas de importación y añade la barra de seguridad para SQLAlchemy.
    """
    # Evaluación dinámica: si es None, va a buscarlo al entorno en este instante
    user = user or os.getenv("DB_USER")
    password = password or os.getenv("DB_PASSWORD") # Asegúrate si tu .env usa DB_PASS o DB_PASSWORD
    host = host or os.getenv("DB_HOST")
    port = port or os.getenv("DB_PORT", "3306")
    
    if db_name:
        return f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}"
    return f"mysql+pymysql://{user}:{password}@{host}:{port}/"


## 1️⃣ Crear Base de Datos
def create_database_if_not_exists(db_name):
    """Crea la base de datos si no existe usando la conexión por defecto."""
    connection_url = get_connection_string()
    engine_server = create_engine(connection_url)
    
    try:
        with engine_server.begin() as con:
            con.execute(text(f"CREATE DATABASE IF NOT EXISTS {db_name}"))
            print(f"✅ Base de datos '{db_name}' verificada/creada con éxito.")
    finally:
        engine_server.dispose()


## 2️⃣ Cargar el DataFrame
def load_dataframe_to_mysql(df, table_name, db_name, if_exists="replace"):
    """Carga un DataFrame pidiéndote solo los datos esenciales."""
    connection_url = get_connection_string(db_name=db_name)
    engine = create_engine(connection_url)
    
    try:
        df.to_sql(table_name, con=engine, if_exists=if_exists, index=False)
        print(f"✅ Datos cargados exitosamente en la tabla '{table_name}'.")
    finally:
        engine.dispose()


## 3️⃣ Definir la Clave Primaria
def set_primary_key(table_name, pk_column, db_name, data_type="INT"):
    """
    Asigna la PK en la tabla indicada. 
    Permite cambiar el tipo de dato (por defecto INT) por si tu clave es VARCHAR.
    """
    connection_url = get_connection_string(db_name=db_name)
    engine = create_engine(connection_url)
    
    try:
        with engine.begin() as con:
            # Primero modificamos la columna para asegurarnos que no acepte nulos
            con.execute(text(f"ALTER TABLE {table_name} MODIFY {pk_column} {data_type} NOT NULL"))
            con.execute(text(f"ALTER TABLE {table_name} ADD PRIMARY KEY ({pk_column})"))
            print(f"✅ Clave primaria '{pk_column}' ({data_type}) asignada en '{table_name}'.")
    finally:
        engine.dispose()


## 4️⃣ Función para definir una Clave Foránea (Foreign Key)
def set_foreign_key(fact_table, dimension_table, fk_column, db_name, pk_column=None, data_type="INT"):
    """
    Crea una relación de clave foránea entre una tabla de hechos y una de dimensión.
    Se añade el parámetro data_type para garantizar que ambas columnas coincidan exactamente en tipo.
    """
    if pk_column is None:
        pk_column = fk_column
        
    connection_url = get_connection_string(db_name=db_name)
    engine = create_engine(connection_url)
    
    constraint_name = f"fk_{fact_table}_{dimension_table}_{fk_column}"
    
    try:
        with engine.begin() as con:
            # En SQL, para que haya FK, el tipo de dato debe ser EXACTAMENTE idéntico al de la PK
            con.execute(text(f"ALTER TABLE {fact_table} MODIFY {fk_column} {data_type} NOT NULL"))
            
            query = f"""
                ALTER TABLE {fact_table}
                ADD CONSTRAINT {constraint_name}
                FOREIGN KEY ({fk_column})
                REFERENCES {dimension_table}({pk_column})
                ON DELETE CASCADE
                ON UPDATE CASCADE
            """
            con.execute(text(query))
            print(f"🔗 Relación creada: {fact_table}.{fk_column} ➡️ {dimension_table}.{pk_column}")
            
    except Exception as e:
        print(f"❌ Error al asignar la clave foránea en {fact_table}: {e}")
        raise
    finally:
        engine.dispose()