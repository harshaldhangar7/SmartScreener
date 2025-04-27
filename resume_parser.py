import os
import re
import logging
from datetime import datetime
import spacy
import fitz  # PyMuPDF
import docx
from pdfminer.high_level import extract_text as pdfminer_extract_text

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load spaCy model for NLP processing
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    # If model not found, download it
    import spacy.cli
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# Common technical skills to look for in resumes
COMMON_SKILLS = [
    # Programming languages
    "python", "java", "javascript", "c++", "c#", "ruby", "php", "swift", "kotlin", "go", "typescript",
    # Web technologies
    "html", "css", "react", "angular", "vue", "node.js", "express", "django", "flask", "spring boot",
    # Databases
    "sql", "mysql", "postgresql", "mongodb", "oracle", "sqlite", "elasticsearch", "redis", "cassandra",
    # Cloud platforms
    "aws", "azure", "gcp", "google cloud", "heroku", "kubernetes", "docker", "terraform",
    # Data science
    "machine learning", "deep learning", "data analysis", "pandas", "numpy", "tensorflow", "pytorch",
    "scikit-learn", "r", "hadoop", "spark", "tableau", "power bi", "data visualization",
    # Other skills
    "git", "github", "ci/cd", "jenkins", "jira", "agile", "scrum", "devops", "restful api", "graphql"
]

def extract_text_from_pdf_pymupdf(pdf_path):
    """Extract text from PDF using PyMuPDF."""
    try:
        text = ""
        doc = fitz.open(pdf_path)
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        logger.error(f"PyMuPDF extraction failed: {str(e)}")
        return None

def extract_text_from_pdf_pdfminer(pdf_path):
    """Extract text from PDF using pdfminer as a fallback method."""
    try:
        return pdfminer_extract_text(pdf_path)
    except Exception as e:
        logger.error(f"PDFMiner extraction failed: {str(e)}")
        return ""

def extract_text_from_docx(docx_path):
    """Extract text from DOCX file."""
    try:
        doc = docx.Document(docx_path)
        text = []
        for paragraph in doc.paragraphs:
            text.append(paragraph.text)
        return '\n'.join(text)
    except Exception as e:
        logger.error(f"DOCX extraction failed: {str(e)}")
        return ""

def extract_name(text):
    """Extract candidate name from the text."""
    # Basic name extraction using the first few lines
    lines = text.split('\n')
    for i in range(min(5, len(lines))):
        line = lines[i].strip()
        # Skip very short lines or lines that look like titles/headers
        if len(line) > 2 and len(line.split()) <= 4 and not any(x in line.lower() for x in ["resume", "cv", "curriculum", "vitae"]):
            return line
    
    # Fallback to NLP
    doc = nlp(text[:1000])  # Process just the beginning for efficiency
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    
    return "Unknown"

def extract_contact_info(text):
    """Extract email and phone from text."""
    # Email extraction
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    email = emails[0] if emails else ""
    
    # Phone extraction
    phone_pattern = r'\b(?:\+\d{1,3}[-\.\s]?)?\(?\d{3}\)?[-\.\s]?\d{3}[-\.\s]?\d{4}\b'
    phones = re.findall(phone_pattern, text)
    phone = phones[0] if phones else ""
    
    return email, phone

def extract_education(text):
    """Extract education information from the text."""
    education = []
    
    # Look for education section
    education_section = ""
    sections = re.split(r'\n\s*(?:EDUCATION|Education|ACADEMIC|Academic).*?\n', text, flags=re.IGNORECASE)
    if len(sections) > 1:
        education_section = sections[1].split('\n\n')[0]
    
    # Find degrees
    degree_patterns = [
        r'\b(?:B\.?S\.?|Bachelor of Science|Bachelor\'s)\b',
        r'\b(?:B\.?A\.?|Bachelor of Arts)\b',
        r'\b(?:M\.?S\.?|Master of Science|Master\'s)\b',
        r'\b(?:M\.?B\.?A\.?|Master of Business Administration)\b',
        r'\b(?:Ph\.?D\.?|Doctor of Philosophy|Doctorate)\b'
    ]
    
    for pattern in degree_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            # Get the surrounding context (30 chars before and after)
            start = max(0, match.start() - 30)
            end = min(len(text), match.end() + 30)
            context = text[start:end]
            
            # Look for a year in the context
            year_match = re.search(r'20\d\d|19\d\d', context)
            year = year_match.group(0) if year_match else ""
            
            # Look for university name
            univ_match = re.search(r'\b(?:University|College|Institute|School) of [A-Za-z\s]+\b', context)
            if not univ_match:
                univ_match = re.search(r'\b[A-Z][a-z]+ (?:University|College|Institute|School)\b', context)
            
            university = univ_match.group(0) if univ_match else ""
            
            # Add to education list
            degree_info = {
                "degree": match.group(0),
                "university": university,
                "year": year
            }
            education.append(degree_info)
    
    return education

