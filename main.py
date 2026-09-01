import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# --- CONFIGURATION ---
URL = "https://cell-leaders.rhapsodyofrealities.org"
CSV_FILE_PATH = "large_data_extracted.csv"
WAIT_TIME_PER_USER = (
    10  # Seconds to wait after each login before moving to the next
)
# ---------------------

# Initialize the Chrome WebDriver
driver = webdriver.Chrome()
driver.maximize_window()

try:
    # Open the CSV file and read the contacts
    with open(CSV_FILE_PATH, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        user_count = 1
        for row in reader:
            user_name = row["Name"].strip()
            user_email = row["Email"].strip()

            # Skip rows where the name couldn't be parsed properly
            if user_name == "N/A" or not user_name:
                print(
                    f"Skipping row {user_count}: Invalid name for email {user_email}"
                )
                user_count += 1
                continue

            print(
                f"\n[{user_count}] Logging in: {user_name} ({user_email})..."
            )

            try:
                # 1. Navigate to the login page
                driver.get(URL)

                # 2. Set up explicit wait utility
                wait = WebDriverWait(driver, 10)

                # 3. Locate the Full Name field and enter the value
                name_field = wait.until(
                    EC.presence_of_element_located((By.ID, "names"))
                )
                name_field.clear()
                name_field.send_keys(user_name)

                # 4. Locate the Email Address field and enter the value
                email_field = wait.until(
                    EC.presence_of_element_located((By.ID, "email"))
                )
                email_field.clear()
                email_field.send_keys(user_email)

                # 5. Submit the form
                login_form = driver.find_element(By.ID, "loginForm_id")
                login_form.submit()

                print(
                    f"Success: Submitted form for {user_name}. Waiting {WAIT_TIME_PER_USER} seconds..."
                )

                # Pause so the page loads/redirects successfully before looping to the next user
                time.sleep(WAIT_TIME_PER_USER)

            except Exception as entry_error:
                print(
                    f"Failed to log in user {user_name} due to an error: {entry_error}"
                )

            user_count += 1

except FileNotFoundError:
    print(
        f"Error: Could not find '{CSV_FILE_PATH}'. Please run your parser script first."
    )
except Exception as e:
    print(f"A critical error occurred: {e}")

finally:
    print("\nBulk login operation complete. Closing browser now.")
    driver.quit()