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


def extract_answers_with_pattern(full_text):
    """
    Extracts answers based on the pattern 'AnswerX.X)' and organizes them into a dictionary.
    """
    # Define the pattern to match 'AnswerX.X)' format and capture its content
    pattern = r'Answer(\d+\.\d+\))(.*?)(?=Answer\d+\.\d+\)|$)'
    matches = re.finditer(pattern, full_text, re.DOTALL)

    # Dictionary to store the extracted answers
    answers = {}
    for match in matches:
        question_number = match.group(1).strip()  # Extracts "1.1" part
        answer_content = match.group(2).strip()  # Extracts the answer content
        answers[question_number] = answer_content

    return answers


def process_file_with_pattern(file_path, output_file):
    """
    Processes a .parquet file, extracts answers using a specific pattern, and saves to a JSON file.
    """
    if not file_path.endswith('.parquet'):
        raise ValueError("Unsupported file format. Use .parquet files only.")

    df = read_parquet_file(file_path)
    if df is None:
        print(f"Failed to read {file_path}.")
        return

    contents_column = 'contents'
    if contents_column not in df.columns:
        print(f"Column '{contents_column}' not found in the DataFrame.")
        return

    all_answers = {}

    # Process each row in the DataFrame
    for idx, row in df.iterrows():
        full_text = row.get(contents_column, '')

        if not isinstance(full_text, str) or not full_text.strip():
            print(f"Skipping empty or invalid content at row {idx}.")
            continue

        print(f"Processing content at row {idx}: {full_text[:100]}...")  # Debug print

        # Extract answers from the text
        extracted_answers = extract_answers_with_pattern(full_text)
        all_answers.update(extracted_answers)  # Merge with the global answers dictionary

    # Save all answers to a JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_answers, f, indent=4, ensure_ascii=False)

    print(f"Successfully saved extracted answers to {output_file}")


# Example usage
if __name__ == "__main__":
    teacher_parquet_path = "/Users/ayrafraihan/Desktop/pythonProject1/finalflow/input_folder/AnswerSheet/parquet/extracted_text.parquet"
    output_json_path = "/Users/ayrafraihan/Desktop/pythonProject1/finalflow/input_folder/AnswerSheet/Json_with_answers/output_chunked.json"
    process_file_with_pattern(teacher_parquet_path, output_json_path)
