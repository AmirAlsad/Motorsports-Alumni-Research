from agency_swarm.tools import BaseTool
from pydantic import Field
from .util import get_web_driver

class GetURL(BaseTool):
    """
    Tool for extracting the URL of the current page in an existing WebDriver session.
    """

    def run(self):
        """
        Retrieves the current URL from the active WebDriver session.
        The WebDriver instance is handled by `get_web_driver` to ensure the agent's context.
        """
        # Access the existing WebDriver instance
        driver = get_web_driver()

        # Fetch and return the current page URL
        current_url = driver.current_url

        # Return the URL of the current page
        return current_url

if __name__ == "__main__":
    tool = GetURL()
    print(tool.run())
