import os
from pdf2image import convert_from_path
from PIL import Image

# Define paths
input_pdf_path = '/Users/tanishta/Desktop/GitHub/ibm_dpk-project/Dataprep/preprep/SE_NOTES.pdf'
image_output_dir = '/Users/tanishta/Desktop/GitHub/ibm_dpk-project/Dataprep/preprep/images'

# Ensure directories exist
os.makedirs(image_output_dir, exist_ok=True)

# Step 1: Convert PDF pages to images
images = convert_from_path(input_pdf_path, fmt='jpeg')
image_paths = []
for i, image in enumerate(images):
    image_path = os.path.join(image_output_dir, f'page_{i + 1}.jpeg')
    image.save(image_path, 'JPEG')
    image_paths.append(image_path)

print(f"Images saved to {image_output_dir}")