from dotenv import load_dotenv
import os
import google.generativeai as genai
from PIL import Image
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
genai.configure(api_key="AIzaSyDkXnTIKq6WNJscymGaWr9avzuD5p22DxA")

class HandwritingRecognizer:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.recognition_prompt = """
        You are an expert in handwriting recognition and text extraction.
        Please analyze the uploaded image and:
        1. Extract all handwritten text you can find
        2. Organize it in a clear, readable format
        3. If there are multiple answers or sections, separate them clearly
        4. Change any text that is unclear or ambiguous according to the context
        5. Maintain the original structure of the handwritten content if possible

        Please provide the extracted handwritten text in a clean, structured format.
        """

    def process_image(self, image):
        try:
            # Convert image to bytes
            import io
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()

            image_parts = [
                {
                    "mime_type": "image/png",
                    "data": img_byte_arr
                }
            ]

            response = self.model.generate_content([self.recognition_prompt, image_parts[0]])
            return response.text

        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            return None

if __name__ == "__main__":
    recognizer = HandwritingRecognizer()

    image_path = "/Users/tanishta/Desktop/GitHub/ibm_dpk-proj/me/answer.jpeg"

    try:
        image = Image.open(image_path)

        extracted_text = recognizer.process_image(image)

        if extracted_text:
            print("Handwritten text extraction completed successfully!")
            print("\nExtracted Handwritten Text:")
            print(extracted_text)
        else:
            print("Failed to extract handwritten text from the image.")

    except Exception as e:
        logger.error(f"Error loading or processing the image: {str(e)}")