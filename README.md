# Handwritten Answer Sheet Evaluation Platform

This project provides an end-to-end pipeline for evaluating handwritten answer sheets against answer keys using OCR, NLP, and similarity scoring. It leverages IBM WatsonX, Llama 3.2 vision models, and modern data processing tools.
### Demo

<video width="600" controls>
  <source src="media/Untitled (1).mov" type="video/mp4">
  Your browser does not support the video tag.
</video>

https://github.com/user-attachments/assets/bdde3cf9-9263-4206-8417-873bde0257d2


### Features
- Upload handwritten answer sheets and answer keys (PDF)
- Extract text using advanced OCR (WatsonX, Tesseract, or Gemini)
- Convert PDFs to Parquet and JSON for structured processing
- Compute similarity scores between student and teacher answers
- Interactive Streamlit web interface for processing and result visualization
- Modular codebase with support for custom embedding models and pipelines
### Challenges
- Handling Handwritten Text : The system faces challenges in accurately interpreting various handwriting styles, including cursive and block letters. Variations in handwriting can lead to misinterpretations or missed text.
- Different Layouts : Answer sheets may have different layouts, which can complicate the extraction process. The system needs to adapt to various formats and structures.
- Scribbles and Missing Answers : Handwritten documents often contain scribbles, corrections, and missing answers, which can affect the accuracy of data extraction.
### Limitations
- Diagram Recognition : Currently, the system is limited in its ability to process complex diagrams. It performs well with simple diagrams like flowcharts and tree structures but struggles with more intricate graphics.
- Graphics-Heavy Content : The system may not accurately interpret documents with heavy graphical content, affecting the extraction of relevant information.
### Future Scope
- Enhanced Diagram Handling : Future developments aim to improve the system's ability to process complex diagrams, expanding its utility in diverse document types.
- Integration with Mass Data Storage : Plans include connecting the system with platforms like KFP and S3 for efficient data retrieval and storage, facilitating large-scale processing of answer sheets and answer keys.
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