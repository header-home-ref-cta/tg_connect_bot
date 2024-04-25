import asyncio,decouple
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By


async def browser_handler(headless=False):

    path_to_webdriver = decouple.config('PATH_TO_WEBDRIVER')
    # Set up Firefox options for headless mode
    options = FirefoxOptions()
    # options.headless = True  # Run Firefox headlessly (without opening a visible browser window)
    if headless:
        options.add_argument("-headless")
    # Create a WebDriver instance (Firefox)
    driver = webdriver.Firefox(service=Service(path_to_webdriver), options=options)
    driver.implicitly_wait(10)
    return driver


async def register_yelp(driver, link):

    print("[seledka] REGISTERING YELP")
    password = decouple.config('PASSWORD')
    # Open the link in the browser
    while True:
        driver.get(link)
        # Wait for the page to load completely (for demonstration, we wait for the title to contain "Google")
        try:
            driver.implicitly_wait(10)
            # WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            # WebDriverWait(driver, 30).until(EC.element_to_be_selected((By.CSS_SELECTOR, 'div[role="main"]')))
            print("[seledka] Page loaded successfully:", driver.title)
            elem = WebDriverWait(driver, 30)
            elem = elem.until(EC.presence_of_element_located((By.ID, "first_name")))
            driver.find_element(By.ID, "first_name").send_keys("Connect")
            driver.find_element(By.ID, "last_name").send_keys("ToYelp")
            driver.find_element(By.ID, "password").send_keys(password)
            driver.find_element(By.ID, "confirm_password").send_keys(password)
            driver.find_element(By.XPATH, "//span[contains(.,\'Sign up\')]").click()
            element = driver.find_element(By.CSS_SELECTOR, "body")
            actions = ActionChains(driver)
            # open email notification settings
            driver.get("https://biz.yelp.com/settings/email")
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            driver.find_element(By.ID, "question_and_answer_email").click()
            driver.find_element(By.XPATH, "//form[@id=\'email_notification_form\']/fieldset/label[3]").click()
            driver.find_element(By.ID, "nearby_jobs").click()
            driver.find_element(By.ID, "business_weekly").click()
            driver.find_element(By.ID, "info_email").click()
            driver.find_element(By.ID, "sales_email").click()
            driver.find_element(By.ID, "deal_email").click()
            driver.find_element(By.ID, "purchased_products_tips").click()
            driver.find_element(By.ID, "instagram_import").click() # !!!!!!1!!111111111111111111111111111
            driver.find_element(By.XPATH, "//span[contains(.,\'Save Settings\')]").click()
            driver.get("https://biz.yelp.com")
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            driver.find_element(By.XPATH, "//button[contains(.,'Resend invite')]").click()
            break

        except Exception as e:
            print("[seledka] Error occurred while waiting for page to load:", e)
            continue


async def assing_alias(driver, email):
    print("[seledka] Assing Alias")
    driver.set_window_size(1024, 768)
    while True:
        try:
            driver.get('https://mail.google.com/mail/u/0/#settings/accounts')
            WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            if driver.current_url.startswith('https://accounts.google.com'):
                # driver.get(
                #     f'https://accounts.google.com/signin/v2/identifier?continue=https://mail.google.com/mail/&service=mail&sacu=1&rip=1&flowName=GlifWebSignIn&flowEntry=ServiceLogin')
                login = decouple.config('OUR_EMAIL')
                your_password = decouple.config('OUR_EMAIL_PASS')
                driver.implicitly_wait(15)
                email_field = driver.find_element(By.ID, 'identifierId').send_keys(login)
                next_button = driver.find_element(By.ID, 'identifierNext').click()
                wait = WebDriverWait(driver, 10)
                password_field = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="password"]')))
                password_field.send_keys(your_password)
                driver.find_element(By.ID, 'passwordNext').click()
                await asyncio.sleep(10)
                print("[autoresp] LOGGED IN")
            if not driver.current_url.startswith("https://mail.google.com/mail/"):
                print(f"[autoresp] {driver.current_url}")
                continue
            driver.get("https://mail.google.com/mail/u/0/#settings/accounts")
            wait = WebDriverWait(driver, 10)
            link = wait.until(EC.presence_of_element_located((By.XPATH, "//span[contains(.,'Add another email address')]")))
            link.click()
            driver.switch_to.window(driver.window_handles[1])
            driver.find_element(By.ID, "focus").send_keys(email)
            driver.find_element(By.ID, "bttn_sub").click()
            await asyncio.sleep(2)
            break
        except Exception as e:
            print(f"[seledka] Error occurred while waiting for page to load:\n{e}")
            continue
    return driver


async def confirm_yelp(driver, link):

    driver.get(link)
    WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.TAG_NAME, "body")))


def close_tab(driver):
    # Close the current tab
    driver.close()


def main():
    # Start the browser handler in the background
    browser_task = asyncio.create_task(browser_handler_headless())  # Use headless browser handler

    # Simulate usage by opening a link and closing the tab after some time
    # asyncio.sleep(5)  # Wait for 5 seconds (simulating some action requiring the browser)

    # Open a link in the browser
    register_yelp(browser_task.result(), "https://www.google.com")  # Use browser instance from the task result

    # Wait for some time before closing the tab
    # asyncio.sleep(30)  # Wait for 30 seconds

    # Close the tab
    close_tab(browser_task.result())  # Use browser instance from the task result


# Run the main coroutine
# asyncio.run(main())
