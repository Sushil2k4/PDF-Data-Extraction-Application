import pandas as pd
import fitz  # PyMuPDF for PDF manipulation
from PIL import Image
import pytesseract
from io import BytesIO

# Ensure Tesseract-OCR is installed and update the path if necessary
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_from_image(image):
    """
    Extract text from an image using Optical Character Recognition (OCR).

    Parameters:
    image (PIL.Image.Image): The image object from which text will be extracted.

    Returns:
    str: The text extracted from the image.
    """
    # Use pytesseract to perform OCR on the image and extract text
    text = pytesseract.image_to_string(image)
    return text

def extract_text_from_pdf(pdf_path):
    """
    Extract text and images from a PDF file.

    Parameters:
    pdf_path (str): The path to the PDF file from which text and images will be extracted.

    Returns:
    list: A list containing text extracted from each page and images in the PDF.
    """
    # Open the PDF file
    pdf_document = fitz.open(pdf_path)
    all_text = []

    # Iterate through each page in the PDF
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        
        # Extract text from the current page
        text = page.get_text()
        all_text.append(text)

        # Extract images from the current page
        for img_index, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            base_image = pdf_document.extract_image(xref)
            image_bytes = base_image["image"]
            image = Image.open(BytesIO(image_bytes))
            
            # Extract text from the image using OCR
            img_text = extract_text_from_image(image)
            all_text.append(f"Image {img_index + 1} Text: {img_text}")

    return all_text

def convert_to_excel(data, output_path):
    """
    Convert extracted data into an Excel file.

    Parameters:
    data (list): A list of strings containing the extracted text.
    output_path (str): The path where the Excel file will be saved.

    Returns:
    None
    """
    # Create a DataFrame from the extracted data
    df = pd.DataFrame(data, columns=["Extracted Text"])
    # Save the DataFrame to an Excel file
    df.to_excel(output_path, index=False)

if __name__ == "__main__":
    """
    Main function to demonstrate the usage of the extraction functions.
    """
    # Path to the input PDF file
    pdf_path = 'pdf_2.pdf'  # Replace with your PDF file path
    # Path to the output Excel file
    output_excel_path = 'excel_storage.xlsx'  # Replace with desired Excel file path

    # Extract text and images from the PDF
    data = extract_text_from_pdf(pdf_path)
    # Convert the extracted data to an Excel file
    convert_to_excel(data, output_excel_path)
    print(f"Data has been successfully extracted and saved to {output_excel_path}")
