import os
import sys
import logging
import argparse
import pandas as pd
import fitz  # PyMuPDF
from PIL import Image, ImageEnhance
from io import BytesIO
import pytesseract
from tqdm import tqdm
from typing import List, Tuple, Optional
import time
import re

# === Logging Configuration ===
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pdf_extraction.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# === Constants ===
DEFAULT_LANGUAGES = ['eng']  # Default language for OCR
MAX_IMAGE_SIZE = (3000, 3000)  # Maximum dimensions for image processing
MIN_IMAGE_SIZE = (50, 50)     # Minimum dimensions for image processing

def validate_tesseract_path(tesseract_path: Optional[str] = None) -> bool:
    """Validate Tesseract OCR path."""
    try:
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        pytesseract.get_tesseract_version()
        return True
    except (pytesseract.TesseractNotFoundError, Exception) as e:
        logger.error(f"Tesseract OCR not found or not working: {e}")
        logger.info("Please install Tesseract OCR and add it to your PATH or specify the path with --tesseract_path")
        return False

def preprocess_image(image: Image.Image) -> Image.Image:
    """Enhance image for better OCR results."""
    try:
        # Convert to grayscale
        image = image.convert('L')
        
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.5)
        
        # Enhance sharpness
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.2)
        
        return image
    except Exception as e:
        logger.warning(f"Image preprocessing failed: {e}")
        return image

def extract_text_from_image(image: Image.Image, languages: List[str] = DEFAULT_LANGUAGES) -> str:
    """Perform OCR on a given image with enhanced preprocessing."""
    try:
        # Validate image size
        if image.width > MAX_IMAGE_SIZE[0] or image.height > MAX_IMAGE_SIZE[1]:
            logger.warning(f"Image too large ({image.width}x{image.height}), resizing...")
            image.thumbnail(MAX_IMAGE_SIZE, Image.Resampling.LANCZOS)
        elif image.width < MIN_IMAGE_SIZE[0] or image.height < MIN_IMAGE_SIZE[1]:
            logger.warning(f"Image too small ({image.width}x{image.height}), skipping OCR")
            return ""

        # Preprocess image
        processed_image = preprocess_image(image)
        
        # Perform OCR with multiple languages if specified
        lang_str = '+'.join(languages)
        custom_config = r'--oem 3 --psm 6'  # OEM 3 = both legacy and LSTM, PSM 6 = assume uniform block of text
        
        text = pytesseract.image_to_string(
            processed_image, 
            lang=lang_str,
            config=custom_config
        )
        
        # Clean up the extracted text
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    except Exception as e:
        logger.error(f"OCR failed: {e}")
        return ""

def extract_images_from_page(page) -> List[Tuple[int, Image.Image]]:
    """Extract and validate images from a PDF page."""
    images = []
    for img_index, img in enumerate(page.get_images(full=True)):
        xref = img[0]
        try:
            base_image = page.parent.extract_image(xref)
            image_bytes = base_image["image"]
            
            with BytesIO(image_bytes) as byte_stream:
                try:
                    image = Image.open(byte_stream)
                    if image.mode not in ['L', 'RGB', 'RGBA']:
                        image = image.convert('RGB')
                    images.append((img_index, image))
                except Exception as img_error:
                    logger.warning(f"Could not open image {img_index + 1}: {img_error}")
        except Exception as e:
            logger.warning(f"Could not extract image {img_index + 1}: {e}")
    
    return images

def extract_text_from_pdf(
    pdf_path: str, 
    languages: List[str] = DEFAULT_LANGUAGES,
    extract_images: bool = True,
    progress_callback: Optional[callable] = None
) -> Tuple[List[str], List[str]]:
    """Extract text and image content from a PDF with enhanced error handling."""
    if not os.path.exists(pdf_path):
        logger.error(f"File not found: {pdf_path}")
        return [], []

    extracted_text = []
    extracted_image_text = []
    total_pages = 0
    processing_time = 0

    try:
        start_time = time.time()
        
        with fitz.open(pdf_path) as pdf_document:
            total_pages = len(pdf_document)
            logger.info(f"Processing {total_pages} pages from {pdf_path}")
            
            for page_num in tqdm(range(total_pages), desc="Processing pages"):
                page = pdf_document[page_num]
                
                # Extract regular text
                text = page.get_text("text", sort=True)  # sort=True for reading order
                if text.strip():
                    extracted_text.append(f"Page {page_num + 1} Text:\n{text}\n")
                
                # Extract text from images if enabled
                if extract_images:
                    images = extract_images_from_page(page)
                    for img_index, image in images:
                        try:
                            img_text = extract_text_from_image(image, languages)
                            if img_text.strip():
                                extracted_image_text.append(
                                    f"Image {img_index + 1} (Page {page_num + 1}) Text:\n{img_text}\n"
                                )
                        except Exception as img_error:
                            logger.warning(f"Could not process image {img_index + 1} on page {page_num + 1}: {img_error}")
                
                if progress_callback:
                    progress_callback(page_num + 1, total_pages)
        
        processing_time = time.time() - start_time
        logger.info(f"PDF processing completed in {processing_time:.2f} seconds")
        logger.info(f"Extracted {len(extracted_text)} text blocks and {len(extracted_image_text)} image texts")
        
        return extracted_text, extracted_image_text

    except Exception as e:
        logger.error(f"Failed to process PDF: {e}", exc_info=True)
        return [], []

