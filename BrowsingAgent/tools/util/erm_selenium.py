import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

wd = None

selenium_config = {
    "chrome_profile_path": None,
    "headless": True,  # Disable headless mode for debugging
    "full_page_screenshot": True,  # Disable full page screenshot for simplicity
}

def get_web_driver():
    print("Initializing WebDriver...")

    global wd, selenium_config

    if wd:
        print("Returning existing WebDriver instance.")
        return wd

    # Temporarily disable profile path to rule out profile issues
    chrome_profile_path = selenium_config.get("chrome_profile_path", None)
    profile_directory = None
    user_data_dir = None
    if isinstance(chrome_profile_path, str) and os.path.exists(chrome_profile_path):
        profile_directory = os.path.split(chrome_profile_path)[-1].strip("\\").rstrip("/")
        user_data_dir = os.path.split(chrome_profile_path)[0].strip("\\").rstrip("/")
        print(f"Using Chrome profile: {profile_directory}")
        print(f"Using Chrome user data dir: {user_data_dir}")
        print(f"Using Chrome profile path: {chrome_profile_path}")

    chrome_options = webdriver.ChromeOptions()
    print("ChromeOptions initialized.")

    print("Installing ChromeDriver using webdriver_manager.")
    chrome_driver_path = ChromeDriverManager().install()
    print(f"ChromeDriver installed at {chrome_driver_path}.")

    # Minimal set of Chrome options
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    # Enable verbose logging
    chrome_options.add_argument("--enable-logging")
    chrome_options.add_argument("--v=1")

    # Disable user data directory and profile settings for simplicity
    if user_data_dir and profile_directory:
         chrome_options.add_argument(f"user-data-dir={user_data_dir}")
         chrome_options.add_argument(f"profile-directory={profile_directory}")
         print(f"Using user data dir: {user_data_dir} and profile directory: {profile_directory}")

    try:
        wd = webdriver.Chrome(service=ChromeService(chrome_driver_path), options=chrome_options)
        print("WebDriver initialized successfully.")
        if wd.capabilities['chrome']['userDataDir']:
            print(f"Profile path in use: {wd.capabilities['chrome']['userDataDir']}")
    except Exception as e:
        print(f"Error initializing WebDriver: {e}")
        raise e

    wd.implicitly_wait(3)
    print("Implicit wait set to 3 seconds.")

    return wd

def set_web_driver(new_wd):
    # remove all popups
    js_script = """
    var popUpSelectors = ['modal', 'popup', 'overlay', 'dialog']; // Add more selectors that are commonly used for pop-ups
    popUpSelectors.forEach(function(selector) {
        var elements = document.querySelectorAll(selector);
        elements.forEach(function(element) {
            // You can choose to hide or remove; here we're removing the element
            element.parentNode.removeChild(element);
        });
    });
    """

    new_wd.execute_script(js_script)

    # Close LinkedIn specific popups
    if "linkedin.com" in new_wd.current_url:
        linkedin_js_script = """
        var linkedinSelectors = ['div.msg-overlay-list-bubble', 'div.ml4.msg-overlay-list-bubble__tablet-height'];
        linkedinSelectors.forEach(function(selector) {
            var elements = document.querySelectorAll(selector);
            elements.forEach(function(element) {
                element.parentNode.removeChild(element);
            });
        });
        """
        new_wd.execute_script(linkedin_js_script)

    #new_wd.execute_script("document.body.style.zoom='1.2'") Removed zoom for this case.

    global wd
    wd = new_wd

def set_selenium_config(config):
    global selenium_config
    selenium_config = config
