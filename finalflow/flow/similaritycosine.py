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

def allocate_marks(score, thresholds, total_marks=4):
    """
    Allocates marks based on similarity score and custom thresholds.
    
    Args:
        score: Similarity score between 0 and 1
        thresholds: Dictionary containing threshold values like:
            {
                "full_marks": 0.8,    # Score needed for full marks
                "high_marks": 0.7,    # Score needed for 75% marks
                "mid_marks": 0.6,     # Score needed for 50% marks
                "low_marks": 0.5      # Score needed for 25% marks
            }
        total_marks: Maximum marks possible (default: 4)
    """
    if score > thresholds["full_marks"]:
        return total_marks
    elif score > thresholds["high_marks"]:
        return total_marks * 0.75
    elif score > thresholds["mid_marks"]:
        return total_marks * 0.5
    elif score > thresholds["low_marks"]:
        return total_marks * 0.25
    else:
        return 0

def main(teacher_file, student_file, output_file, thresholds):
    """
    Main function to compute similarity scores and allocate marks.
    
    Args:
        teacher_file: Path to teacher's embeddings JSON file
        student_file: Path to student's embeddings JSON file
        output_file: Path to save results
        thresholds: Dictionary containing threshold values for mark allocation
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
        similarity_score = float(similarity_scores[i])
        marks_allotted = allocate_marks(similarity_score, thresholds)

        results[question_number] = {
            "most_similar_teacher_question": teacher_question_numbers[most_similar_indices[i]],
            "similarity_score": similarity_score,
            "marks_allotted": marks_allotted
        }

    with open(output_file, 'w') as file:
        json.dump(results, file, indent=4)

# Example usage
if __name__ == "__main__":
    teacher_file = "/Users/tanishta/Desktop/GitHub/ibm/finalflow/results/output1_embeddings.json"
    student_file = "/Users/tanishta/Desktop/GitHub/ibm/finalflow/results/output2_embeddings.json"
    output_file = "/Users/tanishta/Desktop/GitHub/ibm/finalflow/results/result.json"

    # Custom thresholds for mark allocation
    custom_thresholds = {
        "full_marks": float(input("Enter threshold for full marks (e.g., 0.8): ")),
        "high_marks": float(input("Enter threshold for 75% marks (e.g., 0.7): ")),
        "mid_marks": float(input("Enter threshold for 50% marks (e.g., 0.6): ")),
        "low_marks": float(input("Enter threshold for 25% marks (e.g., 0.5): "))
    }

    main(teacher_file, student_file, output_file, thresholds=custom_thresholds)