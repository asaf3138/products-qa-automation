
# Products QA Automation

Automated testing project for a Flask-based product management web application.

The project demonstrates automated testing across four layers:
- Repository integration testing
- Service unit testing
- REST API testing
- UI end-to-end testing

The test suite includes 46 automated tests written in Python using pytest.


## Technologies & Tools

| Technology | Purpose |
|------------|---------|
| Python | Test automation and application logic |
| pytest | Test execution, assertions and fixtures |
| Selenium WebDriver | Automated UI testing |
| Flask | Web application and REST API |
| Flask Test Client | API testing without running a live server |
| MySQL | Database and repository integration testing |
| unittest.mock | Mocking dependencies in unit tests |
| Postman | REST API testing |
| Git & GitHub | Version control and collaboration |
| uv | Python dependency and environment management |



## Test Coverage

The project includes 46 automated tests across four testing layers.

| Testing Layer | Test Type | Number of Tests |
|---------------|-----------|-----------------|
| Repository | Integration Testing | 11 |
| Service | Unit Testing | 19 |
| API | Functional API Testing | 10 |
| UI | End-to-End Testing | 6 |
| **Total** | | **46** |

### Repository Tests
- Verify product creation and retrieval.
- Test product updates and deletion.
- Validate database operations using MySQL.

### Service Tests
- Validate product names and prices.
- Test business logic and error handling.
- Isolate dependencies using mocks and patches.

### API Tests
- Verify product CRUD endpoints.
- Validate HTTP response status codes.
- Test successful and invalid requests.

### UI Tests
- Automate browser interactions using Selenium.
- Verify product creation, editing and deletion.
- Validate product information displayed in the UI.



## Project Structure

```text
products_web_app_project_v2/
├── tests/
│   ├── conftest.py
│   ├── repository/
│   │   └── test_product_repository.py
│   ├── services/
│   │   └── test_product_service.py
│   ├── api/
│   │   └── test_products_api.py
│   └── ui/
│       └── test_product_ui.py
├── run_postman_tests.py
├── pyproject.toml
├── uv.lock
└── README.md
```

### Test Organization

- `tests/repository/` - Database integration tests.
- `tests/services/` - Business logic unit tests.
- `tests/api/` - REST API functional tests.
- `tests/ui/` - Selenium end-to-end tests.
- `tests/conftest.py` - Shared pytest fixtures.
- `run_postman_tests.py` - Postman test collection runner.


## Installation & Setup

### Prerequisites

Before running the project, make sure the following tools are installed:

- Python 3.13 or later
- MySQL Server
- uv (Python package and environment manager)
- Google Chrome (for Selenium UI tests)

### Clone the Repository

```bash
git clone https://github.com/asaf3138/products-qa-automation.git
cd products-qa-automation
```

### Install Dependencies

```bash
uv sync
```

This command creates the Python environment and installs the project dependencies.



### Database Configuration

1. Make sure MySQL Server is installed and running.
2. Copy `config/app_config.example.py` to `config/app_config.py`.
3. Open `config/app_config.py` and update the MySQL connection settings:

```python
db_connection_kwargs = {
    "host": "localhost",
    "user": "root",
    "password": "YOUR_MYSQL_PASSWORD",
    "database": "db1_test"
}
```

4. Replace `YOUR_MYSQL_PASSWORD` with your local MySQL password.

**Important:** Automated integration and UI tests may modify or delete product records. Use a dedicated test database, not a production database.

The real `config/app_config.py` file is excluded from Git to protect local credentials.





### Run the Application

Start the Flask web application:

```bash
uv run python app.py
```

The application must remain running while executing the Selenium UI tests.

### Run Automated Tests

Open a separate terminal in the project directory.

Run the complete pytest test suite:

```bash
uv run pytest -v
```

Run a specific testing layer:

```bash
uv run pytest tests/repository/ -v
uv run pytest tests/services/ -v
uv run pytest tests/api/ -v
uv run pytest tests/ui/ -v
```

### Expected Test Results

The complete automated test suite contains 46 tests:

- 11 Repository integration tests
- 19 Service unit tests
- 10 API functional tests
- 6 Selenium UI end-to-end tests

All 46 tests passed in the verified local test environment.
