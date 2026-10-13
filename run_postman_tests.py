
# Run the Flask application using the test database

from config import app_config

# Select the dedicated test database BEFORE importing app.py
app_config.db_connection_kwargs["database"] = "db1_test"

# Import Flask application only after changing the database
from app import app

if __name__ == "__main__":

    # Display the selected database
    print(
        "Postman test database:",
        app_config.db_connection_kwargs["database"]
    )

    # Start Flask without the automatic reloader
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )
