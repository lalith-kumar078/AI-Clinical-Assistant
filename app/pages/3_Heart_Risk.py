import streamlit as st
import joblib
import pandas as pd
import shap
import matplotlib.pyplot as plt

from utils.auth import check_auth
from utils.translator import translate_text


# =====================================================
# AUTH PROTECTION
# =====================================================
if not check_auth():
    st.warning("Please login to access this page.")
    st.stop()

language = st.session_state.get("language", "English")

st.title("🫀 Heart Disease Risk Prediction")
st.markdown("AI-powered cardiovascular risk assessment system.")

st.divider()


# =====================================================
# LOAD MODEL (Cached)
# =====================================================
@st.cache_resource
def load_heart_model():
    model = joblib.load("models/heart.pkl")
    encoders = joblib.load("models/heart_label_encoders.pkl")
    columns = joblib.load("models/heart_columns.pkl")
    return model, encoders, columns


try:
    model, encoders, columns = load_heart_model()
except Exception:
    st.error("Model files not found. Please check your models folder.")
    st.stop()


# =====================================================
# INPUT SECTION (Cleaner Layout)
# =====================================================
col1, col2 = st.columns(2)

with col1:
    age = st.number_input("Age", 1, 120, 40)
    sex = st.selectbox("Sex", ["M", "F"])
    chest_pain = st.selectbox("Chest Pain Type", ["ATA", "NAP", "ASY", "TA"])
    resting_bp = st.number_input("Resting Blood Pressure", 80, 200, 120)
    cholesterol = st.number_input("Cholesterol", 100, 600, 200)

with col2:
    fasting_bs = st.selectbox("Fasting Blood Sugar > 120 mg/dl", [0, 1])
    resting_ecg = st.selectbox("Resting ECG", ["Normal", "ST", "LVH"])
    max_hr = st.number_input("Max Heart Rate", 60, 220, 150)
    exercise_angina = st.selectbox("Exercise Angina", ["Y", "N"])
    oldpeak = st.number_input("Oldpeak (ST Depression)", 0.0, 10.0, 1.0)
    st_slope = st.selectbox("ST Slope", ["Up", "Flat", "Down"])


st.divider()


# =====================================================
# PREDICTION LOGIC
# =====================================================
if st.button("🔍 Predict Heart Risk", use_container_width=True):

    input_data = {
        "Age": age,
        "Sex": sex,
        "ChestPainType": chest_pain,
        "RestingBP": resting_bp,
        "Cholesterol": cholesterol,
        "FastingBS": fasting_bs,
        "RestingECG": resting_ecg,
        "MaxHR": max_hr,
        "ExerciseAngina": exercise_angina,
        "Oldpeak": oldpeak,
        "ST_Slope": st_slope
    }

    input_df = pd.DataFrame([input_data])

    try:
        # Encode categorical features
        for col in encoders:
            input_df[col] = encoders[col].transform(input_df[col])

        # Match training column order
        input_df = input_df[columns]

        # Predict
        prediction = model.predict(input_df)[0]
        probability = model.predict_proba(input_df)[0][1] * 100

        st.subheader("📊 Prediction Result")

        if prediction == 1:
            result_text = f"High Risk of Heart Disease — {probability:.2f}% probability"
            st.error(translate_text(result_text, language))
        else:
            result_text = f"Low Risk of Heart Disease — {100 - probability:.2f}% probability"
            st.success(translate_text(result_text, language))

        # =====================================================
        # SHAP EXPLANATION
        # =====================================================
        st.subheader("🧠 AI Explanation")

        try:
            explainer = shap.TreeExplainer(model)
            shap_values = explainer(input_df)

            fig = plt.figure(figsize=(8, 5))

            shap.plots.waterfall(
                shap_values[0, :, 1],
                show=False
            )

            st.pyplot(fig)

        except Exception:
            st.info("SHAP explanation not available for this model type.")

    except Exception as e:
        st.error("Prediction failed. Please check inputs or model compatibility.")