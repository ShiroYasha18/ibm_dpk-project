import sys
import os
import io
import json
import base64
import asyncio
import logging

from dotenv import load_dotenv
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from pdf2image import convert_from_path
import fitz

import convert2json
import wat
from pdf2parq import convert_pdf_to_parquet
from ibm_watsonx_ai import APIClient, Credentials
from ibm_watsonx_ai.foundation_models import ModelInference

sys.path.append(os.path.abspath('/Users/tanishta/Desktop/ibm_dpk-project'))
sys.path.append(os.path.abspath('/Users/tanishta/Desktop/ibm_dpk-project/pdf2parquet'))

data_processing_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data_processing'))
sys.path.append(data_processing_path)
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

API_KEY = os.getenv("IBM_API_KEY")
SERVICE_URL = os.getenv("IBM_SERVICE_URL")
PROJECT_ID = os.getenv("IBM_PROJECT_ID")

# Setup IBM Watson Client
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
        self.extraction_prompt = """
You are an expert in handwriting recognition and text extraction.
Your task is to extract **only the text** exactly as it appears in the image.
Do not add any descriptions, explanations, or formatting notes.
Strictly maintain:
- Original structure (paragraphs, sections, equations).
- Subscripts, superscripts, and mathematical symbols as they appear.
- If any part is scribbled or unreadable, simply ignore it.
Only return the extracted text, formatted exactly as it appears and please do maintain the structure.
        """

    def encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    async def process_image(self, image_path):
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
        self.recognizer = HandwritingRecognizer()

    def convert_pdf_to_images(self, pdf_path, output_dir):
        try:
            os.makedirs(output_dir, exist_ok=True)
            doc = fitz.open(pdf_path)
            image_paths = []

            logger.info(f"Processing PDF: {pdf_path} ({len(doc)} pages)")

            if len(doc) == 0:
                logger.error(f"No pages found in PDF: {pdf_path}")
                return []

            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                pix = page.get_pixmap(matrix=fitz.Matrix(150 / 72, 150 / 72))
                image_path = os.path.join(output_dir, f'page_{page_num + 1}.png')
                pix.save(image_path)
                image_paths.append(image_path)
                logger.info(f"Saved page {page_num + 1} as {image_path}")

            return image_paths
        except Exception as e:
            logger.error(f"Error converting PDF to images: {str(e)}")
            return []

    async def extract_text_from_images(self, image_paths):
        extracted_texts = await asyncio.gather(
            *(self._extract_single_image_text(i, path) for i, path in enumerate(image_paths, start=1))
        )
        return extracted_texts

    async def _extract_single_image_text(self, i, image_path):
        try:
            text = await self.recognizer.process_image(image_path)
            logger.info(f'Extracted text from page {i}')
            return (i, text or "[No Text Extracted]")
        except Exception as e:
            logger.error(f"Error processing image {image_path}: {str(e)}")
            return (i, "[Error in Extraction]")

    async def create_text_pdf(self, extracted_texts, output_pdf_path):
        try:
            os.makedirs(os.path.dirname(output_pdf_path), exist_ok=True)

            doc = SimpleDocTemplate(output_pdf_path, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []

            text_style = ParagraphStyle(
                'CustomStyle',
                parent=styles['Normal'],
                fontSize=12,
                leading=14,
                spaceBefore=12,
                spaceAfter=12
            )

            for page_num, text in extracted_texts:
                story.append(Paragraph(f"<b>Page {page_num}</b>", styles['Heading2']))
                for para in text.split('\n'):
                    if para.strip():
                        story.append(Paragraph(para, text_style))

            await asyncio.to_thread(doc.build, story)
            logger.info(f'Successfully created output PDF: {output_pdf_path}')
            return True
        except Exception as e:
            logger.error(f"Error creating output PDF: {str(e)}")
            return False

def process_parquet_directory(input_dir: str, output_json: str):
    all_data = []

    if not os.path.exists(input_dir):
        logger.error(f"Directory {input_dir} does not exist.")
        return

    for file in os.listdir(input_dir):
        if file.endswith(".parquet"):
            file_path = os.path.join(input_dir, file)
            logger.info(f"Processing Parquet file: {file_path}")
            extracted_data = convert2json.process_file(file_path, output_json)
            if extracted_data:
                all_data.extend(extracted_data)

    if all_data:
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, indent=2, ensure_ascii=False)


def get_final_results(file_path, thresholds, difficulty_level, total_marks):
    difficulty_map = {
        "easy": "full_marks",
        "medium": "high_marks",
        "hard": "low_marks"
    }

    if difficulty_level.lower() not in difficulty_map:
        raise ValueError(f"Invalid difficulty level: {difficulty_level}. Expected 'easy', 'medium', or 'hard'.")

    mapped_key = difficulty_map[difficulty_level.lower()]
    level_thresholds = thresholds[mapped_key]

