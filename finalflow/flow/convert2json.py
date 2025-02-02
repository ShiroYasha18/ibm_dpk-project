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

def extract_answers_with_numbers(content):
    """
    Extracts answers and assigns question numbers.
    Handles various answer formats and includes question numbering.
    """
    # Pattern to match question numbers and answers
    patterns = [
        # Match patterns like "Question 1" or "Q1" followed by answer
        r'(?i)(?:question\s*(\d+)|q(\d+)).*?(?:answer|ans)(?:\s*\d+)?[\s:]+(.+?)(?=(?:\n\s*(?:question\s*\d+|q\d+)\s)|$)',
        # Match just answer patterns with numbers
        r'(?i)(?:##\s*)?(?:answer|ans)\s*(\d+)[\s:]+(.+?)(?=(?:\n\s*(?:##\s*)?(?:answer|ans)\s*\d+)|$)',
        # Match any answer pattern
        r'(?i)(?:##\s*)?(?:answer|ans)[\s:]+(.+?)(?=(?:\n\s*(?:##\s*)?(?:answer|ans))|$)'
    ]
    
    answers = []
    question_number = 1  # Default starting number
    
    for pattern in patterns:
        matches = list(re.finditer(pattern, content, re.DOTALL))
        if matches:
            for match in matches:
                # Extract answer content based on pattern type
                if 'question' in pattern.lower() or 'q' in pattern.lower():
                    # Pattern with explicit question number
                    number = match.group(1) or match.group(2)
                    answer_text = match.group(3)
                elif 'answer' in pattern.lower() and r'(\d+)' in pattern:
                    # Pattern with answer number
                    number = match.group(1)
                    answer_text = match.group(2)
                else:
                    # Pattern with no number
                    number = str(question_number)
                    answer_text = match.group(1)
                    question_number += 1

                if answer_text:
                    # Clean up the answer text
                    answer_text = re.sub(r'\s{2,}', ' ', answer_text)  # Remove extra spaces
                    answer_text = re.sub(r'(?m)^\s*[-•·]\s*', '', answer_text)  # Remove bullet points
                    answer_text = answer_text.strip()
                    
                    answers.append({
                        "question_number": number,
                        "contents": answer_text
                    })
            
            # If we found matches with this pattern, no need to try others
            break
    
    return answers

def process_file(file_path, output_json):
    """Processes a .parquet file and saves extracted answers to a JSON file."""
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
    
    all_answers = []
    for _, row in df.iterrows():
        contents = row.get(contents_column, '')
        
        if contents:
            print(f"Processing content: {contents[:100]}...")  # Debug print
            extracted_answers = extract_answers_with_numbers(contents)
            if extracted_answers:
                for answer in extracted_answers:
                    print(f"Extracted answer {answer['question_number']}: {answer['contents'][:100]}...")
                all_answers.extend(extracted_answers)
            else:
                print("No answers found in this content")
    
    if all_answers:
        save_to_json(all_answers, output_json)
        print(f"Successfully saved {len(all_answers)} answers to {output_json}")
    else:
        print("No answers were extracted")

def save_to_json(data, output_file):
    """Saves extracted answers to a JSON file."""
    with open(output_file, 'w') as file:
        json.dump(data, file, indent=4)

# Example usage
if __name__ == "__main__":
    teacher_parquet_path = "/Users/tanishta/Desktop/GitHub/ibm/finalflow/output_folder/teacher.parquet"
    output_json_path = "/Users/tanishta/Desktop/GitHub/ibm/finalflow/results/output2.json"
    process_file(teacher_parquet_path, output_json_path)