import sys
import os

# Get the absolute path of the parent directory where pdf2parq.py is located
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))  # Parent dir
import re
import os
import io
import logging
import asyncio
import base64
import textwrap  # Add this import for text wrapping
from dotenv import load_dotenv
from pdf2image import convert_from_path
from PIL import Image
from ibm_watsonx_ai import APIClient, Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas  # Add this import for canvas
from pdf2parq import convert_pdf_to_parquet
import convert2json
import json
import wat

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


load_dotenv()

API_KEY = os.getenv("IBM_API_KEY")
SERVICE_URL = os.getenv("IBM_SERVICE_URL")
PROJECT_ID = os.getenv("IBM_PROJECT_ID")

credentials = Credentials(url=SERVICE_URL, api_key=API_KEY)
client = APIClient(credentials=credentials)
client.set.default_project(PROJECT_ID)


model_id = "meta-llama/llama-3-2-90b-vision-instruct"
params = {"decoding_method": "greedy", "max_new_tokens": 500}

model = ModelInference(
    model_id=model_id,
    credentials=credentials,
    project_id=PROJECT_ID,
    params=params
)

class HandwritingRecognizer:
    def __init__(self):
        self.extraction_prompt = """EXTRACT TEXT LITERALLY FROM DOCUMENT FOLLOWING THESE RULES:
1. Extract ALL text exactly as written, including:
   - Answer headers like **Answer 1A**
   - Bullet points and numbering
   - Mathematical notations and equations
   - Scribbled text marked as [UNREADABLE]

2. For diagrams:
   - Insert [DIAGRAM] exactly where it appears in the document
   - Do NOT describe or explain diagrams
   - Do NOT add placeholder text about diagrams

3. Strict formatting:
   - Preserve original spacing and line breaks
   - No summaries, interpretations, or additional comments
   - No text about "the image contains" or "overall" sections
   - Never add comments about extraction process

Example of acceptable output:
**Answer 1A**
* Stomach: Breaks down food using acids
[DIAGRAM]
**Answer 1B**
* Plant cell wall structure...
"""
    
    def encode_image(self, image_path):
        """Encode image to base64."""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    async def process_image(self, image_path):
        """Send image to IBM Watson API for handwriting recognition."""
        try:
            image_base64 = self.encode_image(image_path)
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": self.extraction_prompt},
                        {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + image_base64}}
                    ]
                }
            ]

            response = await asyncio.to_thread(model.chat, messages=messages)
            return response["choices"][0]["message"]["content"] if response else None
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            return None


