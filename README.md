# FloraCare AI – Intelligent Flower Plant Health, Care & Sustainability System

> An end-to-end botanical intelligence platform combining **deep learning vision**, **computer-vision stress detection**, **condition-aware plant care scoring**, **data mining analytics**, and **sustainable horticulture guidance**.

---

## Table of Contents
1. [Problem Statement](#problem-statement)
2. [Proposed Solution](#proposed-solution)
3. [Key Features & Innovations](#key-features--innovations)
4. [System Architecture](#system-architecture)
5. [Datasets](#datasets)
6. [Machine Learning & Computer Vision](#machine-learning--computer-vision)
7. [Data Mining Component](#data-mining-component)
8. [Tech Stack](#tech-stack)
9. [Project Structure](#project-structure)
10. [Installation & Setup](#installation--setup)
11. [Running the Application](#running-the-application)
12. [Model Training & Evaluation](#model-training--evaluation)
13. [Limitations & Future Scope](#limitations--future-scope)

---

## Problem Statement
Most plant identification tools stop after outputting a predicted species name. However, urban gardeners, horticulturists, and botanical enthusiasts encounter far more complex real-world challenges:
- **Environmental Mismatch**: Growing species in climates, soils, or sunlight conditions unsuited to their native biomes.
- **Overwatering & Underwatering**: The #1 cause of domestic plant mortality.
- **Early Pathogen Detection**: Inability to identify chlorosis (yellowing), necrosis (brown spots), or wilting before irreversible decline occurs.
- **Unsustainable Horticultural Habits**: Excessive chemical fertilizer usage, high municipal water wastage, and broad-spectrum pesticide hazards that harm pollinator biodiversity.

---

## Proposed Solution
**FloraCare AI** elevates plant recognition into an interactive, full-lifecycle care assistant:
1. **Validates** floral composition before inference to prevent non-plant inputs.
2. **Identifies** the exact flower species across **102 Oxford Flower classes** using MobileNetV2 transfer learning.
3. **Diagnoses** leaf stress symptoms via computer-vision color and necrosis analysis.
4. **Calculates** a dynamic **0–100 Plant Health Score** and **Environment Match Matrix** against user ambient conditions.
5. **Generates** daily actionable task plans (*"What should I do today?"*) and condition-aware watering recommendations (*"Water today / Wait / Check soil first"*).
6. **Simulates** environmental interventions in real-time (*"What-If Simulator"*).
7. **Empowers** sustainable gardening with an **Eco-Sustainability Score** and organic IPM protocols.
8. **Discovers** ecological archetypes via **K-Means clustering** and multidimensional correlation data mining.

---

## Key Features & Innovations

### 1. AI Flower Identification & Validation
- Preprocesses uploaded photos to 224x224 with ImageNet normalization.
- Heuristic vegetation & petal saturation verification (`is_plant_image`) rejects non-flower uploads.
- Outputs predicted species, confidence score, and top-3 candidate species.

### 2. Explainable AI (XAI)
- Rather than opaque black-box predictions, explains *"Why did the AI choose this flower?"* using petal geometry, arrangement, foliage greenness fraction, and dominant color channels.

### 3. Plant Stress Detection (CV)
- Pixel-level HSV / BGR inspection detects:
  - **Chlorosis** (leaf yellowing from nitrogen deficiency or light stress)
  - **Necrosis** (brown spot fungal/bacterial blight)
  - **Wilting** (loss of turgor pressure / darkening)
- Clearly labeled with confidence and safe non-scientific advisory disclaimers.

### 4. Personalized Plant Health Score (0–100)
- Weighted multi-factor evaluation: Temperature (25%), Humidity (20%), Sunlight (20%), Watering (15%), and Soil (20%), minus detected stress penalties.

### 5. Smart Environment Match Matrix
- Compares user inputs against botanical tolerances:
  - Temperature -> Ideal / Slight Issue / Unsuitable
  - Humidity -> Ideal / Low / Too Dry
  - Soil -> Suitable Substrate
  - Sunlight -> Needs Bright Indirect Light

### 6. "What Should I Do Today?" Daily Action Plan
- Delivers 3–5 high-priority, plain-English gardening tasks prioritized by current ambient deviations.

### 7. Smart Watering Advisor
- Condition-aware algorithmic advisor returning **Water Today**, **Wait N Days**, or **Check Soil First**, factoring in recent watering, ambient temperature, humidity, and substrate retention.

### 8. What-If Environmental Simulator
- Interactive real-time sliders (Temperature, Humidity, Sunlight, Soil pH) instantly recalculate Plant Compatibility Score and summarize impact.

### 9. Sustainable Care Mode & Eco-Score (0–100)
- Rewards rainwater harvesting, organic compost amendments, drip irrigation, mulch retention, and biological Integrated Pest Management (IPM).

### 10. Data Mining & Intelligence Dashboard
- Real-time dataset analytics:
  - **Pearson Correlation Matrix** between environmental vectors and disease vulnerability.
  - **K-Means Clustering** (k=4) separating species into distinct ecological archetypes.
  - Interactive Recharts bar, pie, and radar visualizations.

### 11. Species Search & Comparison
- Side-by-side comparative analysis of any two species with an interactive 5-axis Radar Profile.

### 12. Smart Plant Recommender (*"Which Flower Should I Grow?"*)
- Multi-criteria recommendation engine matching user ambient conditions and skill level to the best candidate flowers.

### 13. My Plants & Growth Journal
- Saved plant records with a weekly care schedule (Monday to Sunday) and chronological Computer Vision image comparison tracking canopy coverage (%) and chlorophyll vitality index over time.

---

## Datasets
- **Oxford 102 Flowers**: 102 floral categories from the University of Oxford.
- **Botanical Care Database (`data/flower_care_db.json`)**: Rich species-specific records covering optimal/absolute temperatures, humidity ranges, soil pH and drainage, watering intensity, NPK feeding schedules, common diseases, pests, and visual features.
- **Soil Database (`data/soil_db.json`)**: Physical properties, fertility, water retention, and amendments for Loamy, Sandy, Clay, Peaty, and Chalky soils.
- **Climate Database (`data/climate_db.json`)**: Temperature, humidity, and rainfall envelopes for Tropical, Subtropical, Temperate, Mediterranean, and Arid zones.

---

## Tech Stack
- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Recharts, Lucide React, Axios.
- **Backend**: Python 3.10+ (Python 3.14 compatible), FastAPI, Uvicorn, Pydantic, Starlette.
- **Machine Learning**: PyTorch, Torchvision (MobileNetV2), NumPy, Pillow, OpenCV.
- **Data Mining**: scikit-learn (K-Means, StandardScaler, Pearson Correlation), Pandas.

---

## Project Structure
```
floracare-ai/
├── backend/
│   ├── main.py               # FastAPI application & middleware
│   ├── requirements.txt      # Backend dependencies
│   ├── routes/
│   │   ├── predict.py        # Image validation, inference & stress API
│   │   ├── care.py           # Health score, watering advisor, What-If
│   │   ├── flowers.py        # Catalog search, compare, recommender
│   │   ├── analytics.py      # Data mining summary & K-Means clustering
│   │   └── journal.py        # Plant profiles & CV growth journal
│   ├── services/
│   │   └── scoring.py        # Core algorithmic scoring engine
│   ├── storage/              # Local profile storage & photo uploads
│   ├── tests/
│   │   └── test_api.py       # 12 automated unit/integration tests
│   └── utils/
│       ├── data_loader.py    # Database loaders with LRU caching
│       └── validators.py     # Image and input bounds validators
├── data/
│   ├── flower_care_db.json   # 102 flower care & botanical profiles
│   ├── soil_db.json          # Soil types & characteristics
│   └── climate_db.json       # Climate zones & envelopes
├── frontend/
│   ├── src/
│   │   ├── components/       # Navbar, Footer
│   │   ├── pages/            # 10 full feature pages
│   │   ├── services/api.ts   # Axios API client
│   │   ├── types/index.ts    # TypeScript interfaces
│   │   ├── App.tsx           # Main application state & routing
│   │   └── main.tsx          # React entrypoint
│   ├── package.json          # Frontend dependencies
│   ├── tailwind.config.js    # Botanical theme configuration
│   └── vite.config.ts        # Vite build & proxy settings
├── ml_model/
│   ├── model.py              # MobileNetV2 architecture & weights loader
│   ├── preprocessor.py       # 224x224 transforms & heuristic plant check
│   ├── predict.py            # Prediction pipeline & Explainable AI
│   ├── stress_detector.py    # CV yellowing/brown spot/wilting analysis
│   ├── train.py              # PyTorch fine-tuning on Oxford 102
│   ├── evaluation.py         # Real accuracy, precision, recall & F1
│   └── config.py             # 102 class labels & hyperparameters
└── README.md
```

---

## Installation & Setup

### Prerequisites
- Python 3.10+ (Python 3.14 verified)
- Node.js 18+ and npm
- Git

### 1. Backend Setup
```bash
cd backend
python -m pip install -r requirements.txt
```

### 2. Frontend Setup
```bash
cd ../frontend
npm install
```

---

## Running the Application

### 1. Start the FastAPI Backend
```bash
# From the project root:
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```
- Backend REST API: `http://localhost:8000`
- Interactive Swagger Documentation: `http://localhost:8000/docs`

### 2. Start the React Frontend
```bash
# In the frontend directory:
npm run dev
```
- Web Application: `http://localhost:5173`

---

## Automated Testing
Run the backend test suite:
```bash
python -m pytest backend/tests/test_api.py -v
```

---

## Model Training & Evaluation

### Training MobileNetV2 on Oxford 102 Flowers:
```bash
python ml_model/train.py --epochs 30 --batch-size 32 --lr 0.001
```

### Evaluating the Model:
```bash
python ml_model/evaluation.py
```

---

## Limitations & Advisory Note
- **AI Recommendation Disclaimer**: All health scores, compatibility indices, and stress indications are heuristic AI recommendations designed for guidance. They do not constitute scientific laboratory pathology diagnoses.
- **Physical Soil Testing**: Algorithmic estimates do not replace physical soil moisture probes or chemical NPK test kits.

---

## License
Released under the MIT License. Developed for sustainable botanical education and care intelligence.
