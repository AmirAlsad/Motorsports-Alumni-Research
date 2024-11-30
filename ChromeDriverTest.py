from selenium import webdriver

try:
    # Initialize the ChromeDriver
    driver = webdriver.Chrome()

    # Navigate to a webpage to test if ChromeDriver works
    driver.get('https://www.google.com')

    # Retrieve the ChromeDriver version from the session capabilities
    capabilities = driver.capabilities
    chromedriver_version = capabilities['chrome']['chromedriverVersion'].split(' ')[0]
    print("ChromeDriver version:", chromedriver_version)

    # Optionally, print the page title to confirm navigation
    print("Page title:", driver.title)

except Exception as e:
    print("An error occurred:", e)

finally:
    # Close the browser
    driver.quit()
