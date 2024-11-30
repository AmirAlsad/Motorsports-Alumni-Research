import pandas as pd
import ast  # Import ast for literal_eval

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
    return extracted[:8]  # Limit to the first 8 experiences

# Function to process the scraped_linkedin column
def process_scraped_linkedin(row):
    processed_data = {
        "company": None,
        "company_description": None,
        "company_industry": None,
        "company_website": None,
    }

    # Predefine columns for up to 8 experiences
    for i in range(8):
        processed_data[f"Company_{i}_Name"] = None
        processed_data[f"Company_{i}_Title"] = None
        processed_data[f"Company_{i}_Is_Current"] = None

    try:
        # Get the 'scraped_linkedin' value
        scraped_linkedin_str = row['scraped_linkedin']

        # Check if 'scraped_linkedin' is NaN or empty
        if pd.isna(scraped_linkedin_str) or scraped_linkedin_str.strip() == '':
            # If it's NaN or empty, skip processing
            return processed_data

        # Evaluate the outer string to get the dictionary
        parsed_scraped_linkedin = ast.literal_eval(scraped_linkedin_str)

        # Access the 'output' key
        output_data = parsed_scraped_linkedin.get('output')
        if not isinstance(output_data, dict):
            # Can't proceed, return processed_data as is
            return processed_data

        # Access the 'json_filtered_filtered' key
        scraped_data = output_data.get('json_filtered_filtered')
        if not isinstance(scraped_data, dict):
            # Can't proceed, return processed_data as is
            return processed_data

        # Now proceed as before

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
            processed_data[f"Company_{idx}_Name"] = exp.get("company")
            processed_data[f"Company_{idx}_Title"] = exp.get("title")
            processed_data[f"Company_{idx}_Is_Current"] = exp.get("is_current")

    except Exception as e:
        # If an error occurs, processed_data will remain with None values
        print(f"Error processing row: {e}")
        # Optionally, print debugging information
        # print(f"scraped_linkedin_str: {scraped_linkedin_str}")
        # print(f"parsed_scraped_linkedin: {parsed_scraped_linkedin}")
        # print(f"output_data: {output_data}")
        # print(f"scraped_data: {scraped_data}")
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
