from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Literal
import joblib
import pandas as pd
from ieee_db import get_connenction

app = FastAPI()

model = joblib.load("model.pkl")
features = joblib.load("features.pkl")

CUSTOMER_ACTIVE_LOANS = {
    101: 0,
    102: 1,
    103: 3,
    104: 2
}

class LoanRequest(BaseModel):
    customer_id: int
    loan_amnt: float = Field(ge=10000)
    annual_inc: float = Field(ge=10000)
    dti: float = Field(ge=0, le=100)
    fico_mean: float = Field(ge=300, le=850)
    int_rate: float = Field(gt=0)
    term: Literal["36 months", "60 months"]
    grade: Literal["A","B","C","D","E","F","G"]
    purpose: Literal["education","credit_card","personal","small_business"]

LGD = 0.90

PURPOSE_MAX_MULTIPLIER = {
    "education": 10,
    "personal": 5,
    "small_business": 6,
    "credit_card": 3
}

PURPOSE_EMI_CAP = {
    "education": 0.50,
    "personal": 0.40,
    "small_business": 0.35,
    "credit_card": 0.30
}

TERM_MAP = {"36 months": 1.0, "60 months": 1.1}
GRADE_MAP = {"A":0.9,"B":0.95,"C":1.0,"D":1.05,"E":1.1,"F":1.15,"G":1.2}

def calculate_emi(principal, annual_rate, months):
    r = annual_rate / (12 * 100)
    return principal * r * (1 + r)**months / ((1 + r)**months - 1)

@app.post("/predict")
def predict(data: LoanRequest):

    active_loans = CUSTOMER_ACTIVE_LOANS.get(data.customer_id, 0)
    if active_loans >= 3:
        return {
            "customer_id": data.customer_id,
            "decision": "reject",
            "reason": "Too many active loans"
        }

    payload = data.dict()
    payload.pop("customer_id")
    input_df = pd.DataFrame([payload])[features]
    pd_value = model.predict_proba(input_df)[0][1]

    adjusted_pd = pd_value * TERM_MAP[data.term] * GRADE_MAP[data.grade]
    expected_loss = adjusted_pd * LGD * data.loan_amnt

    months = 36 if data.term == "36 months" else 60
    emi = calculate_emi(data.loan_amnt, data.int_rate, months)

    monthly_income = data.annual_inc / 12
    affordability = emi / monthly_income

    # -------- LOAN AMOUNT HARD CAP --------
    if data.purpose == "credit_card":
        max_loan_allowed = PURPOSE_MAX_MULTIPLIER[data.purpose] * monthly_income
    else:
        max_loan_allowed = PURPOSE_MAX_MULTIPLIER[data.purpose] * data.annual_inc

    if data.loan_amnt > max_loan_allowed:
        return {
            "customer_id": data.customer_id,
            "decision": "reject",
            "reason": "Loan amount exceeds allowed limit",
            "max_allowed": round(max_loan_allowed, 2)
        }

    # -------- FINAL DECISION --------
    if affordability <= PURPOSE_EMI_CAP[data.purpose] and adjusted_pd <= 0.30:
        decision = "accept"
        risk = "low"
    else:
        decision = "reject"
        risk = "high"

    # -------- DB (UNCHANGED) --------
    conn = get_connenction()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO table_name (
            customer_id, loan_amnt, annual_inc, dti, fico_mean, int_rate,
            term, grade, purpose, pd, expected_loss, affordability_ratio,
            decision, risk_level
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """,
        (
            data.customer_id, data.loan_amnt, data.annual_inc, data.dti,
            data.fico_mean, data.int_rate, data.term, data.grade,
            data.purpose, pd_value, expected_loss, affordability,
            decision, risk
        )
    )
    conn.commit()
    cur.close()
    conn.close()

    return {
        "customer_id": data.customer_id,
        "pd": round(pd_value, 3),
        "adjusted_pd": round(adjusted_pd, 3),
        "expected_loss": round(expected_loss, 2),
        "emi": round(emi, 2),
        "affordability_ratio": round(affordability, 2),
        "decision": decision,
        "risk_level": risk
    }

