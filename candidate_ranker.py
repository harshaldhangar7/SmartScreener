import logging
import spacy
from sentence_transformers import SentenceTransformer, util, CrossEncoder
import numpy as np
from collections import defaultdict
from functools import lru_cache
try:
    from app.utils.skill_ontology import get_default_skill_ontology
except Exception:
    get_default_skill_ontology = None

# Fairlearn for bias detection
try:
    from fairlearn.metrics import demographic_parity_difference, equalized_odds_difference
    FAIRLEARN_AVAILABLE = True
except ImportError:
    FAIRLEARN_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load spaCy model for NLP processing
try:
    import time
    spacy_start = time.time()
    logger.info("Loading spaCy model")
    nlp = spacy.load("en_core_web_sm")
    spacy_time = time.time() - spacy_start
    logger.info(f"spaCy model loaded in {spacy_time:.2f} seconds")
except OSError:
    # If model not found, download it
    import spacy.cli
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# Cache for normalized skills
normalized_skills_cache = {}

# Cache for spaCy documents
doc_cache = {}

# Embedding model for dense similarity
embedder: SentenceTransformer | None = None
cross_encoder_model: CrossEncoder | None = None

def get_embedder() -> SentenceTransformer:
    global embedder
    if embedder is None:
        embedder = SentenceTransformer("all-MiniLM-L6-v2")
    return embedder

def get_cross_encoder() -> CrossEncoder:
    global cross_encoder_model
    if cross_encoder_model is None:
        cross_encoder_model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
    return cross_encoder_model

def compute_text_embedding(text: str) -> np.ndarray:
    if not text:
        return np.zeros(384, dtype=np.float32)
    model = get_embedder()
    emb = model.encode(text, normalize_embeddings=True)
    return emb.astype(np.float32)

def try_decode_vector(text_value: str) -> np.ndarray:
    if not text_value:
        return np.array([])
    try:
        import base64, json
        return np.array(json.loads(base64.b64decode(text_value.encode("utf-8")).decode("utf-8")), dtype=np.float32)
    except Exception:
        try:
            import json
            return np.array(json.loads(text_value), dtype=np.float32)
        except Exception:
            return np.array([])

def normalize_skill(skill):
    """Normalize skill string for better matching with caching."""
    if skill in normalized_skills_cache:
        return normalized_skills_cache[skill]
    normalized = skill.strip().lower()
    normalized_skills_cache[skill] = normalized
    return normalized

@lru_cache(maxsize=1000)
def get_skill_similarity(skill1, skill2):
    """Calculate semantic similarity between two skills with caching."""
    # Simple string matching first
    if normalize_skill(skill1) == normalize_skill(skill2):
        return 1.0
    
    # Get or create spaCy documents
    if skill1 not in doc_cache:
        doc_cache[skill1] = nlp(skill1)
    if skill2 not in doc_cache:
        doc_cache[skill2] = nlp(skill2)
    
    doc1 = doc_cache[skill1]
    doc2 = doc_cache[skill2]
    
    # If either doc is empty, return 0
    if not doc1 or not doc2:
        return 0
    
    # Calculate similarity
    return doc1.similarity(doc2)

def calculate_skill_match_score(candidate_skills, required_skills, threshold=0.8):
    """Calculate the skill match score for a candidate with optimized matching and ontology awareness."""
    if not required_skills:
        return 1.0  # Perfect match if no skills required
    
    # Normalize all skills at once
    norm_candidate_skills = [normalize_skill(skill) for skill in candidate_skills]
    norm_required_skills = [normalize_skill(skill) for skill in required_skills]
    
    # Create a set for faster lookups
    candidate_skill_set = set(norm_candidate_skills)
    
    total_matches = 0.0
    ontology = get_default_skill_ontology() if get_default_skill_ontology else None
    
    # For each required skill, find the best matching candidate skill
    for req_skill in norm_required_skills:
        # First check for exact matches
        if req_skill in candidate_skill_set:
            total_matches += 1
            continue
            
        # If no exact match, find the best semantic match and ontology relatedness
        best_match_score = 0.0
        for cand_skill in norm_candidate_skills:
            similarity = get_skill_similarity(req_skill, cand_skill)
            if similarity > best_match_score:
                best_match_score = similarity
            if ontology is not None:
                try:
                    req_node = ontology.canonicalize(req_skill)
                    cand_node = ontology.canonicalize(cand_skill)
                    onto_rel = ontology.relatedness(req_node, cand_node)
                    if onto_rel > best_match_score:
                        best_match_score = onto_rel
                except Exception:
                    pass
        
        # If we found a good match
        if best_match_score >= threshold:
            total_matches += best_match_score
    
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

