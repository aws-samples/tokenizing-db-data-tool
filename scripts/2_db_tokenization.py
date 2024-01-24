#!/usr/local/bin/python

import os
import sys
import json
import pandas as pd
from util import *
import mysql.connector
from argparse import ArgumentParser
from ff3 import FF3Cipher
from passlib.utils.pbkdf2 import pbkdf2
from datetime import date

parser = ArgumentParser()
parser.add_argument("-c", "--config", dest="config",
                    help="table tokenize config")
config = json.loads(parser.parse_args().config)
print(config)

rds = rds()
stage = os.environ['STAGE']
tmp_db_name = os.environ['TMP_DBID']
db_user = os.environ['DB_USER']
db_pass = os.environ['DB_PASS']
secret = sm_get('tokenize_key')['SecretString']
secret = json.loads(secret)

salt = secret['salt']
password= secret['password']
tweak = secret['tweak']
key = pbkdf2(password, salt, 1024, keylen=32, prf='hmac-sha512').hex()

@timeit
def main():
    check_stage(stage, os.path.basename(__file__))
    table_update(config)

def get_conn_mysql():
    tmp_db = find_db(rds, tmp_db_name)
    endpoint = tmp_db['Endpoint']['Address']
    conn = mysql.connector.connect(
        user=db_user,
        password=db_pass,
        host=endpoint,
        database='employees'
    )
    return conn

def fpe_str_tokenize(plaintext):
    prefix_len = 7 - len(plaintext)
    if prefix_len > 0:
        plaintext = "A"*prefix_len + plaintext
    chars="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    c = FF3Cipher.withCustomAlphabet(key, tweak, chars)
    r = c.encrypt(plaintext)
    return r

def fpe_int_tokenize(plaintext):
    plaintext = str(plaintext)
    prefix_len = 7 - len(plaintext)
    if prefix_len > 0:
        plaintext = "0"*prefix_len + plaintext
    chars="0123456789"
    c = FF3Cipher.withCustomAlphabet(key, tweak, chars)
    r = c.encrypt(plaintext)
    r = int(r)
    return r

def date_tokenize(plaintext):
    print(plaintext)
    d = plaintext.replace(day=1)
    d = str(d)
    return d

def table_update(config):
    table = config['table']
    table_after = f"{table}_after"
    schema = config['tokenize_fields']

    #create a new table for storing tokenized data
    c1 = get_conn_mysql()
    cur1 = c1.cursor()
    create_q = f"DROP TABLE IF EXISTS {table_after}; CREATE TABLE {table_after} LIKE {table};"
    cur1.execute(create_q)
    c1.close()

    conn = get_conn_mysql()
    q = f"SELECT * FROM  {table};"
    df = pd.read_sql(q, con=conn)
    print(df)

    for column_type,columns in schema.items():
        if column_type == 'int':
            for column in columns:
                df[column] = df[column].map(fpe_int_tokenize)
        elif column_type == 'string':
            for column in columns:
                df[column] = df[column].map(fpe_str_tokenize)
        elif column_type == 'date':
            for column in columns:
                df[column] = df[column].map(date_tokenize)
    print(df)

    cols = ','.join(list(df.columns))
    value = ''
    for i in range(len(df.columns)-1):
        value += '%%s,'
    value += '%%s'
    query = f"INSERT INTO %s(%s) VALUES ({value})"
    query = query % (table_after, cols)
    cursor = conn.cursor()

    tuples = [tuple(x) for x in df.to_numpy()]
    chunks = [tuples[x:x+500] for x in range(0, len(tuples), 500)]
    for chunk in chunks:
        cursor.executemany(query, chunk)
        conn.commit()

    #drop old table, rename new table
    cursor.execute(f"SET FOREIGN_KEY_CHECKS = 0; DROP TABLE IF EXISTS {table}; ALTER TABLE {table_after} RENAME TO {table};")
    conn.close()

main()
