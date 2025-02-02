import json
import torch
from transformers import AutoTokenizer, AutoModel

def load_granite_model():
    """
    Loads the IBM Granite embedding model.
    """
    model_name = "ibm-granite/granite-embedding-125m-english"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)
    return tokenizer, model

def text_to_vector(text, tokenizer, model):
    """
    Converts text to a vector using the Granite embedding model.
    """
    # Tokenize the input text
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)

    # Pass through the model to get embeddings
    with torch.no_grad():
        outputs = model(**inputs)
    
    # Pool embeddings (e.g., mean pooling)
    embeddings = outputs.last_hidden_state.mean(dim=1)
    return embeddings.squeeze().numpy()

def process_students_json(input_file, output_file):
    """
    Reads student answers from a JSON file, converts 'answer' fields to vectors, and saves the embeddings.
    """
    # Load IBM Granite model
    tokenizer, model = load_granite_model()

    # Read students.json
    with open(input_file, "r") as f:
        student_data = json.load(f)
    
    # Convert each 'answer' field to a vector
    embeddings = []
    for entry in student_data:
        question_number = entry["question_number"]
        answer = entry["answer"]

        # Generate embedding for the 'answer'
        vector = text_to_vector(answer, tokenizer, model)

        # Append to embeddings list
        embeddings.append({
            "question_number": question_number,
            "embedding": vector.tolist()  # Convert numpy array to list for JSON serialization
        })

    # Save embeddings to embeddings.json
    with open(output_file, "w") as f:
        json.dump(embeddings, f, indent=4)
    print(f"Embeddings saved to {output_file}")


# processing both the answersheet and the answer key
process_students_json("teachers2.json", "embeddingsteach2.json")
process_students_json("students2.json", "embeddingsstu2.json")

'''' 
                         NOTE
    Need to Edit this as we are hard coding params as of now we need to pass variables in the arguments '''