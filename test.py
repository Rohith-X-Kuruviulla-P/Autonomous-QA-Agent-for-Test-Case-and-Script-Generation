from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def teardown():
    driver.quit()

try:
    options = webdriver.ChromeOptions()
    options.add_argument('start-maximized')
    driver = webdriver.Chrome(options=options)

    # Step 1: Select the 'Credit Card' payment method from the payment options.
    driver.get(r"C:\Users\rohit\Documents\Autonomous-QA-Agent-for-Test-Case-and-Script-Generation\up1.html")  # Replace with your URL
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'pay-cc'))).click()

    # Step 2: Verify that the checkout form displays the credit card input fields.
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'card-number')))

    print("TEST PASSED")

except Exception as e:
    print(f"TEST FAILED: {str(e)}")
finally:
    teardown()