import streamlit as st
import os
import json
import base64
import fitz  # PyMuPDF
import csv
from openai import OpenAI
from dotenv import load_dotenv
from PIL import Image

# Utility class for processing PDFs and images
class PDFImageProcessor:
    @staticmethod
    def pdf_to_jpeg_no_poppler(pdf_path, output_folder, dpi=150):
        pdf_document = fitz.open(pdf_path)
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        for page_number in range(len(pdf_document)):
            page = pdf_document.load_page(page_number)
            pix = page.get_pixmap(dpi=dpi)
            output_path = os.path.join(output_folder, f"{os.path.splitext(os.path.basename(pdf_path))[0]}_page_{page_number + 1}.jpeg")
            pix.save(output_path)
            yield output_path
        pdf_document.close()

    @staticmethod
    def encode_image_to_base64(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    @staticmethod
    def process_image_to_json(openai_api_key, image_path, model="gpt-4o-mini"):
        client = OpenAI(api_key=openai_api_key)
        base64_img = PDFImageProcessor.encode_image_to_base64(image_path)
        base64_img_with_prefix = f"data:image/png;base64,{base64_img}"
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert at extracting structured data from images. Extract the text from the images",
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Return JSON document with data. Only return JSON not other text"},
                        {"type": "image_url", "image_url": {"url": f"{base64_img_with_prefix}"}},
                    ],
                },
            ],
        )
        json_string = response.choices[0].message.content.strip("```json").strip("```")
        return json.loads(json_string)

    @staticmethod
    def extract_and_save_csv(json_data, output_file):
        with open(output_file, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["FIELD", "ATTRIBUTE"])
            for key, value in json_data.items():
                if isinstance(value, (list, dict)):
                    value = json.dumps(value)
                writer.writerow([key, value])

    @staticmethod
    def calculate_openai_cost(image_path, detail="low"):
        try:
            from PIL import Image

            with Image.open(image_path) as img:
                width, height = img.size

            if detail == "low":
                return 85

            if width > 2048 or height > 2048:
                scale = 2048 / max(width, height)
                width = int(width * scale)
                height = int(height * scale)

            scale = 768 / min(width, height)
            width = int(width * scale)
            height = int(height * scale)

            tiles = (width // 512) * (height // 512)
            return 170 * tiles + 85

        except Exception as e:
            print(f"An error occurred while calculating cost: {e}")
            return 0

# Streamlit app
st.title("Land Titles Extractor")

# Input for OpenAI API Key
openai_api_key = st.text_input("Enter your OpenAI API Key:", type="password")

# File uploader
uploaded_files = st.file_uploader("Upload PDF files:", type="pdf", accept_multiple_files=True)

if openai_api_key and uploaded_files:
    if st.button("Process uploaded files"):
        output_folder = "output_images"
        os.makedirs(output_folder, exist_ok=True)

        json_download_links = []
        csv_download_links = []

        for uploaded_file in uploaded_files:
            pdf_name = uploaded_file.name
            st.write(f"Processing {pdf_name}...")

            pdf_path = os.path.join(output_folder, pdf_name)
            with open(pdf_path, "wb") as f:
                f.write(uploaded_file.read())

            progress_bar = st.progress(0)
            image_files = list(PDFImageProcessor.pdf_to_jpeg_no_poppler(pdf_path, output_folder))

            for idx, image_path in enumerate(image_files):
                st.write(f"Processing image: {os.path.basename(image_path)}")
                try:
                    json_data = PDFImageProcessor.process_image_to_json(openai_api_key, image_path)

                    # Save JSON
                    json_output_path = f"{os.path.splitext(image_path)[0]}.json"
                    with open(json_output_path, "w") as json_file:
                        json.dump(json_data, json_file, indent=4)
                    json_download_links.append(json_output_path)

                    # Save CSV
                    csv_output_path = f"{os.path.splitext(image_path)[0]}.csv"
                    PDFImageProcessor.extract_and_save_csv(json_data, csv_output_path)
                    csv_download_links.append(csv_output_path)

                    # Display cost estimate
                    tokens = PDFImageProcessor.calculate_openai_cost(image_path, detail="high")
                    st.write(f"The number of tokens of processing the {image_path} is: {tokens}, cost: ${0.000150 * tokens / 1000}")
                    st.write(f"Processed {os.path.basename(image_path)} successfully.")
                except Exception as e:
                    st.error(f"Error processing {os.path.basename(image_path)}: {e}")

                progress_bar.progress((idx + 1) / len(image_files))

            st.success(f"Completed processing {pdf_name}.")

        # Downloads Section
        st.header("Downloads")

        # JSON files download
        if json_download_links:
            st.subheader("JSON files download")
            for json_path in json_download_links:
                with open(json_path, "rb") as f:
                    json_data = f.read()
                b64 = base64.b64encode(json_data).decode()
                href = f'<a href="data:application/json;base64,{b64}" download="{os.path.basename(json_path)}">Download {os.path.basename(json_path)}</a>'
                st.markdown(href, unsafe_allow_html=True)

        # CSV files download
        if csv_download_links:
            st.subheader("CSV file download")
            for csv_path in csv_download_links:
                with open(csv_path, "rb") as f:
                    csv_data = f.read()
                b64 = base64.b64encode(csv_data).decode()
                href = f'<a href="data:text/csv;base64,{b64}" download="{os.path.basename(csv_path)}">Download {os.path.basename(csv_path)}</a>'
                st.markdown(href, unsafe_allow_html=True)

        st.success("All files processed successfully.")
