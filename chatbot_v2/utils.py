import spacy
from joblib import load

nlp = spacy.load('en_core_web_sm')


def spacy_tokenizer(text):
    doc = nlp(text)
    return [token.lemma_ for token in doc if not token.is_stop and not token.is_punct]


def predict_intent(text):
    pipeline = load('./resources/models/basic_intent_model.joblib')

    probabilities = pipeline.predict_proba([text])[0]
    max_prob_index = probabilities.argmax()
    intent = pipeline.classes_[max_prob_index]
    confidence = probabilities[max_prob_index]

    # TODO build intent classifier
    # i want all intents to look like this intent.<base-intent>.<sub-intent>

    return intent, confidence
