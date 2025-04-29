import logging
from pdf2parq import convert_pdf_to_parquet  # Import your function
import ssl
import urllib.request

# Disable SSL certificate verification
ssl._create_default_https_context = ssl._create_unverified_context

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_pdf_to_parquet(input_pdf, output_folder):
    """
    Calls the existing pdf2parquet function to process the PDF and convert it to Parquet.
    """
    try:
        logger.info(f"Processing PDF: {input_pdf}")

        # Call the existing function from pdf2parq.py
        convert_pdf_to_parquet(input_pdf, output_folder)

        logger.info(f"Successfully converted {input_pdf} to Parquet at {output_folder}")

    except Exception as e:
        logger.error(f"Error processing PDF: {e}")

# Example usage
if __name__ == "__main__":
    input_pdf_path = "/Users/tanishta/Desktop/ibm_dpk-proj/finalflow/output_folder/extracted_text.pdf"
    output_parquet_folder = "/Users/tanishta/Desktop/ibm_dpk-proj/finalflow/out_parquet"

process_pdf_to_parquet(input_pdf_path, output_parquet_folder)
