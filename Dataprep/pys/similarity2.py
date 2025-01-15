import json
import numpy as np
import faiss  # Facebook AI Similarity Search

def load_embeddings_by_question(file_path):
    """
    Loads embeddings grouped by question number from the JSON file.
    """
    with open(file_path, 'r') as file:
        data = json.load(file)

    question_embeddings = {}
    for entry in data:
        question_number = entry.get("question_number")
        embeddings = entry.get("embedding", None)

        if embeddings:
            question_embeddings[question_number] = embeddings
    return question_embeddings

def calculate_similarity(teacher_embeddings, student_embeddings):
    """
    Calculates similarity scores between teacher and student embeddings using FAISS.
    """
    teacher_embeddings = np.array(teacher_embeddings).astype('float32')
    student_embeddings = np.array(student_embeddings).astype('float32')

    if len(teacher_embeddings.shape) != 2 or len(student_embeddings.shape) != 2:
        raise ValueError("Embeddings must be 2D arrays with shape (num_samples, embedding_dimension).")

    faiss.normalize_L2(teacher_embeddings)
    faiss.normalize_L2(student_embeddings)

    index = faiss.IndexFlatIP(teacher_embeddings.shape[1])
    index.add(teacher_embeddings)

    distances, indices = index.search(student_embeddings, k=1)
    return distances, indices

def allocate_marks(score, difficulty, total_marks=4):
    """
    Allocates marks based on similarity score and difficulty level.
    """
    if difficulty == "hard":
        if score > 0.8:
            return total_marks
        elif 0.7 < score <= 0.8:
            return total_marks * 0.75
        elif 0.6 < score <= 0.7:
            return total_marks * 0.5
        elif 0.5 < score <= 0.6:
            return total_marks * 0.25
        else:
            return 0
    elif difficulty == "medium":
        if score > 0.8:
            return total_marks
        elif 0.6 < score <= 0.8:
            return total_marks * 0.75
        elif 0.5 < score <= 0.6:
            return total_marks * 0.5
        elif 0.4 < score <= 0.5:
            return total_marks * 0.25
        else:
            return 0
    elif difficulty == "easy":
        if score > 0.6:
            return total_marks
        elif 0.4 < score <= 0.6:
            return total_marks * 0.75
        elif 0.3 < score <= 0.4:
            return total_marks * 0.5
        elif 0.2 < score <= 0.3:
            return total_marks * 0.25
        else:
            return 0
    else:
        raise ValueError("Invalid difficulty level. Choose from 'easy', 'medium', or 'hard'.")

def main(teacher_file, student_file, output_file, difficulty="medium"):
    """
    Main function to compute similarity scores and allocate marks.
    """
    teacher_data = load_embeddings_by_question(teacher_file)
    student_data = load_embeddings_by_question(student_file)

    if not teacher_data or not student_data:
        raise ValueError("One or both datasets have no valid embeddings to compare.")

    teacher_question_numbers = list(teacher_data.keys())
    teacher_embeddings = [teacher_data[q] for q in teacher_question_numbers]

    student_question_numbers = list(student_data.keys())
    student_embeddings = [student_data[q] for q in student_question_numbers]

    distances, indices = calculate_similarity(teacher_embeddings, student_embeddings)

    results = {}
    for i, question_number in enumerate(student_question_numbers):
        similarity_score = float(1 - distances[i][0])  # Convert to similarity (1 - distance)
        marks_allotted = allocate_marks(similarity_score, difficulty)

        results[question_number] = {
            "most_similar_teacher_question": teacher_question_numbers[indices[i][0]],
            "similarity_score": similarity_score,
            "marks_allotted": marks_allotted
        }

    with open(output_file, 'w') as file:
        json.dump(results, file, indent=4)

    print(f"Results saved to {output_file}")

# Example usage
teacher_file = "/Users/tanishta/Desktop/Dataprep/embeddingsteach2.json"
student_file = "/Users/tanishta/Desktop/Dataprep/embeddingsstu2.json"
output_file = "/Users/tanishta/Desktop/Dataprep/res2.json"

# You can change the difficulty to "easy", "medium", or "hard"
difficulty_level = "hard"
main(teacher_file, student_file, output_file, difficulty=difficulty_level)