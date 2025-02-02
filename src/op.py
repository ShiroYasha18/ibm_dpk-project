from groq import Groq
import base64
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY is not set in the .env file")

def encode_image(image_path):
    """Encode the image into a base64 string."""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    except FileNotFoundError:
        raise ValueError(f"Image file not found at: {image_path}")

image_path = "/me/meow.jpg"

try:
    base64_image = encode_image(image_path)
except Exception as e:
    print(f"Error encoding image: {e}")
    exit()

try:
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
except Exception as e:
    print(f"Error initializing Groq client: {e}")
    exit()

# Send the chat completion request
try:
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "please extract ALL the handwritten text in the image as it is"
                            "please donot write about the layout"
                            "ignore the text charecterstics like bold italics etc"
                            "answers are seprated by black horizontal lines so seprate out the context like that only stating what is the numbering of the answer was given in the text in image"
                            "write the answer only once"

                        ),
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                        },
                    },
                ],
            }
        ],
        model="llama-3.2-11b-vision-preview",
    )

    # Extract and print the response
    print("\nExtracted Answers from the Image:")
    response = chat_completion.choices[0].message.content
    print(response)

except Exception as e:
    print(f"Error during chat completion: {e}")
