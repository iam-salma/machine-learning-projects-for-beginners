import streamlit as st
import pandas as pd
import joblib

st.set_page_config(page_title="Telecom Churn Prediction", layout="centered")
st.title("📡 Telecom Churn Prediction App")

# ---------------- Load Model + Feature Names ----------------
try:
    model = joblib.load("models/churn_model.pkl")
    feature_names = joblib.load("models/feature_names.pkl")  # saved during training
except Exception as e:
    st.error(f"❌ Error loading model or feature names: {e}")
    st.stop()


# ---------------- Input Form ----------------
with st.form("input_form"):
    st.subheader("Enter Telecom Features")

    year = st.number_input("📅 Year", value=2024)
    month = st.number_input("🗓 Month", value=1, min_value=1, max_value=12)

    circle = st.text_input("🌐 Circle", value="All India")
    type_of_connection = st.text_input("🔌 Type of Connection", value="wireline")
    service_provider = st.text_input("🏢 Service Provider", value="APSFL")

    lag_1_month = st.number_input("⏮ Lag 1 Month Usage", value=647917.0)
    rolling_avg_3m = st.number_input("📊 Rolling Average (3 months)", value=0.0)
    market_share = st.number_input("💼 Market Share", value=0.000543)
    circle_rank = st.number_input("⭐ Circle Rank", value=12.0)

    submitted = st.form_submit_button("🔍 Predict Churn")


# ---------------- Prediction Logic ----------------
if submitted:
    try:
        with st.spinner("⏳ Predicting churn..."):

            # Base raw input
            raw_input = pd.DataFrame([{
                "year": year,
                "month": month,
                "circle": circle,
                "type_of_connection": type_of_connection,
                "service_provider": service_provider,
                "lag_1_month": lag_1_month,
                "rolling_avg_3m": rolling_avg_3m,
                "market_share": market_share,
                "circle_rank": circle_rank
            }])

            # Apply SAME one-hot encoding as training
            input_encoded = pd.get_dummies(raw_input, drop_first=True)

            # Add missing columns from training
            for col in feature_names:
                if col not in input_encoded.columns:
                    input_encoded[col] = 0  # default for missing dummies

            # Ensure same column order
            input_encoded = input_encoded[feature_names]

            # Predict churn probability
            prob = model.predict_proba(input_encoded)[0][1]
            percentage = prob * 100

    except Exception as e:
        st.error(f"❌ Prediction Error: {e}")
        st.stop()

    # ---------------- Styled Result Card ----------------
    st.markdown("""
        <style>
            .result-card {
                background-color: #1e1e1e;
                padding: 25px;
                border-radius: 18px;
                box-shadow: 0 4px 14px rgba(0,0,0,0.5);
                margin-top: 25px;
                text-align: center;
            }
            .result-title {
                font-size: 28px;
                font-weight: 700;
                color: #ffffff;
            }
            .result-value {
                font-size: 42px;
                font-weight: 900;
                color: #00c853;
                margin-top: 10px;
            }
            .result-value-danger {
                font-size: 42px;
                font-weight: 900;
                color: #ff1744;
                margin-top: 10px;
            }
        </style>
    """, unsafe_allow_html=True)

    if prob > 0.5:
        color_class = "result-value-danger"
        message = "⚠️ High Risk of Churn"
    else:
        color_class = "result-value"
        message = "✅ Low Risk of Churn"

    st.markdown(
        f"""
        <div class="result-card">
            <div class="result-title">{message}</div>
            <div class="{color_class}">{percentage:.2f}%</div>
        </div>
        """,
        unsafe_allow_html=True
    )