def get_education_level_score(degree):
    """Calculate education level score based on degree hierarchy with normalization."""
    text = (degree or '').strip().lower()
    if not text:
        return 0
    # Normalize common abbreviations/synonyms
    # PhD
    phd_tokens = ['phd', 'ph.d', 'doctorate', 'doctoral', 'doctor of philosophy']
    if any(tok in text for tok in phd_tokens):
        return 5
    # Master-equivalent
    master_tokens = [
        'master', 'm.s', 'ms', 'm.sc', 'msc', 'mtech', 'm.tech', 'm.e', 'me', 'mca', 'mba'
    ]
    if any(tok in text for tok in master_tokens):
        return 4
    # Bachelor-equivalent
    bachelor_tokens = [
        'bachelor', 'b.s', 'bs', 'b.sc', 'bsc', 'b.e', 'be', 'btech', 'b.tech', 'bca', 'bcs'
    ]
    if any(tok in text for tok in bachelor_tokens):
        return 3
    # Associate / Diploma / Certificate / High school
    if 'associate' in text:
        return 2
    if any(tok in text for tok in ['diploma', 'certificate', 'high school', 'hsc', 'ssc']):
        return 1
    return 0

def get_field_similarity(field1, field2):
    """Calculate similarity between two fields of study."""
    if not field1 or not field2:
        return 0.0
        
    field1 = field1.lower()
    field2 = field2.lower()
    
    # Exact match
    if field1 == field2:
        return 1.0
        
    # Use spaCy for semantic similarity
    doc1 = nlp(field1)
    doc2 = nlp(field2)
    return doc1.similarity(doc2)

def calculate_education_score(candidate_education, required_education):
    """
    Calculate education match score and analytics between candidate and job requirements.
    Returns (score, analytics_dict)
    """
    if not required_education:
        return 1.0, {"details": []}
    if not candidate_education:
        return 0.0, {"details": []}

    total_score = 0.0
    details = []
    weights = {'level': 0.6, 'field': 0.4}

    for req_edu in required_education:
        if isinstance(req_edu, str):
            req_degree = req_edu.lower()
            req_field = ''
        else:
            req_degree = req_edu.get('degree', '').lower()
            req_field = req_edu.get('field', '').lower()
        req_level_score = get_education_level_score(req_degree)
        best_match_score = 0.0
        best_detail = {}

        for cand_edu in candidate_education:
            if isinstance(cand_edu, str):
                cand_degree = cand_edu.lower()
                cand_field = ''
            else:
                cand_degree = cand_edu.get('degree', '').lower()
                cand_field = cand_edu.get('field', '').lower()
            cand_level_score = get_education_level_score(cand_degree)
            if cand_level_score >= req_level_score:
                level_score = 1.0
            else:
                level_score = cand_level_score / req_level_score if req_level_score > 0 else 0
            if req_field:
                field_score = get_field_similarity(req_field, cand_field) if cand_field else 0.0
            else:
                field_score = 1.0
            match_score = (level_score * weights['level']) + (field_score * weights['field'])
            if match_score > best_match_score:
                best_match_score = match_score
                best_detail = {
                    "required_degree": req_degree,
                    "required_field": req_field,
                    "candidate_degree": cand_degree,
                    "candidate_field": cand_field,
                    "level_score": level_score,
                    "field_score": field_score,
                    "match_score": match_score
                }
        total_score += best_match_score
        details.append(best_detail)
    return total_score / len(required_education), {"details": details}

