# 📝 Handwritten Answer Sheet Evaluation Platform

🔍 This project provides an **end-to-end pipeline** for evaluating handwritten answer sheets against answer keys using **OCR**, **NLP**, and **similarity scoring**. It leverages **IBM WatsonX**, **Granite 3.3 Vision models**, and modern data processing tools for scalable, intelligent assessment.

---

## 🧠 Architecture

![Architecture Diagram](media/Handwritten%20Visual%20Question%20EXTRACTED%20TEXT-1%202.jpg)

---

## 🎬 Demo

<video width="600" controls>
  <source src="media/Untitled (1).mov" type="video/mp4">
  Your browser does not support the video tag.
</video>

https://github.com/user-attachments/assets/bdde3cf9-9263-4206-8417-873bde0257d2

---

## ✨ Features

- ✅ Upload **handwritten answer sheets** and **answer keys (PDF)**
- 🧠 Extract text using advanced OCR: **WatsonX**, **Tesseract**, or **Gemini**
- 📄 Convert PDFs to **Parquet** and **JSON** for structured processing
- 📊 Compute **similarity scores** between student and teacher answers
- 🌐 Interactive **Streamlit** web interface for processing & results
- 🔌 **Modular codebase** — easy to plug in custom models or tools

---

## 🚧 Challenges

- ✍️ **Handwriting Styles** – Cursive, block letters, etc., cause OCR inconsistencies  
- 🗂 **Different Layouts** – Adapting to varied answer sheet formats  
- ❌ **Scribbles & Missing Answers** – Common in real-world sheets, affecting accuracy  

---

## ⚠️ Limitations

- 📉 **Diagram Recognition** – Only simple diagrams like flowcharts or trees are supported  
- 🖼️ **Graphics-Heavy Content** – Complex images reduce OCR and NLP accuracy  

---

## 🔮 Future Scope

- 📈 **Enhanced Diagram Support** – Improve complex diagram understanding  
- ☁️ **Mass Data Storage Integration** – Add **KFP**, **S3**, etc., for scalable storage and processing  

---

## 📁 Directory Structure


- `finalflow/flow/` — Main pipeline, Streamlit app, and processing scripts
- `Dataprep/` — Data preparation, embedding, and visualization utilities
- `pdf2parquet/` — PDF to Parquet conversion tools
- `src/` — Additional scripts and utilities

## Installation
1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd pythonProject1
   ```
2. Install dependencies:
 
   

   ```
   pip install -r requirements.txt
      ```
 For pdf2parquet submodule:
 ```
   pip install -r pdf2parquet/   
   requirements.txt
   ```
3. Set up environment variables:
   - Create a.env file in the project root.
   - Add your API keys and other configuration variables.
   - Example.env file is provided for reference.
## Docker Setup
1. Build the Docker image:
 
   
 ```  
   
   docker build -t
   ```
   my-streamlit-app .
2. Run the Docker container:
  
 ```  
   docker run -p 8501:8501
  ``` 
   my-streamlit-app


## Usage
- Launch the Streamlit app:
  ```  streamlit run finalflow/flow/streamlit_app.py```
  

  
 
- Follow the web UI to upload answer sheets and answer keys, process files, and view results.
## Configuration
- Environment variables (API keys, etc.) can be set in a .env file.
- The sample .env file is provided for reference:
   ``` 
   IBM_API_KEY=""
   IBM_SERVICE_URL=""
   IBM_PROJECT_ID=""
   ``` 

- Get these keys from watsonx.ai , which you will get when you create a API key for the foundational models- these can be changed with respect to the model card in the code.

- Paths for input/output folders are configurable in the code.
## Requirements
- Python 3.8+
- IBM WatsonX API credentials (for OCR)
- Optional: Google Gemini API key (for Gemini OCR)
## License
This project is licensed under the Apache License 2.0.

For more details, see the code and comments in each module.