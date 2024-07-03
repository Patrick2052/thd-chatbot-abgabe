"""
only run this from the project base
"""

import pandas as pd
import spacy

from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.metrics import accuracy_score, classification_report
from utils import spacy_tokenizer

from joblib import dump


def train_basic_intent_model():
    df = pd.read_csv('./resources/intents.csv')
    df = df.dropna()

    # df["processed_text"] = df['text'].apply(
    #     lambda text: " ".join(token.text for token in nlp(text.lower())))

    X = df["text"]
    y = df["intent"]

    # X_train, X_test, y_train, y_test = train_test_split(
    # X, y, test_size=0.2, random_state=42)

    vectorizer = TfidfVectorizer(tokenizer=spacy_tokenizer)

    model = LogisticRegression()

    pipeline = make_pipeline(vectorizer, model)
    # pipeline.fit(X_train, y_train)
    pipeline.fit(X, y)
    return pipeline


if __name__ == "__main__":
    print("start...")
    basic_intent_pipeline = train_basic_intent_model()

    dump(basic_intent_pipeline, './resources/models/basic_intent_model.joblib')
    print("finish!")
