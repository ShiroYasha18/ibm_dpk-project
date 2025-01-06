import PyPDF2
import re
import json

def extract_and_save_answers(pdf_path: str, output_file: str = "answers.json") -> None:
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        full_text = ""
        for page in reader.pages:
            full_text += page.extract_text() + "\n"

    pattern = r'Answer(\d+\.\d+\))(.*?)(?=Answer\d+\.\d+\)|$)'
    matches = re.finditer(pattern, full_text, re.DOTALL)

    answers = {}
    for match in matches:
        question_number = match.group(1)  # Gets "1.1)" part
        answer_content = match.group(2).strip()  # Gets the answer content
        answers[question_number] = answer_content

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(answers, f, indent=4, ensure_ascii=False)

    sample_entry = next(iter(answers.items())) if answers else None
    if sample_entry:
        print(f"\nExtraction completed! Sample entry:")
        print(f"Question {sample_entry[0]}: {sample_entry[1][:100]}...")
        print(f"\nTotal answers extracted: {len(answers)}")


if __name__ == "__main__":
    try:
        pdf_path = "me/pd.pdf"
        extract_and_save_answers(pdf_path)

    except FileNotFoundError:
        print("Error: PDF file not found. Please check the file path.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")