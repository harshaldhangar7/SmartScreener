import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import json
import random
from dataclasses import dataclass
from typing import List, Dict, Any, Tuple

import numpy as np
import pandas as pd
from tqdm import tqdm
from sentence_transformers import SentenceTransformer, util
from sklearn.metrics import ndcg_score

from app import app, db
from app import Candidate, JobDescription
from candidate_ranker import rank_candidates


@dataclass
class SilverLabelConfig:
    title_overlap_weight: float = 0.5
    skill_overlap_weight: float = 0.5
    min_positive_score: float = 0.35


def _concat_candidate_text(c: Dict[str, Any]) -> str:
    parts = [
        c.get('name', ''),
        ', '.join(c.get('skills', []) or []),
        ', '.join([exp.get('title','') for exp in (c.get('experience_entries') or []) if isinstance(exp, dict)]),
        ', '.join([f"{e.get('degree','')} {e.get('field','')}" if isinstance(e, dict) else str(e) for e in (c.get('education') or [])])
    ]
    return ' \n '.join([p for p in parts if p])


def _concat_job_text(j: Dict[str, Any]) -> str:
    parts = [
        j.get('title', ''),
        ', '.join(j.get('required_skills', []) or []),
        ', '.join([f"{e.get('degree','')} {e.get('field','')}" if isinstance(e, dict) else str(e) for e in (j.get('required_education') or [])])
    ]
    return ' \n '.join([p for p in parts if p])


def generate_silver_labels(candidates: List[Dict[str, Any]], jobs: List[Dict[str, Any]], cfg: SilverLabelConfig) -> Dict[int, Dict[int, float]]:
    labels: Dict[int, Dict[int, float]] = {}
    for j in jobs:
        job_id = j['id']
        title_tokens = set((j.get('title') or '').lower().split())
        job_skills = set([s.lower() for s in (j.get('required_skills') or [])])
        labels[job_id] = {}
        for c in candidates:
            cand_skills = set([s.lower() for s in (c.get('skills') or [])])
            cand_titles = set([t.lower() for t in [exp.get('title','') for exp in (c.get('experience_entries') or []) if isinstance(exp, dict)] if t])
            title_overlap = 1.0 if any(len(title_tokens.intersection(set(t.split()))) > 0 for t in cand_titles) else 0.0
            skill_overlap = len(job_skills.intersection(cand_skills)) / (len(job_skills) + 1e-8)
            score = cfg.title_overlap_weight * title_overlap + cfg.skill_overlap_weight * skill_overlap
            if score >= cfg.min_positive_score:
                labels[job_id][c['id']] = float(score)
    return labels


def evaluate_baselines(candidates: List[Dict[str, Any]], jobs: List[Dict[str, Any]], labels: Dict[int, Dict[int, float]]) -> pd.DataFrame:
    sbert = SentenceTransformer('all-MiniLM-L6-v2')
    cand_texts = [_concat_candidate_text(c) for c in candidates]
    cand_ids = [c['id'] for c in candidates]
    cand_embs = sbert.encode(cand_texts, normalize_embeddings=True)

    rows = []
    for j in tqdm(jobs, desc='Eval jobs'):
        job_text = _concat_job_text(j)
        job_emb = sbert.encode(job_text, normalize_embeddings=True)
        sims = util.cos_sim(job_emb, cand_embs)[0].cpu().numpy()
        # Predicted ranking
        order = np.argsort(-sims)
        # Build relevance and predicted arrays for nDCG
        true_rel = np.array([labels.get(j['id'], {}).get(cid, 0.0) for cid in cand_ids])[None, :]
        pred_scores = sims[None, :]
        ndcg10 = ndcg_score(true_rel, pred_scores, k=10)

        # System under test ranking
        ranked = rank_candidates(candidates, j)
        # Align to candidate ids
        preds_total = np.array([r['total_score'] for r in ranked])[None, :]
        # We need to map ranked order to cand_ids
        # Ensure candidates input order equals cand_ids order
        ndcg10_sys = ndcg_score(true_rel, preds_total, k=10)

        rows.append({
            'job_id': j['id'],
            'ndcg10_sbert': ndcg10,
            'ndcg10_system': ndcg10_sys,
        })
    return pd.DataFrame(rows)


def main(output_dir: str = 'evaluation/results'):
    os.makedirs(output_dir, exist_ok=True)
    with app.app_context():
        cand_models = Candidate.query.all()
        job_models = JobDescription.query.all()
        candidates = [c.to_dict() for c in cand_models]
        jobs = [j.to_dict() for j in job_models]

    cfg = SilverLabelConfig()
    labels = generate_silver_labels(candidates, jobs, cfg)
    df = evaluate_baselines(candidates, jobs, labels)
    out_csv = os.path.join(output_dir, 'summary.csv')
    df.to_csv(out_csv, index=False)
    print(f"Saved results to {out_csv}")


if __name__ == '__main__':
    main()

