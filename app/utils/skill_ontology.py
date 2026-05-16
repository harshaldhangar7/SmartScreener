import json
import os
from typing import Dict, List, Optional, Tuple, Set


class SkillOntology:
    """
    Minimal skill ontology with optional JSON override.

    JSON structure (optional file: ontology/skills_ontology.json):
    {
      "nodes": {
        "programming_languages": {"name": "Programming Languages", "synonyms": [], "parents": []},
        "python": {"name": "Python", "synonyms": ["py"], "parents": ["programming_languages"]},
        ...
      }
    }
    """

    def __init__(self, json_path: Optional[str] = None):
        self.nodes: Dict[str, Dict] = {}
        if json_path and os.path.exists(json_path):
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.nodes = data.get('nodes', {})
            except Exception:
                self.nodes = {}
        if not self.nodes:
            self.nodes = self._default_nodes()
        # Build name/synonym index
        self.name_to_id: Dict[str, str] = {}
        for node_id, node in self.nodes.items():
            self.name_to_id[node.get('name', '').strip().lower()] = node_id
            for syn in node.get('synonyms', []):
                self.name_to_id[syn.strip().lower()] = node_id

    def _default_nodes(self) -> Dict[str, Dict]:
        return {
            # Categories
            "programming_languages": {"name": "Programming Languages", "synonyms": [], "parents": []},
            "databases": {"name": "Databases", "synonyms": [], "parents": []},
            "cloud": {"name": "Cloud", "synonyms": ["cloud platforms"], "parents": []},
            "ml": {"name": "Machine Learning", "synonyms": ["ml"], "parents": []},
            "ml_frameworks": {"name": "ML Frameworks", "synonyms": [], "parents": ["ml"]},
            "web_frontend": {"name": "Web Frontend", "synonyms": [], "parents": []},
            "web_backend": {"name": "Web Backend", "synonyms": [], "parents": []},

            # Children
            "python": {"name": "Python", "synonyms": [], "parents": ["programming_languages"]},
            "java": {"name": "Java", "synonyms": [], "parents": ["programming_languages"]},
            "javascript": {"name": "JavaScript", "synonyms": ["js"], "parents": ["programming_languages", "web_frontend"]},
            "typescript": {"name": "TypeScript", "synonyms": ["ts"], "parents": ["programming_languages", "web_frontend"]},
            "sql": {"name": "SQL", "synonyms": [], "parents": ["databases"]},
            "mysql": {"name": "MySQL", "synonyms": [], "parents": ["databases"]},
            "postgresql": {"name": "PostgreSQL", "synonyms": ["postgres"], "parents": ["databases"]},
            "mongodb": {"name": "MongoDB", "synonyms": [], "parents": ["databases"]},
            "aws": {"name": "AWS", "synonyms": ["amazon web services"], "parents": ["cloud"]},
            "azure": {"name": "Azure", "synonyms": ["microsoft azure"], "parents": ["cloud"]},
            "gcp": {"name": "GCP", "synonyms": ["google cloud", "google cloud platform"], "parents": ["cloud"]},
            "kubernetes": {"name": "Kubernetes", "synonyms": ["k8s"], "parents": ["cloud"]},
            "docker": {"name": "Docker", "synonyms": [], "parents": ["cloud"]},
            "react": {"name": "React", "synonyms": [], "parents": ["web_frontend"]},
            "angular": {"name": "Angular", "synonyms": [], "parents": ["web_frontend"]},
            "vue": {"name": "Vue", "synonyms": ["vue.js"], "parents": ["web_frontend"]},
            "nodejs": {"name": "Node.js", "synonyms": ["node", "node js"], "parents": ["web_backend", "programming_languages"]},
            "django": {"name": "Django", "synonyms": [], "parents": ["web_backend"]},
            "flask": {"name": "Flask", "synonyms": [], "parents": ["web_backend"]},
            "tensorflow": {"name": "TensorFlow", "synonyms": [], "parents": ["ml_frameworks"]},
            "pytorch": {"name": "PyTorch", "synonyms": [], "parents": ["ml_frameworks"]},
            "scikit_learn": {"name": "scikit-learn", "synonyms": ["sklearn"], "parents": ["ml_frameworks"]},
            "pandas": {"name": "pandas", "synonyms": [], "parents": ["ml"]},
            "numpy": {"name": "numpy", "synonyms": [], "parents": ["ml"]},
            "html": {"name": "HTML", "synonyms": [], "parents": ["web_frontend"]},
            "css": {"name": "CSS", "synonyms": [], "parents": ["web_frontend"]},
        }

    def canonicalize(self, skill: str) -> Optional[str]:
        s = (skill or '').strip().lower()
        if not s:
            return None
        return self.name_to_id.get(s)

    def parents_of(self, node_id: str) -> List[str]:
        node = self.nodes.get(node_id)
        return node.get('parents', []) if node else []

    def ancestors(self, node_id: str) -> Set[str]:
        result: Set[str] = set()
        stack: List[str] = [node_id]
        while stack:
            nid = stack.pop()
            for p in self.parents_of(nid):
                if p not in result:
                    result.add(p)
                    stack.append(p)
        return result

    def are_siblings(self, a: str, b: str) -> bool:
        pa = set(self.parents_of(a))
        pb = set(self.parents_of(b))
        return len(pa.intersection(pb)) > 0 and a != b

    def relatedness(self, a: Optional[str], b: Optional[str]) -> float:
        if a is None or b is None:
            return 0.0
        if a == b:
            return 1.0
        # Siblings share a parent
        if self.are_siblings(a, b):
            return 0.8
        # Ancestor / descendant relationship
        anc_a = self.ancestors(a)
        anc_b = self.ancestors(b)
        if a in anc_b or b in anc_a or len(anc_a.intersection(anc_b)) > 0:
            return 0.6
        return 0.0


_default_instance: Optional[SkillOntology] = None


def get_default_skill_ontology() -> SkillOntology:
    global _default_instance
    if _default_instance is None:
        # Try to load from ontology directory if exists
        json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..', 'ontology', 'skills_ontology.json')
        json_path = os.path.abspath(json_path)
        _default_instance = SkillOntology(json_path if os.path.exists(json_path) else None)
    return _default_instance


