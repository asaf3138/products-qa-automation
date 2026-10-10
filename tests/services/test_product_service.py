import pytest
from unittest.mock import patch

from models.models import Product
from services import product_service

from services.product_service import (
    ProductServiceError,
    ProductNotFoundServiceError
)

from repositories.product_repository import ProductRepositoryError


# -------------------------------------------------
# TEST 1 - Add a valid product using Mock
# -------------------------------------------------

def test_add_product_success():
    # ARRANGE - Create a valid product
    product = Product(
        product_id=0,
        name="Keyboard",
        price=150.0,
        image="keyboard.png"
    )

    # Replace the Repository function with a Mock
    with patch(
        "services.product_service.product_repository.create_product"
    ) as mock_create:

        # Configure the Mock to return product ID 10
        mock_create.return_value = 10

        # ACT - Call the real Service function
        result = product_service.add_product(product)

        # ASSERT - Verify the returned product ID
        assert result == 10

        # Verify the Repository was called exactly once
        # with the correct Product object
        mock_create.assert_called_once_with(product)



# -------------------------------------------------
# TEST 2 - Add product with negative price
# -------------------------------------------------

def test_add_product_negative_price():
    # ARRANGE - Create a product with invalid price
    product = Product(
        product_id=0,
        name="Keyboard",
        price=-50.0,
        image="keyboard.png"
    )

    # Replace the real Repository with a Mock
    with patch(
        "services.product_service.product_repository.create_product"
    ) as mock_create:

        # ACT + ASSERT - Expect a Service error
        with pytest.raises(ProductServiceError):
            product_service.add_product(product)

        # ASSERT - Repository must not be called
        mock_create.assert_not_called()



# -------------------------------------------------
# TEST 3 - Add product with zero price
# -------------------------------------------------

def test_add_product_zero_price():
    # ARRANGE - Create a product with price = 0
    product = Product(
        product_id=0,
        name="Free Product",
        price=0.0,
        image="free.png"
    )

    # Replace the Repository function with a Mock
    with patch(
        "services.product_service.product_repository.create_product"
    ) as mock_create:

        # Simulate a successful product creation
        mock_create.return_value = 20

        # ACT - Call the real Service function
        result = product_service.add_product(product)

        # ASSERT - Verify zero price is accepted
        assert result == 20

        # Verify the Repository was called correctly
        mock_create.assert_called_once_with(product)



# -------------------------------------------------
# TEST 4 - Add product with missing price
# -------------------------------------------------

def test_add_product_null_price():
    # ARRANGE - Create a product without a price
    product = Product(
        product_id=0,
        name="Keyboard",
        price=None,
        image="keyboard.png"
    )

    # Replace the Repository with a Mock
    with patch(
        "services.product_service.product_repository.create_product"
    ) as mock_create:

        # ACT + ASSERT - Expect a Service error
        with pytest.raises(ProductServiceError):
            product_service.add_product(product)

        # ASSERT - Repository must not be called
        mock_create.assert_not_called()



# -------------------------------------------------
# TEST 5 - Add product with a one-character name
# -------------------------------------------------

def test_add_product_name_too_short():
    # ARRANGE - Create a product with an invalid name
    product = Product(
        product_id=0,
        name="A",
        price=100.0,
        image="product.png"
    )

    # Replace the Repository function with a Mock
    with patch(
        "services.product_service.product_repository.create_product"
    ) as mock_create:

        # ACT + ASSERT - Expect a validation error
        with pytest.raises(ProductServiceError):
            product_service.add_product(product)

        # ASSERT - Repository must not be called
        mock_create.assert_not_called()


# -------------------------------------------------
# TEST 6 - Add product with an empty name
# -------------------------------------------------

def test_add_product_empty_name():

    # ARRANGE - Create a product with an empty name
    product = Product(
        product_id=0,
        name="",
        price=100.0,
        image="product.png"
    )

    # Replace the Repository function with a Mock
    with patch(
        "services.product_service.product_repository.create_product"
    ) as mock_create:

        # ACT + ASSERT - Expect a validation error
        with pytest.raises(ProductServiceError):
            product_service.add_product(product)

        # ASSERT - Repository must not be called
        mock_create.assert_not_called()



# -------------------------------------------------
# TEST 7 - Add product with minimum valid name
# -------------------------------------------------

