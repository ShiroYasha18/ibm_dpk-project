import re
import json

def read_txt_file(file_path):
    """Reads a .txt file and returns its content as a string."""
    with open(file_path, 'r') as file:
        return file.read()

def parse_student_data(content):
    """
    Parses student content to extract answers.
    - Removes the word 'answer' from the beginning of answers
    - Handles sub-sections like 'a)', 'i.' within questions
    - Converts \n\n to actual line breaks
    """
    # Split content by "Answer" or "Ans" markers
    question_splits = re.split(r"(?i)\b(?:answer|ans(?:\s*\d*)?)\b", content)
    
    parsed_data = []
    question_number = 1
    
    for question in question_splits:
        question = question.strip()
        if not question:  # Skip empty splits
            continue
        
        # Start processing the answer content
        processed_answer = question
        
        # Convert literal \n\n to actual line breaks
        processed_answer = processed_answer.replace("\n\n", "")
        
        # Handle sub-sections with line breaks
        processed_answer = re.sub(
            r"(?:^|\n)\s*([a-z]\)|[a-z]\.|(?:i|ii|iii|iv|v|vi|vii|viii|ix|x)\.)",
            r"\n\1",
            processed_answer
        )
        
        # Remove leading/trailing whitespace and extra newlines
        processed_answer = "\n".join(line.strip() for line in processed_answer.split("\n"))
        
        # Add to parsed data if not empty
        if processed_answer.strip():
            parsed_data.append({
                "question_number": question_number,
                "answer": processed_answer.strip()
            })
            question_number += 1
    
    return parsed_data

def save_to_json(data, output_file):
    """Saves data to a JSON file."""
    with open(output_file, 'w') as file:
        json.dump(data, file, indent=4)

def process_file(file_path, output_json):
    """Processes a .txt file and saves structured data to a JSON file."""
    if not file_path.endswith('.txt'):
        raise ValueError("Unsupported file format. Use .txt files only.")
        
    content = read_txt_file(file_path)
    data = parse_student_data(content)
    save_to_json(data, output_json)
    print(f"Data saved to {output_json}")

# Example Usage
process_file("/Users/tanishta/Desktop/Dataprep/student.txt", "students2.json")