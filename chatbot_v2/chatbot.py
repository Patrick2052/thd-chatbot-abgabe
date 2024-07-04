from pydantic import BaseModel, ValidationError
from typing import Dict, List, Any, Tuple, Literal, Union
import spacy
from spacy.tokens import Doc
import json
from utils import predict_intent
import random

CHATFLOW_URI = "./resources/conversation.json"


nlp = spacy.load("en_core_web_sm")


class Intent(BaseModel):
    name: str
    text: List[str]
    keywords: List[str]
    enteties: List[str]
    final_response: str | None = None


class Entety(BaseModel):
    name: str
    text: List[str]


class Phrase(BaseModel):
    name: str
    text: List[str]


class CapturedEntety(BaseModel):
    captured_info: str
    base_entety: Entety


class ChatFlowModel(BaseModel):
    intents: Dict[str, Intent]
    enteties: Dict[str, Entety]
    phrases: Dict[str, Phrase]


class ChatMessage(BaseModel):
    type: str = "message"
    meta: dict | str | None = None
    author: Literal["user", "chatbot"]
    text: str


class OutgoingMessage(ChatMessage):
    type: str = "message"
    current_active_intent: str | None = None


class IncomingMessage(ChatMessage):
    # a way for the client to force the bot to change context
    # or reset or something else
    force_action: str | None = None


class ConversationState(BaseModel):
    messages: List[ChatMessage] = []
    # describes if a current intent is active or the bot is looking for an intent
    current_active_intent: Intent | None = None
    captured_enteties: List[CapturedEntety] = []


def get_lemmas_single(text: str, filter_stop_etc=True) -> List[str]:
    """get base version of words in text"""
    doc = nlp(text)

    if filter_stop_etc:
        return [token.lemma_ for token in doc if not token.is_stop and not token.is_punct]
    else:
        return [token.lemma_ for token in doc]


#! initialize the chat conversation flow datastructure
with open(CHATFLOW_URI, "r", encoding="utf-8") as f:
    chat_data = json.load(f)
    # prepare dataset
    try:
        chatflowmodel = ChatFlowModel.model_validate(chat_data)
    except ValidationError as e:
        print(e.errors(include_input=False))
        raise e

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

MAIN_GREETING = """
    Hello I am Atlantic Hotels support bot for you as our guest! \n
    I can help you with various tasks related to your stay. \n
    \n

    \t - Point you to hotel facilities \n
    \t - Schedule a wake up call \n
    \t - Schedule a appointment with our travel agent \n
    \t - Manage your arrival and check-in \n
    \t - Help you with departure and check-out \n
    

    \n
    just tell me which one of these you would like to do and we can get started.
    
    """

SECONDARY_GREETING = """
    What else can i help you with? \n
    \n

    \t - Point you to hotel facilities \n
    \t - Schedule a wake up call \n
    \t - Schedule a appointment with our travel agent \n
    \t - Manage your arrival and check-in \n
    \t - Help you with departure and check-out \n
    

    \n
    just pick one of these and we can get started.
    
    """

FALLBACK = """
    I didn't quite understand what you want to do. Could you rephrase that?
"""
FALLBACKS = [
    "I didn't quite understand what you want to do. Could you rephrase that?"
]

with open('./resources/fallback.txt', "r", encoding="utf-8") as f:
    for line in f:
        FALLBACKS.append(line.strip().replace("\\n", "\n"))


