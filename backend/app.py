from fastapi import FastAPI
import torch, pickle, random, json
import numpy as np
from nltk.stem import WordNetLemmatizer
import nltk

nltk.download("punkt")
lemmatizer = WordNetLemmatizer()

app = FastAPI()

model = torch.load("../model/saved_model/model.pth", map_location="cpu")
words = pickle.load(open("../model/saved_model/words.pkl","rb"))
classes = pickle.load(open("../model/saved_model/classes.pkl","rb"))
intents = json.load(open("../model/dataset/intents.json"))
