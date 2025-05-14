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
