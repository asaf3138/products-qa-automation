from typing import List
import pymysql as sql
from config.app_config import db_connection_kwargs
from models.models import Product


class ProductRepositoryError(Exception): pass


def create_product(product: Product) -> int:
    """
    Adds a product to the database and returns the id assigned by the database engine. Sets the product parameter id.
    :param product: The product to add. Product name must be up to 50 characters, unique, not null. Product price must not be null
    :returns int: The ID of the newly added product.
    :raises ProductRepositoryError: If the product data is invalid (product name exists or null, price is null)
    """
    with sql.connect(**db_connection_kwargs) as con:
        # con.autocommit = True
        cursor = con.cursor()
        prepared_statement = 'insert into products (name, price, image) values (%s, %s, %s)'
        try:
            cursor.execute(prepared_statement, (product.name, product.price, product.image))
            con.commit()
            product.product_id = cursor.lastrowid
            return cursor.lastrowid
        except sql.DatabaseError as e:
            wrapped_error = _wrap_sql_err(e, product)
            raise wrapped_error from e
        except Exception as e:
            raise ProductRepositoryError("Something went wrong!") from e


def read_one(product_id: int) -> Product | None:
    """
    Returns the product with the given id or None if not found.

    :param product_id: The ID of the product to search for.
    :return: The product instance, or None if not found.
    """
    with sql.connect(**db_connection_kwargs) as con:
        # con.autocommit = True
        cursor = con.cursor()
        prepared_statement = 'select * from products where product_id = %s'
        cursor.execute(prepared_statement, (product_id,))
        result = cursor.fetchone()
        if result:
            product = Product(*result)
            return product
        return None


def read_all() -> List[Product]:
    """
    Fetches all products from the database.

    Connects to the database using the configured connection arguments,
    retrieves all records from the 'products' table, and maps them to
    Product instances.

    :return: A list of all Product instances in the database. Returns an
             empty list if no products are found.
    :raises Exception: Passes through database connection or execution errors.
    """
    with sql.connect(**db_connection_kwargs) as con:
        # con.autocommit = True
        cursor = con.cursor()
        cursor.execute('select * from products')
        result = cursor.fetchall()
        products: List[Product] = []
        for row in result:
            product = Product(*row)
            products.append(product)
        return products


def update_product(product: Product) -> bool:
    """
    Updates an existing product in the database.

    :param product: The Product instance containing updated field values.
    :return: True if the product was updated successfully, False if no product matched the given product_id.
    :raises ProductRepositoryError: If the product violate constraints (product name exists or null, price is null)
    """
    with sql.connect(**db_connection_kwargs) as con:
        # con.autocommit = True
        cursor = con.cursor()
        prepared_statement = 'update products set name = %s, price = %s, image = %s where product_id = %s'
        try:
            cursor.execute(prepared_statement, (product.name, product.price, product.image, product.product_id))
            con.commit()
            return cursor.rowcount == 1
        except sql.DatabaseError as e:
            wrapped_error = _wrap_sql_err(e, product)
            raise wrapped_error from e
        except Exception as e:
            raise ProductRepositoryError("Something went wrong!") from e


def delete_product(product_id: int) -> bool:
    """
    Deletes the product with the given product_id.
    :param product_id: The product_id of the product to delete.
    :return: bool: True if the product was deleted successfully, False otherwise.
    """
    with sql.connect(**db_connection_kwargs) as con:
        # con.autocommit = True
        cursor = con.cursor()
        prepared_statement = 'delete from products where product_id = %s'
        cursor.execute(prepared_statement, (product_id,))
        con.commit()
        return cursor.rowcount == 1


def _wrap_sql_err(e: sql.DatabaseError, product: Product):
    error_code = e.args[0]
    if error_code == 1048:  # Column cannot be null
        raw_msg = e.args[1]
        formatted_msg = "Product " + raw_msg[8:].replace("'", "")
        return ProductRepositoryError(formatted_msg)
    elif error_code == 1062:  # Duplicate entry
        return ProductRepositoryError(f'Product name exists: {product.name}')
    elif error_code == 1406:  # Data too long
        return ProductRepositoryError(f'Product name too long: {len(product.name)}')
    else:
        return ProductRepositoryError(f'Some other database error: {e}')
