import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
import uuid
from werkzeug.utils import secure_filename
from resume_parser import parse_resume
from data_storage import save_candidate, get_all_candidates, get_candidate, save_job_description, get_job_description, get_all_job_descriptions
from candidate_ranker import rank_candidates

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default-secret-key-for-development")

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
            
            # Save candidate data
            candidate_id = save_candidate(candidate_data)
            
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
    all_candidates = get_all_candidates()
    return render_template('candidates.html', candidates=all_candidates)

@app.route('/candidate/<candidate_id>')
def candidate_details(candidate_id):
    """Display details for a specific candidate."""
    candidate = get_candidate(candidate_id)
    if candidate:
        return jsonify(candidate)
    return jsonify({"error": "Candidate not found"}), 404

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