def rank_candidates(candidates, job_description):
    """Rank candidates based on job requirements with optimized processing."""
    import time
    start_time = time.time()
    logger.info(f"Starting rank_candidates for {len(candidates)} candidates")

    required_skills = job_description.get('required_skills', [])
    required_education = job_description.get('required_education', [])
    min_experience = job_description.get('min_experience', 0)

    # Pre-process required skills
    norm_required_skills = [normalize_skill(skill) for skill in required_skills]

    ranked_candidates = []

    # Build dense text for candidates and job for embedding similarity
    job_text_parts = [
        job_description.get('title', ''),
        ', '.join(job_description.get('required_skills', []) or []),
        ', '.join([f"{e.get('degree','')} {e.get('field','')}" if isinstance(e, dict) else str(e) for e in (job_description.get('required_education') or [])])
    ]
    job_text = ' \n '.join([p for p in job_text_parts if p])
    job_emb = None
    if job_description.get('embedding'):
        decoded = try_decode_vector(job_description.get('embedding'))
        if decoded.size > 0:
            job_emb = decoded
    if job_emb is None or (hasattr(job_emb, 'size') and job_emb.size == 0):
        emb_start = time.time()
        job_emb = compute_text_embedding(job_text)
        emb_time = time.time() - emb_start
        logger.info(f"Computed job embedding in {emb_time:.2f} seconds")
    
    embedding_computations = 0
    for candidate in candidates:
        # Calculate skill match score (weight: 40%)
        skill_score = calculate_skill_match_score(
            candidate.get('skills', []),
            norm_required_skills
        )

        # Calculate experience score (weight: 30%)
        exp_score = calculate_experience_score(
            candidate.get('experience_years', 0),
            min_experience
        )

        # Calculate education score (weight: 30%) - increased weight for education
        edu_score, edu_analytics = calculate_education_score(
            candidate.get('education', []),
            required_education
        )

        # Dense similarity between resume text proxy and job text
        cand_text_parts = [
            candidate.get('name', ''),
            ', '.join(candidate.get('skills', []) or []),
            ', '.join([exp.get('title','') for exp in (candidate.get('experience_entries') or []) if isinstance(exp, dict)]),
            ', '.join([f"{e.get('degree','')} {e.get('field','')}" if isinstance(e, dict) else str(e) for e in (candidate.get('education') or [])])
        ]
        cand_text = ' \n '.join([p for p in cand_text_parts if p])
        cand_emb = None
        if candidate.get('embedding'):
            decoded = try_decode_vector(candidate.get('embedding'))
            if decoded.size > 0:
                cand_emb = decoded
        if cand_emb is None or (hasattr(cand_emb, 'size') and cand_emb.size == 0):
            emb_start = time.time()
            cand_emb = compute_text_embedding(cand_text)
            embedding_computations += 1
            emb_time = time.time() - emb_start
            logger.debug(f"Computed embedding for {candidate.get('name', 'Unknown')} in {emb_time:.2f} seconds")
        dense_sim = float(util.cos_sim(job_emb, cand_emb).cpu().numpy()[0][0]) if job_emb is not None and cand_emb is not None else 0.0

        # Calculate total score (weighted average + dense similarity)
        total_score = (skill_score * 0.35) + (exp_score * 0.25) + (edu_score * 0.25) + (dense_sim * 0.15)

        # Add to ranked list
        ranked_candidates.append({
            'candidate': candidate,
            'skill_score': skill_score,
            'exp_score': exp_score,
            'edu_score': edu_score,
            'edu_analytics': edu_analytics,
            'total_score': total_score,
            'semantic_similarity_score': dense_sim,
            'matched_skills': get_matched_skills(candidate.get('skills', []), norm_required_skills)
        })
    
    # Sort by total score (descending)
    ranked_candidates.sort(key=lambda x: x['total_score'], reverse=True)

    # Audit bias in ranking
    audit_bias_in_ranking(ranked_candidates, 'gender')
    audit_bias_in_ranking(ranked_candidates, 'ethnicity')

    # Log demographic outcomes for top candidates
    top_candidates = ranked_candidates[:5]
    for i, rc in enumerate(top_candidates):
        cand = rc['candidate']
        logger.info(f"Top {i+1} candidate: {cand.get('name', '')}, gender: {cand.get('gender', '')}, ethnicity: {cand.get('ethnicity', '')}, score: {rc['total_score']}")

    total_time = time.time() - start_time
    logger.info(f"rank_candidates completed in {total_time:.2f} seconds, computed {embedding_computations} embeddings")

    # Optional cross-encoder reranking of top-K - commented out for performance
    # try:
    #     top_k = min(50, len(ranked_candidates))
    #     if top_k > 1:
    #         cross_enc = get_cross_encoder()
    #         pairs = [[job_text, ' \n '.join([
    #             c['candidate'].get('name',''),
    #             ', '.join(c['candidate'].get('skills',[]) or []),
    #             ', '.join([exp.get('title','') for exp in (c['candidate'].get('experience_entries') or []) if isinstance(exp, dict)])
    #         ])] for c in ranked_candidates[:top_k]]
    #         scores = cross_enc.predict(pairs)
    #         # Normalize scores to [0,1]
    #         s_min, s_max = float(np.min(scores)), float(np.max(scores))
    #         norm = [(float(s) - s_min) / (s_max - s_min + 1e-8) for s in scores]
    #         for i, val in enumerate(norm):
    #             ranked_candidates[i]['cross_encoder_score'] = val
    #             # Blend: favor existing total_score with a boost from cross-encoder
    #             ranked_candidates[i]['total_score'] = ranked_candidates[i]['total_score'] * 0.8 + val * 0.2
    #         ranked_candidates.sort(key=lambda x: x['total_score'], reverse=True)
    # except Exception as e:
    #     logger.error(f"Cross-encoder reranking failed: {e}")

    return ranked_candidates

