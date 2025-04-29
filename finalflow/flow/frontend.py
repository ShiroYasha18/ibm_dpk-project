import os
import streamlit as st
import asyncio
import json
import time
import app as pipeline
import sys
import pandas as pd
import io

# Add project paths
sys.path.append(os.path.abspath('/Users/tanishta/Desktop/ibm_dpk-project'))
sys.path.append(os.path.abspath('/Users/tanishta/Desktop/ibm_dpk-project/pdf2parquet'))
sys.path.append(os.path.abspath('/Users/tanishta/Desktop/ibm_dpk-project/data_processing'))

from data_processing.runtime.pure_python import PythonTransformLauncher
from pdf2parquet.dpk_pdf2parquet.transform_python import Pdf2ParquetPythonTransformConfiguration

# Paths for storing uploaded files
ANSWERKEY_FOLDER = "/Users/tanishta/Desktop/ibm_dpk-project/finalflow/input_folder/AnswerKey/clean_pdf"
ANSWERSHEET_FOLDER = "/Users/tanishta/Desktop/ibm_dpk-project/finalflow/input_folder/AnswerSheet/Handwritten"
RESULTS_FOLDER = "/Users/tanishta/Desktop/ibm_dpk-project/finalflow/results"

os.makedirs(ANSWERKEY_FOLDER, exist_ok=True)
os.makedirs(ANSWERSHEET_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

# Helper functions
def save_uploaded_file(uploaded_file, folder):
    file_path = os.path.join(folder, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

def trigger_grading(difficulty, total_marks, thresholds):
    """Run the main grading pipeline asynchronously"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(pipeline.main(difficulty, total_marks, thresholds))

def load_similarity_results():
    """Load similarity results JSON from file"""
    result_file = os.path.join(RESULTS_FOLDER, "similarity_extracted_text_pd.json")
    if os.path.exists(result_file):
        with open(result_file, "r") as f:
            return json.load(f)
    return None

def allocate_marks(score, thresholds, total_marks):
    if score >= thresholds["full_marks"]:
        return total_marks
    elif score >= thresholds["high_marks"]:
        return total_marks * 0.75
    elif score >= thresholds["mid_marks"]:
        return total_marks * 0.5
    elif score >= thresholds["low_marks"]:
        return total_marks * 0.25
    else:
        return 0

st.set_page_config(page_title="Assessly", layout="wide")

with st.sidebar:
    st.title("Grading Assistant: Grade with Ease!")

    st.header("Answer Key Upload")
    answer_key = st.file_uploader("Upload Answer Key", type=['pdf'])
    if answer_key:
        save_uploaded_file(answer_key, ANSWERKEY_FOLDER)
        st.success(f"{answer_key.name} Uploaded Successfully!")

    st.header("Answer Sheet Upload")
    answer_sheets = st.file_uploader("Upload Answer Sheets", type=['pdf'], accept_multiple_files=True)
    if answer_sheets:
        for sheet in answer_sheets:
            save_uploaded_file(sheet, ANSWERSHEET_FOLDER)
        st.success(f"{len(answer_sheets)} PDF(s) Uploaded Successfully!")

    st.header("Difficulty Level")
    difficulty = st.radio("Select Difficulty", ["Easy 🟢", "Medium 🟠", "Hard 🔴", "Customize"], index=1)

    if difficulty == "Customize":
        st.subheader("Customize Difficulty Level")
        difficulty_thresholds = {
            "full_marks": st.slider("Full Marks Threshold", 0.0, 1.0, 0.8),
            "high_marks": st.slider("High Marks Threshold", 0.0, 1.0, 0.7),
            "mid_marks": st.slider("Mid Marks Threshold", 0.0, 1.0, 0.6),
            "low_marks": st.slider("Low Marks Threshold", 0.0, 1.0, 0.5)
        }
    else:
        # Default thresholds
        difficulty_thresholds = {
            "Easy 🟢": {"full_marks": 0.8, "high_marks": 0.7, "mid_marks": 0.6, "low_marks": 0.5},
            "Medium 🟠": {"full_marks": 0.75, "high_marks": 0.65, "mid_marks": 0.55, "low_marks": 0.45},
            "Hard 🔴": {"full_marks": 0.7, "high_marks": 0.6, "mid_marks": 0.5, "low_marks": 0.4}
        }[difficulty]

    total_marks = st.number_input("Enter Total Marks per Question", min_value=1, value=4)

st.title("Assessly")

if st.button("Start Grading Process"):
    if answer_key and answer_sheets:
        with st.spinner("Processing... Please wait ⏳"):
            progress_bar = st.progress(0)
            status_text = st.empty()

            processing_steps = [
                "Uploading answer scripts...",
                "Reading handwritten responses...",
                "Extracting key content...",
                "Matching answers to reference...",
                "Evaluating based on similarity...",
                "Assigning scores carefully...",
                "Summarizing performance metrics...",
                "Double-checking evaluations...",
                "Compiling final reports...",
                "Preparing your results!"
            ]

            for i, step in enumerate(processing_steps):
                time.sleep(1)  # Simulate progress
                progress_bar.progress((i + 1) * 10)
                status_text.text(step)

            trigger_grading(difficulty, total_marks, difficulty_thresholds)

            progress_bar.empty()
            status_text.text("Grading Complete!")


        similarity_results = load_similarity_results()
        if similarity_results:
            comparisons = similarity_results.get('comparisons', [])
            if comparisons:
                comparison_data = []
                total_obtained_marks = 0

                for comp in comparisons:
                    question_number = comp.get("question_number")
                    answer1 = comp.get("answer1", "")
                    answer2 = comp.get("answer2", "")
                    similarity_score = comp.get("similarity_score", 0)

                    marks_obtained = allocate_marks(similarity_score, difficulty_thresholds, total_marks)
                    total_obtained_marks += marks_obtained

                    comparison_data.append({
                        "Question Number": question_number,
                        "Answer 1": answer1,
                        "Answer 2": answer2,
                        "Similarity Score": round(similarity_score, 4),
                        "Marks Obtained": round(marks_obtained, 2)
                    })

                # Convert to DataFrame
                df_results = pd.DataFrame(comparison_data)

                st.subheader("Detailed Results")
                st.dataframe(df_results, use_container_width=True)

                st.success(f"Total Marks Obtained: {round(total_obtained_marks, 2)} / {len(comparisons) * total_marks}")

                # Download Button
                csv_buffer = io.StringIO()
                df_results.to_csv(csv_buffer, index=False)
                st.download_button(
                    label="Download Results as CSV",
                    data=csv_buffer.getvalue(),
                    file_name="grading_results.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No comparisons found in the results.")
        else:
            st.warning("No similarity results file found.")
