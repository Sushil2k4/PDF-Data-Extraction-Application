# PDF-Data-Extraction-Application 📄💻
A Python-based application that extracts data from customer-filled PDF forms, converts the extracted data into structured formats such as Excel or CSV, and handles images within the PDF. This project was developed as part of a hackathon to solve a real-world problem 🤔.

## Features 📝
Accurately extracts text and selection marks from PDF forms 📄
Identifies and interprets tick marks, cross marks, and shaded boxes to determine selected options 📝
Handles and processes images within the PDF using OCR technology 📸
Converts extracted data into structured formats such as Excel or CSV 📊
Supports multi-language text extraction and processing 🌎
Uses machine learning models to recognize and interpret marks on forms 🤖
Integrates with the Gemini API (if applicable) for additional processing needs 📈
Includes a simple user interface using Flask to upload PDFs and download processed files 📁

## Technologies Used 💻
Python 3.x 🐍
PyPDF2 for PDF text extraction 📄
Pillow and OpenCV for image processing 📸
pytesseract for OCR 📊
pandas for data manipulation and conversion to Excel/CSV 📈
TensorFlow or PyTorch for machine learning 🤖
Flask for frontend development 📁
Gemini API (if applicable) for API integration 📈

## Getting Started 🚀
Prerequisites 📝
Python 3.8+ 🐍
PyPDF2 📄
Pillow 📸
OpenCV 📸
pytesseract 📊
pandas 📈
TensorFlow or PyTorch (for machine learning) 🤖
Flask (for frontend) 📁
Gemini API key (if applicable) 📈

## Installation 📦
Clone the repository: git clone https://github.com/your-username/pdf-data-extraction-app.git 📁
Install the required libraries: pip install -r requirements.txt 📈
Set up the Gemini API key (if applicable): export GEMINI_API_KEY=YOUR_API_KEY 📝

## Running the App 🚀
Run the Flask app: python app.py 📁
Open a web browser and navigate to http://localhost:5000 📊
Upload a PDF file and download the processed file 📁

## Documentation 📚
README.md for setup and run instructions 📝
docs/implementation_details.md for implementation details and architecture diagrams 📊
docs/testing.md for testing information 📝

## Contributors 👥
[Sushil Kumar Mishra] (Team Lead) 👨‍💻 <br/>
[Sushil Kumar Mishra] (Developer) 👨‍💻 <br/>
[Divyansh Kumar Singh] (Developer) 👨‍💻 

## Machine Learning 🤖
The app uses pre-trained models or custom models to recognize and interpret marks on forms. We use libraries like TensorFlow or PyTorch to implement these models. For example, we can use a convolutional neural network (CNN) to classify images of tick marks, cross marks, and shaded boxes 📸.

## API Integration 📈
The app integrates with the Gemini API (if applicable) to perform additional processing needs. We use the requests library to make API calls 📊.

## Frontend 📁
The app includes a simple user interface using Flask to upload PDFs and download processed files 📁.