def get_matched_skills(candidate_skills, required_skills, threshold=0.8):
    """Get a list of matched and missing skills for display purposes."""
    if not required_skills or not candidate_skills:
        return {'matched': [], 'missing': required_skills}

    # Normalize skills
    norm_candidate_skills = [normalize_skill(skill) for skill in candidate_skills]

    matched_skills_details = []
    unmatched_required = list(required_skills)  # Create a copy to avoid modifying the original

    for req_skill in required_skills:
        norm_req_skill = normalize_skill(req_skill)
        best_match = None
        best_score = 0
        best_cand_skill = None

        for i, cand_skill in enumerate(norm_candidate_skills):
            similarity = get_skill_similarity(norm_req_skill, cand_skill)
            if similarity >= threshold and similarity > best_score:
                best_match = {'required': req_skill, 'candidate': candidate_skills[i], 'score': similarity}
                best_score = similarity
                best_cand_skill = cand_skill

        if best_match:
            matched_skills_details.append(best_match)
            if req_skill in unmatched_required:
                unmatched_required.remove(req_skill)

    return {'matched': matched_skills_details, 'missing': unmatched_required}

def audit_bias_in_ranking(ranked_candidates, sensitive_attribute='gender'):
    """Audit bias in ranking using Fairlearn."""
    if not FAIRLEARN_AVAILABLE:
        logger.warning("Fairlearn not available for bias audit")
        return None

    # Extract sensitive features and scores
    sensitive_features = []
    scores = []

    for rc in ranked_candidates:
        cand = rc['candidate']
        attr = cand.get(sensitive_attribute, '')
        if attr:
            sensitive_features.append(attr)
            scores.append(rc['total_score'])
        else:
            sensitive_features.append('unknown')
            scores.append(rc['total_score'])

    if not sensitive_features:
        return None

    # For ranking, compute selection rates for top K (assume top 10% selected)
    k = max(1, int(len(scores) * 0.1))
    selected = [1 if i < k else 0 for i in range(len(scores))]

    try:
        dp_diff = demographic_parity_difference(selected, sensitive_features)
        logger.info(f"Demographic parity difference for {sensitive_attribute}: {dp_diff}")
        return {'demographic_parity_difference': dp_diff}
    except Exception as e:
        logger.error(f"Error in bias audit: {e}")
        return None
