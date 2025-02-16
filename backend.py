import os
import sys
import logging
import pandas as pd
import fitz  # PyMuPDF for PDF manipulation
from PIL import Image
import pytesseract
from io import BytesIO

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Ensure Tesseract-OCR is installed and update the path if necessary
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_from_image(image):
    """
    Extract text from an image using Optical Character Recognition (OCR).
    """
    try:
        image = image.convert('L')  # Convert image to grayscale for better OCR accuracy
        text = pytesseract.image_to_string(image)
        return text.strip()
    except Exception as e:
        logging.error(f"Error extracting text from image: {e}")
        return ""

def extract_text_from_pdf(pdf_path):
    """
    Extract text and images from a PDF file.
    """
    if not os.path.exists(pdf_path):
        logging.error(f"File not found: {pdf_path}")
        return []
    
    try:
        pdf_document = fitz.open(pdf_path)
        all_text = []

        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            text = page.get_text("text")
            all_text.append(f"Page {page_num + 1} Text:\n{text}\n")

            for img_index, img in enumerate(page.get_images(full=True)):
                xref = img[0]
                base_image = pdf_document.extract_image(xref)
                image_bytes = base_image["image"]
                image = Image.open(BytesIO(image_bytes))
                
                img_text = extract_text_from_image(image)
                all_text.append(f"Image {img_index + 1} Text:\n{img_text}\n")
        
        logging.info("Text extraction completed successfully.")
        return all_text
    except Exception as e:
        logging.error(f"Error processing PDF: {e}")
        return []

def convert_to_excel(data, output_path):
    """
    Convert extracted data into an Excel file.
    """
    try:
        df = pd.DataFrame(data, columns=["Extracted Text"])
        df.to_excel(output_path, index=False)
        logging.info(f"Data successfully saved to {output_path}")
    except Exception as e:
        logging.error(f"Error saving to Excel: {e}")

if __name__ == "__main__":
    """
    Main function to execute PDF text extraction and save results to an Excel file.
    """
    if len(sys.argv) < 3:
        logging.error("Usage: python script.py <pdf_path> <output_excel_path>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    output_excel_path = sys.argv[2]

    extracted_data = extract_text_from_pdf(pdf_path)
    if extracted_data:
        convert_to_excel(extracted_data, output_excel_path)
