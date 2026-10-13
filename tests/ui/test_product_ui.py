
import time
import pytest

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from models.models import Product
from repositories import product_repository


# Fixture 1 - Browser Setup & Teardown – פתיחת Chrome לפני הבדיקה וסגירתו בסיום
@pytest.fixture
def driver():
    browser = webdriver.Chrome()
    browser.get("http://127.0.0.1:5000")

    yield browser

    browser.quit()


# Fixture 2 - Test Data Setup & Teardown – יצירת מוצר ייחודי במסד הבדיקות וניקויו בסיום
@pytest.fixture
def test_product(test_db):
    product = Product(
        product_id=0,
        name=f"UI Test {time.time_ns()}",
        price=149.90,
        image="mouse.png"
    )

    product_id = product_repository.create_product(product)

    yield product

    product_repository.delete_product(product_id)


# Test 1 - Smoke Testing – בדיקה שעמוד ניהול המוצרים נטען ומציג את הכותרת הנכונה
def test_product_manager_page_loads(driver):
    title = driver.find_element(By.TAG_NAME, "h1")

    assert title.text == "Product Manager"


# Test 2 - Functional Testing – יצירת מוצר דרך הממשק ואימות הופעתו בטבלה
def test_create_product_from_ui(driver, test_db):
    wait = WebDriverWait(driver, 10)
    product_name = f"Selenium Mouse {time.time_ns()}"

    try:
        # Act - מילוי טופס יצירת מוצר
        driver.find_element(By.ID, "name").send_keys(product_name)
        driver.find_element(By.ID, "price").send_keys("149.90")
        driver.find_element(By.ID, "image").send_keys("mouse.png")

        driver.find_element(
            By.CSS_SELECTOR,
            "#product-form button"
        ).click()

        # Assert - המוצר החדש מופיע בטבלה
        wait.until(
            EC.text_to_be_present_in_element(
                (By.ID, "product-table"),
                product_name
            )
        )

        assert product_name in driver.find_element(
            By.ID, "product-table"
        ).text

    finally:
        # Teardown - ניקוי המוצר שנוצר דרך הממשק
        for product in product_repository.read_all():
            if product.name == product_name:
                product_repository.delete_product(product.product_id)
                break


# Test 3 - Functional Testing – בדיקה שלחיצה על Details מציגה את פרטי המוצר הנבחר
def test_view_product_details(driver, test_product):
    driver.refresh()
    wait = WebDriverWait(driver, 10)

    # Act - לחיצה על Details של מוצר הבדיקה
    details_button = wait.until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                f"//tr[td[text()='{test_product.product_id}']]//button[text()='Details']"
            )
        )
    )

    details_button.click()

    # Assert - שם המוצר מופיע באזור הפרטים
    wait.until(
        EC.text_to_be_present_in_element(
            (By.ID, "product-details"),
            test_product.name
        )
    )

    assert test_product.name in driver.find_element(
        By.ID, "product-details"
    ).text


# Test 4 - Functional Testing – בדיקה עצמאית של עדכון מוצר דרך הממשק באמצעות Fixture
def test_update_product_from_ui(driver, test_product):
    driver.refresh()
    wait = WebDriverWait(driver, 10)

    updated_name = f"Updated {test_product.name}"

    # המתנה עד שהמוצר מופיע בטבלה
    wait.until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                f"//tr[td[text()='{test_product.product_id}']]"
            )
        )
    )

    # Act - לחיצה על Edit
    driver.find_element(
        By.XPATH,
        f"//tr[td[text()='{test_product.product_id}']]//button[text()='Edit']"
    ).click()

    # המתנה עד ששם המוצר נטען לטופס
    wait.until(
        EC.text_to_be_present_in_element_value(
            (By.ID, "name"),
            test_product.name
        )
    )

    # שינוי שם המוצר
    name_input = driver.find_element(By.ID, "name")
    name_input.clear()
    name_input.send_keys(updated_name)

    # שמירת העדכון
    driver.find_element(
        By.CSS_SELECTOR,
        "#product-form button"
    ).click()

    # Assert - השם החדש מופיע בטבלה
    wait.until(
        EC.text_to_be_present_in_element(
            (By.ID, "product-table"),
            updated_name
        )
    )

    assert updated_name in driver.find_element(
        By.ID, "product-table"
    ).text


# Test 5 - Functional Testing – מחיקת מוצר דרך הממשק ואימות היעלמותו מהטבלה
def test_delete_product_from_ui(driver, test_product):
    driver.refresh()
    wait = WebDriverWait(driver, 10)

    product_row = (
        By.XPATH,
        f"//tr[td[text()='{test_product.product_id}']]"
    )

    # Act - לחיצה על Delete של מוצר הבדיקה
    delete_button = wait.until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                f"//tr[td[text()='{test_product.product_id}']]//button[text()='Delete']"
            )
        )
    )

    delete_button.click()

    # אישור חלון המחיקה
    driver.switch_to.alert.accept()

    # Assert - המוצר נעלם מהטבלה
    wait.until(
        EC.invisibility_of_element_located(product_row)
    )

    assert test_product.name not in driver.find_element(
        By.ID, "product-table"
    ).text


# Test 6 - Functional Testing – ביטול מחיקת מוצר והשארתו בטבלה
def test_cancel_delete_product_from_ui(driver, test_product):
    driver.refresh()
    wait = WebDriverWait(driver, 10)

    # המתנה לכפתור Delete של מוצר הבדיקה
    delete_button = wait.until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                f"//tr[td[text()='{test_product.product_id}']]//button[text()='Delete']"
            )
        )
    )

    # Act - לחיצה על Delete וביטול הפעולה
    delete_button.click()
    driver.switch_to.alert.dismiss()

    # Assert - המוצר עדיין מופיע בטבלה
    assert test_product.name in driver.find_element(
        By.ID, "product-table"
    ).text
