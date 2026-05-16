import random
import json
from datetime import datetime
from app import app, db, Candidate

# Sample data for generation
first_names = ['John', 'Jane', 'Michael', 'Sarah', 'David', 'Emily', 'Chris', 'Anna', 'Robert', 'Lisa']
last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez']
domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']
skills_list = [
    'Python', 'Java', 'JavaScript', 'C++', 'SQL', 'Machine Learning', 'Data Analysis',
    'React', 'Node.js', 'AWS', 'Docker', 'Git', 'Agile', 'Scrum', 'HTML', 'CSS'
]
degrees = ['Bachelor of Science', 'Master of Science', 'PhD', 'Bachelor of Arts', 'MBA']
fields = ['Computer Science', 'Engineering', 'Mathematics', 'Business', 'Physics']
job_titles = ['Software Engineer', 'Data Scientist', 'Product Manager', 'Designer', 'Analyst']
companies = ['Google', 'Microsoft', 'Amazon', 'Apple', 'Facebook', 'Tesla', 'Netflix']

def generate_candidate():
    first = random.choice(first_names)
    last = random.choice(last_names)
    name = f"{first} {last}"
    email = f"{first.lower()}.{last.lower()}@{random.choice(domains)}"
    phone = f"+1{random.randint(1000000000, 9999999999)}"
    gender = random.choice(['Male', 'Female'])
    ethnicity = random.choice(['Caucasian', 'African American', 'Hispanic', 'Asian', 'Other'])
    num_skills = random.randint(3, 8)
    skills = random.sample(skills_list, num_skills)
    experience_years = random.uniform(0, 15)
    education = []
    num_degrees = random.randint(1, 3)
    for _ in range(num_degrees):
        degree = random.choice(degrees)
        field = random.choice(fields)
        year = random.randint(2000, 2023)
        university = f"{random.choice(['University of', 'College of', 'Institute of'])} {random.choice(['California', 'New York', 'Texas', 'Florida'])}"
        education.append({
            'degree': degree,
            'field': field,
            'university': university,
            'year': str(year)
        })
    experience_entries = []
    num_jobs = random.randint(1, 5)
    current_year = 2023
    for i in range(num_jobs):
        title = random.choice(job_titles)
        company = random.choice(companies)
        start_year = current_year - random.randint(1, 5)
        end_year = current_year if i == 0 else start_year + random.randint(1, 4)
        experience_entries.append({
            'title': title,
            'company': company,
            'start_year': start_year,
            'end_year': end_year,
            'duration': end_year - start_year
        })
        current_year = start_year
    return {
        'name': name,
        'email': email,
        'phone': phone,
        'gender': gender,
        'ethnicity': ethnicity,
        'skills': skills,
        'experience_years': experience_years,
        'education': education,
        'experience_entries': experience_entries,
        'resume_filename': f"{name.replace(' ', '_')}.pdf"
    }

def main(num_candidates=150):
    with app.app_context():
        # Clear existing candidates
        Candidate.query.delete()
        db.session.commit()
        
        for i in range(num_candidates):
            data = generate_candidate()
            candidate = Candidate(
                name=data['name'],
                email=data['email'],
                phone=data['phone'],
                gender=data['gender'],
                ethnicity=data['ethnicity'],
                skills=data['skills'],
                experience_years=data['experience_years'],
                education=data['education'],
                experience_entries=data['experience_entries'],
                resume_filename=data['resume_filename'],
                parsed_date=datetime.now()
            )
            db.session.add(candidate)
        db.session.commit()
        print(f"Generated {num_candidates} synthetic candidates.")

if __name__ == '__main__':
    main()