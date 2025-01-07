import re
import json
from PyPDF2 import PdfReader

def read_pdf_file(file_path):
    """Reads a .pdf file and returns its content as a string."""
    reader = PdfReader(file_path)
    content = ""
    for page in reader.pages:
        content += page.extract_text()
    return content

def parse_teacher_data(content):
    """
    Parses teacher content to extract questions and main answers.
    The question is extracted by looking for patterns like "question", "q", "q1", etc., 
    until "answer" or "ans" is encountered.
    """
    # Split content by questions using regex for "Question", "Q", etc.
    question_splits = re.split(r"(?i)(question\s*\d*[:.]*)", content)
    parsed_data = []
    question_number = 1

    for i in range(1, len(question_splits), 2):
        question_header = question_splits[i].strip()
        body_text = question_splits[i + 1].strip() if i + 1 < len(question_splits) else ""

        # Extract question part using regex for 'question', 'q', 'q1', etc., till 'answer', 'ans'
        question_match = re.match(r"(.*?)(?=\s*(?:answer|ans|a\s*\.)\s*)", body_text, re.IGNORECASE)
        if question_match:
            question_text = question_match.group(1).strip()
            answer_text = body_text[question_match.end():].strip()
        else:
            question_text = question_header
            answer_text = body_text

        # Store the question and main answer
        question_entry = {
            "question_number": question_number,
            "question": question_text,
            "answer": answer_text
        }
        
        parsed_data.append(question_entry)
        question_number += 1
    
    return parsed_data

def save_to_json(data, output_file):
    """Saves data to a JSON file."""
    with open(output_file, 'w') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

def process_file(file_path, output_json):
    """Processes a .pdf file and saves structured data to a JSON file."""
    if not file_path.endswith('.pdf'):
        raise ValueError("Unsupported file format. Use .pdf files only.")
    
    content = read_pdf_file(file_path)
    data = parse_teacher_data(content)
    save_to_json(data, output_json)
    print(f"Data saved to {output_json}")

# Example Usage
process_file("/Users/tanishta/Desktop/Dataprep/teacher.pdf", "teachers2.json")