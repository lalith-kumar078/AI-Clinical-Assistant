import streamlit as st
import fitz
import re
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

from utils.auth import check_auth
from utils.translator import translate_text


# =====================================================
# AUTH PROTECTION
# =====================================================
if not check_auth():
    st.warning("Please login to access this page.")
    st.stop()

language = st.session_state.get("language", "English")

st.title("📄 Medical Report Analyzer")


# =====================================================
# PDF TEXT EXTRACTION
# =====================================================
def extract_text_from_pdf(uploaded_file):
    text = ""
    try:
        file_bytes = uploaded_file.read()
        pdf = fitz.open(stream=file_bytes, filetype="pdf")

        for page in pdf:
            text += page.get_text()

        return text.strip()

    except Exception:
        return ""


# =====================================================
# LOAD SUMMARIZATION MODEL (Cached)
# =====================================================
@st.cache_resource
def load_summarizer():
    model_name = "google/flan-t5-base"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    return tokenizer, model


# =====================================================
# CLINICAL VALUE EXTRACTION
# =====================================================
def extract_medical_values(text):

    findings = {}

    # Blood Pressure
    bp_match = re.search(r'(\d{2,3})/(\d{2,3})', text)
    if bp_match:
        systolic = int(bp_match.group(1))
        diastolic = int(bp_match.group(2))
        findings["Blood Pressure"] = f"{systolic}/{diastolic}"
        findings["BP_Status"] = (
            "High" if systolic > 140 or diastolic > 90 else "Normal"
        )

    # Cholesterol
    chol_match = re.search(r'cholesterol.*?(\d+)', text, re.IGNORECASE)
    if chol_match:
        chol = int(chol_match.group(1))
        findings["Cholesterol"] = f"{chol} mg/dL"
        findings["Cholesterol_Status"] = (
            "High" if chol > 200 else "Normal"
        )

    # Hemoglobin
    hb_match = re.search(r'hemoglobin.*?(\d+)', text, re.IGNORECASE)
    if hb_match:
        hb = int(hb_match.group(1))
        findings["Hemoglobin"] = f"{hb} g/dL"
        findings["Hemoglobin_Status"] = (
            "Low" if hb < 12 else "Normal"
        )

    return findings


# =====================================================
# FILE UPLOADER
# =====================================================
uploaded_file = st.file_uploader(
    "Upload Medical Report (PDF)",
    type=["pdf"]
)

if uploaded_file:

    st.info("Extracting text from report...")

    extracted_text = extract_text_from_pdf(uploaded_file)

    if not extracted_text:
        st.error("Could not extract text from PDF.")
        st.stop()

    # Display preview
    st.subheader("📑 Extracted Text (Preview)")
    st.text_area(
        "Report Content",
        extracted_text[:2000],
        height=250
    )

    # =====================================================
    # SUMMARIZATION
    # =====================================================
    st.info("Loading AI model...")
    tokenizer, model = load_summarizer()

    st.info("Generating AI Summary...")

    # Limit input length for model
    cleaned_text = extracted_text[:2000]

    input_prompt = f"Summarize this medical report clearly:\n{cleaned_text}"

    try:
        inputs = tokenizer(
            input_prompt,
            return_tensors="pt",
            truncation=True
        )

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_length=150
            )

        summary_text = tokenizer.decode(
            outputs[0],
            skip_special_tokens=True
        )

        translated_summary = translate_text(summary_text, language)

        st.subheader("🧠 AI-Generated Summary")
        st.success(translated_summary)

    except Exception:
        st.error("Failed to generate summary.")
        st.stop()

    # =====================================================
    # CLINICAL INSIGHTS
    # =====================================================
    st.subheader("📊 Extracted Clinical Insights")

    findings = extract_medical_values(extracted_text)

    if findings:
        for key, value in findings.items():
            if "Status" not in key:

                status_key = f"{key}_Status"
                status = findings.get(status_key, "")

                display_text = f"{key}: {value} — {status}"
                translated_display = translate_text(display_text, language)

                if status in ["High", "Low"]:
                    st.error(translated_display)
                else:
                    st.success(translated_display)
    else:
        st.info("No key medical values detected.")