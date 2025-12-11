from nltk.tokenize import word_tokenize
import re


def normalize_text(text: str) -> list:
    text = text.lower()
    text = re.sub(r"[^a-z0-9 ]", "", text)
    return word_tokenize(text)