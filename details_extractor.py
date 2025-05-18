# Import necessary libraries
import pytesseract                        # OCR tool to extract text from images
from pdf2image import convert_from_path  # Convert PDF pages to images
import pandas                            # For working with tabular data
import os                                # For accessing file directories
import re                                # For pattern matching (like emails)
import spacy                             # For Natural Language Processing

# Load spaCy's small English model
nlp_model = spacy.load("en_core_web_sm")

# Predefined list of known technical skills
list_of_known_skills = [
    "python", "java", "c++", "html", "css", "javascript", "sql",
    "machine learning", "data science", "nlp", "excel", "django", "flask"
]

# Function to convert a PDF to text using OCR
def get_text_from_pdf(pdf_file_path):
    print(f"Converting PDF file: {pdf_file_path} into text")

    all_text = ""

    # Convert each page in the PDF into an image
    pages_as_images = convert_from_path(pdf_file_path)

    # Apply OCR on each image to extract text
    for page_index, image in enumerate(pages_as_images):
        print(f"Processing page {page_index + 1}")
        text_from_page = pytesseract.image_to_string(image)
        all_text = all_text + text_from_page + "\n"

    return all_text

# Function to extract email address from text
def get_email_address(text_input):
    print("Extracting email address from text...")
    email_regex_pattern = r"\b[\w\.-]+@[\w\.-]+\.\w{2,4}\b"
    match_result = re.search(email_regex_pattern, text_input)
    if match_result:
        return match_result.group()
    else:
        return "Not Found"

# Function to extract name using spaCy NER
def get_person_name(text_input):
    print("Extracting person name from text...")
    document = nlp_model(text_input)
    for entity in document.ents:
        if entity.label_ == "PERSON":
            return entity.text
    return "Not Found"

# Function to identify skills from the skill list
def get_skills_from_text(text_input):
    print("Extracting skills from text...")
    text_lowercase = text_input.lower()
    found_skills_list = []

    for skill in list_of_known_skills:
        if skill.lower() in text_lowercase:
            found_skills_list.append(skill)

    # Return unique values only
    return list(set(found_skills_list))

# Function to extract all resume information
def extract_resume_information(pdf_path):
    print(f"\nReading Resume File: {pdf_path}")

    text_from_resume = get_text_from_pdf(pdf_path)

    extracted_name = get_person_name(text_from_resume)
    extracted_email = get_email_address(text_from_resume)
    extracted_skills = get_skills_from_text(text_from_resume)

    return {
        "File Name": os.path.basename(pdf_path),
        "Candidate Name": extracted_name,
        "Email": extracted_email,
        "Skills": ", ".join(extracted_skills)
    }

# Function to filter candidates based on skill
def filter_by_required_skill(data_frame, required_skill):
    print(f"\nFiltering candidates who have the skill: {required_skill}")
    return data_frame[data_frame["Skills"].str.contains(required_skill, case=False)]

# Main logic of the script
if __name__ == "__main__":
    folder_path_for_resumes = "resumes"
    list_of_all_resume_data = []

    print("Starting Resume Extraction Process...\n")

    # Loop through all PDF files in the folder
    for single_file in os.listdir(folder_path_for_resumes):
        if single_file.endswith(".pdf"):
            full_file_path = os.path.join(folder_path_for_resumes, single_file)
            resume_info = extract_resume_information(full_file_path)
            list_of_all_resume_data.append(resume_info)

    # Convert list to DataFrame
    resume_data_frame = pandas.DataFrame(list_of_all_resume_data)

    # Save extracted data to a CSV file
    output_file_path = "output/extracted_resume_data.csv"
    resume_data_frame.to_csv(output_file_path, index=False)
    print(f"\nAll data has been saved to: {output_file_path}")

    # Ask the user to enter a skill to filter
    required_skill_input = input("\nEnter a skill to filter candidates (e.g., Python): ")
    filtered_candidates = filter_by_required_skill(resume_data_frame, required_skill_input)

    # Show results
    print("\nFiltered Candidates:")
    if not filtered_candidates.empty:
        print(filtered_candidates)
    else:
        print("No candidates found with the specified skill.")
