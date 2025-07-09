# backend/app/validator/download_model.py
from transformers import pipeline
from .validator import SQLValidator
from ..config import CODET5_MODEL

def preload():
    pipeline("text2text-generation", model=CODET5_MODEL, device=-1)

if __name__ == "__main__":
    preload()
    print("Model cached.")
