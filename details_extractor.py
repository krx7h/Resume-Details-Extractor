# Import necessary libraries
import pytesseract                      # OCR tool to extract text from images
from pdf2image import convert_from_path # Convert PDF pages to images
import pandas as pd                    # For tabular data storage
import os                              # To read files from directories
import re                              # For pattern matching (email, etc.)
import spacy                           # For extracting names and analyzing text

# Load spaCy's small English model for basic NLP
nlp = spacy.load("en_core_web_sm")

# Define a set of known technical skills to search for in resumes
SKILLS_DATABASE = {
    "python", "java", "c++", "html", "css", "javascript", "sql",
    "machine learning", "data science", "nlp", "excel", "django", "flask"
}

# Function to convert PDF pages into text using OCR
def extract_text_from_pdf(pdf_file_path):
    print(f"🔍 Converting {pdf_file_path} to text...")
    
    # Convert PDF to image pages
    pages = convert_from_path(pdf_file_path)
    full_text = ""

    # Process each page with OCR
    for page_number, image in enumerate(pages):
        print(f"📄 Processing page {page_number + 1}")
        page_text = pytesseract.image_to_string(image)
        full_text += page_text + "\n"

    return full_text

# Function to extract email using regex
def extract_email_from_text(text):
    print("📧 Extracting email...")
    email_pattern = r"\b[\w\.-]+@[\w\.-]+\.\w{2,4}\b"
    match = re.search(email_pattern, text)
    return match.group() if match else "Not Found"

# Function to extract person's name using spaCy NER
def extract_name_from_text(text):
    print("🙍 Extracting name...")
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    return "Not Found"

# Function to identify skills from known skill list
def extract_skills_from_text(text):
    print("🧠 Extracting skills...")
    text = text.lower()
    found_skills = []

    for skill in SKILLS_DATABASE:
        if skill.lower() in text:
            found_skills.append(skill)

    return list(set(found_skills))  # Remove duplicates

# Main function to extract all details from a single resume
def extract_resume_details(pdf_path):
    print(f"\n📁 Reading file: {pdf_path}")

    # Step 1: OCR - Convert PDF to text
    extracted_text = extract_text_from_pdf(pdf_path)

    # Step 2: Extract fields
    name = extract_name_from_text(extracted_text)
    email = extract_email_from_text(extracted_text)
    skills = extract_skills_from_text(extracted_text)

    return {
        "File": os.path.basename(pdf_path),
        "Name": name,
        "Email": email,
        "Skills": ", ".join(skills)
    }

# Function to filter candidates by skill
def filter_candidates_by_skill(dataframe, skill):
    print(f"\n🔍 Filtering candidates with skill: {skill}")
    return dataframe[dataframe["Skills"].str.contains(skill, case=False)]

# Entry point of the script
if __name__ == "__main__":
    # Folder where resumes are stored
    resume_folder = "resumes"

    # List to store each resume's extracted details
    all_resume_data = []

    print("🚀 Starting Resume Extraction...\n")

    # Go through each file in the resumes folder
    for file in os.listdir(resume_folder):
        if file.endswith(".pdf"):
            file_path = os.path.join(resume_folder, file)
            details = extract_resume_details(file_path)
            all_resume_data.append(details)

    # Convert list of dicts to DataFrame
    df = pd.DataFrame(all_resume_data)

    # Save to CSV
    output_path = "output/extracted_data.csv"
    df.to_csv(output_path, index=False)
    print(f"\n✅ Extraction completed. Data saved to {output_path}")

    # Ask HR to filter by a specific skill
    search_skill = input("\n🔎 Enter a skill to filter candidates (e.g., Python): ")
    filtered_df = filter_candidates_by_skill(df, search_skill)

    # Display filtered candidates
    print("\n🎯 Filtered Candidates:")
    print(filtered_df if not filtered_df.empty else "No candidates found with that skill.")
