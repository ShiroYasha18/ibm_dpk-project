import os
import re
import json
import logging

logger = logging.getLogger(__name__)

def process_file(input_file, output_file):
    """
    Process a parquet file and extract answers.
    
    Args:
        input_file: Path to parquet file
        output_file: Path to output JSON file
        
    Returns:
        Extracted data
    """
    try:
        import pandas as pd
        
        # Read parquet file
        df = pd.read_parquet(input_file)
        
        # Extract text from dataframe
        text = " ".join(df["text"].astype(str).tolist())
        
        # Extract answers from text
        answers = extract_answers(text)
        
        # Create output data
        output_data = [{
            "document_id": os.path.splitext(os.path.basename(input_file))[0],
            "filename": os.path.basename(input_file).replace(".parquet", ".pdf"),
            "answers": answers
        }]
        
        # Ensure the directory exists (but not nested)
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Write output file
        with open(output_file, "w") as f:
            json.dump(output_data, f, indent=2)
        
        return output_data
    except Exception as e:
        logger.error(f"Error processing file {input_file}: {str(e)}")
        return None

def extract_answers(text):
    """
    Extract answers from text.
    """
    answers = {}
    
    # Combined pattern using alternation for different formats
    pattern = r'''
        (?:  # First format: **Answer 2B** or **Answer 2B)**
            \*\*Answer\s+(\d+[A-Z]?)\)?\*\*
        )
        |
        (?:  # Second format: Answer2B or Answer2B)
            Answer\s*(\d+[A-Z]?)\)?
        )
        |
        (?:  # Third format: Answer 2B or Answer 2B)
            Answer\s+(\d+[A-Z]?)\)?
        )
        (.*?)(?=(?:Answer|\*\*Answer|\[DIAGRAM\]|\Z))
    '''
    
    matches = re.finditer(pattern, text, re.DOTALL | re.IGNORECASE | re.VERBOSE)
    
    for match in matches:
        # Extract answer number from whichever group matched
        answer_num = next((g for g in match.groups()[:3] if g), None)
        answer_text = match.group(4).strip()
        
        if answer_num and answer_text:
            # Clean and store the answer
            clean_text = re.sub(r'\s+', ' ', answer_text)
            answers[answer_num] = clean_text
    
    return answers

def process_parquet_directory(input_dir, output_dir):
    """
    Process all parquet files in a directory.
    
    Args:
        input_dir: Directory containing parquet files
        output_dir: Directory to save JSON files
        
    Returns:
        List of processed files
    """
    processed_files = []
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Process each parquet file
    for file in os.listdir(input_dir):
        if file.endswith(".parquet"):
            input_file = os.path.join(input_dir, file)
            
            # Create output file path (directly in output_dir, not in a nested folder)
            output_file = os.path.join(output_dir, file.replace(".parquet", ".json"))
            
            # Process file
            result = process_file(input_file, output_file)
            
            if result:
                processed_files.append(output_file)
    
    return processed_files