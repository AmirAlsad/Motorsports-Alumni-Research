import pandas as pd
import json

# Function to extract relevant fields from the experiences array
def extract_experience_fields(experiences):
    extracted = []
    for exp in experiences:
        extracted.append({
            "company": exp.get("company"),
            "company_linkedin_url": exp.get("company_linkedin_url"),
            "description": exp.get("description"),
            "is_current": exp.get("is_current"),
            "title": exp.get("title")
        })
    return extracted

# Function to process the scraped_linkedin column
def process_scraped_linkedin(row):
    processed_data = {
        "company": None,
        "company_description": None,
        "company_industry": None,
        "company_website": None,
        "Current_Company": None,
        "Current_Title": None,
        "Previous_Company_0": None,
        "Previous_Company_0_Title": None,
        "Previous_Company_1": None,
        "Previous_Company_1_Title": None,
        "Previous_Company_2": None,
        "Previous_Company_2_Title": None
    }

    try:
        # Load the JSON from the 'scraped_linkedin' field
        scraped_data = json.loads(row['scraped_linkedin'])

        # Extract primary fields from the main object
        processed_data.update({
            "company": scraped_data.get("company"),
            "company_description": scraped_data.get("company_description"),
            "company_industry": scraped_data.get("company_industry"),
            "company_website": scraped_data.get("company_website"),
        })

        # Extract experiences and expand them
        experiences = scraped_data.get("experiences", [])
        experience_data = extract_experience_fields(experiences)

        # Add the experiences fields as new columns
        for idx, exp in enumerate(experience_data):
            if exp.get("is_current") and processed_data["Current_Company"] is None:
                processed_data["Current_Company"] = exp.get("company")
                processed_data["Current_Title"] = exp.get("title")
            else:
                position_label = f"Previous_Company_{idx}"
                processed_data[position_label] = exp.get("company")
                processed_data[f"{position_label}_Title"] = exp.get("title")

    except (json.JSONDecodeError, TypeError, KeyError):
        # If scraped_linkedin is empty or invalid, processed_data will remain with None values
        pass

    return processed_data

# Load the input CSV file
input_file_path = 'scraped_linkedin.csv'  # Replace with your input CSV file path
output_file_path = 'final_datasheet.csv'  # Replace with your desired output CSV file path

# Read the CSV file into a DataFrame
df = pd.read_csv(input_file_path)

# Process each row and collect the results
processed_rows = df.apply(process_scraped_linkedin, axis=1).apply(pd.Series)

# Combine the original DataFrame with the processed data
final_df = pd.concat([df.drop(columns=['scraped_linkedin']), processed_rows], axis=1)

# Save the result to a new CSV file
final_df.to_csv(output_file_path, index=False)
print(f"Processed data saved to {output_file_path}")
