import sys

import pymysql as sql
from config.app_config import db_connection_kwargs


# get database connection kwargs
host, user, password, database = db_connection_kwargs.values()

def create_db():
    with sql.connect(host=host, user=user, password=password) as con:
        try:
            con.autocommit = True
            cursor = con.cursor()
            cursor.execute(f'create database `{database}`')
            print(f'Database `{database}` created')
        except Exception as e:
            print('INFO: ', e, file=sys.stderr)



def create_table():
    with sql.connect(host=host, user=user, password=password, db=database) as con:
        try:
            con.autocommit = True
            cursor = con.cursor()
            cursor.execute('''
                create table `products`(
                `product_id` int primary key auto_increment,
                `name` varchar(50) unique not null,
                `price` float not null,
                `image` varchar(255)
            );''')
            print(f'Table `products` created')
        except Exception as e:
            print('INFO: ', e, file=sys.stderr)



def drop_database() -> int:
    with sql.connect(**db_connection_kwargs) as con:
        con.autocommit = True
        cursor = con.cursor()
        cursor.execute(f'drop database `{database}`')
        return cursor.rowcount

def truncate_products_table():
    with sql.connect(**db_connection_kwargs) as con:
        con.autocommit = True
        cursor = con.cursor()
        cursor.execute(f'truncate products')


if __name__ == '__main__':
    # create_database()
    # drop_database()
    create_db()
    create_table()