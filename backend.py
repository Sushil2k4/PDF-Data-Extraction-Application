import os
import sys
import logging
import argparse
import pandas as pd
import fitz  # PyMuPDF
from PIL import Image
from io import BytesIO
import pytesseract
from tqdm import tqdm
from typing import List

# === Logging Configuration ===
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# === Tesseract Path (Edit this as per your setup) ===
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def extract_text_from_image(image: Image.Image, lang: str = 'eng') -> str:
    """Perform OCR on a given image."""
    try:
        gray_image = image.convert('L')
        text = pytesseract.image_to_string(gray_image, lang=lang)
        return text.strip()
    except Exception as e:
        logging.error(f"OCR failed: {e}")
        return ""


def extract_text_from_pdf(pdf_path: str, lang: str = 'eng') -> List[str]:
    """Extract text and image content from a PDF."""
    if not os.path.exists(pdf_path):
        logging.error(f"File not found: {pdf_path}")
        return []

    try:
        pdf_document = fitz.open(pdf_path)
        extracted_content = []

        for page_num in tqdm(range(len(pdf_document)), desc="Processing pages"):
            page = pdf_document[page_num]
            text = page.get_text("text")

            if text.strip():
                extracted_content.append(f"Page {page_num + 1} Text:\n{text}\n")

            for img_index, img in enumerate(page.get_images(full=True)):
                xref = img[0]
                base_image = pdf_document.extract_image(xref)
                image_bytes = base_image["image"]

                try:
                    image = Image.open(BytesIO(image_bytes))
                    img_text = extract_text_from_image(image, lang=lang)
                    if img_text.strip():
                        extracted_content.append(f"Image {img_index + 1} (Page {page_num + 1}) Text:\n{img_text}\n")
                except Exception as img_error:
                    logging.warning(f"Could not process image {img_index + 1} on page {page_num + 1}: {img_error}")

        logging.info("PDF text extraction completed.")
        return extracted_content

    except Exception as e:
        logging.error(f"Failed to process PDF: {e}")
        return []


def convert_to_excel(data: List[str], output_path: str) -> None:
    """Convert extracted text to an Excel spreadsheet."""
    try:
        df = pd.DataFrame({"Extracted Text": data})
        df.to_excel(output_path, index=False, engine='openpyxl')
        logging.info(f"Data saved to Excel: {output_path}")
    except Exception as e:
        logging.error(f"Failed to write Excel file: {e}")


def parse_arguments():
    """Command-line argument parsing."""
    parser = argparse.ArgumentParser(description="Extract text (including from images) in PDFs and export to Excel.")
    parser.add_argument("pdf_path", help="Path to the input PDF file.")
    parser.add_argument("output_excel_path", help="Path to the output Excel file.")
    parser.add_argument("--lang", default="eng", help="OCR language (default: eng)")

    return parser.parse_args()


def main():
    args = parse_arguments()

    if not os.path.exists(args.pdf_path):
        logging.error(f"The specified PDF file does not exist: {args.pdf_path}")
        sys.exit(1)

    extracted_data = extract_text_from_pdf(args.pdf_path, lang=args.lang)
    if extracted_data:
        convert_to_excel(extracted_data, args.output_excel_path)
    else:
        logging.warning("No data extracted from PDF.")


if __name__ == "__main__":
    main()