def test_add_product_minimum_valid_name():

    # ARRANGE - Create a product with a 2-character name
    product = Product(
        product_id=0,
        name="AB",
        price=100.0,
        image="product.png"
    )

    # Replace the Repository function with a Mock
    with patch(
        "services.product_service.product_repository.create_product"
    ) as mock_create:

        # Simulate successful product creation
        mock_create.return_value = 30

        # ACT - Call the real Service function
        result = product_service.add_product(product)

        # ASSERT - Verify the returned product ID
        assert result == 30

        # Verify the Repository was called correctly
        mock_create.assert_called_once_with(product)



# -------------------------------------------------
# TEST 8 - Repository error during product creation
# -------------------------------------------------

def test_add_product_repository_error():

    # ARRANGE - Create a valid product
    product = Product(
        product_id=0,
        name="Keyboard",
        price=100.0,
        image="keyboard.png"
    )

    # Replace the Repository function with a Mock
    with patch(
        "services.product_service.product_repository.create_product"
    ) as mock_create:

        # Simulate a Repository error
        mock_create.side_effect = ProductRepositoryError(
            "Product name exists: Keyboard"
        )

        # ACT + ASSERT - Expect a Service error
        with pytest.raises(
            ProductServiceError,
            match="Product name exists: Keyboard"
        ):
            product_service.add_product(product)

        # ASSERT - Verify Repository was called once
        mock_create.assert_called_once_with(product)



# -------------------------------------------------
# TEST 9 - Get an existing product
# -------------------------------------------------

def test_get_product_success():

    # ARRANGE - Create an expected product
    expected_product = Product(
        product_id=10,
        name="Keyboard",
        price=150.0,
        image="keyboard.png"
    )

    # Replace the Repository function with a Mock
    with patch(
        "services.product_service.product_repository.read_one"
    ) as mock_read:

        # Simulate a product returned by the Repository
        mock_read.return_value = expected_product

        # ACT - Call the real Service function
        result = product_service.get_product(10)

        # ASSERT - Verify the returned product
        assert result == expected_product

        # ASSERT - Verify Repository was called correctly
        mock_read.assert_called_once_with(10)



# -------------------------------------------------
# TEST 10 - Get a product that does not exist
# -------------------------------------------------

def test_get_product_not_found():

    # ARRANGE - Product ID that does not exist
    product_id = 999

    # Replace the Repository function with a Mock
    with patch(
        "services.product_service.product_repository.read_one"
    ) as mock_read:

        # Simulate a product that was not found
        mock_read.return_value = None

        # ACT + ASSERT - Expect a not-found error
        with pytest.raises(
            ProductNotFoundServiceError,
            match="Product not found: 999"
        ):
            product_service.get_product(product_id)

        # ASSERT - Verify Repository was called correctly
        mock_read.assert_called_once_with(product_id)



# -------------------------------------------------
# TEST 11 - Get all products successfully
# -------------------------------------------------

def test_get_all_products_success():

    # ARRANGE - Create two expected products
    product1 = Product(
        product_id=1,
        name="Keyboard",
        price=150.0,
        image="keyboard.png"
    )

    product2 = Product(
        product_id=2,
        name="Mouse",
        price=80.0,
        image="mouse.png"
    )

    expected_products = [product1, product2]

    # Replace the Repository function with a Mock
    with patch(
        "services.product_service.product_repository.read_all"
    ) as mock_read_all:

        # Simulate Repository returning a list
        mock_read_all.return_value = expected_products

        # ACT - Call the real Service function
        result = product_service.get_all_products()

        # ASSERT - Verify the returned list
        assert result == expected_products

        # ASSERT - Verify Repository was called once
        mock_read_all.assert_called_once_with()



# -------------------------------------------------
# TEST 12 - Get all products when list is empty
# -------------------------------------------------

def test_get_all_products_empty():

    # ARRANGE - Replace Repository with a Mock
    with patch(
        "services.product_service.product_repository.read_all"
    ) as mock_read_all:

        # Simulate an empty database
        mock_read_all.return_value = []

        # ACT - Call the real Service function
        result = product_service.get_all_products()

        # ASSERT - Verify an empty list is returned
        assert result == []

        # ASSERT - Verify Repository was called once
        mock_read_all.assert_called_once_with()



# -------------------------------------------------
# TEST 13 - Update an existing product successfully
# -------------------------------------------------

def test_update_product_success():

    # ARRANGE - Create a product with updated details
    product = Product(
        product_id=10,
        name="Gaming Keyboard",
        price=250.0,
        image="gaming_keyboard.png"
    )

    # Replace the Repository function with a Mock
    with patch(
        "services.product_service.product_repository.update_product"
    ) as mock_update:

        # Simulate successful update in Repository
        mock_update.return_value = True

        # ACT - Call the real Service function
        result = product_service.update_product(product)

        # ASSERT - Service should return None
        assert result is None

        # ASSERT - Repository called exactly once
        mock_update.assert_called_once_with(product)



