# import pdfplumber

# # Path to your PDF file
# pdf_path = "C:/Users/hp/OneDrive/Desktop/ResumeParser/resumes/Antonios F. Takos - Resume.pdf"

# # Initialize an empty string to store the extracted text
# text_content = ""

# # Open the PDF
# with pdfplumber.open(pdf_path) as pdf:
#     # Iterate through each page
#     for page in pdf.pages:
#         # Extract text from the page and add it to the string
#         text_content += page.extract_text() + "\n"

# # Print or process the extracted text
# print(text_content)
import pdfplumber
import re
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List

app = FastAPI()

# Allow CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Define regex patterns for different sections
SECTION_PATTERNS = {
    "experience": r"(?i)\bexperience\b[:\-]?\s*(.*?)(?=\b(?:projects|skills|certifications|education|$)\b)",
    "projects": r"(?i)\bprojects\b[:\-]?\s*(.*?)(?=\b(?:experience|skills|certifications|education|$)\b)",
    "skills": r"(?i)\bskills\b[:\-]?\s*(.*?)(?=\b(?:experience|projects|certifications|education|$)\b)",
    "certifications": r"(?i)\bcertifications\b[:\-]?\s*(.*?)(?=\b(?:experience|projects|skills|education|$)\b)",
    "education": r"(?i)\beducation\b[:\-]?\s*(.*?)(?=\b(?:experience|projects|skills|certifications|$)\b)"
}

# Helper function to extract text from the PDF
def extract_text_from_pdf(file: UploadFile) -> str:
    text_content = ""
    with pdfplumber.open(file.file) as pdf:
        for page in pdf.pages:
            text_content += page.extract_text() + "\n"
    return text_content

# Helper function to extract sections based on patterns
def extract_sections(text: str) -> Dict[str, List[str]]:
    sections = {}

    # Assume the first line is the name
    first_line = text.splitlines()[0].strip()
    sections["name"] = first_line if first_line else "Not Found"

    # Extract all instances for other sections
    for section, pattern in SECTION_PATTERNS.items():
        match = re.search(pattern, text, re.DOTALL)
        if match:
            # Split by lines and clean up whitespace
            sections[section] = [line.strip() for line in match.group(1).strip().splitlines() if line.strip()]
        else:
            sections[section] = ["Not Found"]
    
    return sections

# FastAPI endpoint to receive PDF and return JSON
@app.post("/extract_resume/")
async def extract_resume(file: UploadFile = File(...)):
    # Extract the full text from the PDF
    text = extract_text_from_pdf(file)
    
    # Extract specific sections from the text
    extracted_info = extract_sections(text)
    
    return extracted_info
