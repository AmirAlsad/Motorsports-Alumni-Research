import json
import csv
import re
import os
import sys

from openai import OpenAI
from agency_swarm import Agent, Agency
from SearchAgent import SearchAgent

from dotenv import load_dotenv
load_dotenv()

progress_file = "progress.txt"

def load_progress():
    """Load the last processed filename and index from a text file."""
    try:
        with open(progress_file, "r") as f:
            data = f.read().strip()
            if data == 'done' or not data:
                # Processing is complete or no progress recorded
                return None, -1
            else:
                filename, index = data.split(',')
                return filename, int(index)
    except (FileNotFoundError, ValueError):
        # Start from the beginning if file is missing or contains invalid data
        return None, -1

def save_progress(filename, index):
    """Save the last processed filename and index to a text file."""
    with open(progress_file, "w") as f:
        f.write(f"{filename},{index}")

def remove_prefixes(name):
    # Remove prefixes like "Mr.", "Ms.", "Dr.", and "Mrs."
    name = re.sub(r"^(Mr\.|Ms\.|Dr\.|Mrs\.)\s+", "", name)

    # Split the name and capture only the first and last parts
    parts = name.split()

    # Keep the first and last parts, joining them back together
    if len(parts) > 2:
        # If there are more than two parts, retain only the first and last part
        name = f"{parts[0]} {parts[-1]}"

    # Preserve apostrophes in last names
    return re.sub(r"\s+", " ", name).strip()

def get_first_name(cleaned_name):
    # Split the name and return the first part as the first name
    return cleaned_name.split()[0]

def get_last_name(cleaned_name):
    # Split the name and return the second part as the last name
    return cleaned_name.split()[1]

def extract_link(response):
    # Regular expression to match URLs with optional surrounding square brackets
    url_pattern = r'\[?(https?://[^\s\)\]]+)\]?'

    # Find the first URL match in the response
    match = re.search(url_pattern, response)

    # Return the first matched URL if found, otherwise return None
    return match.group(1) if match else None

# Directory containing JSON files
data_directory = 'students_data'

# List and sort all JSON files in the directory
json_files = sorted([f for f in os.listdir(data_directory) if f.endswith('.json')])

# Load last progress
last_filename, start_index = load_progress()

# Flag to indicate whether we've found the last processed file
found_last_file = False if last_filename else True

for json_file in json_files:
    if not found_last_file:
        if json_file == last_filename:
            found_last_file = True
        else:
            # Skip until we reach the last processed file
            continue

    # Load the JSON data
    with open(os.path.join(data_directory, json_file), 'r') as f:
        data = json.load(f)

    # Open the CSV file in append mode
    with open('linkedin_links.csv', mode='a', newline='') as csv_file:
        fieldnames = ["name", "class_year", "degrees", "major", "link"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        # Write header only if the file is new
        if os.stat('linkedin_links.csv').st_size == 0:
            writer.writeheader()

        # Determine starting index
        if json_file == last_filename and start_index != -1:
            current_start_index = start_index + 1  # Start from the next user after the last processed
        else:
            current_start_index = 0

        index_processed = current_start_index - 1  # Initialize index_processed

        for index in range(current_start_index, len(data)):
            obj = data[index]
            try:
                # Agency Initialization
                selenium_config = {
                    # your profile path
                    "chrome_profile_path": "/Users/amiralsad/Library/Application Support/Google/Chrome/Profile 3",
                    "headless": False,
                    "full_page_screenshot": True,
                }

                search_agent = SearchAgent(selenium_config=selenium_config)

                agency = Agency([search_agent])

                print('Setup Agency.')

                # Remove prefixes from the "name" field
                cleaned_name = remove_prefixes(obj["name"])
                first_name = get_first_name(cleaned_name)
                last_name = get_last_name(cleaned_name)

                provided_link = f"https://www.linkedin.com/search/results/people/?keywords={first_name}%20{last_name}&origin=FACETED_SEARCH&schoolFilter=%5B%221503%22%5D&sid=X._"

                # Call the agency to process the cleaned name
                command = f"""Access the provided URL and complete the necessary actions based on the following steps:

# Steps

1. **Read the URL**: Access the provided link, `{provided_link}` and use the '[send screenshot]' command to view the page.
2. **Login Instructions**:
    - If you are not logged in already, log in to the website using the '[highlight text fields]' command and the following credentials:
    - **Username**: `amir7alsad@gmail.com`
    - **Password**: `@17AMIR17amir17@`
3. **Navigate and Search**:
    - Click on the first profile that appears in the search results using the `ClickElement` tool.
    - If there are no search results, reply to the user indicating that no profiles were found.
4. **Extract URL**:
    - Use the `GetURL` tool to extract the current URL of the profile page.
5. **Respond with the Outcome**:
    - Provide the user with the extracted URL from the `GetURL` tool if successful.
    - If no search results are present, simply state that no profiles were found.

# Notes
- Only use the given credentials if prompted or if access is restricted.
- Don't respond to the user with anything other than the extracted URL or an error message."""

                result = agency.get_completion(message=command)  # Replace with appropriate call
                extracted_link = extract_link(result)

                print(result)

                # Assume result contains the link generated by the agency
                obj["link"] = extracted_link  # Add the link to the object

                # Write the updated object as a row in the CSV
                writer.writerow(obj)

                # Update index_processed after successful processing
                index_processed = index

                # Save progress after each successful processing
                save_progress(json_file, index_processed)

            except Exception as e:
                print(f"Error processing user {obj['name']}: {e}")
                print("Saving progress and exiting.")
                # Save last successfully processed index
                save_progress(json_file, index_processed)
                sys.exit(1)  # Exit the script

        # After finishing processing the current file
        # Mark the file as completed by setting index to -1
        save_progress(json_file, -1)

# After processing all files
with open(progress_file, "w") as f:
    f.write("done")
print("Processing complete. Progress has been reset.")
