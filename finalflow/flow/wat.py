import pandas as pd
import re
import spacy

# Load the spaCy model
nlp = spacy.load("en_core_web_sm")


def read_parquet_file(file_path):
    """Reads a .parquet file and returns its contents as a pandas DataFrame."""
    try:
        df = pd.read_parquet(file_path)
        print("DataFrame loaded successfully!")
        return df
    except Exception as e:
        print(f"Error reading Parquet file {file_path}: {e}")
        return None
def process_parquet_file(file_path):
    """Process the Parquet file, extract answers, and print them."""
    # Read the Parquet file
    df = read_parquet_file(file_path)

    if df is None:
        print("Failed to load the Parquet file.")
        return

    # Check the structure of the DataFrame
    print("Columns in DataFrame:", df.columns)

    # Check if the 'contents' column exists
    if 'contents' not in df.columns:
        print("Column 'contents' not found in the DataFrame.")
        return

    # Process each row in the DataFrame
    for idx, row in df.iterrows():
        print(f"Processing row {idx}...")

        # Inspect the content of the row
        full_text = row['contents']
        print(f"Row {idx} Content: {full_text[:500]}...")  # Print the first 500 characters for inspection

        # Ensure the content is a string
        if not isinstance(full_text, str):
            print(f"Skipping row {idx} as the content is not a string.")
            continue

        print(f"Row {idx} Answers:")

        # Extract answers using regex
        answers = extract_answers(full_text)

        # Check if answers are found and print them
        if answers:
            for answer in answers:
                print(f"Answer Number: {answer['answer_number']}")
                print(f"Answer Text: {answer['answer_text']}")
                print("-" * 50)
        else:
            print(f"No answers found in row {idx}.")
            print("-" * 50)

# Path to the Parquet file
parquet_file_path = input("Enter the path of the Parquet file: ")

# Call the function to process the Parquet file
process_parquet_file(parquet_file_path)
