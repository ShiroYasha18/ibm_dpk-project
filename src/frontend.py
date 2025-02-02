import os
import streamlit as st
import PyPDF2
import time
import google.generativeai as genai

# Global configuration
ANSWERKEY_FOLDER = 'answerkeys'
ANSWERSHEET_FOLDER = 'answersheets'

# Ensure folders exist
os.makedirs(ANSWERKEY_FOLDER, exist_ok=True)
os.makedirs(ANSWERSHEET_FOLDER, exist_ok=True)

# Gemini API Configuration
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


def generate_thematic_processing_phrases():
    """Generate thematically connected processing phrases"""
    model = genai.GenerativeModel('gemini-pro')

    prompt = """Create a sequence of 10 processing phrases that are:
    1. Emoji-rich
    2. Under 50 characters
    3. Thematically connected like a story
    4. Metaphorical and creative
    5. Related to evaluation and processing

    The phrases should flow like a narrative of transformation and discovery."""

    try:
        response = model.generate_content(prompt)
        phrases = response.text.strip().split('\n')

        # Clean and format phrases
        return [phrase.strip() for phrase in phrases if phrase.strip()]
    except Exception as e:
        return [
            "🌱 Planting seeds of knowledge...",
            "💧 Watering academic roots...",
            "🌿 Nurturing scholarly sprouts...",
            "🍃 Pruning learning branches...",
            "🌳 Growing wisdom's forest...",
            "🍂 Harvesting intellectual fruits...",
            "🔬 Analyzing growth patterns...",
            "📊 Mapping knowledge landscape...",
            "🏆 Cultivating excellence...",
            "✨ Blooming academic potential..."
        ]


def process_pdf(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    return len(reader.pages)


def main():
    st.set_page_config(page_title="📝 IntelliGrade by 👁️🐝M", layout="wide")

    # Sidebar for uploads and difficulty selection
    with st.sidebar:
        st.title("🎓 IntelliGrade")

        # Answer Key Upload Section
        st.header("📋 Answer Key Upload")
        answer_key = st.file_uploader("Upload Answer Key 🔑", type=['pdf'])
        if answer_key:
            with open(os.path.join(ANSWERKEY_FOLDER, answer_key.name), "wb") as f:
                f.write(answer_key.getbuffer())
            st.success(f"✅ {answer_key.name} Uploaded Successfully!")

        # Answer Sheet Upload Section
        st.header("📄 Answer Sheet Upload")
        answer_sheets = st.file_uploader("Upload Answer Sheets 📝", type=['pdf'], accept_multiple_files=True)
        if answer_sheets:
            for sheet in answer_sheets:
                with open(os.path.join(ANSWERSHEET_FOLDER, sheet.name), "wb") as f:
                    f.write(sheet.getbuffer())
            st.success(f"✅ {len(answer_sheets)} PDF Answer Sheet(s) Uploaded!")

        # Difficulty Selection Section
        st.header("🎚️ Difficulty Level")
        difficulty = st.radio(
            "Select Difficulty 🧩",
            ["Easy 🟢", "Medium 🟠", "Hard 🔴"],
            index=1  # Default to Medium
        )

    # Main content area
    st.title("IntelliGrade 🪡")

    if st.button("🚀 Start Grading Process"):
        if answer_key and answer_sheets:
            # Generate thematic phrases
            processing_phrases = generate_thematic_processing_phrases()

            progress_bar = st.progress(0)
            status_text = st.empty()

            # Progressive processing with thematic phrases
            for i, phrase in enumerate(processing_phrases, 1):
                progress_bar.progress(i * 10)
                status_text.text(phrase)
                time.sleep(0.5)  # Slight pause between phrases

            # Processing results
            col1, col2 = st.columns(2)

            with col1:
                key_pages = process_pdf(answer_key)
                sheet_pages = [process_pdf(sheet) for sheet in answer_sheets]

                st.write(f"📄 Answer Key: {key_pages} page(s)")
                st.write(f"📝 Answer Sheets: {len(sheet_pages)} sheet(s)")

            with col2:
                # Scoring section
                st.subheader("📊 Processing Summary")
                st.metric(label="🏅 Total Sheets", value=len(sheet_pages))
                st.metric(label="📈 Difficulty", value=difficulty)

            st.balloons()
            st.success("✨ Grading Complete!")
        else:
            st.warning("Please upload answer key and sheets first!")

if __name__ == "__main__":
    main()