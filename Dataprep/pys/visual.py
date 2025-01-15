import json
import matplotlib.pyplot as plt

def load_similarity_data(file_path):
    """
    Loads similarity data from the res21.json file.
    """
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def plot_similarity_scores(data, difficulty, title):
    """
    Plots similarity scores with horizontal shading on the y-axis for scoring regions.
    """
    # Extract question numbers, similarity scores, and marks allotted
    questions = list(data.keys())
    similarity_scores = [data[q]["similarity_score"] for q in questions]
    marks_allotted = [data[q]["marks_allotted"] for q in questions]

    # Plot settings
    plt.figure(figsize=(10, 6))

    # Shaded areas for scoring based on difficulty
    x_min, x_max = 0, len(questions) + 1
    y_min, y_max = 0, 1

    if difficulty == "easy":
        plt.axhspan(0.6, y_max, color="green", alpha=0.2, label="Full Marks")
        plt.axhspan(0.4, 0.6, color="yellow", alpha=0.2, label="3/4 Marks")
        plt.axhspan(0.3, 0.4, color="orange", alpha=0.2, label="1/2 Marks")
        plt.axhspan(0.2, 0.3, color="blue", alpha=0.2, label="1/4 Marks")

    elif difficulty == "medium":
        plt.axhspan(0.8, y_max, color="green", alpha=0.2, label="Full Marks")
        plt.axhspan(0.6, 0.8, color="yellow", alpha=0.2, label="3/4 Marks")
        plt.axhspan(0.5, 0.6, color="orange", alpha=0.2, label="1/2 Marks")        
        plt.axhspan(0.4, 0.5, color="blue", alpha=0.2, label="1/4 Marks")

    elif difficulty == "hard":
        plt.axhspan(0.8, y_max, color="green", alpha=0.2, label="Full Marks")
        plt.axhspan(0.7, 0.8, color="yellow", alpha=0.2, label="3/4 Marks")
        plt.axhspan(0.6, 0.7, color="orange", alpha=0.2, label="1/2 Marks")
        plt.axhspan(0.5, 0.6, color="blue", alpha=0.2, label="1/4 Marks")

    # Scatter plot for similarity scores
    plt.scatter(range(1, len(questions) + 1), similarity_scores, c="blue", label="Similarity Scores")
    plt.plot(range(1, len(questions) + 1), similarity_scores, linestyle="--", alpha=0.6)

    # Annotate points with marks allotted
    for i, score in enumerate(similarity_scores):
        plt.text(i + 1, score, f"{marks_allotted[i]} Marks", fontsize=8, color="red")

    # Plot aesthetics
    plt.title(title)
    plt.xlabel("Question Number")
    plt.ylabel("Similarity Score")
    plt.xlim(x_min, x_max)
    plt.ylim(y_min, y_max)
    plt.xticks(range(1, len(questions) + 1))
    plt.yticks([round(y, 1) for y in list(plt.yticks()[0])])
    plt.grid(True)
    plt.legend()
    plt.show()

def plot_all_difficulties(file_path):
    """
    Generates plots for all difficulty levels using similarity data.
    """
    data = load_similarity_data(file_path)

    difficulties = ["easy", "medium", "hard"]
    for difficulty in difficulties:
        plot_similarity_scores(data, difficulty, title=f"Similarity Scores for {difficulty.capitalize()} Difficulty")

# Example usage
file_path = "/Users/tanishta/Desktop/GitHub/ibm_dpk-project/Dataprep/res/res21.json"
plot_all_difficulties(file_path)
