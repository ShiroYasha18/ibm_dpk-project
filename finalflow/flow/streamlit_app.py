import streamlit as st
import os
import json
import asyncio
import sys
from pathlib import Path

# Add the current directory and parent directory to the path to import local modules
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))  # Parent dir
# Add the pdf2parquet module to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

# Import the main processing functions
from app import PDFHandwritingExtractor, convert_pdf_to_parquet, process_parquet_directory
import wat

# Set up logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define paths
BASE_DIR = Path("/Users/ayrafraihan/Desktop/pythonProject1/finalflow")
ANSWERSHEET_DIR = BASE_DIR / "input_folder/AnswerSheet/Handwritten"
ANSWERKEY_DIR = BASE_DIR / "input_folder/AnswerKey/clean_pdf"
ANSWERSHEET_CLEAN_DIR = BASE_DIR / "input_folder/AnswerSheet/clean_pdf"
ANSWERSHEET_PARQUET_DIR = BASE_DIR / "input_folder/AnswerSheet/parquet"
ANSWERKEY_PARQUET_DIR = BASE_DIR / "input_folder/AnswerKey/parquet"
ANSWERSHEET_JSON_DIR = BASE_DIR / "input_folder/AnswerSheet/Json_with_answers"
ANSWERKEY_JSON_DIR = BASE_DIR / "input_folder/AnswerKey/Json_with_answers"
RESULTS_DIR = BASE_DIR / "results"
TEMP_IMAGE_DIR = BASE_DIR / "input_folder/AnswerSheet/tempimg"

