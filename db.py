import os

import psycopg2
from peewee import *
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

postgres_database = os.getenv('POSTGRES_DATABASE', None)
postgres_database_default = 'esocialdocs'
postgres_host = os.getenv('POSTGRES_HOST')
postgres_password = os.getenv('POSTGRES_PASSWORD')
postgres_port = os.getenv('POSTGRES_PORT')
postgres_user = os.getenv('POSTGRES_USER')

if postgres_database is None:
    postgres_database = postgres_database_default
    con = psycopg2.connect(
        host=postgres_host,
        password=postgres_password,
        port=postgres_port,
        user=postgres_user,
    )
    con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = con.cursor()
    cursor.execute(
        "SELECT datname FROM pg_database "
        f"WHERE datname='{postgres_database}';"
    )
    if cursor.fetchone() is None:
        cursor.execute(f"CREATE DATABASE {postgres_database}")
    con.close()

pg_db = PostgresqlDatabase(
    database=postgres_database,
    user=postgres_user, 
    password=postgres_password,
    host=postgres_host,
    port=postgres_port,
)


class Arquivo(Model):
    nome = CharField()
    link = CharField()
    data = DateTimeField()
    arquivo = CharField(unique=True)

    class Meta:
        database = pg_db


class Inscrito(Model):
    id = IntegerField(primary_key=True)
    nome = CharField()
    ativo = BooleanField(default=False)


    class Meta:
        database = pg_db


Arquivo.create_table(safe=True)
Inscrito.create_table(safe=True)