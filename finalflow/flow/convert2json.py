import pandas as pd
import re
import json
from typing import Dict, List


def extract_answers(text: str) -> Dict[str, str]:
    """
    Extract answers from text based on 'Answer X.Y)' pattern with markdown formatting.
    """
    answers = {}

    try:
        # Updated pattern to handle markdown formatting with asterisks
        pattern =r'Answer\s*(\d+\.\d+)\)\s*(.*?)(?=\s*Answer\s*\d+\.\d+\)|$)'

        matches = re.finditer(pattern, text, re.DOTALL)

        for match in matches:
            answer_num = match.group(1).rstrip('.)')  # Remove trailing dot and parenthesis
            content = match.group(2).strip()

            # Clean up the content
            # Remove markdown bullet points
            content = re.sub(r'^\s*-\s*', '', content, flags=re.MULTILINE)
            # Remove asterisk bullet points
            content = re.sub(r'^\s*\*\s*', '', content, flags=re.MULTILINE)
            # Remove any remaining markdown formatting
            content = re.sub(r'\*\*|\*', '', content)
            # Normalize whitespace
            content = re.sub(r'\s+', ' ', content)
            content = content.strip()

            if content:
                answers[answer_num] = content
                print(f"Found Answer {answer_num}")
                print(f"Content: {content[:100]}...")

    except Exception as e:
        print(f"Error in extract_answers: {str(e)}")
        import traceback
        traceback.print_exc()

    return answers


def process_parquet(file_path: str, output_path: str) -> None:
    """
    Process parquet file and extract answers into JSON.
    """
    try:
        print(f"Reading parquet file: {file_path}")
        df = pd.read_parquet(file_path)
        print(f"DataFrame shape: {df.shape}")

        all_answers = []

        for idx, row in df.iterrows():
            content = row['contents']
            filename = row['filename']
            document_id = row['document_id']

            if isinstance(content, str):
                print(f"\nProcessing content from file: {filename}")
                print("First 200 characters of content:")
                print(content[:200])

                # Extract answers from content
                answers = extract_answers(content)
                print(f"Found {len(answers)} answers")

                if answers:
                    result = {
                        "document_id": document_id,
                        "filename": filename,
                        "answers": answers
                    }
                    all_answers.append(result)
                    print(f"Successfully extracted answers for {filename}")

        if all_answers:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(all_answers, f, indent=2, ensure_ascii=False)
            print(f"\nResults saved to: {output_path}")
            print("\nFirst document answers:")
            print(json.dumps(all_answers[0]['answers'], indent=2))
        else:
            print("\nNo answers were extracted from any document")

            # Debug: Print the raw content with line numbers
            print("\nDebug: Raw content with line numbers:")
            for i, line in enumerate(content.split('\n')):
                print(f"{i + 1}: {line}")

    except Exception as e:
        print(f"Error processing file: {str(e)}")
        import traceback
        traceback.print_exc()


