
import os
import base64
import io
from fastapi import FastAPI, File, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import pytesseract
from PIL import Image
import pdfplumber
import docx
import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer
import openai

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

texts = []
metadatas = []

model = SentenceTransformer("all-MiniLM-L6-v2")
index = faiss.IndexFlatL2(384)

class QueryRequest(BaseModel):
    question: str
    image_base64: str = None

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    filename = file.filename
    ext = filename.split('.')[-1].lower()
    content = await file.read()

    text = ""
    if ext == "pdf":
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
    elif ext == "docx":
        doc = docx.Document(io.BytesIO(content))
        text = "\n".join([p.text for p in doc.paragraphs])
    elif ext == "txt":
        text = content.decode()
    elif ext in ["jpg", "jpeg", "png"]:
        image = Image.open(io.BytesIO(content))
        text = pytesseract.image_to_string(image)
    elif ext == "csv":
        df = pd.read_csv(io.BytesIO(content))
        text = df.to_string()
    elif ext == "db":
        text = "SQLite support pending"
    else:
        return {"error": "Unsupported file type"}

    chunks = [text[i:i+500] for i in range(0, len(text), 400)]
    embeddings = model.encode(chunks)

    for i, emb in enumerate(embeddings):
        index.add(emb.reshape(1, -1))
        texts.append(chunks[i])
        metadatas.append({"filename": filename, "chunk": i})

    return {"status": "uploaded", "chunks": len(chunks)}

@app.post("/query")
async def query(request: QueryRequest):
    question = request.question
    if request.image_base64:
        image = Image.open(io.BytesIO(base64.b64decode(request.image_base64)))
        question += " " + pytesseract.image_to_string(image)

    q_emb = model.encode([question])
    D, I = index.search(q_emb, k=5)

    context = "\n\n".join([texts[i] for i in I[0]])
    prompt = f"Context: {context}\n\nQuestion: {question}\nAnswer:"

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )

    answer = response["choices"][0]["message"]["content"]
    return {
        "answer": answer.strip(),
        "context": context,
        "source": [metadatas[i] for i in I[0]]
    }
