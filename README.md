# Land titles text extraction 

### Author: George Felobes  
### Version: 1.0  

---

## Overview
This application processes PDF files, extracts structured data, and saves it as JSON and CSV for analysis or record-keeping. It uses PyMuPDF for handling PDFs and OpenAI's API for advanced data extraction.

---

## Features
- **PDF to Image Conversion:** Converts multi-page PDFs into high-resolution JPEG images.
- **Intelligent Data Extraction:** Uses OpenAI's API to extract structured data from images with confidence scoring.
- **Data Transformation:** Saves extracted data in CSV format for easy usage.
- **Cost Estimation:** Calculates token usage and costs for OpenAI API calls.

---

## Prerequisites
1. Python 3.8 or above.
2. Required Python libraries:
   - `fitz` (PyMuPDF)
   - `openai`
   - `pydantic`
   - `Pillow`
3. OpenAI API key with access to the specified model.
4. Input PDF files with standardized formatting.

---

## Workflow
1. **PDF to JPEG Conversion:** Converts each page of the input PDF into a JPEG image.
2. **Data Extraction:** Processes images through OpenAI's API to extract structured data.
3. **CSV Export:** Saves extracted data into CSV files with key-value pairs.
4. **Cost Analysis:** Reports token costs for processing each image using OpenAI's API.

---

## Instructions to Run the App

### 1. Set Up the Environment
- Create and activate a virtual environment:
  ```bash
  python -m venv env
  source env/bin/activate  # On Windows: env\\Scripts\\activate
  ```

### 2. Install Dependencies
- Install required libraries using the `requirements.txt` file:
  ```bash
  pip install -r requirements.txt
  ```

### 3. Configure Your API Key
- Add your OpenAI API key as an environment variable:
  ```bash
  export OPENAI_API_KEY=your_api_key_here
  ```
- **Alternative (Not Recommended):** Hardcode the API key in the script.

### 4. Run the Application
- Launch the Streamlit app:
  ```bash
  streamlit run app.py
  ```
- Ensure this command is executed inside the activated virtual environment.

---

## Use Cases
- Automating land title data extraction for legal, real estate, or administrative purposes.
- Digitizing and formatting land title information for record-keeping.
- Reducing manual labor in data entry and processing.

---

## Notes
- The app assumes a standardized format for PDF inputs. Non-standard PDFs may require adjustments in the code.
- Running costs depend on the OpenAI API usage and the number of images processed.

---

## Disclaimer
This application assumes standard formatting of input PDFs. Variations in formatting may require customizations for optimal results.