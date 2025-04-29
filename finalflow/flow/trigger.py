import os
import io
import logging
import asyncio
from dotenv import load_dotenv
from pdf2image import convert_from_path
from PIL import Image
import google.generativeai as genai
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from pdf2parq import convert_pdf_to_parquet
import convert2json
import json
import wat

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

class HandwritingRecognizer:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.recognition_prompt = """
        You are an expert in handwriting recognition and text extraction.
        Extract all readable handwritten text and maintain the original structure.
        Clearly separate different sections, paragraphs, or responses.
        Also do Ignore things like bold and italic text and write them as normal text
        """

    async def process_image(self, image):
        """Send image to Gemini API for handwriting recognition asynchronously."""
        try:
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()

            image_parts = [{"mime_type": "image/png", "data": img_byte_arr}]

            response = await asyncio.to_thread(self.model.generate_content, [self.recognition_prompt, image_parts[0]])
            return response.text if response else None

        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            return None

class PDFHandwritingExtractor:
    def __init__(self):
        self.recognizer = HandwritingRecognizer()

    async def convert_pdf_to_images(self, pdf_path, output_dir, dpi=300):
        """Convert PDF pages to images asynchronously."""
        try:
            os.makedirs(output_dir, exist_ok=True)
            images = await asyncio.to_thread(convert_from_path, pdf_path, dpi=dpi)

            image_paths = []
            for i, image in enumerate(images):
                output_path = os.path.join(output_dir, f'page_{i+1}.png')
                await asyncio.to_thread(image.save, output_path, 'PNG')
                image_paths.append(output_path)
                logger.info(f'Saved page {i+1} as {output_path}')

            return image_paths
        except Exception as e:
            logger.error(f"Error converting PDF to images: {str(e)}")
            return []

    async def extract_text_from_images(self, image_paths):
        """Extract text from images asynchronously using Gemini API."""
        extracted_texts = await asyncio.gather(
            *(self._extract_single_image_text(i, image_path) for i, image_path in enumerate(image_paths, start=1))
        )
        return extracted_texts

    async def _extract_single_image_text(self, i, image_path):
        """Extract text from a single image."""
        try:
            image = await asyncio.to_thread(Image.open, image_path)
            text = await self.recognizer.process_image(image)
            logger.info(f'Extracted text from page {i}')
            return (i, text or "[No Text Extracted]")
        except Exception as e:
            logger.error(f"Error processing image {image_path}: {str(e)}")
            return (i, "[Error in Extraction]")

    async def create_text_pdf(self, extracted_texts, output_pdf_path):
        """Create a structured PDF with extracted text asynchronously."""
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


import os
import convert2json  # Ensure this module has process_parquet


def process_parquet_directory(input_dir: str, output_json: str):

    all_data = []

    if not os.path.exists(input_dir):
        print(f"Error: Directory {input_dir} does not exist.")
        return

    for file in os.listdir(input_dir):
        if file.endswith(".parquet"):
            file_path = os.path.join(input_dir, file)
            print(f"Processing Parquet file: {file_path}")
            extracted_data = convert2json.process_file(file_path, output_json)

            if extracted_data:
                all_data.extend(extracted_data)

    if all_data:
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, indent=2, ensure_ascii=False)





async def main():
    input_pdf = "/Users/tanishta/Desktop/ibm_dpk-project/finalflow/input_folder/AnswerSheet/Handwritten/mew.pdf"  # Input PDF
    extracted_text_pdf = "/Users/tanishta/Desktop/ibm_dpk-project/finalflow/input_folder/AnswerSheet/clean_pdf/extracted_text.pdf"
    temp_image_dir = "/Users/tanishta/Desktop/ibm_dpk-project/finalflow/input_folder/AnswerSheet/tempimg"
    input_folder_parquet_answersheet = "/Users/tanishta/Desktop/ibm_dpk-project/finalflow/input_folder/AnswerSheet/clean_pdf"
    output_folder_parquet_answersheet = "/Users/tanishta/Desktop/ibm_dpk-project/finalflow/input_folder/AnswerSheet/parquet"
    input_folder_parquet_answerkey = "/Users/tanishta/Desktop/ibm_dpk-project/finalflow/input_folder/AnswerKey/clean_pdf"
    output_folder_parquet_answerkey= "/Users/tanishta/Desktop/ibm_dpk-project/finalflow/input_folder/AnswerKey/parquet"
    output_json_answerkey="/Users/tanishta/Desktop/ibm_dpk-project/finalflow/input_folder/AnswerKey/Json_with_answers/"
    output_json_answersheet="/Users/tanishta/Desktop/ibm_dpk-project/finalflow/input_folder/AnswerSheet/Json_with_answers/"
    result= "/Users/tanishta/Desktop/ibm_dpk-project/finalflow/results"

    extractor = PDFHandwritingExtractor()

    # Convert PDF to images
    logger.info("Converting PDF to images...")
    image_paths = await extractor.convert_pdf_to_images(input_pdf, temp_image_dir)

    if not image_paths:
        logger.error("No images were created from the PDF")
        return

    # Extract text from images
    logger.info("Extracting text from images using Gemini...")
    extracted_texts = await extractor.extract_text_from_images(image_paths)

    if not extracted_texts:
        logger.error("No text was extracted from the images")
        return

    # Create output PDF with extracted text
    logger.info("Creating output PDF...")

    # Continue with the rest of your code
    success = await extractor.create_text_pdf(extracted_texts, extracted_text_pdf)

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



if __name__ == "__main__":
    asyncio.run(main())