def extract_skills(text):
    """Extract skills from the text."""
    skills = []
    text_lower = text.lower()
    
    # Check for common skills
    for skill in COMMON_SKILLS:
        if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
            skills.append(skill)
    
    # Look for skills section
    skills_section = ""
    sections = re.split(r'\n\s*(?:SKILLS|Skills|TECHNICAL SKILLS|Technical Skills).*?\n', text, flags=re.IGNORECASE)
    if len(sections) > 1:
        skills_section = sections[1].split('\n\n')[0]
        
        # Process skills section with NLP
        doc = nlp(skills_section)
        for chunk in doc.noun_chunks:
            skill = chunk.text.lower().strip()
            # Filter out stop words and very short skills
            if len(skill) > 2 and skill not in skills:
                skills.append(skill)
    
    return list(set(skills))  # Remove duplicates

def extract_experience(text):
    """Extract work experience and total years."""
    experience_entries = []
    total_years = 0
    
    # Look for experience section
    experience_section = ""
    sections = re.split(r'\n\s*(?:EXPERIENCE|Experience|WORK EXPERIENCE|Work Experience|PROFESSIONAL EXPERIENCE|Professional Experience).*?\n', text, flags=re.IGNORECASE)
    if len(sections) > 1:
        experience_section = sections[1]
    
    # Extract job titles, companies, and dates
    job_patterns = [
        r'(?P<title>[A-Z][A-Za-z\s]+?)\s+(?:at|@)\s+(?P<company>[A-Z][A-Za-z\s]+)\s+(?P<date>\d{1,2}/\d{1,2}|\d{4}\s*[-–—]\s*(?:Present|Current|\d{4}))',
        r'(?P<company>[A-Z][A-Za-z\s]+)\s*[,|\|]\s*(?P<title>[A-Za-z\s]+?)\s+(?P<date>\d{1,2}/\d{1,2}|\d{4}\s*[-–—]\s*(?:Present|Current|\d{4}))',
        r'(?P<title>[A-Z][A-Za-z\s]+?)\n(?P<company>[A-Z][A-Za-z\s]+)\n(?P<date>\d{1,2}/\d{1,2}|\d{4}\s*[-–—]\s*(?:Present|Current|\d{4}))'
    ]
    
    for pattern in job_patterns:
        for match in re.finditer(pattern, text, re.MULTILINE):
            title = match.group('title').strip()
            company = match.group('company').strip()
            date_str = match.group('date').strip()
            
            start_year = None
            end_year = None
            
            # Parse the date string to extract years
            date_match = re.search(r'(\d{4})\s*[-–—]\s*(\d{4}|Present|Current)', date_str)
            if date_match:
                start_year = int(date_match.group(1))
                end_year_str = date_match.group(2)
                if end_year_str.lower() in ['present', 'current']:
                    end_year = datetime.now().year
                else:
                    end_year = int(end_year_str)
            
            if start_year and end_year:
                years = end_year - start_year
                total_years += years
                
                experience_entries.append({
                    'title': title,
                    'company': company,
                    'start_year': start_year,
                    'end_year': end_year_str,
                    'duration': years
                })
    
    # If we couldn't extract specific experiences, make a rough estimate from the text
    if not experience_entries:
        # Look for years of experience
        exp_match = re.search(r'(\d+)\+?\s*(?:years|yrs)(?:\s+of)?\s+experience', text, re.IGNORECASE)
        if exp_match:
            total_years = int(exp_match.group(1))
    
    return experience_entries, total_years

def parse_resume(file_path, original_filename):
    """Parse resume and extract relevant information."""
    # Determine file type
    file_extension = os.path.splitext(original_filename)[1].lower()
    
    # Extract text based on file type
    if file_extension == '.pdf':
        text = extract_text_from_pdf_pymupdf(file_path)
        if not text:  # If PyMuPDF fails, try PDFMiner
            text = extract_text_from_pdf_pdfminer(file_path)
    elif file_extension in ['.docx', '.doc']:
        text = extract_text_from_docx(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_extension}")
    
    if not text:
        raise ValueError("Failed to extract text from the document")
    
    # Extract information from text
    name = extract_name(text)
    email, phone = extract_contact_info(text)
    education = extract_education(text)
    skills = extract_skills(text)
    experience_entries, total_years = extract_experience(text)
    
    # Compile candidate data
    candidate_data = {
        'id': os.urandom(8).hex(),
        'name': name,
        'email': email,
        'phone': phone,
        'skills': skills,
        'education': education,
        'experience_entries': experience_entries,
        'experience_years': total_years,
        'resume_filename': original_filename,
        'parsed_date': datetime.now().isoformat()
    }
    
    return candidate_data
