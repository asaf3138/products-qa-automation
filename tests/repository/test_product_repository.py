import pytest
import uuid

from models.models import Product
from repositories import product_repository

from repositories import product_repository
from repositories.product_repository import ProductRepositoryError


def test_create_product_success(test_db):
    """
    Test successful product creation in the Repository.

    Verify:
    1. A valid product is inserted into MySQL.
    2. A numeric product ID is returned.
    3. The Product object receives the generated ID.
    4. The saved product contains the correct data.
    """

    # -------------------------
    # ARRANGE - Prepare test data
    # -------------------------

    # Generate a unique name to avoid duplicate-name errors
    unique_name = f"QA-{uuid.uuid4().hex[:12]}"

    # Create a valid Product object
    product = Product(
        product_id=0,
        name=unique_name,
        price=150.0,
        image="keyboard.png"
    )

    # Store the ID for cleanup
    product_id = None

    try:
        # -------------------------
        # ACT - Execute the function
        # -------------------------

        # Call the real Repository function
        product_id = product_repository.create_product(product)

        # -------------------------
        # ASSERT - Verify the results
        # -------------------------

        # Verify the returned ID is an integer
        assert isinstance(product_id, int)

        # Verify the generated ID is positive
        assert product_id > 0

        # Verify the ID was assigned to the Product object
        assert product.product_id == product_id

        # Retrieve the product from the test database
        saved_product = product_repository.read_one(product_id)

        # Verify the product exists
        assert saved_product is not None

        # Verify all saved fields
        assert saved_product.product_id == product_id
        assert saved_product.name == unique_name
        assert saved_product.price == 150.0
        assert saved_product.image == "keyboard.png"

    finally:
        # -------------------------
        # CLEANUP - Remove test data
        # -------------------------

        # Delete only the product created by this test
        if product_id is not None:
            product_repository.delete_product(product_id)





# -------------------------------------------------
# TEST 2 - Duplicate product name
# -------------------------------------------------
def test_create_product_duplicate_name(test_db):
    # ARRANGE - Create a product with a unique name
    unique_name = f"QA-{uuid.uuid4().hex[:12]}"

    first_product = Product(
        product_id=0,
        name=unique_name,
        price=100.0,
        image="first.png"
    )

    duplicate_product = Product(
        product_id=0,
        name=unique_name,
        price=200.0,
        image="second.png"
    )

    first_product_id = None

    try:
        # Save the first product successfully
        first_product_id = product_repository.create_product(
            first_product
        )

        # ACT + ASSERT - A duplicate name must raise an error
        with pytest.raises(ProductRepositoryError):
            product_repository.create_product(
                duplicate_product
            )

        # Verify the original product was not changed
        saved_product = product_repository.read_one(
            first_product_id
        )

        assert saved_product is not None
        assert saved_product.name == unique_name
        assert saved_product.price == 100.0

    finally:
        # CLEANUP - Delete the original test product
        if first_product_id is not None:
            product_repository.delete_product(first_product_id)


# -------------------------------------------------
# TEST 3 - Missing product name
# -------------------------------------------------
def test_create_product_null_name(test_db):
    # ARRANGE - Create a product without a name
    product = Product(
        product_id=0,
        name=None,
        price=100.0,
        image="test.png"
    )

    # ACT + ASSERT - The Repository must reject NULL names
    with pytest.raises(ProductRepositoryError):
        product_repository.create_product(product)




# -------------------------------------------------
# TEST 4 - Product name longer than 50 characters
# -------------------------------------------------
def test_create_product_name_too_long(test_db):
    # ARRANGE - Create a product with 51 characters
    long_name = "A" * 51

    product = Product(
        product_id=0,
        name=long_name,
        price=100.0,
        image="test.png"
    )

    # ACT + ASSERT - The Repository must reject long names
    with pytest.raises(ProductRepositoryError):
        product_repository.create_product(product)




# -------------------------------------------------
# TEST 5 - Read an existing product
# -------------------------------------------------
def test_read_one_existing_product(test_db):
    # ARRANGE - Prepare a unique test product
    unique_name = f"QA-{uuid.uuid4().hex[:12]}"

    product = Product(
        product_id=0,
        name=unique_name,
        price=250.0,
        image="mouse.png"
    )

    product_id = None

    try:
        # Save the product in the test database
        product_id = product_repository.create_product(product)

        # ACT - Retrieve the product by its ID
        result = product_repository.read_one(product_id)

        # ASSERT - Verify the returned product
        assert result is not None
        assert isinstance(result, Product)

        assert result.product_id == product_id
        assert result.name == unique_name
        assert result.price == 250.0
        assert result.image == "mouse.png"

    finally:
        # CLEANUP - Remove the test product
        if product_id is not None:
            product_repository.delete_product(product_id)





# -------------------------------------------------
# TEST 6 - Read a product that does not exist
# -------------------------------------------------
def test_read_one_non_existing_product(test_db):
    # ARRANGE - Find an ID that does not exist
    # in the test database
    import pymysql
    from config.app_config import db_connection_kwargs

    test_config = db_connection_kwargs.copy()
    test_config["database"] = "db1_test"

    with pymysql.connect(**test_config) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT COALESCE(MAX(product_id), 0) + 1 FROM products"
            )
            missing_product_id = cursor.fetchone()[0]

    # ACT - Try to retrieve a non-existing product
    result = product_repository.read_one(missing_product_id)

    # ASSERT - The Repository should return None
    assert result is None




