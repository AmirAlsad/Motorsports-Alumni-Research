import os
import csv
import requests
import json
import pandas as pd
from dotenv import load_dotenv

# Load API key from environment variables
load_dotenv()
API_KEY = os.getenv("RELEVANCE_API_KEY")  # Ensure the API key is set in the .env file

# Define the API URL and headers
API_URL = "https://api-bcbe5a.stack.tryrelevance.com/latest/studios/eb6eea74-829c-4f28-8340-5339bb13c216/trigger_limited"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": API_KEY
}

def process_csv(input_file, output_file):
    # Load the input CSV file into a DataFrame
    df = pd.read_csv(input_file)

    # Add a new column for the scraped LinkedIn data
    df['scraped_linkedin'] = None

    # Iterate over each row in the DataFrame
    for index, row in df.iterrows():
        try:
            # Prepare the API request payload
            payload = {
                "params": {
                    "url": row['link'],  # Use the 'link' column from the CSV
                    "name": ""  # Leave the 'name' field empty
                },
                "project": "51ff8f1c-9565-4989-8bd3-9370ea705f24"
            }

            # Make the API request
            response = requests.post(API_URL, headers=HEADERS, data=json.dumps(payload))

            # Check if the response is successful
            if response.status_code == 200:
                # Extract and store the response data
                df.at[index, 'scraped_linkedin'] = response.json()
            else:
                # Log the error for this entry
                print(f"Error for {row['name']} ({row['link']}): {response.status_code} {response.text}")
        except Exception as e:
            print(f"Exception for {row['name']} ({row['link']}): {e}")
            df.at[index, 'scraped_linkedin'] = None

    # Save the updated DataFrame to the output CSV file
    df.to_csv(output_file, index=False)
    print(f"Processed data saved to {output_file}")

# Run the script
if __name__ == "__main__":
    input_csv = "linkedin_links.csv"  # Replace with your input file name
    output_csv = "scraped_linkedin.csv"  # Replace with your desired output file name

    process_csv(input_csv, output_csv)
