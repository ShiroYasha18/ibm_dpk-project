import os
import json
import pandas as pd
import re
import wat  # Import similarity comparison module


def extract_answers(text: str):
    """Extract answers with proper formatting."""
    answers = {}
    try:
        pattern = r'Answer\s*(\d+\.\d+)\)?\s*(.*?)(?=\s*Answer\s*\d+\.\d+|\Z)'
        matches = re.finditer(pattern, text, re.DOTALL)

        for match in matches:
            number = match.group(1).strip()
            content = match.group(2).strip()
            content = re.sub(r'\s+', ' ', content)  # Normalize whitespace
            answers[number] = content

        return answers
    except Exception as e:
        print(f"Error extracting answers: {e}")
        return {}


def process_parquet_file(input_file: str, output_file: str):
    """Processes a single parquet file and saves extracted answers in JSON."""
    try:
        df = pd.read_parquet(input_file)

        result = [{
            "document_id": str(df.iloc[0].get('document_id', '')),
            "filename": str(df.iloc[0].get('filename', '')),
            "answers": extract_answers(df.iloc[0].get('contents', ''))
        }]

        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        return result
    except Exception as e:
        print(f"Error processing {input_file}: {e}")
        return []


def process_parquet_directory(input_dir: str, output_dir: str, similarity_output: str):
    """Processes multiple parquet files, extracts answers to JSON, and computes similarity scores."""
    all_data = []

    if not os.path.exists(input_dir):
        print(f"Error: Directory {input_dir} does not exist.")
        return

    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(similarity_output, exist_ok=True)

    for file in os.listdir(input_dir):
        if file.endswith(".parquet"):
            file_path = os.path.join(input_dir, file)
            output_file = os.path.join(output_dir, f"{file.replace('.parquet', '.json')}")  # Fix path issue
            print(f"Processing Parquet file: {file_path}")
            extracted_data = process_parquet_file(file_path, output_file)

            if extracted_data:
                all_data.extend(extracted_data)

    if all_data:
        print(f"Saved {len(all_data)} answers to {output_dir}")

    # Compute similarity scores after extracting all JSONs
    wat.compare_jsons(output_dir, output_dir, similarity_output)
    print(f"Similarity scores saved in {similarity_output}")
