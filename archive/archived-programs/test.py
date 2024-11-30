import re

def extract_link(response):
    # Regular expression to match URLs with optional surrounding square brackets
    url_pattern = r'\[?(https?://[^\s\)\]]+)\]?'

    # Find the first URL match in the response
    match = re.search(url_pattern, response)

    # Return the first matched URL if found, otherwise return None
    return match.group(1) if match else None

# Test cases to handle slight variations in response formats
response_1 = "Here is the URL of the profile: [https://www.linkedin.com/in/wasayanwer/]."
response_2 = "Profile link: (https://www.linkedin.com/in/wasayanwer/)"
response_3 = "Visit https://example.com for more details."
response_4 = "No URL here, just text."

# Testing the function
print(extract_link(response_1))  # Expected: "https://www.linkedin.com/in/wasayanwer/"
print(extract_link(response_2))  # Expected: "https://www.linkedin.com/in/wasayanwer/"
print(extract_link(response_3))  # Expected: "https://example.com"
print(extract_link(response_4))  # Expected: None
