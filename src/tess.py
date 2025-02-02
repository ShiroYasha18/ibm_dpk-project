import pytesseract
from PIL import Image
import os

pytesseract.pytesseract.tesseract_cmd = r'/opt/homebrew/bin/tesseract'  # Update this with the correct path

# Function to extract text and preserve formatting
def extract_text_with_formatting(image_path):
    # Open the image
    img = Image.open(image_path)

    text = pytesseract.image_to_string(img)

    return text

image_path = "/me/meow.jpg"

# Extract text
extracted_text = extract_text_with_formatting(image_path)

# Save the extracted text to a file
output_text_path = "extracted_txt.txt"
with open(output_text_path, "w") as text_file:
    text_file.write(extracted_text)

print(f"Text successfully extracted and saved to {output_text_path}")
