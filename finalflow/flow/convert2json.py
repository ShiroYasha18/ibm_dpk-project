import json
import pandas as pd
import re
import os


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
    Extracts answers based on the pattern 'AnswerX.X)' and organizes them into a list of dictionaries.
    Removes the pattern from the content for clean output.
    """
    pattern =r'Answer\s(\d+\.\d+)\)?\s*(.*?)(?=\s*Answer\s\d+\.\d+|\Z)'


    matches = re.finditer(pattern, full_text, re.DOTALL)
    answers = []

    for match in matches:
        question_number = match.group(1).strip()  # Extracts "X.X" part
        answer_content = match.group(2).strip()  # Extracts the answer content

        # Clean the content by removing extra whitespace and formatting
        cleaned_content = re.sub(r'\s{2,}', ' ', answer_content)
        cleaned_content = re.sub(r'^[-•·]\s*', '', cleaned_content, flags=re.MULTILINE)

        answers.append({
            "question_number": question_number,
            "content": cleaned_content
        })
    for i in answers:
        print(i)
    return answers

  # Add this line before writing to JSON


def process_file_with_pattern(file_path, output_folder):
    """Processes a .parquet file, extracts answers using a specific pattern, and saves to a JSON file."""
    try:
        if not file_path.endswith('.parquet'):
            raise ValueError(f"Unsupported file format: {file_path}. Use .parquet files only.")

        df = read_parquet_file(file_path)
        if df is None:
            print(f"Failed to read {file_path}.")
            return

        if 'contents' not in df.columns:
            print(f"Column 'contents' not found in the DataFrame.")
            return

        all_answers = []
        for idx, row in df.iterrows():
            full_text = row.get('contents', '')

            if not isinstance(full_text, str) or not full_text.strip():
                print(f"Skipping empty or invalid content at row {idx}.")
                continue

            print(f"Processing content at row {idx}: {full_text[:100]}...")

            extracted_answers = extract_answers_with_pattern(full_text)
            all_answers.extend(extracted_answers)

        output_file = os.path.join(output_folder, os.path.basename(file_path).replace(".parquet", ".json"))

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_answers, f, indent=4, ensure_ascii=False)

        print(f"Successfully saved extracted answers to {output_file}")

    except Exception as e:
        print(f"Error processing file {file_path}: {e}")


def process_folder(input_folder, output_folder):
    """Processes all .parquet files in the given input folder and saves the extracted JSON files to the output folder."""
    try:
        if not os.path.exists(input_folder):
            raise FileNotFoundError(f"Input folder '{input_folder}' does not exist.")

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        parquet_files = [f for f in os.listdir(input_folder) if f.endswith('.parquet')]

        if not parquet_files:
            print(f"No .parquet files found in {input_folder}.")
            return

        print(f"Found {len(parquet_files)} .parquet files. Processing...")

        for parquet_file in parquet_files:
            input_file_path = os.path.join(input_folder, parquet_file)
            process_file_with_pattern(input_file_path, output_folder)

        print("Processing completed.")

    except Exception as e:
        print(f"Error processing folder: {e}")
if __name__ == '__main__':
    input_folder="/Users/ayrafraihan/Desktop/pythonProject1/finalflow/input_folder/AnswerKey/parquet"
    output_folder="/Users/ayrafraihan/Desktop/pythonProject1/finalflow/input_folder/AnswerKey/Json_with_answers"
    process_folder(input_folder, output_folder)