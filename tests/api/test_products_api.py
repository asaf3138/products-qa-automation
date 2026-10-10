
from services import product_service
import importlib
import pytest
from unittest.mock import patch
from models.models import Product


# -------------------------------------------------
# API TEST 1 - Get all products successfully
# -------------------------------------------------
@pytest.fixture  #מכין סביבת בדיקה שניתן להשתמש בה בבדיקות
def client():

    # Prevent database initialization during app import  מחליף זמנית פונקציה אמיתית בפונקציה מדומה
    with patch("db.init_db.create_db"), \
         patch("db.init_db.create_table"), \
         patch("time.sleep"):

        flask_app = importlib.import_module("app").app

    # Flask testing configuration
    flask_app.config["TESTING"] = True

    # Create a Flask test client
    with flask_app.test_client() as test_client:  #מאפשר לשלוח בקשות HTTP מדומות לאפליקציית Flask
        yield test_client


def test_get_all_products_success(client):

    # ARRANGE - Prepare products returned by Service
    products = [
        Product(1, "Keyboard", 150.0, "keyboard.png"),
        Product(2, "Mouse", 80.0, "mouse.png")
    ]

    # Replace the real Service function with a Mock
    with patch(
        "app.product_service.get_all_products"
    ) as mock_get_all:

        mock_get_all.return_value = products

        # ACT - Send a GET request to Flask
        response = client.get("/api/products") #שולח בקשת GET לנתיב שנבחר

        # ASSERT - Verify HTTP status code
        assert response.status_code == 200 # מחזיר את קוד ה־HTTP של התגובה

        # ASSERT - Verify JSON response
        assert response.get_json() == [ #מחזיר את גוף תגובת ה־JSON כאובייקט Python
            {
                "product_id": 1,
                "name": "Keyboard",
                "price": 150.0,
                "image": "keyboard.png"
            },
            {
                "product_id": 2,
                "name": "Mouse",
                "price": 80.0,
                "image": "mouse.png"
            }
        ]

        # ASSERT - Verify Service was called once
        mock_get_all.assert_called_once_with() #מוודא שה־Service הופעל בדיוק פעם אחת



# -------------------------------------------------
# API TEST 2 - Get an existing product by ID
# -------------------------------------------------

def test_get_product_by_id_success(client):

    # ARRANGE - Create a product returned by Service
    product = Product(
        product_id=10,
        name="Gaming Keyboard",
        price=250.0,
        image="keyboard.png"
    )

    # Replace the real Service function with a Mock
    with patch(
        "app.product_service.get_product"
    ) as mock_get_product:

        # Simulate an existing product
        mock_get_product.return_value = product

        # ACT - Send a GET request to Flask
        response = client.get("/api/products/10")

        # ASSERT - Verify HTTP status code
        assert response.status_code == 200

        # ASSERT - Verify JSON response
        assert response.get_json() == {
            "product_id": 10,
            "name": "Gaming Keyboard",
            "price": 250.0,
            "image": "keyboard.png"
        }

        # ASSERT - Verify Service was called correctly
        mock_get_product.assert_called_once_with(10)



# -------------------------------------------------
# API TEST 3 - Get a product that does not exist
# -------------------------------------------------

def test_get_product_by_id_not_found(client):

    # ARRANGE - Product ID that does not exist
    product_id = 999

    # Replace the real Service function with a Mock
    with patch(
        "app.product_service.get_product"
    ) as mock_get_product:

        # Simulate a Service error
        mock_get_product.side_effect = (
            product_service.ProductNotFoundServiceError(
                "Product not found: 999"
            )
        )

        # ACT - Send a GET request to Flask
        response = client.get(f"/api/products/{product_id}")

        # ASSERT - Verify HTTP status code
        assert response.status_code == 404

        # ASSERT - Verify JSON error response
        assert response.get_json() == {
            "error": "Product not found: 999"
        }

        # ASSERT - Verify Service was called once
        mock_get_product.assert_called_once_with(product_id)



# -------------------------------------------------
# API TEST 4 - Create a product successfully
# -------------------------------------------------

def test_create_product_success(client):

    # ARRANGE - Prepare JSON request data
    product_data = {
        "name": "Gaming Mouse",
        "price": 199.90,
        "image": "mouse.png"
    }

    # Replace the real Service function with a Mock
    with patch(
        "app.product_service.add_product"
    ) as mock_add_product:

        # Simulate a successful product creation
        mock_add_product.return_value = 15

        # ACT - Send a POST request with JSON data
        response = client.post(
            "/api/products",
            json=product_data
        )

        # ASSERT - Verify HTTP status code
        assert response.status_code == 201

        # ASSERT - Verify JSON response
        assert response.get_json() == {
            "message": "Product added",
            "id": 15
        }

        # ASSERT - Verify Service was called once
        mock_add_product.assert_called_once()

        # ASSERT - Verify the Product sent to Service
        created_product = mock_add_product.call_args.args[0]

        assert isinstance(created_product, Product)
        assert created_product.product_id == 0
        assert created_product.name == "Gaming Mouse"
        assert created_product.price == 199.90
        assert created_product.image == "mouse.png"



# -------------------------------------------------
# API TEST 5 - Create product with invalid price
# -------------------------------------------------

def test_create_product_invalid_price(client):

    # ARRANGE - Prepare invalid JSON data
    product_data = {
        "name": "Gaming Mouse",
        "price": "abc",
        "image": "mouse.png"
    }

    # Replace the real Service function with a Mock
    with patch(
        "app.product_service.add_product"
    ) as mock_add_product:

        # ACT - Send POST request with invalid data
        response = client.post(
            "/api/products",
            json=product_data
        )

        # ASSERT - Verify HTTP status code
        assert response.status_code == 400

        # ASSERT - Verify JSON error response
        assert "error" in response.get_json()

        # ASSERT - Verify Service was not called
        mock_add_product.assert_not_called()



