import os
import json
import numpy as np
from langchain_community.embeddings import OpenAIEmbeddings
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv

load_dotenv()


def compare_jsons(folder1, folder2, output_folder):
    """Compares JSON answer files in two folders and stores similarity scores."""

    files1 = {f for f in os.listdir(folder1) if f.endswith(".json")}
    files2 = {f for f in os.listdir(folder2) if f.endswith(".json")}

    common_files = files1.intersection(files2)
    if not common_files:
        print("No matching JSON files found between the two folders.")
        return

    os.makedirs(output_folder, exist_ok=True)

    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set. Make sure you have added it to your .env file.")

    embedding_model = OpenAIEmbeddings(openai_api_key=openai_api_key)

    for filename in common_files:
        json_path1 = os.path.join(folder1, filename)
        json_path2 = os.path.join(folder2, filename)

        with open(json_path1, "r", encoding="utf-8") as f1:
            data1 = json.load(f1)
        with open(json_path2, "r", encoding="utf-8") as f2:
            data2 = json.load(f2)

        if not data1 or not data2:
            print(f"Skipping {filename} due to empty JSON.")
            continue

        answers_dict1 = data1[0]["answers"] if data1 else {}
        answers_dict2 = data2[0]["answers"] if data2 else {}

        similarity_results = []
        for key in set(answers_dict1.keys()).intersection(answers_dict2.keys()):
            try:
                embedding1 = embedding_model.embed_documents([answers_dict1[key]])[0]
                embedding2 = embedding_model.embed_documents([answers_dict2[key]])[0]

                similarity_score = cosine_similarity(
                    np.array(embedding1).reshape(1, -1),
                    np.array(embedding2).reshape(1, -1)
                )[0][0]

                similarity_results.append({
                    "question_number": key,
                    "document_1": answers_dict1[key],
                    "document_2": answers_dict2[key],
                    "similarity_score": similarity_score
                })
            except Exception as e:
                print(f"Error processing question {key}: {e}")

        output_path = os.path.join(output_folder, f"similarity_{filename}")
        with open(output_path, "w", encoding="utf-8") as outf:
            json.dump(similarity_results, outf, indent=4)

        print(f"Similarity scores saved in {output_path}")
