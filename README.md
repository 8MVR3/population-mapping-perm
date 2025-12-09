# 🏢 Population Mapping for Perm Region

Machine Learning pipeline for estimating population distribution in buildings using OpenStreetMap data and areal interpolation.

## 📊 Project Overview

This project predicts population at building-level resolution using:
- **OSM Data**: Buildings, roads, POIs from OpenStreetMap
- **Zonal Data**: Administrative zones with population statistics
- **ML Model**: Random Forest regression for population estimation

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/your-username/population-mapping-perm.git
cd population-mapping-perm
```
### 2. Setup environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# or: source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
```
### 3. Run the pipeline
```bash
# 1. Download OSM data
python scripts/extract_osm.py --place "Perm, Russia" --out-dir data/osm

# 2. Create building features
python scripts/featurize.py

# 3. Prepare training data
python scripts/make_training.py

# 4. Train the model
python scripts/train.py

# 5. Make predictions
python scripts/predict.py
```

### 📁 Project Structure
```text
population-mapping/
├── data/               # Data directories
│   ├── osm/           # Raw OSM data
│   ├── features/      # Building features
│   ├── train/         # Training data
│   ├── zones/         # Population zones
│   └── predictions/   # Model predictions
├── models/            # Trained ML models
├── scripts/           # Python scripts
│   ├── extract_osm.py     # OSM data download
│   ├── featurize.py       # Feature engineering
│   ├── make_training.py   # Training data preparation
│   ├── train.py           # Model training
│   └── predict.py         # Population prediction
├── notebooks/         # Jupyter notebooks
├── requirements.txt   # Python dependencies
└── README.md         # This file
```

### 🛠️ Dependencies
See `requirements.txt` for full list:

geopandas, osmnx, scikit-learn

pandas, numpy, shapely

joblib, click, folium

👥 Team
Vyacheslav Mikholap
Irina Melnichenko
Vladislav Ogay

📄 License
MIT License - see LICENSE file for details.