def convert_to_excel(
    text_data: List[str], 
    image_text_data: List[str], 
    output_path: str,
    separate_sheets: bool = False
) -> bool:
    """Convert extracted text to an Excel spreadsheet with improved formatting."""
    try:
        writer = pd.ExcelWriter(output_path, engine='openpyxl')
        
        if separate_sheets:
            # Create separate sheets for text and image text
            text_df = pd.DataFrame({"Extracted Text": text_data})
            text_df.to_excel(writer, sheet_name='Document Text', index=False)
            
            img_text_df = pd.DataFrame({"Extracted Image Text": image_text_data})
            img_text_df.to_excel(writer, sheet_name='Image Text', index=False)
        else:
            # Combine all data into one sheet
            combined_data = text_data + image_text_data
            combined_df = pd.DataFrame({"Extracted Content": combined_data})
            combined_df.to_excel(writer, index=False)
        
        # Save the Excel file
        writer.close()
        
        # Validate the output file was created
        if not os.path.exists(output_path):
            raise IOError("Excel file was not created successfully")
        
        logger.info(f"Data successfully saved to Excel: {output_path}")
        return True
    
    except Exception as e:
        logger.error(f"Failed to write Excel file: {e}", exc_info=True)
        return False

def parse_arguments():
    """Enhanced command-line argument parsing with validation."""
    parser = argparse.ArgumentParser(
        description="Advanced PDF text and image extraction tool with OCR capabilities.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "pdf_path",
        help="Path to the input PDF file."
    )
    
    parser.add_argument(
        "output_excel_path",
        help="Path to the output Excel file."
    )
    
    parser.add_argument(
        "--lang",
        default="eng",
        help="OCR language(s) as comma-separated list (e.g., 'eng,spa,fra')."
    )
    
    parser.add_argument(
        "--tesseract_path",
        default=None,
        help="Custom path to Tesseract OCR executable."
    )
    
    parser.add_argument(
        "--no_images",
        action="store_false",
        dest="extract_images",
        help="Disable image text extraction."
    )
    
    parser.add_argument(
        "--separate_sheets",
        action="store_true",
        help="Store document text and image text in separate Excel sheets."
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging."
    )
    
    return parser.parse_args()

def validate_arguments(args) -> bool:
    """Validate command line arguments."""
    if not os.path.exists(args.pdf_path):
        logger.error(f"The specified PDF file does not exist: {args.pdf_path}")
        return False
    
    output_dir = os.path.dirname(args.output_excel_path) or '.'
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
        except Exception as e:
            logger.error(f"Could not create output directory: {e}")
            return False
    
    if not validate_tesseract_path(args.tesseract_path):
        return False
    
    return True

def main():
    args = parse_arguments()
    
    if args.debug:
        logger.setLevel(logging.DEBUG)
    
    if not validate_arguments(args):
        sys.exit(1)
    
    # Parse languages
    languages = [lang.strip() for lang in args.lang.split(',') if lang.strip()]
    
    # Process PDF
    extracted_text, extracted_image_text = extract_text_from_pdf(
        args.pdf_path,
        languages=languages,
        extract_images=args.extract_images
    )
    
    if not extracted_text and not extracted_image_text:
        logger.warning("No data extracted from PDF.")
        sys.exit(1)
    
    # Save to Excel
    success = convert_to_excel(
        extracted_text,
        extracted_image_text,
        args.output_excel_path,
        separate_sheets=args.separate_sheets
    )
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)
