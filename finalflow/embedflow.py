import json
import torch
from transformers import AutoTokenizer, AutoModel

def load_embedding_model():
    """
    Loads the IBM Granite embedding model.
    """
    model_name = "ibm-granite/granite-embedding-125m-english"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)
    return tokenizer, model

def text_to_embedding(text, tokenizer, model):
    """
    Converts a given text into an embedding vector using the IBM Granite model.
    """
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)

    with torch.no_grad():
        outputs = model(**inputs)

    # Use mean pooling of embeddings
    embedding = outputs.last_hidden_state.mean(dim=1)
    return embedding.squeeze().tolist()  # Convert to list for JSON serialization

def process_json_to_embeddings(input_json, output_json):
    """
    Reads a JSON file, extracts 'contents', converts them into embeddings, and saves them.
    """
    # Load the IBM Granite model
    tokenizer, model = load_embedding_model()

    # Load JSON file
    try:
        with open(input_json, "r") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading JSON file {input_json}: {e}")
        return

    # Ensure data is a list of entries
    if not isinstance(data, list):
        print("Error: JSON data should be a list of entries.")
        return

    # Generate embeddings
    embeddings = []
    for entry in data:
        # Extract the 'contents' key
        content = entry.get("contents", "")
        if content:
            vector = text_to_embedding(content, tokenizer, model)
            embeddings.append({"contents": vector})  # Save embedding vector
        else:
            print(f"Warning: 'contents' key missing or empty in entry: {entry}")

    # Save embeddings to a new JSON file
    try:
        with open(output_json, "w") as f:
            json.dump(embeddings, f, indent=4)
        print(f"Embeddings saved to {output_json}")
    except Exception as e:
        print(f"Error saving JSON file {output_json}: {e}")
        
if __name__ == "__main__":
    # Input JSON files containing 'contents'
    input_json_path_1 = "output1.json"
    input_json_path_2 = "output2.json"

    # Output JSON files for embeddings
    output_json_path_1 = "output1_embeddings.json"
    output_json_path_2 = "output2_embeddings.json"

    # Process both JSON files and generate embeddings
    process_json_to_embeddings(input_json_path_1, output_json_path_1)
    process_json_to_embeddings(input_json_path_2, output_json_path_2)