async def main(difficulty, total_marks, thresholds):
    input_pdf = "/Users/tanishta/Desktop/ibm_dpk-project/finalflow/input_folder/AnswerSheet/Handwritten/mew.pdf"
    extracted_text_pdf = "/Users/tanishta/Desktop/ibm_dpk-project/finalflow/input_folder/AnswerSheet/clean_pdf/extracted_text.pdf"
    input_pdf_answerkey = "/Users/tanishta/Desktop/ibm_dpk-project/finalflow/input_folder/AnswerKey/clean_pdf/pd.pdf"
    temp_image_dir = "/Users/tanishta/Desktop/ibm_dpk-project/finalflow/input_folder/AnswerSheet/tempimg"
    input_folder_parquet_answersheet = "/Users/tanishta/Desktop/ibm_dpk-project/finalflow/input_folder/AnswerSheet/clean_pdf"
    output_folder_parquet_answersheet = "/Users/tanishta/Desktop/ibm_dpk-project/finalflow/input_folder/AnswerSheet/parquet"
    input_folder_parquet_answerkey = "/Users/tanishta/Desktop/ibm_dpk-project/finalflow/input_folder/AnswerKey/clean_pdf"
    output_folder_parquet_answerkey= "/Users/tanishta/Desktop/ibm_dpk-project/finalflow/input_folder/AnswerKey/parquet"
    output_json_answerkey="/Users/tanishta/Desktop/ibm_dpk-project/finalflow/input_folder/AnswerKey/Json_with_answers/"
    output_json_answersheet="/Users/tanishta/Desktop/ibm_dpk-project/finalflow/input_folder/AnswerSheet/Json_with_answers/"
    result= "/Users/tanishta/Desktop/ibm_dpk-project/finalflow/results"

    print("PDF conversion completed!")
    extractor = PDFHandwritingExtractor()

    # Convert PDF to images
    logger.info("Converting PDF to images...")
    image_paths_answer_sheet = extractor.convert_pdf_to_images(input_pdf, temp_image_dir)
    image_paths_answer_key = extractor.convert_pdf_to_images(input_pdf_answerkey, temp_image_dir)
    image_paths = image_paths_answer_sheet + image_paths_answer_key

    if not image_paths:
        logger.error("No images were created from the PDF")
        return

    # Extract text from images
    logger.info("Extracting text from images using LLama 3.2 vision model from WatsonX by IBM...")
    extracted_texts = await extractor.extract_text_from_images(image_paths)

    if not extracted_texts:
        logger.error("No text was extracted from the images")
        return

    # Create output PDF with extracted text
    logger.info("Creating output PDF...")

    # Continue with the rest of your code
    success = extractor.create_text_pdf

    if not success:
        logger.error("Failed to create extracted text PDF")
        return

    try:
        logger.info(f"Processing PDF: {input_pdf}")
        convert_pdf_to_parquet(input_folder_parquet_answersheet, output_folder_parquet_answersheet)
        logger.info(f"Successfully converted answer sheet {input_folder_parquet_answersheet} to Parquet at {output_folder_parquet_answersheet}")

    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
    try:
        logger.info(f"Processing PDF: {input_folder_parquet_answerkey}")
        convert_pdf_to_parquet(input_folder_parquet_answerkey, output_folder_parquet_answerkey)
        logger.info(
            f"Successfully converted answer key {input_folder_parquet_answerkey} to Parquet at {output_folder_parquet_answerkey}")

    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
    # now converting the parquets to jsons for both answersheet and answerkey
    try:
        logger.info("Extracting answers from Answer Key Parquet files and saving to JSON...")
        process_parquet_directory(output_folder_parquet_answerkey, output_json_answerkey)
    except Exception as e:
        logger.error(f"Error extracting answers from Answer Key Parquet: {e}")
    try:
        logger.info("Extracting answers from Answer Sheet Parquet files and saving to JSON...")
        process_parquet_directory(output_folder_parquet_answersheet, output_json_answersheet)
    except Exception as e:
        logger.error(f"Error extracting answers from Answer Sheet Parquet: {e}")

    try:
        logger.info("Comparing Jsons with Cosine Similarity...")
        wat.compare_jsons(output_json_answersheet,output_json_answerkey,result)

    except Exception as e:
        logger.error(f"Error comparing: {e}")

def trigger_grading(difficulty, total_marks, thresholds):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main(difficulty, total_marks, thresholds))

# Example call to trigger_grading with some values
trigger_grading(difficulty="easy", total_marks=100, thresholds=[50, 75])

if __name__ == "__main__":
    asyncio.run(main())