# -------------------------------------------------
# TEST 7 - Read all products
# -------------------------------------------------
def test_read_all_products(test_db):
    # ARRANGE - Create a unique test product
    unique_name = f"QA-{uuid.uuid4().hex[:12]}"

    product = Product(
        product_id=0,
        name=unique_name,
        price=350.0,
        image="monitor.png"
    )

    product_id = None

    try:
        # Save the product in the test database
        product_id = product_repository.create_product(product)

        # ACT - Retrieve all products
        products = product_repository.read_all()

        # ASSERT - Verify the result is a list
        assert isinstance(products, list)

        # Verify all returned items are Product objects
        assert all(isinstance(p, Product) for p in products)

        # Find the product created by this test
        matching_products = [
            p for p in products
            if p.product_id == product_id
        ]

        # Verify our product appears exactly once
        assert len(matching_products) == 1

        # Verify its data
        saved_product = matching_products[0]

        assert saved_product.name == unique_name
        assert saved_product.price == 350.0
        assert saved_product.image == "monitor.png"

    finally:
        # CLEANUP - Delete the test product
        if product_id is not None:
            product_repository.delete_product(product_id)




# -------------------------------------------------
# TEST 8 - Update an existing product
# -------------------------------------------------
def test_update_existing_product(test_db):
    # ARRANGE - Create a product
    unique_name = f"QA-{uuid.uuid4().hex[:12]}"

    product = Product(
        product_id=0,
        name=unique_name,
        price=100.0,
        image="old.png"
    )

    product_id = None

    try:
        # Save the original product
        product_id = product_repository.create_product(product)

        # Prepare updated values
        product.name = f"Updated-{uuid.uuid4().hex[:8]}"
        product.price = 250.0
        product.image = "new.png"

        # ACT - Update the product
        result = product_repository.update_product(product)

        # ASSERT - Verify update was successful
        assert result is True

        # Read the product again from MySQL
        updated_product = product_repository.read_one(product_id)

        assert updated_product is not None
        assert updated_product.product_id == product_id
        assert updated_product.name == product.name
        assert updated_product.price == 250.0
        assert updated_product.image == "new.png"

    finally:
        # CLEANUP - Delete the test product
        if product_id is not None:
            product_repository.delete_product(product_id)




# -------------------------------------------------
# TEST 9 - Update a product that does not exist
# -------------------------------------------------
def test_update_non_existing_product(test_db):
    # ARRANGE - Find an ID that does not exist
    import pymysql
    from config.app_config import db_connection_kwargs

    test_config = db_connection_kwargs.copy()
    test_config["database"] = "db1_test"

    with pymysql.connect(**test_config) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT COALESCE(MAX(product_id), 0) + 1 FROM products"
            )
            missing_product_id = cursor.fetchone()[0]

    # Create a Product object with the missing ID
    product = Product(
        product_id=missing_product_id,
        name=f"QA-{uuid.uuid4().hex[:12]}",
        price=500.0,
        image="missing.png"
    )

    # ACT - Try to update the missing product
    result = product_repository.update_product(product)

    # ASSERT - The update must return False
    assert result is False

    # Verify the update did not create a new product
    saved_product = product_repository.read_one(
        missing_product_id
    )

    assert saved_product is None




# -------------------------------------------------
# TEST 10 - Delete an existing product
# -------------------------------------------------
def test_delete_existing_product(test_db):
    # ARRANGE - Create a product for deletion
    unique_name = f"QA-{uuid.uuid4().hex[:12]}"

    product = Product(
        product_id=0,
        name=unique_name,
        price=400.0,
        image="delete.png"
    )

    product_id = None

    try:
        # Save the product in the test database
        product_id = product_repository.create_product(product)

        # Verify the product exists before deletion
        saved_product = product_repository.read_one(product_id)
        assert saved_product is not None

        # ACT - Delete the product
        result = product_repository.delete_product(product_id)

        # ASSERT - Verify successful deletion
        assert result is True

        # Verify the product no longer exists
        deleted_product = product_repository.read_one(product_id)
        assert deleted_product is None

    finally:
        # CLEANUP - Ensure the product is removed
        if product_id is not None:
            product_repository.delete_product(product_id)





# -------------------------------------------------
# TEST 11 - Delete a product that does not exist
# -------------------------------------------------
def test_delete_non_existing_product(test_db):
    # ARRANGE - Find an ID that does not exist
    import pymysql
    from config.app_config import db_connection_kwargs

    test_config = db_connection_kwargs.copy()
    test_config["database"] = "db1_test"

    with pymysql.connect(**test_config) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT COALESCE(MAX(product_id), 0) + 1 FROM products"
            )
            missing_product_id = cursor.fetchone()[0]

    # ACT - Try to delete a non-existing product
    result = product_repository.delete_product(
        missing_product_id
    )

    # ASSERT - No product was deleted
    assert result is False

    # Verify the product still does not exist
    saved_product = product_repository.read_one(
        missing_product_id
    )

    assert saved_product is None
