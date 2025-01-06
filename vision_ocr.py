from groq import Groq
from PIL import Image
import os
from dotenv import load_dotenv

from op import api_key


def process_image(image_path: str) -> str:
    """Process image and extract handwritten text with specific formatting process only images as of now"""
    try:
        groq_client = Groq(api_key=os.environ.get('GROQ_API_KEY'))

        with Image.open(image_path) as img:
            img_data = img

        prompt = """Please extract ALL the handwritten text in the image exactly as it appears.
        Do not write about the layout.
        Ignore text characteristics like bold, italics, etc.
        Answers are separated by black horizontal lines, so separate the context accordingly, stating what numbering was given to each answer in the image.
        Write each answer only once."""

        response = groq_client.chat.completions.create(
            model="llama-3.2-90b-vision-preview",
            messages=[{
                "role": "user",
                "content": prompt,
                "images": [img_data]
            }]
        )
        return response.choices[0].message.content

    except FileNotFoundError:
        return "Error: Image file not found"
    except Exception as e:
        return f"Error processing image: {str(e)}"


def main():
    load_dotenv()
    image_path = "me/meow.jpg"
    result = process_image(image_path)
    print(result)


if __name__ == "__main__":
    main()