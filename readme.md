# Credit Risk Prediction api  (ML + FastAPI + Streamlit)

An end-to-end **loan default risk prediction system** that combines machine learning, business rules, and a production-ready backend API to simulate real-world credit decisioning used in banks and NBFCs.

The system predicts **Probability of Default (PD)**, calculates **Expected Loss**, evaluates **affordability**, and returns a final **loan approval decision**.

---

## 🚀 Features

- ML-based Probability of Default (PD) prediction using **LightGBM**
- Robust preprocessing with missing value handling and encoding
- Business-rule driven decision engine (EMI caps, loan limits, grade & term risk adjustment)
- Production-ready **FastAPI** backend
- **Streamlit** frontend for easy testing
- PostgreSQL database logging for audit & tracking
- Modular and scalable architecture

---

## 🧠 Machine Learning Model

- **Algorithm:** LightGBM Classifier  
- **Target:** Loan Default (1 = Default, 0 = Non-default)  
- **Metric:** ROC-AUC  
- **Class imbalance handling:** `class_weight="balanced"`

### Feature Engineering
- Mean FICO score derived from credit range
- Numerical + categorical preprocessing using `ColumnTransformer`
- One-hot encoding with unseen category handling

### Input Features
- Loan Amount  
- Annual Income  
- Debt-to-Income Ratio (DTI)  
- FICO Mean  
- Interest Rate  
- Loan Term  
- Credit Grade  
- Loan Purpose  

---

## 🏗️ Architecture

ML Training (scikit-learn + LightGBM)
↓
Serialized Model (joblib)
↓
FastAPI Prediction Service
↓
Business Rules + Risk Logic
↓
PostgreSQL (Decision Storage)
↓
Streamlit Frontend



---

## 🔧 Tech Stack

- Python
- LightGBM
- scikit-learn
- FastAPI
- Pydantic
- PostgreSQL
- Streamlit
- Joblib
- Pandas / NumPy

---

## 📦 Project Structure

.
├── main.py # Model training & evaluation
├── api.py # FastAPI backend
├── streamlit_app.py # Streamlit frontend
├── db.py # Database connection
├── model.pkl # Trained ML pipeline
├── features.pkl # Feature order persistence
├── loan.csv # Dataset
└── README.md


---

## ⚙️ Installation & Setup

### 1. Clone the repository

git clone https://github.com/SVChaithanya/Credit-Risk-Prediction-api.git
cd loan-risk-system

2. Install dependencies
pip install -r requirements.txt

3. Train the model
python main.py

4. Start the FastAPI server
uvicorn api:app --reload

5. Run the Streamlit app
streamlit run streamlit_app.py

🔮 API Endpoint
POST /predict

Request Body

{
  "customer_id": 101,
  "loan_amnt": 200000,
  "annual_inc": 600000,
  "dti": 25,
  "fico_mean": 720,
  "int_rate": 12.5,
  "term": "36 months",
  "grade": "B",
  "purpose": "credit_card"
}


Response

{
  "customer_id": 101,
  "pd": 0.18,
  "adjusted_pd": 0.19,
  "expected_loss": 34200,
  "emi": 6700,
  "affordability_ratio": 0.32,
  "decision": "accept",
  "risk_level": "low"
}


🧮 Decision Logic (Business Rules)

Reject if customer has ≥ 3 active loans

Adjust PD using loan term and credit grade

Calculate EMI and affordability ratio

Purpose-based EMI caps

Purpose-based maximum loan limits

Final decision based on:

Adjusted PD ≤ 0.30

Affordability within allowed threshold

This mirrors real-world banking credit policies, not academic ML demos.




🗄️ Database Logging

All loan decisions are stored in PostgreSQL with:

Customer details

PD & Expected Loss

Affordability metrics

Final decision & risk level




📈 Future Improvements

Authentication & role-based access

Model monitoring & drift detection

Feature store integration

Dockerization & cloud deployment

Batch scoring pipeline

Explainability (SHAP)
 

