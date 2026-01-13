from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import torch
import json
import random
import numpy as np
import pickle
import nltk
import os
from nltk.stem import WordNetLemmatizer

from auth import hash_password, verify_password, create_token, verify_token
from database import cursor, conn

# ================= APP =================

app = FastAPI(title="AI Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= NLTK =================

try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")

try:
    nltk.data.find("corpora/wordnet")
except LookupError:
    nltk.download("wordnet")

lemmatizer = WordNetLemmatizer()

# ================= PATHS =================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "..", "model")

WORDS_PATH = os.path.join(MODEL_DIR, "saved_model", "words.pkl")
CLASSES_PATH = os.path.join(MODEL_DIR, "saved_model", "classes.pkl")
MODEL_PATH = os.path.join(MODEL_DIR, "saved_model", "model.pth")
INTENTS_PATH = os.path.join(MODEL_DIR, "dataset", "intents.json")

# ================= LOAD DATA =================

words = pickle.load(open(WORDS_PATH, "rb"))
classes = pickle.load(open(CLASSES_PATH, "rb"))
intents = json.load(open(INTENTS_PATH, "r", encoding="utf-8"))

# ================= MODEL =================

class ChatBotModel(torch.nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super().__init__()
        self.fc1 = torch.nn.Linear(input_size, hidden_size)
        self.relu = torch.nn.ReLU()
        self.fc2 = torch.nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x = self.relu(self.fc1(x))
        return self.fc2(x)

model = ChatBotModel(len(words), 128, len(classes))
model.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"))
model.eval()

# ================= NLP =================

def clean_sentence(sentence):
    tokens = nltk.word_tokenize(sentence)
    return [lemmatizer.lemmatize(w.lower()) for w in tokens if w.isalnum()]

def bag_of_words(sentence):
    sentence_words = clean_sentence(sentence)
    bag = np.zeros(len(words), dtype=np.float32)
    for i, w in enumerate(words):
        if w in sentence_words:
            bag[i] = 1
    return bag

def predict_class(sentence):
    bow = bag_of_words(sentence)
    tensor = torch.from_numpy(bow).unsqueeze(0)

    with torch.no_grad():
        output = model(tensor)
        _, predicted = torch.max(output, dim=1)

    return classes[predicted.item()]

def get_response(tag):
    for intent in intents["intents"]:
        if intent["tag"] == tag:
            return random.choice(intent["responses"])
    return "Sorry, I didn't understand that."

# ================= MODELS =================

class ChatRequest(BaseModel):
    message: str

class User(BaseModel):
    email: str
    password: str

# ================= ROUTES =================

@app.get("/")
def root():
    return {"message": "AI Chatbot Backend Running 🚀"}

@app.post("/signup")
def signup(user: User):
    hashed = hash_password(user.password)
    try:
        cursor.execute(
            "INSERT INTO users (email, password) VALUES (?, ?)",
            (user.email, hashed)
        )
        conn.commit()
        return {"message": "User created"}
    except:
        return {"error": "User already exists"}

@app.post("/login")
def login(user: User):
    cursor.execute(
        "SELECT password FROM users WHERE email=?",
        (user.email,)
    )
    row = cursor.fetchone()

    if row and verify_password(user.password, row[0]):
        token = create_token(user.email)
        return {"token": token}

    return {"error": "Invalid credentials"}

# 🔐 PROTECTED CHAT ENDPOINT
@app.post("/chat")
def chat(
    data: ChatRequest,
    authorization: str = Header(None)
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = authorization.split(" ")[1]
    user_email = verify_token(token)

    if not user_email:
        raise HTTPException(status_code=401, detail="Invalid token")

    tag = predict_class(data.message)
    response = get_response(tag)
    return {"reply": response}
