import json
import pandas as pd
import re

def extract_questions_and_answers(contents):
    """
    Extracts questions and answers from the content.
    Detects answer identifiers such as 'ANSWER', 'Ans 2', '2.', etc.
    """
    # Regular expression to match answer identifiers and content
    pattern = r'-\s*\*\*ANSWER\*\*\s*(.*?)(?=-\s*\*\*ANSWER\*\*|$)'
    
    # Find all matches in the content
    matches = re.finditer(pattern, contents, re.DOTALL)
    
    questions_and_answers = []
    for idx, match in enumerate(matches, 1):
        answer_text = match.group(1).strip()
        
        # Clean up the answer text
        answer_text = re.sub(r'\s+', ' ', answer_text)  # Replace multiple spaces with single space
        answer_text = re.sub(r'[\n\r]+', ' ', answer_text)  # Replace newlines with spaces
        
        questions_and_answers.append({
            "question_number": str(idx),
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
    
    # Inspect DataFrame columns
    print("DataFrame Columns:", df.columns)
    print(df.head())
    
    contents_column = 'contents'
    if contents_column not in df.columns:
        print(f"Column '{contents_column}' not found in the DataFrame.")
        return
    
    all_data = []
    for idx, row in df.iterrows():
        contents = row.get(contents_column, '')
        
        if contents:
            print(f"Processing contents for question {idx + 1}: {contents[:200]}...")
            questions_and_answers = extract_questions_and_answers(contents)
            all_data.extend(questions_and_answers)
        else:
            print(f"Empty contents found for row: {row}")
    
    print(f"Extracted data to save: {all_data}")
    
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
    parquet_file_path_1 = "/Users/ayrafraihan/Desktop/pythonProject1/finalflow/input_folder/AnswerKey/parquet/pd.parquet"
    output_json_path_1 = "/Users/ayrafraihan/Desktop/pythonProject1/finalflow/input_folder/AnswerKey/parquet/output1.json"
    
    process_file(parquet_file_path_1, output_json_path_1)