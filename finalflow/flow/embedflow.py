import json
import torch
from transformers import AutoTokenizer, AutoModel
import os

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
    if not text:
        return []
    
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    
    with torch.no_grad():
        outputs = model(**inputs)
    
    embedding = outputs.last_hidden_state.mean(dim=1)
    return embedding.squeeze().tolist()

def process_json_to_embeddings(input_json, output_json):
    """
    Reads a JSON file, extracts 'contents', converts them into embeddings, and saves them.
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_json), exist_ok=True)
        
        # Load the model
        tokenizer, model = load_embedding_model()
        
        # Load JSON file
        with open(input_json, "r") as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            return
        
        # Generate embeddings
        embeddings = []
        for i, entry in enumerate(data, 1):
            content = entry.get("contents", "").strip()
            question_number = entry.get("question_number", str(i))
            
            if content:
                vector = text_to_embedding(content, tokenizer, model)
                embedding_entry = {
                    "question_number": question_number,
                    "contents": content,
                    "embedding": vector
                }
                embeddings.append(embedding_entry)
        
        # Save embeddings
        with open(output_json, "w") as f:
            json.dump(embeddings, f)
            
    except Exception:
        pass

if __name__ == "__main__":
    input_json_path_1 = "/Users/tanishta/Desktop/GitHub/ibm/finalflow/results/output1.json"
    input_json_path_2 = "/Users/tanishta/Desktop/GitHub/ibm/finalflow/results/output2.json"
    
    output_json_path_1 = "/Users/tanishta/Desktop/GitHub/ibm/finalflow/results/output1_embeddings.json"
    output_json_path_2 = "/Users/tanishta/Desktop/GitHub/ibm/finalflow/results/output2_embeddings.json"
    
    process_json_to_embeddings(input_json_path_1, output_json_path_1)
    process_json_to_embeddings(input_json_path_2, output_json_path_2)