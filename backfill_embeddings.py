import os
import logging
from app import app, db
from app import Candidate, JobDescription, encode_vector_to_text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def _load_model():
    try:
        from sentence_transformers import SentenceTransformer
        return SentenceTransformer(os.environ.get("EMBEDDING_MODEL", "all-MiniLM-L6-v2"))
    except Exception as e:
        logger.error(f"Failed to load embedding model: {e}")
        return None

def _concat_candidate_text(c):
    parts = [
        c.name or '',
        ', '.join(c.skills or []),
        ', '.join([exp.get('title','') for exp in (c.experience_entries or []) if isinstance(exp, dict)]),
        ', '.join([f"{e.get('degree','')} {e.get('field','')}" if isinstance(e, dict) else str(e) for e in (c.education or [])])
    ]
    return ' \n '.join([p for p in parts if p])

def _concat_job_text(j):
    parts = [
        j.title or '',
        ', '.join(j.required_skills or []),
        ', '.join([f"{e.get('degree','')} {e.get('field','')}" if isinstance(e, dict) else str(e) for e in (j.required_education or [])])
    ]
    return ' \n '.join([p for p in parts if p])

def main():
    model = _load_model()
    if model is None:
        return
    with app.app_context():
        # Candidates
        candidates = Candidate.query.all()
        updated = 0
        for c in candidates:
            try:
                if not c.embedding:
                    text_value = _concat_candidate_text(c)
                    vector = model.encode(text_value, normalize_embeddings=True).tolist()
                    c.embedding = encode_vector_to_text(vector)
                    updated += 1
            except Exception as e:
                logger.error(f"Skip candidate {c.id}: {e}")
        # Jobs
        jobs = JobDescription.query.all()
        for j in jobs:
            try:
                if not j.embedding:
                    text_value = _concat_job_text(j)
                    vector = model.encode(text_value, normalize_embeddings=True).tolist()
                    j.embedding = encode_vector_to_text(vector)
                    updated += 1
            except Exception as e:
                logger.error(f"Skip job {j.id}: {e}")
        db.session.commit()
        logger.info(f"Backfill complete. Updated {updated} records.")

if __name__ == '__main__':
    main()