# -------------------------------------------------
# TEST 14 - Update a product that does not exist
# -------------------------------------------------

def test_update_product_not_found():

    # ARRANGE - Create a product with a non-existing ID
    product = Product(
        product_id=999,
        name="Gaming Keyboard",
        price=250.0,
        image="gaming_keyboard.png"
    )

    # Replace the Repository function with a Mock
    with patch(
        "services.product_service.product_repository.update_product"
    ) as mock_update:

        # Simulate a product that was not found
        mock_update.return_value = False

        # ACT + ASSERT - Expect a not-found error
        with pytest.raises(
            ProductNotFoundServiceError,
            match="Product not found: 999"
        ):
            product_service.update_product(product)

        # ASSERT - Verify Repository was called correctly
        mock_update.assert_called_once_with(product)



# -------------------------------------------------
# TEST 15 - Update product with negative price
# -------------------------------------------------

def test_update_product_negative_price():

    # ARRANGE - Create a product with an invalid price
    product = Product(
        product_id=10,
        name="Gaming Keyboard",
        price=-50.0,
        image="gaming_keyboard.png"
    )

    # Replace the Repository function with a Mock
    with patch(
        "services.product_service.product_repository.update_product"
    ) as mock_update:

        # ACT + ASSERT - Expect a validation error
        with pytest.raises(ProductServiceError):
            product_service.update_product(product)

        # ASSERT - Repository must not be called
        mock_update.assert_not_called()



# -------------------------------------------------
# TEST 16 - Update product with a short name
# -------------------------------------------------

def test_update_product_name_too_short():

    # ARRANGE - Create a product with an invalid name
    product = Product(
        product_id=10,
        name="A",
        price=150.0,
        image="product.png"
    )

    # Replace the Repository function with a Mock
    with patch(
        "services.product_service.product_repository.update_product"
    ) as mock_update:

        # ACT + ASSERT - Expect a validation error
        with pytest.raises(ProductServiceError):
            product_service.update_product(product)

        # ASSERT - Repository must not be called
        mock_update.assert_not_called()



# -------------------------------------------------
# TEST 17 - Repository error during product update
# -------------------------------------------------

def test_update_product_repository_error():

    # ARRANGE - Create a valid product
    product = Product(
        product_id=10,
        name="Gaming Keyboard",
        price=250.0,
        image="gaming_keyboard.png"
    )

    # Replace the Repository function with a Mock
    with patch(
        "services.product_service.product_repository.update_product"
    ) as mock_update:

        # Simulate a Repository error
        mock_update.side_effect = ProductRepositoryError(
            "Product name exists: Gaming Keyboard"
        )

        # ACT + ASSERT - Expect a Service error
        with pytest.raises(
            ProductServiceError,
            match="Product name exists: Gaming Keyboard"
        ):
            product_service.update_product(product)

        # ASSERT - Verify Repository was called once
        mock_update.assert_called_once_with(product)





# -------------------------------------------------
# TEST 18 - Delete an existing product successfully
# -------------------------------------------------

def test_delete_product_success():

    # ARRANGE - Product ID to delete
    product_id = 10

    # Replace the Repository function with a Mock
    with patch(
        "services.product_service.product_repository.delete_product"
    ) as mock_delete:

        # Simulate successful deletion
        mock_delete.return_value = True

        # ACT - Call the real Service function
        result = product_service.delete_product(product_id)

        # ASSERT - Service should return None
        assert result is None

        # ASSERT - Repository called exactly once
        mock_delete.assert_called_once_with(product_id)



# -------------------------------------------------
# TEST 19 - Delete a product that does not exist
# -------------------------------------------------

def test_delete_product_not_found():

    # ARRANGE - Product ID that does not exist
    product_id = 999

    # Replace Repository function with a Mock
    with patch(
        "services.product_service.product_repository.delete_product"
    ) as mock_delete:

        # Simulate product not found
        mock_delete.return_value = False

        # ACT + ASSERT - Expect a not-found error
        with pytest.raises(
            ProductNotFoundServiceError,
            match="Product not found: 999"
        ):
            product_service.delete_product(product_id)

        # ASSERT - Verify Repository was called once
        mock_delete.assert_called_once_with(product_id)
