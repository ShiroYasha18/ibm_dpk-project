import json
import pandas as pd
import re

def extract_questions_and_answers(contents):
    """
    Extracts questions and answers from the content.
    Detects answer identifiers such as 'ANSWER', 'Ans 2', '2.', etc.
    """

    # Regular expression to match answer identifiers like 'ANSWER', 'Ans 2', '2.', '2)', etc.
    answer_pattern = re.compile(r'\b(ANSWER|Ans\s*\d*|\b\d+\.)\b', re.IGNORECASE)

    # Split content by answer identifiers
    segments = answer_pattern.split(contents)

    # Remove empty strings and trim whitespace
    segments = [s.strip() for s in segments if s.strip()]

    # Check if we have any segments after splitting
    print(f"Extracted segments: {segments}")

    # Structure extracted questions and answers
    questions_and_answers = []
    for idx in range(1, len(segments), 2):  # Iterate over answers
        question_number = (idx // 2) + 1  # Generate question number dynamically (1, 2, 3, ...)
        answer_text = segments[idx]  # Extract answer

        # Remove "ANSWER" or any other unnecessary prefix
        answer_text = re.sub(r'^\s*(ANSWER|Ans\s*\d*)[:.-]?\s*', '', answer_text, flags=re.IGNORECASE)

        questions_and_answers.append({
            "question_number": str(question_number),  # Ensure question number is stored as a string
            "contents": answer_text
        })

    return questions_and_answers

def process_file(file_path, output_json):
    """Processes a .parquet file and saves structured data to a JSON file."""
    if not file_path.endswith('.parquet'):
        raise ValueError("Unsupported file format. Use .parquet files only.")
        
    df = read_parquet_file(file_path)
    if df is None:
        print(f"Failed to read {file_path}.")
        return
    
    # Inspect DataFrame columns and check if contents are available
    print("DataFrame Columns:", df.columns)  # Print column names
    print(df.head())  # Print first few rows to inspect structure
    
    # Assuming the contents are in a column named 'contents' (adjust if different)
    contents_column = 'contents'
    if contents_column not in df.columns:
        print(f"Column '{contents_column}' not found in the DataFrame.")
        return
    
    all_data = []
    for _, row in df.iterrows():
        # Get the contents of the 'contents' column
        contents = row.get(contents_column, '')
        
        if contents:
            print(f"Processing contents: {contents[:200]}...")  # Show first 200 chars for debugging
            # Extract questions and answers from contents
            questions_and_answers = extract_questions_and_answers(contents)
            all_data.extend(questions_and_answers)  # Add extracted questions to list
        else:
            print(f"Empty contents found for row: {row}")  # Show the whole row if contents are missing
    
    # Print all extracted data to ensure it's populated correctly
    print(f"Extracted data to save: {all_data}")
    
    # Save to JSON only if all_data is not empty
    if all_data:
        save_to_json(all_data, output_json)
        print(f"Data saved to {output_json}")
    else:
        print("No data to save.")

def read_parquet_file(file_path):
    """Reads a .parquet file and returns its contents as a pandas DataFrame."""
    try:
        df = pd.read_parquet(file_path)
        return df
    except Exception as e:
        print(f"Error reading Parquet file {file_path}: {e}")
        return None

def save_to_json(data, output_file):
    """Saves data to a JSON file."""
    with open(output_file, 'w') as file:
        json.dump(data, file, indent=4)

# Example Usage
if __name__ == "__main__":
    # Replace with your actual file paths
    parquet_file_path_1 = "/Users/tanishta/Desktop/GitHub/ibm/finalflow/output_folder/extracted_stu.parquet"
    output_json_path_1 = "output1.json"

    # Process the file and generate the output JSON
    process_file(parquet_file_path_1, output_json_path_1)