class PDFHandwritingExtractor:
    def __init__(self):
        # Remove OpenAI client and use the existing IBM Watson model
        pass
        
    async def convert_pdf_to_images(self, pdf_path, output_dir):
        """
        Convert PDF to images.
        
        Args:
            pdf_path: Path to PDF file
            output_dir: Directory to save images
            
        Returns:
            List of paths to images
        """
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Clear existing files in output directory
        for file in os.listdir(output_dir):
            file_path = os.path.join(output_dir, file)
            if os.path.isfile(file_path):
                os.unlink(file_path)
        
        try:
            # Convert PDF to images
            images = convert_from_path(pdf_path, dpi=300)
            
            image_paths = []
            for i, image in enumerate(images):
                image_path = os.path.join(output_dir, f"page_{i+1}.jpg")
                image.save(image_path, "JPEG")
                image_paths.append(image_path)
                
            return image_paths
        except Exception as e:
            logger.error(f"Error converting PDF to images: {str(e)}")
            return []
    
    async def extract_text_from_images(self, image_paths):
        """
        Extract text from images using the IBM Watson Llama 3.2 vision model.
        
        Args:
            image_paths: List of paths to images
            
        Returns:
            List of extracted texts
        """
        extracted_texts = []
        
        for i, image_path in enumerate(image_paths):
            try:
                # Load image
                with open(image_path, "rb") as img_file:
                    image_data = img_file.read()
                    image_base64 = base64.b64encode(image_data).decode("utf-8")
                
                # Create prompt with improved diagram handling instructions
                prompt = """
                Extract all text from this image of a handwritten or printed document.
                
                Important instructions for diagram handling:
                1. When you see a diagram, mark it with [DIAGRAM] exactly where it appears
                2. Pay close attention to answer numbering (like "**Answer 1B**") 
                3. Make sure to associate diagrams with the correct answer number
                4. If a diagram appears between two answers, determine which answer it belongs to based on context
                5. If a diagram appears at the top of a page, check if it belongs to an answer from the previous page
                
                Format the output as plain text, preserving the original structure including paragraphs, 
                bullet points, and answer numbering.
                """
                
                # Use IBM Watson model instead of OpenAI
                messages = [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                        ]
                    }
                ]
                
                response = await asyncio.to_thread(model.chat, messages=messages)
                extracted_text = response["choices"][0]["message"]["content"] if response else None
                
                # Add page metadata to help with post-processing
                if extracted_text:
                    extracted_text = f"<!-- PAGE {i+1} -->\n{extracted_text}"
                    extracted_texts.append(extracted_text)
                    logger.info(f"Successfully extracted text from image {i+1}/{len(image_paths)}")
                
            except Exception as e:
                logger.error(f"Error extracting text from image {image_path}: {str(e)}")
        
        # Post-process the extracted texts to fix diagram associations
        processed_texts = self._post_process_texts(extracted_texts)
        
        return processed_texts
    
    def _post_process_texts(self, texts):
        """
        Post-process extracted texts to improve diagram association with answers.
        
        Args:
            texts: List of extracted texts
            
        Returns:
            List of processed texts
        """
        # Combine all texts to analyze the document as a whole
        combined_text = "\n".join(texts)
        
        # Look for answer patterns
        answer_pattern = re.compile(r'\*\*Answer\s+(\d+[A-Z]?)\*\*')
        
        # Find all answers in the text
        answers = answer_pattern.findall(combined_text)
        
        # Look for diagrams at page boundaries
        page_boundary_pattern = re.compile(r'<!-- PAGE \d+ -->\s*\[DIAGRAM\]')
        page_boundaries = page_boundary_pattern.finditer(combined_text)
        
        # Process each page boundary diagram
        for match in page_boundaries:
            # Get the position of the diagram
            diagram_pos = match.start()
            
            # Find the last answer before this diagram
            last_answer = None
            last_answer_pos = 0
            
            for answer in answers:
                answer_heading = f"**Answer {answer}**"
                answer_pos = combined_text.find(answer_heading, last_answer_pos)
                
                if 0 <= answer_pos < diagram_pos:
                    last_answer = answer
                    last_answer_pos = answer_pos
                elif answer_pos > diagram_pos:
                    break
            
            # Find the next answer after this diagram
            next_answer = None
            for answer in answers:
                answer_heading = f"**Answer {answer}**"
                answer_pos = combined_text.find(answer_heading, diagram_pos)
                
                if answer_pos > diagram_pos:
                    next_answer = answer
                    break
            
            # If we found a last answer and next answer, check which one the diagram belongs to
            if last_answer and next_answer:
                # Check the context around the diagram
                context_after = combined_text[diagram_pos:diagram_pos+100].lower()
                
                # If the context after the diagram refers to a diagram, it likely belongs to the next answer
                if "a diagram" in context_after or "the diagram" in context_after:
                    # The diagram belongs to the next answer, no change needed
                    pass
                else:
                    # The diagram likely belongs to the previous answer
                    # We'll add a note for further processing
                    combined_text = combined_text[:diagram_pos] + f"<!-- DIAGRAM BELONGS TO ANSWER {last_answer} -->\n" + combined_text[diagram_pos:]
        
        # Split the processed text back into pages
        page_pattern = re.compile(r'<!-- PAGE \d+ -->')
        processed_texts = page_pattern.split(combined_text)
        
        # Remove empty entries and strip whitespace
        processed_texts = [text.strip() for text in processed_texts if text.strip()]
        
        return processed_texts
    
    async def create_text_pdf(self, texts, output_path):
        """
        Create a PDF with extracted text.
        
        Args:
            texts: List of extracted texts
            output_path: Path to save PDF
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create a PDF
            c = canvas.Canvas(output_path, pagesize=letter)
            width, height = letter
            
            for text in texts:
                # Remove any processing comments
                text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
                
                # Create a text object
                textobject = c.beginText()
                textobject.setTextOrigin(50, height - 50)
                textobject.setFont("Helvetica", 12)
                
                # Add text to the text object
                for line in text.split('\n'):
                    # Check if line is a diagram marker
                    if line.strip() == "[DIAGRAM]":
                        textobject.textLine("[DIAGRAM PLACEHOLDER]")
                    else:
                        # Wrap long lines
                        wrapped_lines = textwrap.wrap(line, width=80)
                        if wrapped_lines:
                            for wrapped_line in wrapped_lines:
                                textobject.textLine(wrapped_line)
                        else:
                            textobject.textLine("")
                
                # Draw the text object
                c.drawText(textobject)
                
                # Add a new page
                c.showPage()
            
            # Save the PDF
            c.save()
            
            return True
        except Exception as e:
            logger.error(f"Error creating PDF: {str(e)}")
            return False

class AnswerKeyExtractor(PDFHandwritingExtractor):
    def __init__(self):
        super().__init__()  # Call parent class constructor
        self.recognizer = AnswerKeyDiagramRecognizer()

    async def extract_text_from_images(self, image_paths):
        """Extract text from images asynchronously using IBM Watson."""
        extracted_texts = await asyncio.gather(
            *(self._extract_single_image_text(i, image_path) for i, image_path in enumerate(image_paths, start=1))
        )
        return extracted_texts

    async def _extract_single_image_text(self, i, image_path):
        """Extract text from a single image."""
        try:
            text = await self.recognizer.process_image(image_path)  # Pass file path instead of image object
            logger.info(f'Extracted text from page {i}')
            
            # Apply thorough cleaning to ensure no metadata remains
            if text:
                # The cleaning is now done in the process_image method
                pass
                
            return (i, text or "[No Text Extracted]")
        except Exception as e:
            logger.error(f"Error processing image {image_path}: {str(e)}")
            return (i, "[Error in Extraction]")
    
    def _clean_html_tags(self, text):
        """Clean up HTML-like tags that might cause issues with PDF creation."""
        import re
        # Replace HTML-like tags with plain text equivalents
        text = re.sub(r'<\s*SUB\s*>', '_', text, flags=re.IGNORECASE)
        text = re.sub(r'<\s*/\s*SUB\s*>', '', text, flags=re.IGNORECASE)
        text = re.sub(r'<\s*SUP\s*>', '^', text, flags=re.IGNORECASE)
        text = re.sub(r'<\s*/\s*SUP\s*>', '', text, flags=re.IGNORECASE)
        # Remove any other HTML-like tags that might cause issues
        text = re.sub(r'<[^>]*>', '', text)
        return text


class AnswerKeyDiagramRecognizer:
    def __init__(self):
        self.extraction_prompt = """
