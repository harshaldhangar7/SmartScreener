import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
import uuid
from werkzeug.utils import secure_filename
from resume_parser import parse_resume
from candidate_ranker import rank_candidates
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default-secret-key-for-development")

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Database models
class Candidate(db.Model):
    __tablename__ = 'candidates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    skills = db.Column(db.JSON)  # List of skills
    experience_years = db.Column(db.Float, default=0)
    education = db.Column(db.JSON)  # List of education objects
    experience_entries = db.Column(db.JSON)  # List of experience objects
    resume_filename = db.Column(db.String(255))
    parsed_date = db.Column(db.DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"<Candidate(id={self.id}, name='{self.name}')>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email if self.email else '',
            'phone': self.phone if self.phone else '',
            'skills': self.skills if self.skills else [],
            'education': self.education if self.education else [],
            'experience_entries': self.experience_entries if self.experience_entries else [],
            'experience_years': self.experience_years,
            'resume_filename': self.resume_filename,
            'parsed_date': self.parsed_date.isoformat() if self.parsed_date else None
        }

class JobDescription(db.Model):
    __tablename__ = 'job_descriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    required_skills = db.Column(db.JSON)  # List of required skills
    min_experience = db.Column(db.Float, default=0)
    created_date = db.Column(db.DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"<JobDescription(id={self.id}, title='{self.title}')>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'required_skills': self.required_skills if self.required_skills else [],
            'min_experience': self.min_experience,
            'created_date': self.created_date.isoformat() if self.created_date else None
        }

# Create database tables
with app.app_context():
    db.create_all()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Render the home page."""
    return render_template('index.html')

@app.route('/upload_resume', methods=['POST'])
def upload_resume():
    """Handle resume upload, parsing and storage."""
    if 'resume' not in request.files:
        flash('No file part', 'danger')
        return redirect(request.url)
    
    file = request.files['resume']
    
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        # Generate a unique filename to avoid collisions
        original_filename = secure_filename(file.filename)
        file_extension = original_filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)
        
        try:
            # Parse the resume
            candidate_data = parse_resume(filepath, original_filename)
            
            # Save candidate data to database
            new_candidate = Candidate(
                name=candidate_data['name'],
                email=candidate_data['email'],
                phone=candidate_data['phone'],
                skills=candidate_data['skills'],
                experience_years=candidate_data['experience_years'],
                education=candidate_data['education'],
                experience_entries=candidate_data['experience_entries'],
                resume_filename=candidate_data['resume_filename'],
                parsed_date=datetime.now()
            )
            db.session.add(new_candidate)
            db.session.commit()
            
            # Remove the file after parsing to save space
            os.remove(filepath)
            
            flash('Resume uploaded and parsed successfully!', 'success')
            return redirect(url_for('candidates'))
        except Exception as e:
            logger.error(f"Error processing resume: {str(e)}")
            flash(f'Error processing resume: {str(e)}', 'danger')
            # Clean up the file if there's an error
            if os.path.exists(filepath):
                os.remove(filepath)
            return redirect(url_for('index'))
    
    flash('Invalid file type. Please upload a PDF or DOCX file.', 'danger')
    return redirect(url_for('index'))

@app.route('/candidates')
def candidates():
    """Display all candidates."""
    all_candidates = Candidate.query.all()
    return render_template('candidates.html', candidates=[c.to_dict() for c in all_candidates])

@app.route('/candidate/<int:candidate_id>')
def candidate_details(candidate_id):
    """Display details for a specific candidate."""
    candidate = Candidate.query.get(candidate_id)
    if candidate:
        return jsonify(candidate.to_dict())
    return jsonify({"error": "Candidate not found"}), 404

@app.route('/candidate/<int:candidate_id>/edit', methods=['GET', 'POST'])
def edit_candidate(candidate_id):
    """Edit a candidate's information."""
    candidate = Candidate.query.get(candidate_id)
    
    if not candidate:
        flash('Candidate not found', 'danger')
        return redirect(url_for('candidates'))
    
    if request.method == 'POST':
        # Update candidate data
        candidate.name = request.form.get('name')
        candidate.email = request.form.get('email')
        candidate.phone = request.form.get('phone')
        
        # Update skills - convert comma-separated string to list
        skills_text = request.form.get('skills', '')
        candidate.skills = [skill.strip() for skill in skills_text.split(',') if skill.strip()]
        
        # Update experience years
        try:
            candidate.experience_years = float(request.form.get('experience_years', 0))
        except ValueError:
            candidate.experience_years = 0
        
        db.session.commit()
        flash('Candidate updated successfully!', 'success')
        return redirect(url_for('candidates'))
    
    # For GET requests, render the edit form
    return render_template('edit_candidate.html', candidate=candidate.to_dict())

@app.route('/candidate/<int:candidate_id>/delete', methods=['POST'])
def delete_candidate(candidate_id):
    """Delete a candidate."""
    candidate = Candidate.query.get(candidate_id)
    
    if not candidate:
        flash('Candidate not found', 'danger')
    else:
        db.session.delete(candidate)
        db.session.commit()
        flash('Candidate deleted successfully!', 'success')
    
    return redirect(url_for('candidates'))

@app.route('/job_description', methods=['GET', 'POST'])
def job_description():
    """Add or view job descriptions."""
    if request.method == 'POST':
        job_data = {
            'title': request.form.get('title'),
            'required_skills': request.form.get('required_skills').split(','),
            'min_experience': request.form.get('min_experience', 0)
        }
        
        # Clean and normalize the skills
        job_data['required_skills'] = [skill.strip().lower() for skill in job_data['required_skills'] if skill.strip()]
        
        # Save job description
        job_id = save_job_description(job_data)
        
        flash('Job description saved successfully!', 'success')
        return redirect(url_for('ranking', job_id=job_id))
    
    return render_template('job_description.html', job_descriptions=get_all_job_descriptions())

@app.route('/ranking/<job_id>')
def ranking(job_id):
    """Rank candidates based on a job description."""
    job = get_job_description(job_id)
    if not job:
        flash('Job description not found', 'danger')
        return redirect(url_for('job_description'))
    
    candidates = get_all_candidates()
    ranked_candidates = rank_candidates(candidates, job)
    
    return render_template('ranking.html', job=job, ranked_candidates=ranked_candidates)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
