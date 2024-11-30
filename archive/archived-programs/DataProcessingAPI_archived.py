import json
import re
import csv
import time
import requests

# Replace these with your own API key and Custom Search Engine ID (CSE ID)
API_KEY = ""
CSE_ID = ""

def remove_prefixes(name):
    # Pattern to match "Mr.", "Ms.", "Mrs.", "Dr.", at the start
    pattern = r"^(Mr\.|Ms\.|Dr\.|Mrs\.)\s+"
    name = re.sub(pattern, "", name)  # Remove the title if present

    # Pattern to match a middle initial (single capital letter without a period and followed by a space)
    name = re.sub(r"\b[A-Z]\b", "", name)  # Remove the middle initial if present

    # Remove extra whitespace that might result from replacements
    return re.sub(r"\s+", " ", name).strip()

def find_linkedin_profile(name):
    query = f'{name} "Massachusetts Institute of Technology"'
    url = f"https://www.googleapis.com/customsearch/v1"
    params = {
        "key": API_KEY,
        "cx": CSE_ID,
        "q": query,
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        results = response.json().get("items", [])
        if results:
            return results[0]["link"]
        else:
            return None
    except requests.exceptions.RequestException as e:
        return f"An error occurred: {e}"

def process_data(data, delay=1):
    processed_data = []
    for entry in data:
        cleaned_name = remove_prefixes(entry['name'])
        linkedin_profile = find_linkedin_profile(cleaned_name)
        processed_data.append({"name": cleaned_name, "linkedin_profile": linkedin_profile})
        time.sleep(delay)
    return processed_data

# Load JSON data from file
with open('students_data.json', 'r') as f:
    data = json.load(f)

# Process data
processed_data = process_data(data)

# Save data to CSV
with open('output_with_linkedin.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=["name", "linkedin_profile"])
    writer.writeheader()
    writer.writerows(processed_data)

print("Data processed and saved to output_with_linkedin.csv.")
