import pandas as pd
import psycopg2
from sqlalchemy import create_engine
from pymongo import MongoClient


#defing function for diffrent source types
def read_csv_source(path):
    df = pd.read_csv(path)
    return df

def read_mysql_source(connection_string , table):
    engine = create_engine(connection_string)
    query = f"SELECT * FROM {table}"
    df = pd.read_sql(query, engine)
    return df

def read_mongodb_source(connection_string, collection):
    client = MongoClient(connection_string)
    db = client["test"]
    collection = db[collection]

    data = list(collection.find())

    df = pd.DataFrame(data)
    if '_id' in df.columns:
        df = df.drop(columns=['_id'])
    return df

# function to map data types
def map_dtype(dtype):
    if 'int' in str(dtype):
        return 'INT'
    elif 'float' in str(dtype):
        return 'FLOAT'
    else:
        return 'TEXT'
    
# function to create table if not exists
def create_table_if_not_exists(df , table_name , cursor):
    columns = []
    for col , dtype in df.dtypes.items():
        sql_type = map_dtype(dtype)
        columns.append(f"{col} {sql_type}")

    columns_sql = ", ".join(columns)
    create_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        {columns_sql}
    )
    """

    cursor.execute(create_query)

# Insert data safely 
def insert_dataframe(df , table_name , cursor):
    cols = ", ".join(df.columns)
    placeholders = ", ".join(["%s"] * len(df.columns))

    insert_query = f"""
    INSERT INTO {table_name} ({cols}) VALUES ({placeholders})
    """

    for row in df.itertuples(index=False):
        cursor.execute(insert_query, tuple(row))

    

conn = psycopg2.connect(
    host="localhost",
    database="mydb",
    user="postgres",
    password="postgres"
)
cur = conn.cursor()
cur.execute("""
            SELECT  source_type, connection_info, source_object , target_table
            FROM source_registry 
            WHERE enabled = true
            """)
sources = cur.fetchall()

for source in sources:
    source_type = source[0]
    connection_info = source[1]
    source_object = source[2]
    table = source[3]

    print(f"Processing {source_type} -> {table}")

    if source_type == "csv":
        df = read_csv_source(source_object)
    elif source_type == "mysql":
        df = read_mysql_source(connection_info, source_object)
    elif source_type == "mongodb":
        df = read_mongodb_source(connection_info, source_object)
    else:
        print("Unkonwn source")
        continue

    create_table_if_not_exists(df , table , cur)

    insert_dataframe(df , table , cur)

    #cur.execute(f"UPDATE source_registry SET enabled = false WHERE source_type = '{source_type}' AND source_object = '{source_object}'")

conn.commit()

print("Data ingestion completed.")