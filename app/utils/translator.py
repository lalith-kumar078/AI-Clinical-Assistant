from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import streamlit as st
import torch

@st.cache_resource
def load_translator():
    model_name = "Helsinki-NLP/opus-mt-en-hi"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    return tokenizer, model

def translate_text(text, language):
    if language == "English":
        return text

    tokenizer, model = load_translator()

    inputs = tokenizer(text, return_tensors="pt", truncation=True)
    outputs = model.generate(**inputs, max_length=512)
    translated = tokenizer.decode(outputs[0], skip_special_tokens=True)

    return translated
