from pdf2image import convert_from_path
import os
from PIL import Image
from vision_ocr import HandwritingRecognizer
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.units import inch
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PDFHandwritingExtractor:
    def __init__(self):
        self.recognizer = HandwritingRecognizer()

    def convert_pdf_to_images(self, pdf_path, output_dir, dpi=300):
        """Convert PDF pages to images"""
        try:
            os.makedirs(output_dir, exist_ok=True)
            images = convert_from_path(pdf_path, dpi=dpi)

            image_paths = []
            for i, image in enumerate(images):
                output_path = os.path.join(output_dir, f'page_{i + 1}.png')
                image.save(output_path, 'PNG')
                image_paths.append(output_path)
                logger.info(f'Saved page {i + 1} as {output_path}')

            return image_paths
        except Exception as e:
            logger.error(f"Error converting PDF to images: {str(e)}")
            return []

    def extract_text_from_images(self, image_paths):
        """Extract text from images using handwriting recognizer"""
        extracted_texts = []
        for image_path in image_paths:
            try:
                image = Image.open(image_path)
                text = self.recognizer.process_image(image)
                if text:
                    extracted_texts.append(text)
                    logger.info(f'Successfully extracted text from {image_path}')
                else:
                    logger.warning(f'No text extracted from {image_path}')
            except Exception as e:
                logger.error(f"Error processing image {image_path}: {str(e)}")

        return extracted_texts

    def create_text_pdf(self, texts, output_pdf_path):
        """Create a PDF from extracted texts"""
        try:
            os.makedirs(os.path.dirname(output_pdf_path), exist_ok=True)

            doc = SimpleDocTemplate(
                output_pdf_path,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )

            styles = getSampleStyleSheet()
            story = []

            # Create a custom style for the text
            text_style = ParagraphStyle(
                'CustomStyle',
                parent=styles['Normal'],
                fontSize=12,
                leading=14,
                spaceBefore=12,
                spaceAfter=12
            )

            # Add each page's text as a paragraph
            for i, text in enumerate(texts, 1):
                # Add page number
                page_header = Paragraph(
                    f"<b>Page {i}</b>",
                    styles['Heading1']
                )
                story.append(page_header)

                # Add extracted text
                text_paragraphs = text.split('\n')
                for para in text_paragraphs:
                    if para.strip():
                        story.append(Paragraph(para, text_style))

                # Add some space between pages
                story.append(Paragraph("<br/><br/>", styles['Normal']))

            doc.build(story)
            logger.info(f'Created PDF with extracted text: {output_pdf_path}')
            return True

        except Exception as e:
            logger.error(f"Error creating PDF: {str(e)}")
            return False


def main():
    # Configure paths
    input_pdf = "/Users/ayrafraihan/Desktop/pythonProject1/me/meow.pdf"  # Replace with your input PDF path
    temp_image_dir = "/finalflow/tempimg"
    output_pdf = "/Users/ayrafraihan/Desktop/pythonProject1/out/extracted_text.pdf"

    # Create extractor instance
    extractor = PDFHandwritingExtractor()

    try:
        # Step 1: Convert PDF to images
        logger.info("Converting PDF to images...")
        image_paths = extractor.convert_pdf_to_images(input_pdf, temp_image_dir)

        if not image_paths:
            logger.error("No images were created from the PDF")
            return

        # Step 2: Extract text from images
        logger.info("Extracting text from images...")
        extracted_texts = extractor.extract_text_from_images(image_paths)

        if not extracted_texts:
            logger.error("No text was extracted from the images")
            return

        # Step 3: Create output PDF
        logger.info("Creating output PDF...")
        success = extractor.create_text_pdf(extracted_texts, output_pdf)

        if success:
            logger.info("Process completed successfully!")
        else:
            logger.error("Failed to create output PDF")

        # Clean up temporary images
        for image_path in image_paths:
            try:
                os.remove(image_path)
            except Exception as e:
                logger.warning(f"Could not delete temporary file {image_path}: {str(e)}")
        try:
            os.rmdir(temp_image_dir)
        except Exception as e:
            logger.warning(f"Could not delete temporary directory: {str(e)}")

    except Exception as e:
        logger.error(f"An error occurred during processing: {str(e)}")


if __name__ == "__main__":
    main()