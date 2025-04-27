import logging
import spacy
from collections import defaultdict

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

def normalize_skill(skill):
    """Normalize skill string for better matching."""
    return skill.strip().lower()

def get_skill_similarity(skill1, skill2):
    """Calculate semantic similarity between two skills."""
    # Simple string matching first
    if normalize_skill(skill1) == normalize_skill(skill2):
        return 1.0
    
    # Use spaCy for semantic similarity
    doc1 = nlp(skill1)
    doc2 = nlp(skill2)
    
    # If either doc is empty, return 0
    if not doc1 or not doc2:
        return 0
    
    # Calculate similarity
    return doc1.similarity(doc2)

def calculate_skill_match_score(candidate_skills, required_skills, threshold=0.8):
    """Calculate the skill match score for a candidate.
    
    Args:
        candidate_skills: List of candidate's skills
        required_skills: List of skills required for the job
        threshold: Similarity threshold to consider a skill match
    
    Returns:
        float: Score between 0 and 1 representing the match percentage
    """
    if not required_skills:
        return 1.0  # Perfect match if no skills required
    
    # Normalize skills
    norm_candidate_skills = [normalize_skill(skill) for skill in candidate_skills]
    norm_required_skills = [normalize_skill(skill) for skill in required_skills]
    
    total_matches = 0
    
    # Track matches to avoid double counting
    matched_candidate_skills = set()
    
    # For each required skill, find the best matching candidate skill
    for req_skill in norm_required_skills:
        best_match_score = 0
        best_match_idx = -1
        
        for i, cand_skill in enumerate(norm_candidate_skills):
            if i in matched_candidate_skills:
                continue  # Skip already matched skills
                
            # Calculate similarity
            similarity = get_skill_similarity(req_skill, cand_skill)
            
            if similarity > best_match_score:
                best_match_score = similarity
                best_match_idx = i
        
        # If we found a good match
        if best_match_score >= threshold:
            total_matches += best_match_score
            if best_match_idx != -1:
                matched_candidate_skills.add(best_match_idx)
    
    # Calculate score as a percentage of required skills matched
    return total_matches / len(required_skills)

def calculate_experience_score(candidate_exp_years, min_experience):
    """Calculate experience match score."""
    try:
        min_exp = float(min_experience)
    except (ValueError, TypeError):
        min_exp = 0
    
    if min_exp <= 0:
        return 1.0  # No minimum experience required
    
    try:
        candidate_exp = float(candidate_exp_years)
    except (ValueError, TypeError):
        candidate_exp = 0
    
    if candidate_exp < min_exp:
        # Partial credit for experience close to the minimum
        return max(0, candidate_exp / min_exp)
    else:
        # Full credit for meeting minimum plus bonus for extra experience (capped at 1.5)
        extra_exp_bonus = min(0.5, (candidate_exp - min_exp) / (min_exp * 2))
        return 1.0 + extra_exp_bonus

def rank_candidates(candidates, job_description):
    """Rank candidates based on job requirements.
    
    Args:
        candidates: List of candidate dictionaries
        job_description: Dictionary with job requirements
    
    Returns:
        List of dictionaries with candidates and their scores, sorted by score
    """
    required_skills = job_description.get('required_skills', [])
    min_experience = job_description.get('min_experience', 0)
    
    ranked_candidates = []
    
    for candidate in candidates:
        # Calculate skill match score (weight: 70%)
        skill_score = calculate_skill_match_score(
            candidate.get('skills', []), 
            required_skills
        )
        
        # Calculate experience score (weight: 30%)
        exp_score = calculate_experience_score(
            candidate.get('experience_years', 0),
            min_experience
        )
        
        # Calculate total score (weighted average)
        total_score = (skill_score * 0.7) + (exp_score * 0.3)
        
        # Add to ranked list
        ranked_candidates.append({
            'candidate': candidate,
            'skill_score': skill_score,
            'exp_score': exp_score,
            'total_score': total_score,
            'matched_skills': get_matched_skills(candidate.get('skills', []), required_skills)
        })
    
    # Sort by total score (descending)
    ranked_candidates.sort(key=lambda x: x['total_score'], reverse=True)
    
    return ranked_candidates

def get_matched_skills(candidate_skills, required_skills, threshold=0.8):
    """Get a list of matched skills for display purposes."""
    if not required_skills or not candidate_skills:
        return []
    
    # Normalize skills
    norm_candidate_skills = [normalize_skill(skill) for skill in candidate_skills]
    norm_required_skills = [normalize_skill(skill) for skill in required_skills]
    
    matched_skills = []
    
    for req_skill in norm_required_skills:
        best_match = None
        best_score = 0
        
        for cand_skill in norm_candidate_skills:
            similarity = get_skill_similarity(req_skill, cand_skill)
            if similarity >= threshold and similarity > best_score:
                best_match = {'required': req_skill, 'candidate': cand_skill, 'score': similarity}
                best_score = similarity
                
        if best_match:
            matched_skills.append(best_match)
    
    return matched_skills
