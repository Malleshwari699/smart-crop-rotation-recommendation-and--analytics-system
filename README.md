# 🌾 Smart Crop Rotation Recommendation & Analytics System

An AI-powered agriculture decision-support system that recommends the best crop
based on soil nutrients, climate conditions, and previous crop history — built
with **Python**, **scikit-learn**, and **Streamlit**.

---

## 📁 Project Structure

```
smart_crop_recommendation/
│
├── app.py               # Main Streamlit application
├── train_model.py       # ML model training script
├── model.pkl            # Trained Random Forest model bundle
├── metrics.json         # Saved evaluation metrics
├── requirements.txt     # Python dependencies
├── README.md
│
├── dataset/
│   └── crop_data.csv    # Training dataset (20 crops, 8 features)
│
├── utils/
│   └── language.py      # Multi-language support (EN / HI / TE)
│
└── images/
    ├── confusion_matrix.png     # Auto-generated after training
    └── feature_importance.png   # Auto-generated after training
```

---

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. (Optional) Re-train the model manually
python train_model.py

# 3. Launch the web app
streamlit run app.py
```

> **Note:** The app auto-trains the model on the **first run** if `model.pkl`
> is not found.

---

## 🤖 Machine Learning Model

| Setting          | Value                          |
|-----------------|-------------------------------|
| Algorithm        | Random Forest Classifier       |
| Estimators       | 200 trees                      |
| Train/Test split | 80% / 20% (1,760 / 440 samples) |
| Input features   | N, P, K, Temperature, Humidity, pH, Rainfall, Previous Crop |
| Target           | Recommended Crop               |

### Evaluation Metrics
- **Accuracy** — overall correctness
- **Precision** — crop-level positive predictive value
- **Recall** — crop-level sensitivity
- **F1 Score** — harmonic mean of precision & recall

---

## 🌿 Supported Crops (22)

Rice · Wheat · Maize · Cotton · Chickpea · Kidney Beans · Pigeon Peas ·
Moth Beans · Mung Bean · Blackgram · Lentil · Pomegranate · Banana ·
Mango · Grapes · Watermelon · Muskmelon · Apple · Orange · Papaya ·
Coconut · Jute · Coffee

> **Dataset:** 2,200 real samples (100 per crop), perfectly balanced,
> sourced from `Crop_recommendation_with_previous_crop.csv`.

---

## 🖥️ App Pages

| Page                 | Description                                                |
|---------------------|------------------------------------------------------------|
| 🏠 Home              | Project overview, objectives, supported crops              |
| 🌱 Crop Prediction   | Enter soil/climate data → get crop + fertilizer suggestion |
| 📊 Analytics         | Pie, bar, scatter, violin, and correlation charts          |
| 📈 Model Performance | Accuracy metrics, confusion matrix, feature importance     |
| ℹ️ About             | Technologies used, run instructions                        |

---

## 🌐 Multi-Language Support

Select language from the sidebar:

| Feature         | English         | Hindi                      | Telugu                    |
|----------------|-----------------|---------------------------|--------------------------|
| Predict button  | Predict Crop    | फसल की भविष्यवाणी करें    | పంట అంచనా వేయండి          |
| Home page       | Home            | मुख्य पृष्ठ               | హోమ్                      |

---

## 🛠️ Technologies

- **Python 3.x** — core language
- **scikit-learn** — Random Forest, metrics
- **Streamlit** — interactive dashboard
- **Plotly** — interactive charts
- **Matplotlib / Seaborn** — static charts & heatmaps
- **Pandas / NumPy** — data processing
- **Joblib** — model serialization

---

## 💊 Fertilizer Recommendations

Each predicted crop comes with a tailored fertilizer suggestion, e.g.:

- **Rice** → Urea + DAP (Diammonium Phosphate)
- **Wheat** → NPK 12-32-16 + Urea
- **Cotton** → DAP + MOP (Muriate of Potash)
- …and 17 more crops

---

*Built with ❤️ for Sustainable Agriculture*
