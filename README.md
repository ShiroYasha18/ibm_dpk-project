# Handwritten Answer Sheet Evaluation Platform

This project provides an end-to-end pipeline for evaluating handwritten answer sheets against answer keys using OCR, NLP, and similarity scoring. It leverages IBM WatsonX, Llama 3.2 vision models, and modern data processing tools.

## Features
- Upload handwritten answer sheets and answer keys (PDF)
- Extract text using advanced OCR (WatsonX, Tesseract, or Gemini)
- Convert PDFs to Parquet and JSON for structured processing
- Compute similarity scores between student and teacher answers
- Interactive Streamlit web interface for processing and result visualization
- Modular codebase with support for custom embedding models and pipelines

## Directory Structure
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
   requirements.txt```
   

## Usage
- Launch the Streamlit app:
  ```  streamlit run finalflow/flow/streamlit_app.py```
  

  
 
- Follow the web UI to upload answer sheets and answer keys, process files, and view results.
## Configuration
- Environment variables (API keys, etc.) can be set in a .env file.
- Paths for input/output folders are configurable in the code.
## Requirements
- Python 3.8+
- IBM WatsonX API credentials (for OCR)
- Optional: Google Gemini API key (for Gemini OCR)
## License
This project is licensed under the Apache License 2.0.

For more details, see the code and comments in each module.