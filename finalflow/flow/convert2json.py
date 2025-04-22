import os
import json
import pandas as pd
import re
import wat  # Import similarity comparison module


def extract_answers(text: str):
    """
    Extract answers from the text with improved diagram handling.
    
    Args:
        text: Text to extract answers from
        
    Returns:
        Dictionary of answers
    """
    answers = {}
    
    # Process any diagram association comments
    diagram_association = {}
    association_pattern = re.compile(r'<!-- DIAGRAM BELONGS TO ANSWER (\d+[A-Z]?) -->')
    for match in association_pattern.finditer(text):
        answer_num = match.group(1)
        diagram_association[answer_num] = True
    
    # Remove processing comments
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
    
    # Improved regex pattern to detect answer patterns
    answer_pattern = re.compile(r'\*\*Answer\s+(\d+[A-Z]?)\*\*\s*(.*?)(?=\*\*Answer\s+\d+[A-Z]?\*\*|\Z)', 
                               re.DOTALL)
    
    # Find all answers
    matches = answer_pattern.findall(text)
    
    for answer_num, answer_text in matches:
        # Clean up the answer text
        answer_text = answer_text.strip()
        
        # If this answer should have a diagram according to our processing
        if answer_num in diagram_association and "[DIAGRAM]" not in answer_text:
            answer_text = answer_text + "\n[DIAGRAM]"
        
        # Store the answer
        answers[answer_num] = answer_text
    
    # Additional processing for diagrams
    # Look for diagrams that might be incorrectly associated
    for answer_num, answer_text in list(answers.items()):
        if "[DIAGRAM]" in answer_text:
            # Check if the diagram is at the end of this answer and the next answer starts with text about a diagram
            if answer_text.strip().endswith("[DIAGRAM]"):
                # Find the next answer number
                current_num = answer_num[0]
                current_letter = answer_num[1] if len(answer_num) > 1 else ""
                
                # Look for the next answer in sequence
                next_answer_num = None
                if current_letter:
                    # Try next letter (e.g., 1B -> 1C)
                    next_letter = chr(ord(current_letter) + 1)
                    next_answer_num = f"{current_num}{next_letter}"
                else:
                    # Try next number (e.g., 1 -> 2)
                    next_answer_num = str(int(current_num) + 1)
                
                # Check if the next answer exists and starts with text about a diagram
                if next_answer_num in answers:
                    next_text = answers[next_answer_num].lower()
                    if next_text.startswith("a diagram") or next_text.startswith("the diagram"):
                        # Move the diagram to the next answer
                        answers[next_answer_num] = "[DIAGRAM]\n" + answers[next_answer_num]
                        answers[answer_num] = answers[answer_num].replace("[DIAGRAM]", "").strip()
    
    return answers

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

def convert_text_to_json(text_file, output_dir):
    """
    Convert text file to JSON.
    
    Args:
        text_file: Path to text file
        output_dir: Directory to save JSON
        
    Returns:
        Path to JSON file
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Read text file
        with open(text_file, "r") as f:
            text = f.read()
        
        # Extract answers
        answers = extract_answers(text)
        
        # Create JSON file
        json_file = os.path.join(output_dir, os.path.basename(text_file).replace(".txt", ".json"))
        
        # Write JSON file
        with open(json_file, "w") as f:
            json.dump(answers, f, indent=4)
        
        return json_file
    except Exception as e:
        logger.error(f"Error converting text to JSON: {str(e)}")
        return None

if __name__ == "__main__":
    input="/Users/ayrafraihan/Desktop/pythonProject1/finalflow/input_folder/AnswerKey/parquet"
    output="/Users/ayrafraihan/Desktop/pythonProject1/finalflow/input_folder/AnswerKey/Json_with_answers"
    process_file(input, output)
