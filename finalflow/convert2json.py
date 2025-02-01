import json
import pandas as pd
import re

def read_parquet_file(file_path):
    """Reads a .parquet file and returns its contents as a pandas DataFrame."""
    try:
        df = pd.read_parquet(file_path)
        return df
    except Exception as e:
        print(f"Error reading Parquet file {file_path}: {e}")
        return None

def extract_only_answers(content):
    """
    Extracts only the answers by:
    - Removing everything before 'Answer:', 'Ans1:', 'A1:', etc.
    - Cleaning up Markdown headers, bullet points, and extra spaces.
    """

    # 1️⃣ Find the first occurrence of 'Answer', 'Ans1', 'A1', etc.
    match = re.search(r"(?i)\b(answer|ans\s*\d*|a\s*\d*)\b", content)

    if match:
        content = content[match.end():]  # Keep only the content **after** the answer starts

    # 2️⃣ Remove any markdown headers (## a), ## 1., etc.)
    content = re.sub(r"##\s*[a-zA-Z0-9]+\)", "", content)

    # 3️⃣ Remove bullet points and excessive newlines
    content = re.sub(r"[-•●]", "", content)  # Remove special bullet characters
    content = re.sub(r"\n+", " ", content)  # Convert multiple newlines to a single space
    content = re.sub(r"\s+", " ", content).strip()  # Remove extra spaces

    return {"contents": content} if content else None  # Return only if content is found

def process_file(file_path, output_json):
    """Processes a .parquet file and saves extracted answers to a JSON file."""
    if not file_path.endswith('.parquet'):
        raise ValueError("Unsupported file format. Use .parquet files only.")
        
    df = read_parquet_file(file_path)
    if df is None:
        print(f"Failed to read {file_path}.")
        return
    
    # Assuming answers are in a column named 'contents' (adjust if different)
    contents_column = 'contents'
    if contents_column not in df.columns:
        print(f"Column '{contents_column}' not found in the DataFrame.")
        return
    
    all_answers = []
    for _, row in df.iterrows():
        contents = row.get(contents_column, '')
        
        if contents:
            extracted_answer = extract_only_answers(contents)  # Extract **only** answer
            if extracted_answer:
                all_answers.append(extracted_answer)

    # Save extracted answers to JSON
    save_to_json(all_answers, output_json)
    print(f"Data saved to {output_json}")

def save_to_json(data, output_file):
    """Saves extracted answers to a JSON file."""
    with open(output_file, 'w') as file:
        json.dump(data, file, indent=4)

# **Process the Uploaded Parquet File**
teacher_parquet_path = "/Users/tanishta/Desktop/GitHub/ibm/finalflow/output_folder/teacher.parquet"
output_json_path =  "output2.json"
process_file(teacher_parquet_path, output_json_path)

# Output JSON Path
print(f"Extracted answers saved to: {output_json_path}")