import os
import json
import numpy as np
from transformers import AutoTokenizer, AutoModel
from sentence_transformers import SentenceTransformer
import torch
from itertools import product
import re


class SentenceTransformerEmbeddings:
    def __init__(self):
        """Initialize Sentence-Transformer Embedding Model"""
        model_name = "sentence-transformers/all-mpnet-base-v2"

        self.model = SentenceTransformer(model_name)

    def embed_text(self, text):
        """Generate embedding for a single text"""
        return self.model.encode(text, convert_to_numpy=True)


def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split('([0-9]+)', s)]


def compare_jsons(folder1, folder2, output_folder):
    """Compares JSON answer files in two folders regardless of filenames."""

    files1 = [f for f in os.listdir(folder1) if f.endswith(".json")]
    files2 = [f for f in os.listdir(folder2) if f.endswith(".json")]

    os.makedirs(output_folder, exist_ok=True)

    try:
        embedding_model = SentenceTransformerEmbeddings()
    except Exception as e:
        print(f"Error loading Sentence-Transformer model: {e}")
        return

    for file1, file2 in product(files1, files2):
        json_path1 = os.path.join(folder1, file1)
        json_path2 = os.path.join(folder2, file2)

        try:
            with open(json_path1, "r", encoding="utf-8") as f1:
                data1 = json.load(f1)
            with open(json_path2, "r", encoding="utf-8") as f2:
                data2 = json.load(f2)

            if not isinstance(data1, list) or not isinstance(data2, list) or not data1 or not data2:
                print(f"Skipping comparison of {file1} and {file2} - invalid JSON structure")
                continue

            answers_dict1 = data1[0].get("answers", {})
            answers_dict2 = data2[0].get("answers", {})

            similarity_results = []

            common_keys = set(answers_dict1.keys()) & set(answers_dict2.keys())

            if not common_keys:
                print(f"No matching answer indices found between {file1} and {file2}")
                continue

            sorted_keys = sorted(common_keys, key=natural_sort_key)

            for key in sorted_keys:
                answer1 = re.sub(r'[*●]', '', answers_dict1[key].strip())
                answer2 = re.sub(r'[*●]', '', answers_dict2[key].strip())

                if not answer1 or not answer2 or answer1 == "```" or answer2 == "```" or answer1 == "**)" or answer2 == "**)":
                    print(f"Skipping question {key} - empty or invalid answer")
                    continue

                try:
                    embedding1 = embedding_model.embed_text(answer1)
                    embedding2 = embedding_model.embed_text(answer2)

                    similarity_score = float(
                        np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2)))

                    similarity_results.append({
                        "question_number": key,
                        "answer1": answer1,
                        "answer2": answer2,
                        "similarity_score": similarity_score
                    })
                except Exception as e:
                    print(f"Error processing question {key} when comparing {file1} and {file2}: {e}")

            if similarity_results:
                output_filename = f"similarity_{os.path.splitext(file1)[0]}_{os.path.splitext(file2)[0]}.json"
                output_path = os.path.join(output_folder, output_filename)

                similarity_results.sort(key=lambda x: natural_sort_key(x["question_number"]))

                with open(output_path, "w", encoding="utf-8") as outf:
                    json.dump({
                        "file1": {
                            "path": json_path1,
                            "document_id": data1[0].get("document_id", ""),
                            "filename": data1[0].get("filename", "")
                        },
                        "file2": {
                            "path": json_path2,
                            "document_id": data2[0].get("document_id", ""),
                            "filename": data2[0].get("filename", "")
                        },
                        "comparisons": similarity_results
                    }, outf, indent=4, ensure_ascii=False)
                print(f"Saved comparison results to {output_path}")

        except Exception as e:
            print(f"Error comparing {file1} and {file2}: {e}")


if __name__ == "__main__":
    folder1 = "/Users/tanishta/Desktop/ibm_dpk-project/finalflow/input_folder/AnswerKey/Json_with_answers"
    folder2 = "/Users/tanishta/Desktop/ibm_dpk-project/finalflow/input_folder/AnswerSheet/Json_with_answers"
    output_folder = "/Users/tanishta/Desktop/ibm_dpk-project/finalflow/results"

    compare_jsons(folder1, folder2, output_folder)