# Ensure directories exist
for directory in [ANSWERSHEET_DIR, ANSWERKEY_DIR, ANSWERSHEET_CLEAN_DIR, 
                 ANSWERSHEET_PARQUET_DIR, ANSWERKEY_PARQUET_DIR, 
                 ANSWERSHEET_JSON_DIR, ANSWERKEY_JSON_DIR, 
                 RESULTS_DIR, TEMP_IMAGE_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Function to save uploaded file
def save_uploaded_file(uploaded_file, directory):
    try:
        file_path = os.path.join(directory, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return file_path
    except Exception as e:
        st.error(f"Error saving file: {e}")
        return None

# Function to display results from JSON file
def display_results(result_file):
    try:
        with open(result_file, "r") as f:
            results = json.load(f)
        
        st.header("Results")
        st.json(results)
        
        # Create a more user-friendly display
        st.subheader("Similarity Scores")
        
        # Check if the results have the expected structure
        if "comparisons" in results:
            # Format for similarity_extracted_text_pd.json
            for comparison in results["comparisons"]:
                st.write(f"**Question {comparison.get('question_number', 'Unknown')}**")
                st.write(f"Similarity Score: {comparison.get('similarity_score', 'N/A')}")
                st.write(f"Student Answer: {comparison.get('answer1', 'N/A')}")
                st.write(f"Teacher Answer: {comparison.get('answer2', 'N/A')}")
                st.write("---")
        else:
            # Format for other result structures
            for item in results:
                if "answers" in item:
                    st.write(f"Document: {item.get('filename', 'Unknown')}")
                    
                    for answer_num, answer_data in item["answers"].items():
                        st.write(f"**Answer {answer_num}**")
                        st.write(f"Similarity Score: {answer_data.get('similarity', 'N/A')}")
                        st.write(f"Student Answer: {answer_data.get('student_answer', 'N/A')}")
                        st.write(f"Teacher Answer: {answer_data.get('teacher_answer', 'N/A')}")
                        st.write("---")
        
        return True
    except Exception as e:
        st.error(f"Error displaying results: {e}")
        st.write("Raw result file path:", result_file)
        return False

# Async function to process PDFs
async def process_pdfs(answersheet_path, answerkey_path):
    try:
        # Extract text from handwritten answer sheet
        extractor = PDFHandwritingExtractor()
        
        # Convert PDF to images
        st.info("Converting PDF to images...")
        image_paths = await extractor.convert_pdf_to_images(answersheet_path, TEMP_IMAGE_DIR)
        
        if not image_paths:
            st.error("No images were created from the PDF")
            return None
        
        # Extract text from images
        st.info("Extracting text from images using LLama 3.2 vision model from WatsonX by IBM...")
        extracted_texts = await extractor.extract_text_from_images(image_paths)
        
        if not extracted_texts:
            st.error("No text was extracted from the images")
            return None
        
        # Create output PDF with extracted text
        extracted_text_pdf = os.path.join(ANSWERSHEET_CLEAN_DIR, f"extracted_{os.path.basename(answersheet_path)}")
        st.info("Creating output PDF with extracted text...")
        success = await extractor.create_text_pdf(extracted_texts, extracted_text_pdf)
        
        if not success:
            st.error("Failed to create extracted text PDF")
            return None
        
        # Convert PDFs to Parquet
        st.info("Converting answer sheet to Parquet...")
        convert_pdf_to_parquet(str(ANSWERSHEET_CLEAN_DIR), str(ANSWERSHEET_PARQUET_DIR))
        
        st.info("Converting answer key to Parquet...")
        convert_pdf_to_parquet(str(ANSWERKEY_DIR), str(ANSWERKEY_PARQUET_DIR))
        
        # Convert Parquet to JSON
        st.info("Extracting answers from Answer Key Parquet files and saving to JSON...")
        process_parquet_directory(str(ANSWERKEY_PARQUET_DIR), str(ANSWERKEY_JSON_DIR))
        
        st.info("Extracting answers from Answer Sheet Parquet files and saving to JSON...")
        process_parquet_directory(str(ANSWERSHEET_PARQUET_DIR), str(ANSWERSHEET_JSON_DIR))
        
        # Compare JSONs
        st.info("Comparing JSONs with Cosine Similarity...")
        result_file = wat.compare_jsons(str(ANSWERSHEET_JSON_DIR), str(ANSWERKEY_JSON_DIR), str(RESULTS_DIR))
        
        return result_file
    
    except Exception as e:
        st.error(f"Error processing PDFs: {e}")
        import traceback
        st.error(traceback.format_exc())
        return None

# Streamlit UI
def main():
    st.title("Handwritten Answer Sheet Evaluation")
    
    # Create tabs for different functionalities
    tab1, tab2 = st.tabs(["Process New Files", "View Existing Results"])
    
    with tab1:
        st.write("Upload your handwritten answer sheet and answer key PDFs for evaluation")
        
        # Create sidebar for file uploads
        with st.sidebar:
            st.header("Upload Files")
            
            # Upload answer sheet
            st.subheader("Handwritten Answer Sheet")
            answersheet_file = st.file_uploader("Upload your handwritten answer sheet", 
                                               type=["pdf"], 
                                               key="answersheet")
            
            # Upload answer key
            st.subheader("Answer Key")
            answerkey_file = st.file_uploader("Upload your answer key", 
                                             type=["pdf"], 
                                             key="answerkey")
            
            # Process button
            process_button = st.button("Process PDFs")
        
        # Main content area for processing
        if process_button:
            if not answersheet_file:
                st.error("Please upload a handwritten answer sheet")
                return
            
            if not answerkey_file:
                st.error("Please upload an answer key")
                return
            
            # Save uploaded files
            with st.spinner("Saving uploaded files..."):
                answersheet_path = save_uploaded_file(answersheet_file, ANSWERSHEET_DIR)
                answerkey_path = save_uploaded_file(answerkey_file, ANSWERKEY_DIR)
                
                if not answersheet_path or not answerkey_path:
                    return
            
            # Process PDFs
            with st.spinner("Processing PDFs... This may take a few minutes."):
                result_file = asyncio.run(process_pdfs(answersheet_path, answerkey_path))
                
                if result_file:
                    st.success("Processing complete!")
                    display_results(result_file)
    
    with tab2:
        st.write("View existing evaluation results")
        
        # List all JSON files in the results directory
        result_files = [f for f in os.listdir(str(RESULTS_DIR)) if f.endswith('.json')]
        
        if not result_files:
            st.info("No result files found. Process some files first.")
        else:
            selected_file = st.selectbox("Select a result file to view", result_files)
            
            if selected_file:
                result_file_path = os.path.join(str(RESULTS_DIR), selected_file)
                display_results(result_file_path)

if __name__ == "__main__":
    main()