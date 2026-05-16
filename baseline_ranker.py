from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def rank_candidates_baseline(candidates, job_description):
    """
    Ranks candidates using a traditional TF-IDF keyword matching model.
    This serves as the baseline for research comparison.
    """
    
    # Create a corpus of text from the job description and each candidate's resume
    job_text = f"{job_description.get('title', '')} {' '.join(job_description.get('required_skills', []))}"
    
    candidate_texts = []
    for candidate in candidates:
        # Combine key fields from the candidate's profile for TF-IDF
        cand_text = f"{' '.join(candidate.get('skills', []))} {' '.join([exp.get('title','') for exp in (candidate.get('experience_entries') or []) if isinstance(exp, dict)])}"
        candidate_texts.append(cand_text)

    if not any(candidate_texts):
        # If all candidate texts are empty, return a zero-scored list with minimal structure
        return [{
            'candidate': c,
            'total_score': 0.0,
            'skill_score': 0.0,
            'exp_score': 0.0,
            'edu_score': 0.0,
            'semantic_similarity_score': 0.0,
            'matched_skills': {'matched': [], 'missing': job_description.get('required_skills', [])},
            'edu_analytics': {'details': []}
        } for c in candidates]

    # Vectorize the corpus
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform([job_text] + candidate_texts)

    # Calculate cosine similarity between the job description (first doc) and all candidates
    cosine_similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

    ranked_candidates = []
    for i, candidate in enumerate(candidates):
        # For baseline, we only have TF-IDF similarity, so set other scores to 0 or estimate
        total_score = float(cosine_similarities[i])
        # Approximate skill score from TF-IDF (since TF-IDF is mainly on skills)
        skill_score = min(total_score * 1.5, 1.0)  # Boost a bit since it's skill-focused
        ranked_candidates.append({
            'candidate': candidate,
            'total_score': total_score,
            'skill_score': skill_score,
            'exp_score': 0.0,  # Baseline doesn't analyze experience
            'edu_score': 0.0,  # Baseline doesn't analyze education
            'semantic_similarity_score': total_score,  # Use TF-IDF as semantic proxy
            'matched_skills': {'matched': [], 'missing': job_description.get('required_skills', [])},  # Baseline doesn't compute this
            'edu_analytics': {'details': []}
        })

    ranked_candidates.sort(key=lambda x: x['total_score'], reverse=True)
    return ranked_candidates