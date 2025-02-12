import os
import streamlit as st
import asyncio
import json
import shutil
import time
from app import main  # Importing the backend processing function

# Paths for storing uploaded files
ANSWERKEY_FOLDER = "/Users/ayrafraihan/Desktop/pythonProject1/finalflow/input_folder/AnswerKey/clean_pdf"
ANSWERSHEET_FOLDER =  "/Users/ayrafraihan/Desktop/pythonProject1/finalflow/input_folder/AnswerSheet/Handwritten/mew.pdf"

RESULTS_FOLDER ="/Users/ayrafraihan/Desktop/pythonProject1/finalflow/results"

os.makedirs(ANSWERKEY_FOLDER, exist_ok=True)
os.makedirs(ANSWERSHEET_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)


def save_uploaded_file(uploaded_file, folder):
    """Save uploaded file to the specified folder"""
    file_path = os.path.join(folder, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path


def load_similarity_results():
    """Load similarity scores JSON if available"""
    result_file = os.path.join(RESULTS_FOLDER, "similarity_results.json")
    if os.path.exists(result_file):
        with open(result_file, "r") as f:
            return json.load(f)
    return None


def trigger_grading():
    """Run the main grading pipeline asynchronously"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())


st.set_page_config(page_title="📝 IntelliGrade", layout="wide")

with st.sidebar:
    st.title("🎓 IntelliGrade")

    st.header("📋 Answer Key Upload")
    answer_key = st.file_uploader("Upload Answer Key 🔑", type=['pdf'])
    if answer_key:
        save_uploaded_file(answer_key, ANSWERKEY_FOLDER)
        st.success(f"✅ {answer_key.name} Uploaded Successfully!")

    st.header("📄 Answer Sheet Upload")
    answer_sheets = st.file_uploader("Upload Answer Sheets 📝", type=['pdf'], accept_multiple_files=True)
    if answer_sheets:
        for sheet in answer_sheets:
            save_uploaded_file(sheet, ANSWERSHEET_FOLDER)
        st.success(f"✅ {len(answer_sheets)} PDF(s) Uploaded!")

    st.header("🎚️ Difficulty Level")
    difficulty = st.radio("Select Difficulty 🧩", ["Easy 🟢", "Medium 🟠", "Hard 🔴"], index=1)

st.title("IntelliGrade 🪡")

if st.button("🚀 Start Grading Process"):
    if answer_key and answer_sheets:
        with st.spinner("Processing... Please wait ⏳"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            processing_steps = [
                "🌱 Planting seeds of knowledge...", "💧 Watering academic roots...",
                "🌿 Nurturing scholarly sprouts...", "🍃 Pruning learning branches...",
                "🌳 Growing wisdom's forest...", "🍂 Harvesting intellectual fruits...",
                "🔬 Analyzing growth patterns...", "📊 Mapping knowledge landscape...",
                "🏆 Cultivating excellence...", "✨ Blooming academic potential..."
            ]

            for i, step in enumerate(processing_steps):
                time.sleep(1)  # Simulate processing delay
                progress_bar.progress((i + 1) * 10)
                status_text.text(step)

            trigger_grading()
            progress_bar.empty()
            status_text.text("✨ Grading Complete!")

        # Load results and display
        similarity_results = load_similarity_results()
        if similarity_results:
            st.json(similarity_results)
        else:
            st.warning("No results found. Please check logs.")
    else:
        st.warning("Please upload an answer key and at least one answer sheet.")
