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

st.title("🩺 Disease Prediction")


# =====================================================
# LOAD MODEL (Cached)
# =====================================================
@st.cache_resource
def load_model():
    model = joblib.load("models/disease.pkl")
    encoder = joblib.load("models/disease_label_encoder.pkl")
    symptoms = joblib.load("models/symptom_columns.pkl")
    return model, encoder, symptoms


model, encoder, symptoms = load_model()


# =====================================================
# SYMPTOM SELECTION
# =====================================================
st.write("Select your symptoms:")

selected_symptoms = []

# Show in columns for cleaner UI
cols = st.columns(3)

for i, symptom in enumerate(symptoms):
    with cols[i % 3]:
        if st.checkbox(symptom):
            selected_symptoms.append(symptom)


# =====================================================
# PREDICTION
# =====================================================
if st.button("Predict Disease"):

    if not selected_symptoms:
        st.warning("Please select at least one symptom.")
        st.stop()

    input_vector = [0] * len(symptoms)

    for symptom in selected_symptoms:
        index = symptoms.index(symptom)
        input_vector[index] = 1

    input_df = pd.DataFrame([input_vector], columns=symptoms)

    probabilities = model.predict_proba(input_df)[0]
    top_indices = probabilities.argsort()[-3:][::-1]

    st.subheader("🔍 Top 3 Possible Diseases")

    for idx in top_indices:
        disease_name = encoder.inverse_transform([idx])[0]
        confidence = probabilities[idx] * 100
        st.write(f"*{disease_name}* — {confidence:.2f}%")

    # Most likely
    predicted_disease = encoder.inverse_transform([top_indices[0]])[0]
    result_text = f"Most Likely Disease: {predicted_disease}"

    st.success(translate_text(result_text, language))

    # =====================================================
    # SHAP EXPLANATION
    # =====================================================
    st.subheader("🧠 Why This Prediction?")

    try:
        explainer = shap.TreeExplainer(model)
        shap_values = explainer(input_df)

        fig = plt.figure()
        shap.plots.waterfall(
            shap_values[0, :, top_indices[0]],
            show=False
        )

        st.pyplot(fig)

    except Exception:
        st.info("SHAP explanation not available for this model.")