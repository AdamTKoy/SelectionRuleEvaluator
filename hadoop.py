import pyodbc
import pandas as pd
import os
from datetime import date

TRACK_FILE = "last_run.txt"

def refreshData():
    today = str(date.today())

    filesToRefresh = [('SQL/active_mmac.sql', 'Data/active_mmac.csv'), 
                    ('SQL/feature_synonyms.sql', 'Data/ftr_syn_table.csv'),
                    ('SQL/model_synonyms.sql', 'Data/mdl_syn_table.csv')]

    conn = pyodbc.connect("DSN=PPS IMPALA", autocommit=True)

    for filepath, filename in filesToRefresh:

        with open(filepath, 'r') as file:
            sql_query = file.read()

        df = pd.read_sql(sql_query, conn)
        df.to_csv(filename, index=False)

    # log date of last run
    if os.path.exists(TRACK_FILE):
        with open(TRACK_FILE, 'w') as f:
            f.write(today)
    else:
        print('last_run.txt not found!')

# TO INSTALL:
# pip install sqlalchemy
# pip install impyla

# PROGRAM:
#from sqlalchemy import create_engine

# Default Impala port is 21050
#engine = create_engine('impala://haddde-impala.navistar.com:21050/your_database')
#connection = engine.connect()

# Execute a query
#result = connection.execute("SELECT * FROM your_table LIMIT 10")
#for row in result:
#    print(row)

# OR: if authentication is required (?)
#engine = create_engine(
#    'impala://hostname:21050',
#    connect_args={'auth_mechanism': 'GSSAPI', 'kerberos_service_name': 'impala'}
#)
