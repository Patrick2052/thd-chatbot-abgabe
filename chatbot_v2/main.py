import json
from flask import Flask, request, jsonify
from pydantic import BaseModel
from typing import Dict, List, Any, Tuple, Literal
import spacy
from spacy.tokens import Doc

nlp = spacy.load("en_core_web_sm")


def tokenize_text(text: str):
    res = nlp(text)
    print(type(res))
    return res
    # return [token.text.lower() for token in nlp(text)]


# def get_lemmas(phrases):
#     """get the base version of the words in the phrase"""
#     return [[token.lemma_ for token in nlp(phrase)] for phrase in phrases]


def get_lemmas_single(text: str, filter_stop_etc=True) -> List[str]:
    """get base version of words in text"""
    doc = nlp(text)

    if filter_stop_etc:
        return [token.lemma_ for token in doc if not token.is_stop and not token.is_punct]
    else:
        return [token.lemma_ for token in doc]


class Intent(BaseModel):
    name: str
    text: List[str]
    keywords: List[str]
    enteties: List[str]


class Entety(BaseModel):
    name: str
    text: List[str]


class CapturedEntety(BaseModel):
    captured_info: str
    base_entety: Entety


class ChatFlowModel(BaseModel):
    intents: Dict[str, Intent]
    enteties: Dict[str, Entety]


class ChatMessage(BaseModel):
    author: Literal["user", "chatbot"]
    text: str


class ConversationState(BaseModel):
    messages: List[ChatMessage] = []
    # describes if a current intent is active or the bot is looking for an intent
    current_active_intent: Intent | None = None
    captured_enteties: List[CapturedEntety] = []


# ! init the chatbot dataset
with open('/home/patrick/projects/thd-chatbot-project/chatbot_v2/resources/conversation.json', "r", encoding="utf-8") as f:
    chat_data = json.load(f)
    # prepare dataset
    chatflowmodel = ChatFlowModel.model_validate(chat_data)

    for intent, data in chatflowmodel.intents.items():
        cleaned_keywords = []

        for keyword in data.keywords:
            for lemma in get_lemmas_single(keyword):
                if lemma not in cleaned_keywords:
                    cleaned_keywords.append(lemma)

        data.keywords = cleaned_keywords
    f.close()

    # ! asser that all enteties in intents exist in enteties
    for intent_key, intent in chatflowmodel.intents.items():
        for ent in intent.enteties:
            assert any(
                ent == defined_ent for defined_ent in chatflowmodel.enteties.keys()), f"Entity: '{ent}' is not defined"


conversation_state = ConversationState()
print(conversation_state)
# conversation_state.append()


def infer_intent(user_input: str) -> List[Dict[str, Any]]:
    # words = [word.lower() for word in user_input.split(" ")]

    # ! this section is basically keyword analysis
    possible_intents = []
    user_in_lemmas = get_lemmas_single(user_input)

    for word in user_in_lemmas:
        # for every user in lemma
        for intent, data in chatflowmodel.intents.items():
            # check all possibel intents
            if word in data.keywords:
                # check all their keywords
                for pos_intent in possible_intents:
                    # if
                    if pos_intent["intent"] == intent:
                        pos_intent["keyword_matches"] += 1
                    break
                else:
                    possible_intents.append({
                        "intent": data,
                        "keyword_matches": 1
                    })
            else:
                continue

    best_intent = None
    if possible_intents:
        best_intent = max(possible_intents, key=lambda x: x["keyword_matches"])

    return possible_intents, best_intent


print("greeting i am chatbot")
print("what can i help you with, ... , possible options are")
while True:

    user_input = input("type: ")
    conversation_state.messages.append(
        ChatMessage(author="user", text=user_input))
    # intents = infer_intent(user_input)
    # if not intents:
    #     print("############ no intent found ###############")
    # else:
    #     print(chatflowmodel.intents.get(intents[0]["intent"]).text[0])
    # text_info = tokenize_text(user_input)
    possible_intents, best_intent = infer_intent(user_input)
    print(possible_intents)
    print("best: ", best_intent)

    if not possible_intents:
        print("sorry i didn't get that..., possible options...")

    conversation_state.current_active_intent = best_intent["intent"]

    #! response needs to come from bot -> for one the intent response
    needed_enteties = []

    # for needed_ent in conversation_state.current_active_intent.enteties:
    #     if not any(ent.name == needed_ent for ent in conversation_state.captured_enteties):

    # print([token.dep_ for token in text_info])
    # print([(ent, ent.text, ent.label_) for ent in text_info.ents])