class Chatbot():
    """the main chatbot and its logic"""

    def __init__(self, websocket: Any):
        self.chatflowmodel = chatflowmodel
        self.websocket = websocket

        self.chat_messages: List[ChatMessage] = []
        self.current_active_intent: Intent | None = None

        self.needed_enteties: List[Entety] = []
        self.active_entity: Entety | None = None
        self.waiting_for_entity_res: bool = False

        # a dict with intent name and the captured enteties for it
        self.captured_enteties: List[CapturedEntety] = []

    async def initialize(self):
        await self.send_response(MAIN_GREETING)

    async def handle_message(self, msg: str):
        """handle a message from the user"""
        print("handle: ", msg)
        raw_msg = msg.lower()

        try:
            message = IncomingMessage.model_validate_json(raw_msg)
        except ValidationError as e:
            print("Message invalid ", e)
            await self.send_response("Message struct invalid - please fix")
            return

        if message.force_action is not None:
            action = message.force_action
            if action == "reset":
                await self.send_response("Sorry for messing this up \n Resetting the conversation to base state...")
                await self.reset_to_default_chat_state()
                await self.send_response(SECONDARY_GREETING)
            return

        self.append_chat_message(message)

        # TODO implement force client actions

        # ! if no active intent - figure out what the user wants
        print("current intent: ", self.current_active_intent)
        if self.current_active_intent is None:
            # figure out a intent
            # print("figure out intent")
            possible_intents, best_intent = self.infer_base_intent(
                message.text)
            if not best_intent:
                await self.send_response(random.choice(FALLBACKS))
            else:
                # print(f"-- new active intent -> {best_intent['intent']}")
                self.current_active_intent = best_intent['intent']
                await self.send_state_update("intent", self.current_active_intent.name)

                await self.send_response(
                    f"Intent: {best_intent['intent'].text[0]}")
                # ! new active intent -> set needed entities
                print("[current active intent entities] ", [
                      ent for ent in self.current_active_intent.enteties])

                for ent_name in self.current_active_intent.enteties:
                    self.append_needed_ent(ent_name)
                print("[INIT NEEDED ENTS] -- updated needed enteties ",
                      [ent.name for ent in self.needed_enteties])
                self.active_entity = self.needed_enteties.pop()
                await self.send_response(self.active_entity.text[0], meta={"active_entity": self.active_entity.name, "sent by": "intent init"})

        else:  # ! there is a running intent - figure out its enteties...
            # await self.send_response("intent is already given - i need to check fo needed ents ")

            # ! ######################
            # ! handle active entity
            # ! ######################

            # if there is an active entity handle this message as response to that
            if self.active_entity:
                print("[ACTIVE ENTITY]: ", self.active_entity.name)

                self.add_captured_entity(self.active_entity, message.text)
                print("setting active entity to none")
                self.active_entity = None
            print("[NO ACTIVE ENTITY]")

            # ! ######################
            # ! get next active entity if there is one
            # ! ######################

            if self.needed_enteties and self.active_entity is None:
                print("[CRITICAL] - before: ",
                      [ent.name for ent in self.needed_enteties])
                self.active_entity = self.needed_enteties.pop()
                print("[CRITICAL] - after: ",
                      [ent.name for ent in self.needed_enteties])

                print("settings active entity")
                await self.send_response(self.active_entity.text[0])
            else:

                # ! ######################
                # ! generate summary
                # ! ######################

                # ! there is no needed entity - present result

                await self.send_response(self.current_active_intent.final_response)

                res = ""
                for ent in self.captured_enteties:
                    res += f"{ent.base_entety.name}:{ent.captured_info}, \n"

                await self.send_response(res)
                # await self.send_response(
                #     f"################# end of conversation (reset) #########################")

                await self.send_response(SECONDARY_GREETING)
                await self.reset_to_default_chat_state()
                return

            # TODO handle error
            print("needed ents update  ", self.needed_enteties)

        print("\n-----------------[END OF HANDLE]---------------\n")
        if self.current_active_intent:
            print("active intent: ", self.current_active_intent.name)
        print("active entity", self.active_entity)
        print("needed ents", [ent.name for ent in self.needed_enteties])
        print("Captured: ", self.captured_enteties)
        print("\n-----------------[END OF HANDLE]---------------\n")

    async def send_response(self, text: str, meta: dict | str = None):
        """send a response to the chat"""

        res = OutgoingMessage(
            meta=meta,
            author="chatbot",
            text=text,
        )
        if self.current_active_intent is not None:
            res.current_active_intent = self.current_active_intent.name

        self.append_chat_message(res)

        await self.websocket.send(res.model_dump_json())

    async def send_state_update(self, key: str, value: str):
        await self.websocket.send(json.dumps({
            "type": "state_update",
            "key": key,
            "value": value
        }))

    # def activate_entity_from_needed(self, entity_name: str):
    #     if any(ent.name == entity_name for ent in self.needed_enteties):
    # def get_next_needed_entity(self):
    #     self.active_entity = self.needed_enteties.pop()

    def append_needed_ent(self, entity_name: str):
        """
        append a needed ent to the needed ents by 
        its name (str)
        """
        # print(f"appending needed ent(): {entity_name}", self.needed_enteties)
        print("[STARTING ADD APPEND NEW ENT] ", entity_name)
        if self.needed_enteties:
            # if there are needed ents
            # check if entity name in needed ents
            if any(ent.name == entity_name for ent in self.needed_enteties):
                return
            else:
                # insert
                ent = self.get_entity_by_name(entity_name)
                if ent is not None:
                    self.needed_enteties.append(ent)

        else:
            print("[NO NEEDED ENTS YET]")
            # there are not needed ents yet
            ent = self.get_entity_by_name(entity_name)
            if ent is not None:
                print(f"appending ent: {ent.name}")
                self.needed_enteties.append(ent)

        print("now", [ent.name for ent in self.needed_enteties])

    def add_captured_entity(self, entity: Entety, value):
        self.captured_enteties.append(CapturedEntety(
            captured_info=value,
            base_entety=entity
        ))

    def get_entity_by_name(self, entity_name: str) -> Entety | None:
        print("getting ent ", entity_name)
        res = self.chatflowmodel.enteties.get(entity_name)
        print("res ", res)
        return res

    async def reset_to_default_chat_state(self):
        self.current_active_intent = None
        self.active_entity = None
        self.needed_enteties = []
        self.captured_enteties = []
        await self.send_state_update("intent", "No Intent")

    def infer_base_intent(self, text: str) -> Tuple[List[Dict[str, Union[Intent, str, int]]], Dict[str, Union[Intent, str, int]]]:
        """
        Infer the basic intent of a message
        """
        possible_intents = []
        best_intent = None

        ml_intent, confidence = predict_intent(text.lower())
        print("ml intent : ", ml_intent, confidence)
        if confidence < 0.4:
            print("fallback")

            # ! this section is basically keyword analysis
            user_in_lemmas = get_lemmas_single(text)

            # ! word spotting
            for word in user_in_lemmas:
                # for every user in lemma
                for intent_name, intent in self.chatflowmodel.intents.items():
                    # check all possibel intents
                    if word in intent.keywords:
                        # check all their keywords
                        for pos_intent in possible_intents:
                            # if
                            if pos_intent["intent"] == intent:
                                pos_intent["keyword_matches"] += 1
                            break
                        else:
                            possible_intents.append({
                                "intent": intent,
                                "keyword_matches": 1
                            })
                    else:
                        continue

            if possible_intents:
                best_intent = max(possible_intents,
                                  key=lambda x: x["keyword_matches"])
        else:
            possible_intents = [].append(
                {"intent": ml_intent, "keyword_matches": None})
            best_intent = {"intent": self.chatflowmodel.intents.get(
                ml_intent), "keyword_matches": None}

        print("best intent ", best_intent)

        return possible_intents, best_intent

    def append_chat_message(self, msg: ChatMessage):
        # author: Literal["user", "chatbot"],
        # text: str):
        """append a chat message"""
        self.chat_messages.append(msg)
