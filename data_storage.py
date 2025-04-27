import os
import json
import uuid
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Ensure data directory exists
DATA_DIR = 'data'
CANDIDATES_FILE = os.path.join(DATA_DIR, 'candidates.json')
JOB_DESCRIPTIONS_FILE = os.path.join(DATA_DIR, 'job_descriptions.json')

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Initialize data files if they don't exist
def initialize_data_files():
    if not os.path.exists(CANDIDATES_FILE):
        with open(CANDIDATES_FILE, 'w') as f:
            json.dump([], f)
    
    if not os.path.exists(JOB_DESCRIPTIONS_FILE):
        with open(JOB_DESCRIPTIONS_FILE, 'w') as f:
            json.dump([], f)

initialize_data_files()

def save_candidate(candidate_data):
    """Save candidate data to the JSON file."""
    try:
        # Generate ID if not present
        if 'id' not in candidate_data:
            candidate_data['id'] = str(uuid.uuid4())
        
        # Add timestamp if not present
        if 'parsed_date' not in candidate_data:
            candidate_data['parsed_date'] = datetime.now().isoformat()
        
        # Load existing data
        candidates = []
        if os.path.exists(CANDIDATES_FILE) and os.path.getsize(CANDIDATES_FILE) > 0:
            with open(CANDIDATES_FILE, 'r') as f:
                candidates = json.load(f)
        
        # Add new candidate
        candidates.append(candidate_data)
        
        # Save updated data
        with open(CANDIDATES_FILE, 'w') as f:
            json.dump(candidates, f, indent=2)
        
        return candidate_data['id']
    
    except Exception as e:
        logger.error(f"Error saving candidate data: {str(e)}")
        raise

def get_all_candidates():
    """Get all candidates from the JSON file."""
    try:
        if os.path.exists(CANDIDATES_FILE) and os.path.getsize(CANDIDATES_FILE) > 0:
            with open(CANDIDATES_FILE, 'r') as f:
                return json.load(f)
        return []
    
    except Exception as e:
        logger.error(f"Error loading candidate data: {str(e)}")
        return []

def get_candidate(candidate_id):
    """Get a specific candidate by ID."""
    try:
        candidates = get_all_candidates()
        for candidate in candidates:
            if candidate['id'] == candidate_id:
                return candidate
        return None
    
    except Exception as e:
        logger.error(f"Error getting candidate: {str(e)}")
        return None

def save_job_description(job_data):
    """Save job description to the JSON file."""
    try:
        # Generate ID if not present
        if 'id' not in job_data:
            job_data['id'] = str(uuid.uuid4())
        
        # Add timestamp
        job_data['created_date'] = datetime.now().isoformat()
        
        # Load existing data
        job_descriptions = []
        if os.path.exists(JOB_DESCRIPTIONS_FILE) and os.path.getsize(JOB_DESCRIPTIONS_FILE) > 0:
            with open(JOB_DESCRIPTIONS_FILE, 'r') as f:
                job_descriptions = json.load(f)
        
        # Add new job description
        job_descriptions.append(job_data)
        
        # Save updated data
        with open(JOB_DESCRIPTIONS_FILE, 'w') as f:
            json.dump(job_descriptions, f, indent=2)
        
        return job_data['id']
    
    except Exception as e:
        logger.error(f"Error saving job description: {str(e)}")
        raise

def get_all_job_descriptions():
    """Get all job descriptions from the JSON file."""
    try:
        if os.path.exists(JOB_DESCRIPTIONS_FILE) and os.path.getsize(JOB_DESCRIPTIONS_FILE) > 0:
            with open(JOB_DESCRIPTIONS_FILE, 'r') as f:
                return json.load(f)
        return []
    
    except Exception as e:
        logger.error(f"Error loading job descriptions: {str(e)}")
        return []

def get_job_description(job_id):
    """Get a specific job description by ID."""
    try:
        job_descriptions = get_all_job_descriptions()
        for job in job_descriptions:
            if job['id'] == job_id:
                return job
        return None
    
    except Exception as e:
        logger.error(f"Error getting job description: {str(e)}")
        return None
