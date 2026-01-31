import streamlit as st
import requests

PD_THRESHOLD = 0.12
LGD = 0.45
st.title("Loan Risk Prediction")

customer_id = st.number_input("Customer ID", min_value=0, step=1)

loan_amnt = st.number_input("Loan Amount", min_value=0)
annual_inc = st.number_input("Annual Income", min_value=0)
dti = st.slider("DTI (%)", min_value=0, max_value=100)
fico = st.slider("FICO Score", min_value=300, max_value=850)
int_rate = st.number_input("Interest Rate (%)", min_value=0)

term = st.selectbox("Loan Term", ["36 months", "60 months"])
grade = st.selectbox("Grade", ["A", "B", "C", "D", "E", "F", "G"])
purpose = st.selectbox(
    "Purpose",
    ["education", "credit_card", "personal", "small_business"]
)

if st.button("Predict"):
    payload = {
        "customer_id": int(customer_id),
        "loan_amnt": loan_amnt,
        "annual_inc": annual_inc,
        "dti": dti,
        "fico_mean": fico,
        "int_rate": int_rate,
        "term": term,
        "grade": grade,
        "purpose": purpose
    }

    try:
        response = requests.post(
            "http://127.0.0.1:8000/predict",
            json=payload
        )

        if response.status_code != 200:
            st.error(f"API Error: {response.text}")
        else:
            result = response.json()
            st.subheader("📊 prediction od the customers details:")

            st.success(f"Customer ID: {result['customer_id']}")
            st.metric("Probability of Default (PD)", round(result["pd"], 4))
            st.metric("Expected Loss", round(result["expected_loss"], 2))
            st.metric("Affordability Ratio", round(result["affordability_ratio"], 2))
            st.metric("Decision", result["decision"])
            st.metric("Risk Level", result["risk_level"])

    except Exception as e:
        st.error(f"Request failed: {e}")

