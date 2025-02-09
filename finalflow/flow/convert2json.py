import os
import json
import pandas as pd
import re
import wat  # Import similarity comparison module


def extract_answers(text: str):
    """Extract answers with both decimal and alphanumeric formatting."""
    answers = {}
    try:
        pattern = r'Answer\s*(?:(\d+\.\d+)|(\d+[A-Za-z]))\)?\s*(.*?)(?=\s*Answer\s*(?:\d+\.\d+|\d+[A-Za-z])|\Z)'

        '''       Patterns it can match :
       Answer1.1) Some text
       Answer 2.3) Other text
       Answer 2C) More text 
       Answer 5A Different text
        '''

        matches = re.finditer(pattern, text, re.DOTALL)

        for match in matches:
            number = match.group(1) if match.group(1) else match.group(2)
            content = match.group(3).strip()
            content = re.sub(r'\s+', ' ', content)  # Normalize whitespace
            answers[number] = content

        return answers
    except Exception as e:
        print(f"Error extracting answers: {e}")
        return {}

def process_file(input_file: str, output_dir: str):
    """Processes a single parquet file and saves extracted answers in JSON."""
    if not os.path.exists(input_file):
        print(f"Error: File {input_file} does not exist.")
        return

    if not input_file.endswith(".parquet"):
        print(f"Error: {input_file} is not a Parquet file.")
        return

    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"{os.path.basename(input_file).replace('.parquet', '.json')}")

    try:
        df = pd.read_parquet(input_file)
        result = [{
            "document_id": str(df.iloc[0].get('document_id', '')),
            "filename": str(df.iloc[0].get('filename', '')),
            "answers": extract_answers(df.iloc[0].get('contents', ''))
        }]

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"Processed {input_file} -> {output_file}")
    except Exception as e:
        print(f"Error processing {input_file}: {e}")



def process_parquet_directory(input_dir: str, output_dir: str, similarity_output: str):
    """Processes multiple parquet files, extracts answers to JSON, and computes similarity scores."""
    process_file(input_dir, output_dir)

    if os.listdir(output_dir):
        print(f"Saved extracted answers to {output_dir}")


    wat.compare_jsons(output_dir, output_dir, similarity_output)
    print(f"Similarity scores saved in {similarity_output}")

if __name__ == "__main__":
    input="/Users/ayrafraihan/Desktop/pythonProject1/finalflow/input_folder/AnswerKey/parquet"
    output="/Users/ayrafraihan/Desktop/pythonProject1/finalflow/input_folder/AnswerKey/Json_with_answers"
    process_file(input, output)
