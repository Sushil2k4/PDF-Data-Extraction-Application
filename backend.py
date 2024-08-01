#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os
import PyPDF2
import pandas as pd
import pytesseract
import cv2
from flask import Flask, request, jsonify
from pdf2image import convert_from_path
from PIL import Image

app = Flask(__name__)

def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfFileReader(file)
        for page_num in range(reader.numPages):
            text += reader.getPage(page_num).extract_text()
    return text

def extract_images_from_pdf(pdf_path, output_folder):
    images = convert_from_path(pdf_path)
    image_paths = []
    for i, image in enumerate(images):
        image_path = os.path.join(output_folder, f'image_{i}.png')
        image.save(image_path, 'PNG')
        image_paths.append(image_path)
    return image_paths

def extract_marks_from_images(image_paths):
    results = []
    for image_path in image_paths:
        image = cv2.imread(image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            roi = binary[y:y+h, x:x+w]
            text = pytesseract.image_to_string(roi, config='--psm 6')
            if 'x' in text.lower() or '✓' in text:
                results.append((x, y, text))
    return results

def convert_to_csv(data, output_path):
    df = pd.DataFrame(data)
    df.to_csv(output_path, index=False)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"})
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"})
    if file:
        file_path = os.path.join("./", file.filename)
        file.save(file_path)
        text = extract_text_from_pdf(file_path)
        output_folder = "./extracted_images"
        os.makedirs(output_folder, exist_ok=True)
        image_paths = extract_images_from_pdf(file_path, output_folder)
        marks = extract_marks_from_images(image_paths)
        data = {
            'text': [text],
            'marks': [marks],
        }
        output_csv_path = "./extracted_data.csv"
        convert_to_csv(data, output_csv_path)
        with open(output_csv_path, 'r') as f:
            csv_content = f.read()
        return jsonify({"csv": csv_content})

if __name__ == '__main__':
    app.run(port=5000)


# In[2]:


pip install pdf2image


# In[ ]:




