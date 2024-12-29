import streamlit as st
import os
import fitz  # PyMuPDF
import base64
import csv
import re
from pydantic import BaseModel

class ExtractedData(BaseModel):
    extracted_text: str
    confidence: float

class PDFImageProcessor:
    @staticmethod
    def pdf_to_jpeg_no_poppler(pdf_path, output_folder, dpi=150):
        try:
            pdf_document = fitz.open(pdf_path)
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)

            for page_number in range(len(pdf_document)):
                page = pdf_document.load_page(page_number)
                pix = page.get_pixmap(dpi=dpi)
                output_path = os.path.join(output_folder, f"page_{page_number + 1}.jpeg")
                pix.save(output_path)

            pdf_document.close()
        except Exception as e:
            st.error(f"An error occurred while converting PDF to JPEG: {e}")

    @staticmethod
    def extract_and_save_csv(text_data, output_file):
        try:
            json_match = re.search(r'\{.*\}', text_data, re.DOTALL)
            if not json_match:
                raise ValueError("No valid JSON data found in the provided text.")

            json_data = eval(json_match.group())  # Safely evaluate JSON

            with open(output_file, "w", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["FIELD", "ATTRIBUTE"])
                for key, value in json_data.items():
                    writer.writerow([key, value])

            st.success(f"CSV data has been extracted and saved to {output_file}")

        except Exception as e:
            st.error(f"An error occurred: {e}")

# Streamlit App
st.title("PDF to JPEG and Text Extraction")

uploaded_pdf = st.file_uploader("Upload a PDF file", type=["pdf"])
output_folder = st.text_input("Output Folder", "output_images")

if st.button("Convert PDF to JPEG"):
    if uploaded_pdf is not None:
        pdf_path = os.path.join("temp", uploaded_pdf.name)
        with open(pdf_path, "wb") as f:
            f.write(uploaded_pdf.getbuffer())

        PDFImageProcessor.pdf_to_jpeg_no_poppler(pdf_path, output_folder)
        st.success(f"PDF has been converted to JPEG images in {output_folder}")

# Allowing users to process images
if st.button("Process All Images in Folder"):
    if os.path.exists(output_folder):
        for image_file in os.listdir(output_folder):
            if image_file.endswith(".jpeg"):
                st.write(f"Processing {image_file}...")
                # Simulated response from OpenAI's API for demonstration purposes
                extracted_text = "{" + f"\"key\": \"value\" for {image_file}" + "}"  # Placeholder
                output_csv = os.path.join(output_folder, f"{os.path.splitext(image_file)[0]}.csv")
                PDFImageProcessor.extract_and_save_csv(extracted_text, output_csv)
    else:
        st.error(f"Output folder {output_folder} does not exist.")

st.info("This is a basic app. Integration with OpenAI requires valid API keys and setup.")
