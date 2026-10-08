from typing import List
from repositories import product_repository
from models.models import Product
from repositories.product_repository import ProductRepositoryError


class ProductNotFoundServiceError(Exception): pass


class ProductServiceError(Exception): pass


def add_product(product: Product) -> int:
    """
    Adds a product to the database.
    :param product: The product to add.
    :returns int: The ID of the newly added product.
    :raises ProductServiceError: If the product data is invalid (product name exists or null, price is null) or violates application logic (price is negative or product name is less than 2 characters).
    """
    if product.price is None or product.price < 0:
        raise ProductServiceError("Product price must be positive.")
    if not product.name or len(product.name) < 2:
        raise ProductServiceError("Product name must be at list 2 characters long.")
    try:
        return product_repository.create_product(product)
    except ProductRepositoryError as e:
        raise ProductServiceError(str(e))


def get_product(product_id: int) -> Product:
    """
     Get product by id.
    :param product_id: The product ID.
    :returns: Product: The product with the given ID
    :raises ProductNotFoundError: If product not found.
    """
    product = product_repository.read_one(product_id)
    if product:
        return product
    raise ProductNotFoundServiceError(f"Product not found: {product_id}")


def get_all_products() -> List[Product]:
    """
    Get all products.
    :return: List[Product]: A list of all products.
    """
    return product_repository.read_all()


def update_product(product: Product) -> None:
    """
    Updates the product with the given product_id.
    :param product: The product to update.
    :raises: ProductNotFoundServiceError: if the product not found.
    :raises: ProductServiceError: if the product could not be updated for illegal input.
    """
    if product.price is None or product.price < 0:
        raise ProductServiceError("Product price must be positive.")
    if not product.name or len(product.name) < 2:
        raise ProductServiceError("Product name must be at list 2 characters long.")
    try:
        if not product_repository.update_product(product):
            raise ProductNotFoundServiceError(f"Product not found: {product.product_id}")
    except ProductRepositoryError as e:
        raise ProductServiceError(str(e))


def delete_product(product_id: int) -> None:
    """
    Deletes the product with the given product_id.
    :param product_id: The product_id of the product to delete.
    :raises: ProductNotFoundServiceError: if the product not found.
    """
    if not product_repository.delete_product(product_id):
        raise ProductNotFoundServiceError(f"Product not found: {product_id}")
