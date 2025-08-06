
import streamlit as st
import requests
import base64

st.title("📚 RAG Chatbot")

api_url = st.text_input("API Base URL", "http://127.0.0.1:8000")

uploaded_file = st.file_uploader("Upload Document", type=["pdf", "docx", "txt", "jpg", "png", "csv", "db"])
if uploaded_file and st.button("Upload"):
    res = requests.post(f"{api_url}/upload", files={"file": uploaded_file})
    st.json(res.json())

question = st.text_input("Your Question")
img = st.file_uploader("Optional Image for OCR", type=["jpg", "jpeg", "png"])

if st.button("Ask"):
    payload = {"question": question}
    if img:
        img_bytes = img.read()
        payload["image_base64"] = base64.b64encode(img_bytes).decode()
    res = requests.post(f"{api_url}/query", json=payload)
    st.json(res.json())
