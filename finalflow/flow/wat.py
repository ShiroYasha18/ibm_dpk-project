import os
import json
import numpy as np
from transformers import AutoTokenizer, AutoModel
from sklearn.metrics.pairwise import cosine_similarity
import torch
from itertools import product
import re
from ibm_watsonx_ai import APIClient, Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
from dotenv import load_dotenv

load_dotenv()

class GraniteEmbeddings:
    def __init__(self):
        """Initialize IBM Granite Embedding Model"""
        model_name = "ibm-granite/granite-embedding-125m-english"

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)

    def embed_text(self, text):
        """Generate embedding for a single text"""
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            padding=True,
            truncation=True
        )

        with torch.no_grad():
            outputs = self.model(**inputs)

        return outputs.last_hidden_state[:, 0, :].cpu().numpy()


def natural_sort_key(s):

    return [int(text) if text.isdigit() else text.lower()
            for text in re.split('([0-9]+)', s)]


class AnswerEvaluator:
    def __init__(self):
        self.credentials = Credentials(
            url=os.getenv("IBM_SERVICE_URL"),
            api_key=os.getenv("IBM_API_KEY")
        )
        # Update to use the supported IBM Granite model
        self.model = ModelInference(
            model_id="ibm/granite-3-3-8b-instruct",
            credentials=self.credentials,
            project_id=os.getenv("IBM_PROJECT_ID"),
            params={"decoding_method": "greedy", "max_new_tokens": 500}
        )
        self.prompt_template = """Analyze and score the student's answer against the reference answer. Consider:
- Key concept coverage
- Technical accuracy
- Explanation clarity
- Diagram understanding (if mentioned)

Output JSON format:
{{
  "score": 0-100,
  "breakdown": {{
    "accuracy": 0-50,
    "completeness": 0-30,
    "clarity": 0-20
  }},
  "feedback": "Concise technical feedback"
}}

Reference Answer: {ref_answer}
Student Answer: {student_answer}"""

    def evaluate_pair(self, ref_answer, student_answer):
        try:
            prompt = self.prompt_template.format(
                ref_answer=ref_answer,
                student_answer=student_answer
            )
            
            response = self.model.generate(prompt)
            return json.loads(response["results"][0]["generated_text"])
        except Exception as e:
            print(f"Evaluation error: {str(e)}")
            return {"error": str(e)}


def compare_jsons(folder1, folder2, output_folder):
    """Compares JSON answer files in two folders regardless of filenames."""

    # Ensure output directory exists
    os.makedirs(output_folder, exist_ok=True)
    
    # Get JSON files from folders (only actual files, not directories)
    files1 = [f for f in os.listdir(folder1) if f.endswith(".json") and os.path.isfile(os.path.join(folder1, f))]
    files2 = [f for f in os.listdir(folder2) if f.endswith(".json") and os.path.isfile(os.path.join(folder2, f))]

    print(f"Found {len(files1)} JSON files in {folder1}: {files1}")
    print(f"Found {len(files2)} JSON files in {folder2}: {files2}")

    if not files1 or not files2:
        print(f"No valid JSON files found in one or both directories")
        return

    try:
        embedding_model = GraniteEmbeddings()
    except Exception as e:
        print(f"Error loading Granite model: {e}")
        return

    # Compare each file from folder1 with each file from folder2
    for file1 in files1:
        for file2 in files2:
            json_path1 = os.path.join(folder1, file1)
            json_path2 = os.path.join(folder2, file2)
            
            # Skip if either path is a directory
            if os.path.isdir(json_path1) or os.path.isdir(json_path2):
                print(f"Skipping comparison - one or both paths are directories: {json_path1}, {json_path2}")
                continue
                
            print(f"Comparing {json_path1} with {json_path2}")

            try:
                with open(json_path1, "r", encoding="utf-8") as f1:
                    data1 = json.load(f1)
                with open(json_path2, "r", encoding="utf-8") as f2:
                    data2 = json.load(f2)

                # Check if data is valid
                if not isinstance(data1, list) or not isinstance(data2, list) or not data1 or not data2:
                    print(f"Skipping comparison - invalid JSON structure")
                    continue

                answers_dict1 = data1[0].get("answers", {})
                answers_dict2 = data2[0].get("answers", {})

                similarity_results = []

                common_keys = set(answers_dict1.keys()) & set(answers_dict2.keys())
                if not common_keys:
                    print(f"No matching answer indices found between files")
                    continue

                sorted_keys = sorted(common_keys, key=natural_sort_key)
                print(f"Found {len(sorted_keys)} matching questions")

                evaluator = AnswerEvaluator()

                for key in sorted_keys:
                    answer1 = answers_dict1[key].strip()
                    answer2 = answers_dict2[key].strip()

                    if not answer1 or not answer2 or answer1 == "```" or answer2 == "```" or answer1 == "**"or answer2== "**" :
                        print(f"Skipping question {key} - empty or invalid answer")
                        continue

                    try:
                        embedding1 = embedding_model.embed_text(answer1)
                        embedding2 = embedding_model.embed_text(answer2)

                        similarity_score = float(cosine_similarity(embedding1, embedding2)[0][0])
                        print(f"Question {key} similarity score: {similarity_score}")

                        similarity_results.append({
                            "question_number": key,
                            "answer1": answer1,
                            "answer2": answer2,
                            "similarity_score": similarity_score
                        })
                    except Exception as e:
                        print(f"Error processing question {key}: {e}")

                if similarity_results:
                    output_filename = f"similarity_{os.path.splitext(file1)[0]}_{os.path.splitext(file2)[0]}.json"
                    output_path = os.path.join(output_folder, output_filename)

                    similarity_results.sort(key=lambda x: natural_sort_key(x["question_number"]))

                    result_data = {
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
                    }
                    
                    with open(output_path, "w", encoding="utf-8") as outf:
                        json.dump(result_data, outf, indent=4, ensure_ascii=False)
                    print(f"Saved comparison results to {output_path}")
                else:
                    print("No similarity results were generated")
            except Exception as e:
                print(f"Error comparing files: {e}")
                import traceback
                print(traceback.format_exc())


if __name__ == "__main__":
    folder1 = "/Users/ayrafraihan/Desktop/pythonProject1/finalflow/input_folder/AnswerKey/Json_with_answers"
    folder2 = "/Users/ayrafraihan/Desktop/pythonProject1/finalflow/input_folder/AnswerSheet/Json_with_answers"
    output_folder = "/Users/ayrafraihan/Desktop/pythonProject1/finalflow/results"

    compare_jsons(folder1, folder2, output_folder)