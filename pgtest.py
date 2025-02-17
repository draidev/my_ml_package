import psycopg2

import os
import numpy as np
import pandas as pd

host = "1.1.1.1"
port = "5433"
user = ""
name = ""
password = ""
db_name = "pe_dataset"

db = psycopg2.connect(host=host, dbname=name, user=user, password=password, port=port)


"""
    case2) sqlalchemy
"""
import sqlalchemy
from sqlalchemy import create_engine

engine = create_engine("postgresql://lockard_ai:secudaim00!@192.168.100.206:5433/lockard_ai_test")

engine.execute("DROP TABLE IF EXISTS public.pe_dataset;") # drop table if exists

temp_df.to_sql(name='pe_dataset', con=engine, schema='public', if_exists='fail', index=True, \
                 index_label='id', chunksize=2, dtype={ \
                     'id':sqlalchemy.types.INTEGER(),\
                         'Machine':sqlalchemy.types.INTEGER(),\
                             'SizeOfOptionalHeader':sqlalchemy.types.INTEGER()\
                             })
