# Smart Resume Screener - Figures and Diagrams

This document contains all the figures and diagrams for the Smart Resume Screener system.

## List of Figures

1. [System Architecture of Smart Resume Screener](#figure-1-system-architecture-of-smart-resume-screener)
2. [Candidate Ranking Workflow](#figure-2-candidate-ranking-workflow)
3. [Dashboard UI Design](#figure-3-dashboard-ui-design)
4. [Bias Detection Flowchart](#figure-4-bias-detection-flowchart)
5. [Example Candidate Score Breakdown](#figure-5-example-candidate-score-breakdown)
6. [Fairness Metrics Visualization](#figure-6-fairness-metrics-visualization)
7. [Research Design Methodology](#figure-7-research-design-methodology)

---

## Figure 1: System Architecture of Smart Resume Screener

```mermaid
graph TB
    A[User Interface<br/>HTML/CSS/JS<br/>Flask Templates] --> B[Flask Web Server<br/>app.py]
    B --> C[Authentication<br/>Flask-Login<br/>User Management]
    B --> D[Resume Upload<br/>File Processing]
    B --> E[Job Management<br/>CRUD Operations]
    B --> F[Candidate Management<br/>CRUD Operations]

    D --> G[Resume Parser<br/>resume_parser.py<br/>PDF/DOCX Processing]
    G --> H[AI Resume Analyzer<br/>ai_resume_analyzer.py<br/>OpenAI GPT Analysis]

    B --> I[Candidate Ranker<br/>candidate_ranker.py<br/>Traditional NLP + Embeddings]
    I --> J[AI Candidate Ranker<br/>ai_candidate_ranker.py<br/>GPT-enhanced Ranking]

    C --> K[(Database<br/>SQLite/MySQL<br/>SQLAlchemy)]
    D --> K
    E --> K
    F --> K
    G --> K
    H --> K

    I --> L[Bias Detection<br/>Fairlearn Library<br/>Demographic Parity]
    J --> L

    B --> M[Dashboard<br/>Statistics & Analytics<br/>Real-time Metrics]

    N[External Services] --> O[OpenAI API<br/>GPT-4o-mini]
    N --> P[Sentence Transformers<br/>all-MiniLM-L6-v2]
    N --> Q[spaCy<br/>NLP Processing]

    H --> O
    I --> P
    I --> Q

    style A fill:#e1f5fe
    style B fill:#fff3e0
    style K fill:#f3e5f5
    style N fill:#e8f5e8
```

**Description:** The system architecture shows a Flask-based web application with modular components for resume processing, AI analysis, candidate ranking, and bias detection. The core components include user authentication, file upload handling, database operations, and integration with external AI services.

---

## Figure 2: Candidate Ranking Workflow

```mermaid
flowchart TD
    A[Start: Job Description Created] --> B[User Selects Ranking Model]
    B --> C{Model Type?}

    C -->|AI-Enhanced| D[Load Base Ranker<br/>candidate_ranker.py]
    C -->|Traditional| E[Load Traditional Ranker<br/>candidate_ranker.py]
    C -->|Baseline| F[Load Baseline Ranker<br/>baseline_ranker.py]

    D --> G[Perform Base Ranking<br/>Skill/Experience/Education Matching]
    E --> G
    F --> H[Perform TF-IDF Ranking]

    G --> I[Check AI Availability<br/>ai_analyzer.is_available()]
    I -->|AI Available| J[Enhance Rankings with AI<br/>ai_candidate_ranker.py]
    I -->|AI Not Available| K[Use Base Rankings Only]

    J --> L[AI Job Match Analysis<br/>Per Candidate]
    L --> M[Combine Scores<br/>60% Traditional + 40% AI]

    H --> N[Return Baseline Rankings]
    K --> N
    M --> N

    N --> O[Sort by Final Score<br/>Descending Order]
    O --> P[Audit Bias<br/>audit_bias_in_ranking()]
    P --> Q[Log Demographic Outcomes]
    Q --> R[Return Ranked Candidates<br/>With Scores & Analytics]

    style A fill:#e8f5e8
    style R fill:#ffebee
```

**Description:** The candidate ranking workflow supports multiple ranking models (AI-enhanced, traditional semantic, baseline TF-IDF). The AI-enhanced model combines traditional NLP scoring with GPT-based analysis, includes bias auditing, and provides comprehensive scoring breakdowns.

---

## Figure 3: Dashboard UI Design

```mermaid
graph TD
    A[Dashboard Layout<br/>Glass-morphism Design] --> B[Header Section]
    A --> C[Statistics Cards]
    A --> D[Navigation Tabs]
    A --> E[Recent Activities]
    A --> F[Top Candidates Preview]

    B --> B1[Logo & Title<br/>Smart Resume Screener]
    B --> B2[User Menu<br/>Profile/Logout]

    C --> C1[Total Candidates<br/>Animated Counter]
    C --> C2[Active Jobs<br/>Animated Counter]
    C --> C3[AI Analyzed<br/>Progress Indicator]
    C --> C4[Avg Quality Score<br/>Gauge Chart]

    D --> D1[Dashboard Tab<br/>Active]
    D --> D2[Upload Tab]
    D --> D3[Candidates Tab]
    D --> D4[Jobs Tab]

    E --> E1[Resume Uploaded<br/>2 hours ago]
    E --> E2[Job Created<br/>Just now]
    E --> E3[AI Analysis Completed<br/>1 hour ago]

    F --> F1[Candidate 1<br/>Quality: 92%]
    F --> F2[Candidate 2<br/>Quality: 88%]
    F --> F3[Candidate 3<br/>Quality: 85%]

    G[Responsive Design] --> H[Desktop Layout<br/>4-column grid]
    G --> I[Tablet Layout<br/>2-column grid]
    G --> J[Mobile Layout<br/>Single column]

    style A fill:#f3e5f5
    style C fill:#e1f5fe
    style G fill:#fff3e0
```

**Description:** The dashboard features a modern glass-morphism UI with four main tabs, real-time statistics, recent activity feed, and top candidate previews. The design is fully responsive across desktop, tablet, and mobile devices.

---

## Figure 4: Bias Detection Flowchart

```mermaid
flowchart TD
    A[Ranking Process Complete] --> B[Extract Sensitive Attributes<br/>Gender, Ethnicity]
    B --> C[Extract Ranking Scores<br/>total_score for each candidate]

    C --> D{Check Fairlearn<br/>Available?}
    D -->|Yes| E[Calculate Selection Rates<br/>Top 10% as selected]
    D -->|No| F[Skip Bias Audit<br/>Log Warning]

    E --> G[Compute Demographic Parity<br/>demographic_parity_difference()]
    G --> H[Log Results<br/>demographic_parity_difference value]

    H --> I[Check Threshold<br/>|difference| > 0.1]
    I -->|Bias Detected| J[Log Warning<br/>Potential bias in ranking]
    I -->|Acceptable| K[Log Info<br/>Bias within acceptable range]

    F --> L[End Bias Audit]
    J --> L
    K --> L

    L --> M[Continue with Rankings<br/>Display results to user]

    style A fill:#ffebee
    style L fill:#e8f5e8
```

**Description:** The bias detection process uses Fairlearn library to audit ranking fairness. It calculates demographic parity differences for sensitive attributes like gender and ethnicity, logging warnings when bias exceeds acceptable thresholds.

---

## Figure 5: Example Candidate Score Breakdown

```mermaid
pie title Candidate Score Breakdown - John Smith
    "Skills Match (35%)" : 32
    "Experience Match (25%)" : 22
    "Education Match (25%)" : 20
    "Semantic Similarity (15%)" : 13

classDef high fill:#4caf50,color:#fff
classDef medium fill:#ff9800,color:#fff
classDef low fill:#f44336,color:#fff

%% Breakdown Details
%% Skills Match: 32/35 (91.4% of skills matched)
%% Experience Match: 22/25 (5 years experience, meets 3 year min)
%% Education Match: 20/25 (Bachelor's in CS, good field match)
%% Semantic Similarity: 13/15 (High embedding similarity)
```

```mermaid
xychart-beta
    title Detailed Scoring Components
    bar [91, 88, 80, 87, 15, 92]
    x-axis ["Skills Match", "Experience Match", "Education Match", "Semantic Similarity", "AI Enhancement", "Final Combined Score"]

%% AI Enhancement adds +15 points to base score
%% Final Score = (Base Score × 0.85) + (AI Score × 0.15)
```

**Description:** This example shows how individual scoring components (skills, experience, education, semantic similarity) combine to create the final candidate score. The AI-enhanced model further refines this with GPT analysis.

---

## Figure 6: Fairness Metrics Visualization

```mermaid
graph LR
    A[Fairness Metrics Dashboard] --> B[Demographic Parity]
    A --> C[Equal Opportunity]
    A --> D[Disparate Impact]

    B --> B1[Gender Parity<br/>Difference: 0.05<br/>Status: ✓ Acceptable]
    B --> B2[Ethnicity Parity<br/>Difference: 0.08<br/>Status: ✓ Acceptable]

    C --> C1[Gender Equal Opportunity<br/>Difference: 0.03<br/>Status: ✓ Acceptable]
    C --> C2[Ethnicity Equal Opportunity<br/>Difference: 0.06<br/>Status: ✓ Acceptable]

    D --> D1[Gender Disparate Impact<br/>Ratio: 0.95<br/>Status: ✓ Acceptable]
    D --> D2[Ethnicity Disparate Impact<br/>Ratio: 0.92<br/>Status: ✓ Acceptable]

    E[Historical Trends] --> F[Monthly Tracking<br/>Bias metrics over time]
    E --> G[Alert Thresholds<br/>Warning: >0.1<br/>Critical: >0.2]

    style A fill:#f3e5f5
    style B1 fill:#e8f5e8
    style B2 fill:#e8f5e8
    style C1 fill:#e8f5e8
    style C2 fill:#e8f5e8
    style D1 fill:#e8f5e8
    style D2 fill:#e8f5e8
```

```mermaid
xychart-beta
    title "Fairness Metrics Trends (Last 6 Months)"
    x-axis [Jan, Feb, Mar, Apr, May, Jun]
    y-axis "Bias Difference" 0 --> 0.3
    line "Gender Parity" [0.02, 0.05, 0.03, 0.08, 0.04, 0.05]
    line "Ethnicity Parity" [0.01, 0.03, 0.06, 0.04, 0.07, 0.08]
    line "Threshold" [0.1, 0.1, 0.1, 0.1, 0.1, 0.1]
```

**Description:** The fairness metrics visualization tracks demographic parity, equal opportunity, and disparate impact across protected attributes. Historical trends help identify patterns and ensure ongoing fairness in the ranking system.
7. [Research Design Methodology](#figure-7-research-design-methodology)

---

## Figure 7: Research Design Methodology

```mermaid
flowchart TD
    A[Research Design: AI vs Baseline Ranking Comparison<br/>Experimental Methodology] --> B[Data Collection<br/>Load Candidates & Job Descriptions<br/>from Database]
    B --> C[Silver Label Generation<br/>Title/Skill Overlap Scoring<br/>Configurable Weights]
    C --> D[Experimental Setup<br/>Configure Evaluation Parameters<br/>SilverLabelConfig]
    
    D --> E[Baseline Evaluation<br/>SBERT Semantic Similarity<br/>all-MiniLM-L6-v2 Embeddings]
    D --> F[System Evaluation<br/>AI-Enhanced Ranking<br/>Smart Resume Screener]
    
    E --> G[Compute nDCG@10<br/>Baseline Performance<br/>Cosine Similarity Ranking]
    F --> H[Compute nDCG@10<br/>System Performance<br/>Combined NLP + AI Scoring]
    
    G --> I[Statistical Comparison<br/>Hypothesis Testing<br/>H₀ vs H₁]
    H --> I
    
    I --> J[Results Analysis<br/>Performance Gains<br/>Significance Testing]
    J --> K[Fairness Audit<br/>Bias Detection Metrics<br/>Demographic Parity]
    
    K --> L[Generate Report<br/>evaluation/results/summary.csv<br/>nDCG Scores Comparison]
    
    style A fill:#f3e5f5
    style I fill:#ffebee
    style L fill:#e8f5e8
```

**Description:** The research design follows an experimental methodology comparing AI-enhanced candidate ranking against SBERT baseline methods. Silver labels are generated from job-candidate data using title and skill overlap, then nDCG@10 is computed for both approaches to test the hypothesis that AI improves ranking quality. The design includes fairness auditing to ensure ethical evaluation.