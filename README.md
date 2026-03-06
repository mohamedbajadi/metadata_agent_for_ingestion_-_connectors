# Metadata-Driven Data Ingestion MVP

## Overview

This project demonstrates a **metadata-driven data ingestion pipeline** capable of loading data from multiple external sources into a centralized PostgreSQL database.

Instead of writing a new ingestion script for each source, the system uses a **metadata registry table** that defines how data should be extracted and loaded.

The ingestion agent automatically:

1. Reads metadata from a registry table
2. Detects the source type (CSV, MySQL, MongoDB)
3. Connects to the source system
4. Extracts the data into a pandas DataFrame
5. Automatically creates the target table if it does not exist
6. Loads the data into PostgreSQL

This MVP simulates the architecture commonly used in modern **data platforms and ELT pipelines**, similar to systems used with cloud warehouses like Snowflake.

---

# Architecture

```
                +-----------------------+
                |     source_registry   |
                |  (PostgreSQL table)  |
                +-----------+-----------+
                            |
                            v
                 Python Metadata Agent
             (pandas + psycopg2 connectors)
                            |
          +-----------------+------------------+
          |                 |                  |
          v                 v                  v
        CSV              MySQL              MongoDB
      (files)        (Docker source)      (NoSQL source)
          |                 |                  |
          +-------- Data Extraction -----------+
                            |
                            v
                Automatic Schema Detection
                    (pandas df.dtypes)
                            |
                            v
                   PostgreSQL Target Tables
```

---

# How It Works

### 1 Metadata Registry

A **PostgreSQL metadata table (`source_registry`)** defines all ingestion sources.

Each row represents a pipeline configuration including:

* source type
* connection information
* source object (file, table, or collection)
* target table

---

### 2 Ingestion Agent

The Python ingestion agent:

1. Reads enabled sources from `source_registry`
2. Detects the connector type
3. Uses the appropriate connector to extract data
4. Converts the data into a pandas DataFrame
5. Automatically generates a SQL schema from `df.dtypes`
6. Creates the target table if it does not exist
7. Inserts the data into PostgreSQL

---

# Project Structure

```
project/
│
├── data/
│   ├── sales.csv
│   ├── users.csv
│   └── products.csv
│
├── ingestion_agent.py
├── README.md
```

---

# Requirements

* Python 3.9+
* Docker
* PostgreSQL
* Python libraries:

```
pandas
psycopg2
sqlalchemy
pymysql
pymongo
openpyxl
```

Install dependencies:

```bash
pip install pandas psycopg2 sqlalchemy pymysql pymongo openpyxl
```

---

# Running PostgreSQL with Docker

Start a PostgreSQL container:

```bash
docker run --name metadata-db \
-e POSTGRES_PASSWORD=postgres \
-p 5432:5432 \
-d postgres
```

Connection settings:

```
host: localhost
port: 5432
user: postgres
password: postgres
database: mydb
```

---

# Running MySQL Source with Docker

To simulate an external database source:

```bash
docker run --name mysql-source \
-e MYSQL_ROOT_PASSWORD=root \
-e MYSQL_DATABASE=sourcedb \
-p 3307:3306 \
-d mysql:8
```

Access MySQL container:

```bash
docker exec -it mysql-source mysql -uroot -proot
```

Create sample dataset:

```sql
USE sourcedb;

CREATE TABLE products (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100),
    price FLOAT
);

INSERT INTO products (name, price) VALUES
("Laptop",1200),
("Mouse",25),
("Keyboard",70);
```

---

# Metadata Table

Create the registry table:

```sql
CREATE TABLE source_registry (
    source_id TEXT,
    source_type TEXT,
    connection_info TEXT,
    source_object TEXT,
    target_table TEXT,
    enabled BOOLEAN
);
```

---

# Example Metadata Records

### CSV Source

```sql
INSERT INTO source_registry VALUES
(
'products_csv',
'csv',
'data/products.csv',
NULL,
'products_raw',
true
);
```

---

### MySQL Source

```sql
INSERT INTO source_registry VALUES
(
'mysql_products',
'mysql',
'mysql+pymysql://root:root@localhost:3307/sourcedb',
'products',
'products_mysql_raw',
true
);
```

---

### MongoDB Source

```sql
INSERT INTO source_registry VALUES
(
'mongo_products',
'mongodb',
'mongodb://localhost:27017',
'products',
'mongo_products_raw',
true
);
```

---

# Running the Ingestion Agent

Execute the ingestion pipeline:

```bash
python ingestion_agent.py
```

The agent will:

* Read the metadata registry
* Detect source connectors
* Extract data from each source
* Automatically create target tables
* Load the data into PostgreSQL

---

# Example Output

```
Processing csv -> products_raw
Processing mysql -> products_mysql_raw
Processing mongodb -> mongo_products_raw

Data ingestion completed.
```

---

# Key Idea

This project demonstrates a **metadata-driven ingestion architecture**, where data pipelines are dynamically generated using metadata instead of hard-coded scripts.

This approach is widely used in modern **data engineering platforms** to scale ingestion across many data sources.

---

# Possible Improvements

Future improvements could include:

* Connector plugin architecture
* Incremental loading
* Schema evolution handling
* Parallel ingestion
* Workflow orchestration (Airflow or Prefect)
* Integration with Snowflake or cloud warehouses
* Data validation and monitoring
* Containerized pipeline deployment
