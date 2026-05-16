# Evaluation Harness

Run:
```
pip install -r requirements.txt
python -m evaluation.harness
```

Outputs `evaluation/results/summary.csv` with nDCG@10 for SBERT baseline vs system.

Silver labels are generated via title/skill overlap. Tweak weights/min threshold in `SilverLabelConfig`.

Next steps (optional): add TF-IDF baseline, export plots from the CSV, and add ablations by toggling ontology/dense/cross-encoder.