You are an expert in document analysis. Extract ONLY the exact text content from this document.

IMPORTANT: Your response should contain ONLY the extracted text, nothing else.

DO NOT include:
- Any part of these instructions
- Explanatory text like "Here is what I found" or "Extracted text:"
- Descriptions about the document
- Markdown formatting like ## or **
- Any commentary about the content

If diagrams are present, simply describe them briefly between [DIAGRAM] tags.

Extract the text exactly as it appears, maintaining its original structure.
"""

    def encode_image(self, image_path):
        """Encode image to base64."""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    async def process_image(self, image_path):
        try:
            image_base64 = self.encode_image(image_path)
            messages = [{
                "role": "user",
                "content": [
                    {"type": "text", "text": self.extraction_prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                ]
            }]
            response = await asyncio.to_thread(model.chat, messages=messages)
            text = response["choices"][0]["message"]["content"] if response else None
            
            # Post-process to remove any prompt-like text that might have been included
            if text:
                text = self._clean_prompt_artifacts(text)
            
            return text
        except Exception as e:
            logger.error(f"Answer key processing error: {str(e)}")
            return None
            
    def _clean_prompt_artifacts(self, text):
        """Remove any prompt-like artifacts from the extracted text."""
        # Remove common phrases that might be included
        phrases_to_remove = [
            "Here is the extracted text:",
            "Extracted text:",
            "Here's what I found:",
            "Here is what we found:",
            "We were unable to identify a diagram in this image.",
            "**Diagram Identification and Description:**",
            "There are no diagrams or images in this document.",
            "## Page",
        ]
        
        for phrase in phrases_to_remove:
            text = text.replace(phrase, "")
        
        # Remove instruction-like content
        lines = text.split('\n')
        filtered_lines = []
        skip_section = False
        
        for line in lines:
            # Skip lines that look like instructions
            if any(marker in line.lower() for marker in ["extract all text", "for diagrams", "formatting rules"]):
                skip_section = True
                continue
            
            if skip_section and line.strip() == "":
                skip_section = False
                continue
                
            if not skip_section:
                filtered_lines.append(line)
        
        return '\n'.join(filtered_lines).strip()

import os
import convert2json  # Ensure this module has process_parquet


def process_parquet_directory(input_dir: str, output_dir: str):
    """
    Process all parquet files in a directory and convert them to JSON.
    
    Args:
        input_dir: Directory containing parquet files
        output_dir: Directory to save JSON files
    """
    all_data = []

    if not os.path.exists(input_dir):
        print(f"Error: Directory {input_dir} does not exist.")
        return

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    for file in os.listdir(input_dir):
        if file.endswith(".parquet"):
            file_path = os.path.join(input_dir, file)
            print(f"Processing Parquet file: {file_path}")
            
            # Create output path for this specific file
            base_name = os.path.splitext(os.path.basename(file))[0]
            file_output = os.path.join(output_dir, f"{base_name}.json")
                
            try:
                # Check if file already exists
                if os.path.exists(file_output):
                    print(f"File {file_output} already exists. Skipping.")
                    continue
                    
                extracted_data = convert2json.process_file(file_path, file_output)
                if extracted_data:
                    all_data.extend(extracted_data)
                    print(f"Processed {file_path} -> {file_output}")
            except Exception as e:
                print(f"Error processing {file_path}: {str(e)}")

    # Save combined data if needed
    if all_data and len(all_data) > 0:
        combined_output = os.path.join(output_dir, "combined_data.json")
        with open(combined_output, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, indent=2, ensure_ascii=False)





async def main():
    # Define directories
    handwritten_dir = "/Users/ayrafraihan/Desktop/pythonProject1/finalflow/input_folder/AnswerSheet/Handwritten"
    extracted_text_dir = "/Users/ayrafraihan/Desktop/pythonProject1/finalflow/input_folder/AnswerSheet/clean_pdf"
    temp_image_dir = "/Users/ayrafraihan/Desktop/pythonProject1/finalflow/input_folder/AnswerSheet/tempimg"
    input_folder_parquet_answersheet = "/Users/ayrafraihan/Desktop/pythonProject1/finalflow/input_folder/AnswerSheet/clean_pdf"
    output_folder_parquet_answersheet = "/Users/ayrafraihan/Desktop/pythonProject1/finalflow/input_folder/AnswerSheet/parquet"
    input_folder_parquet_answerkey = "/Users/ayrafraihan/Desktop/pythonProject1/finalflow/input_folder/AnswerKey/clean_pdf"
    output_folder_parquet_answerkey= "/Users/ayrafraihan/Desktop/pythonProject1/finalflow/input_folder/AnswerKey/parquet"
    output_json_answerkey="/Users/ayrafraihan/Desktop/pythonProject1/finalflow/input_folder/AnswerKey/Json_with_answers/"
    output_json_answersheet="/Users/ayrafraihan/Desktop/pythonProject1/finalflow/input_folder/AnswerSheet/Json_with_answers/"
    result= "/Users/ayrafraihan/Desktop/pythonProject1/finalflow/results"

    # Process Answer Sheet
    extractor = PDFHandwritingExtractor()
    
    # Check if handwritten directory exists
    if not os.path.exists(handwritten_dir):
        logger.error(f"Handwritten directory not found: {handwritten_dir}")
        return
    
    # Find all PDF files in the directory
    pdf_files = [f for f in os.listdir(handwritten_dir) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        logger.error(f"No PDF files found in directory: {handwritten_dir}")
        return
    
    # Create output directory for extracted text
    os.makedirs(extracted_text_dir, exist_ok=True)
    
    # Process each PDF file
    for pdf_file in pdf_files:
        input_pdf = os.path.join(handwritten_dir, pdf_file)
        logger.info(f"Processing answer sheet PDF: {input_pdf}")
        
        # Define output path for this PDF
        output_filename = f"extracted_{os.path.splitext(pdf_file)[0]}.pdf"
        extracted_text_pdf = os.path.join(extracted_text_dir, output_filename)
        
        # Convert PDF to images
        logger.info(f"Converting PDF to images: {input_pdf}")
        image_paths = await extractor.convert_pdf_to_images(input_pdf, temp_image_dir)

        if not image_paths:
            logger.error(f"No images were created from the PDF: {pdf_file}")
            continue

        # Extract text from images
        logger.info(f"Extracting text from images using LLama 3.2 vision model for {pdf_file}...")
        extracted_texts = await extractor.extract_text_from_images(image_paths)

        if not extracted_texts:
            logger.error(f"No text was extracted from the images for {pdf_file}")
            continue

        # Create output PDF with extracted text
        logger.info(f"Creating output PDF with extracted text: {extracted_text_pdf}")
        success = await extractor.create_text_pdf(extracted_texts, extracted_text_pdf)

        if not success:
            logger.error(f"Failed to create extracted text PDF for {pdf_file}")
            continue
        
        logger.info(f"Successfully processed answer sheet: {pdf_file}")
    
    # Check if any files were processed
    processed_files = [f for f in os.listdir(extracted_text_dir) if f.lower().endswith('.pdf')]
    if not processed_files:
        logger.error("No answer sheet PDFs were successfully processed")
        return
    
    logger.info(f"Successfully saved processed answer sheets to {extracted_text_dir}")
    
    # In the main function, update the answer key processing section:
    
    # Process Answer Key through VLM pipeline
    try:
        logger.info("Processing Answer Key with diagram understanding...")
        answerkey_extractor = AnswerKeyExtractor()
        
        # Original answer key directory
        input_answerkey_dir = "/Users/ayrafraihan/Desktop/pythonProject1/finalflow/input_folder/AnswerKey/original"
        
        # Check if directory exists
        if not os.path.exists(input_answerkey_dir):
            logger.error(f"Answer key directory not found: {input_answerkey_dir}")
            return
        
        # Find all PDF files in the directory
        pdf_files = [f for f in os.listdir(input_answerkey_dir) if f.lower().endswith('.pdf')]
        
        if not pdf_files:
            logger.error(f"No PDF files found in directory: {input_answerkey_dir}")
            return
        
        # Create temp directory for answer key images
        answerkey_temp_dir = "/Users/ayrafraihan/Desktop/pythonProject1/finalflow/input_folder/AnswerKey/tempimg"
        os.makedirs(answerkey_temp_dir, exist_ok=True)
        
        # Process each PDF file
        for pdf_file in pdf_files:
            input_answerkey_pdf = os.path.join(input_answerkey_dir, pdf_file)
            logger.info(f"Processing answer key PDF: {input_answerkey_pdf}")
            
            # Process answer key PDF
            logger.info(f"Converting answer key PDF to images: {input_answerkey_pdf}")
            answerkey_images = await answerkey_extractor.convert_pdf_to_images(
                input_answerkey_pdf,
                answerkey_temp_dir
            )
            
            if not answerkey_images:
                logger.error(f"No images were created from the answer key PDF: {pdf_file}")
                continue
            
            # Extract text with diagrams
            logger.info(f"Extracting text and diagrams from answer key images for {pdf_file}...")
            answerkey_texts = await answerkey_extractor.extract_text_from_images(answerkey_images)
            
            if not answerkey_texts:
                logger.error(f"No text was extracted from the answer key images for {pdf_file}")
                continue
            
            # Save processed PDF to clean_pdf directory
            os.makedirs(input_folder_parquet_answerkey, exist_ok=True)
            output_filename = f"processed_{os.path.splitext(pdf_file)[0]}.pdf"
            answerkey_clean_pdf = os.path.join(input_folder_parquet_answerkey, output_filename)
            
            logger.info(f"Creating answer key PDF with extracted text and diagrams: {answerkey_clean_pdf}")
            success = await answerkey_extractor.create_text_pdf(answerkey_texts, answerkey_clean_pdf)
            
            if not success:
                logger.error(f"Failed to create answer key PDF for {pdf_file}")
                continue
            
            logger.info(f"Successfully processed answer key: {pdf_file}")
        
        # Check if any files were processed
        processed_files = [f for f in os.listdir(input_folder_parquet_answerkey) if f.lower().endswith('.pdf')]
        if not processed_files:
            logger.error("No answer key PDFs were successfully processed")
            return
        
        logger.info(f"Successfully saved processed answer keys to {input_folder_parquet_answerkey}")
    except Exception as e:
        logger.error(f"Error processing answer key: {e}")
        import traceback
        logger.error(traceback.format_exc())

    # Convert PDFs to Parquet
    try:
        logger.info(f"Converting answer sheet to Parquet...")
        convert_pdf_to_parquet(input_folder_parquet_answersheet, output_folder_parquet_answersheet)
        logger.info(f"Successfully converted answer sheet to Parquet")
        
        logger.info(f"Converting processed answer key to Parquet...")
        convert_pdf_to_parquet(input_folder_parquet_answerkey, output_folder_parquet_answerkey)
        logger.info(f"Successfully converted answer key to Parquet")
    except Exception as e:
        logger.error(f"Error converting PDFs to Parquet: {e}")
        return

    # Convert Parquet to JSON
    try:
        logger.info("Converting answer sheet parquet to JSON...")
        process_parquet_directory(output_folder_parquet_answersheet, output_json_answersheet)
        logger.info("Successfully converted answer sheet parquet to JSON")
        
        logger.info("Converting answer key parquet to JSON...")
        process_parquet_directory(output_folder_parquet_answerkey, output_json_answerkey)
        logger.info("Successfully converted answer key parquet to JSON")
    except Exception as e:
        logger.error(f"Error converting parquet to JSON: {str(e)}")
        return

    # In the main function, update these lines:
    # Compare JSONs
    try:
        logger.info("Comparing JSONs with LLM evaluation...")
        # Ensure the result directory exists
        os.makedirs(result, exist_ok=True)
        
        # Print debug info
        print(f"Answer Key JSON directory: {output_json_answerkey}")
        print(f"Answer Sheet JSON directory: {output_json_answersheet}")
        print(f"Results directory: {result}")
        
        # Check if JSON files exist
        ak_files = os.listdir(output_json_answerkey)
        as_files = os.listdir(output_json_answersheet)
        
        print(f"Answer Key JSON files: {ak_files}")
        print(f"Answer Sheet JSON files: {as_files}")
        
        # Call the comparison function
        wat.compare_jsons(output_json_answersheet, output_json_answerkey, result)
        
        # Verify results were saved
        result_files = os.listdir(result)
        if result_files:
            print(f"Results saved: {result_files}")
        else:
            print(f"Warning: No result files were created in {result}")
    except Exception as e:
        logger.error(f"Error comparing JSONs: {e}")
        import traceback
        logger.error(traceback.format_exc())



if __name__ == "__main__":
    asyncio.run(main())


# Move the AnswerKeyDiagramRecognizer and AnswerKeyExtractor classes before the main function
# and after the PDFHandwritingExtractor class
