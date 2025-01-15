import json
import numpy as np

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

def cosine_similarity(vec1, vec2):
    """
    Calculate cosine similarity between two vectors.
    """
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    dot_product = np.dot(vec1, vec2)
    norm_vec1 = np.linalg.norm(vec1)
    norm_vec2 = np.linalg.norm(vec2)
    return dot_product / (norm_vec1 * norm_vec2)

def calculate_similarity(teacher_embeddings, student_embeddings):
    """
    Calculates similarity scores between teacher and student embeddings using cosine similarity.
    """
    similarity_scores = []
    most_similar_indices = []

    for stu_embedding in student_embeddings:
        scores = [cosine_similarity(stu_embedding, teach_embedding) for teach_embedding in teacher_embeddings]
        max_index = np.argmax(scores)
        similarity_scores.append(scores[max_index])
        most_similar_indices.append(max_index)

    return similarity_scores, most_similar_indices

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

    similarity_scores, most_similar_indices = calculate_similarity(teacher_embeddings, student_embeddings)

    results = {}
    for i, question_number in enumerate(student_question_numbers):
        similarity_score = float(similarity_scores[i])  # Convert similarity to float
        marks_allotted = allocate_marks(similarity_score, difficulty)

        results[question_number] = {
            "most_similar_teacher_question": teacher_question_numbers[most_similar_indices[i]],
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