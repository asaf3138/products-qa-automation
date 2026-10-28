
import pytest
from unittest.mock import patch

from config.app_config import db_connection_kwargs


@pytest.fixture
def test_db():
    # Arrange: copy the original database configuration
    test_config = db_connection_kwargs.copy()

    # Use the dedicated test database
    test_config["database"] = "db1_test"

    # Safety check
    assert test_config["database"] == "db1_test"

    # Temporarily replace the repository configuration
    with patch(
        "repositories.product_repository.db_connection_kwargs",
        test_config
    ):
        yield