# -------------------------------------------------
# API TEST 6 - Create product with negative price
# -------------------------------------------------

def test_create_product_negative_price(client):

    # ARRANGE - Prepare JSON with negative price
    product_data = {
        "name": "Gaming Mouse",
        "price": -50.0,
        "image": "mouse.png"
    }

    # Replace the real Service function with a Mock
    with patch(
        "app.product_service.add_product"
    ) as mock_add_product:

        # Simulate business validation error
        mock_add_product.side_effect = (
            product_service.ProductServiceError(
                "Product price must be positive."
            )
        )

        # ACT - Send POST request to Flask
        response = client.post(
            "/api/products",
            json=product_data
        )

        # ASSERT - Verify HTTP status code
        assert response.status_code == 400

        # ASSERT - Verify JSON error response
        assert response.get_json() == {
            "error": "Product price must be positive."
        }

        # ASSERT - Verify Service was called once
        mock_add_product.assert_called_once()

        # ASSERT - Verify negative price reached Service
        created_product = mock_add_product.call_args.args[0]

        assert isinstance(created_product, Product)
        assert created_product.price == -50.0



# -------------------------------------------------
# API TEST 7 - Update an existing product successfully
# -------------------------------------------------

def test_update_product_success(client):

    # ARRANGE - Prepare updated product data
    product_data = {
        "name": "Gaming Keyboard",
        "price": 299.90,
        "image": "keyboard.png"
    }

    # Replace the real Service function with a Mock
    with patch(
        "app.product_service.update_product"
    ) as mock_update:

        # Simulate a successful update
        mock_update.return_value = None

        # ACT - Send PUT request with JSON data
        response = client.put(
            "/api/products/10",
            json=product_data
        )

        # ASSERT - Verify HTTP status code
        assert response.status_code == 200

        # ASSERT - Verify JSON response
        assert response.get_json() == {
            "message": "Product updated"
        }

        # ASSERT - Verify Service was called once
        mock_update.assert_called_once()

        # ASSERT - Verify the Product sent to Service
        updated_product = mock_update.call_args.args[0]

        assert isinstance(updated_product, Product)
        assert updated_product.product_id == 10
        assert updated_product.name == "Gaming Keyboard"
        assert updated_product.price == 299.90
        assert updated_product.image == "keyboard.png"



# -------------------------------------------------
# API TEST 8 - Update a product that does not exist
# -------------------------------------------------

def test_update_product_not_found(client):

    # ARRANGE - Prepare updated product data
    product_id = 999

    product_data = {
        "name": "Gaming Keyboard",
        "price": 299.90,
        "image": "keyboard.png"
    }

    # Replace the real Service function with a Mock
    with patch(
        "app.product_service.update_product"
    ) as mock_update:

        # Simulate a product that does not exist
        mock_update.side_effect = (
            product_service.ProductNotFoundServiceError(
                "Product not found: 999"
            )
        )

        # ACT - Send PUT request to Flask
        response = client.put(
            f"/api/products/{product_id}",
            json=product_data
        )

        # ASSERT - Verify HTTP status code
        assert response.status_code == 404

        # ASSERT - Verify JSON error response
        assert response.get_json() == {
            "error": "Product not found: 999"
        }

        # ASSERT - Verify Service was called once
        mock_update.assert_called_once()

        # ASSERT - Verify product ID sent to Service
        updated_product = mock_update.call_args.args[0]

        assert isinstance(updated_product, Product)
        assert updated_product.product_id == product_id
        assert updated_product.name == "Gaming Keyboard"
        assert updated_product.price == 299.90
        assert updated_product.image == "keyboard.png"



# -------------------------------------------------
# API TEST 9 - Delete an existing product successfully
# -------------------------------------------------

def test_delete_product_success(client):

    # ARRANGE - Product ID to delete
    product_id = 10

    # Replace the real Service function with a Mock
    with patch(
        "app.product_service.delete_product"
    ) as mock_delete:

        # Simulate successful deletion
        mock_delete.return_value = None

        # ACT - Send DELETE request to Flask
        response = client.delete(
            f"/api/products/{product_id}"
        )

        # ASSERT - Verify HTTP status code
        assert response.status_code == 200

        # ASSERT - Verify JSON response
        assert response.get_json() == {
            "message": "Product deleted"
        }

        # ASSERT - Verify Service was called once
        mock_delete.assert_called_once_with(product_id)



# -------------------------------------------------
# API TEST 10 - Delete a product that does not exist
# -------------------------------------------------

def test_delete_product_not_found(client):

    # ARRANGE - Product ID that does not exist
    product_id = 999

    # Replace the real Service function with a Mock
    with patch(
        "app.product_service.delete_product"
    ) as mock_delete:

        # Simulate a product that was not found
        mock_delete.side_effect = (
            product_service.ProductNotFoundServiceError(
                "Product not found: 999"
            )
        )

        # ACT - Send DELETE request
        response = client.delete(
            f"/api/products/{product_id}"
        )

        # ASSERT - Verify HTTP status code
        assert response.status_code == 404

        # ASSERT - Verify JSON error response
        assert response.get_json() == {
            "error": "Product not found"
        }

        # ASSERT - Verify Service was called correctly
        mock_delete.assert_called_once_with(product_id)
