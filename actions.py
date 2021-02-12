
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from action_utterance_template import templates
import os
import pandas as pd

from langdetect import detect
from google_trans_new import google_translator  

translator = google_translator()  
def get_template(action_name, language, script, templates=templates):
    return templates[action_name][language][script]


def get_language_and_script(tracker):
    """Return script and language from the latest user message."""
    script = "latin"
    language = "en"
    for event in reversed(tracker.events):
        if event.get("event") == "user":
            parse_data = event['parse_data']
            language = parse_data['language']['name']
            script = parse_data['script']
            break
    return language, script


class ActionGreet(Action):

    def name(self) -> Text:
        return "action_greet"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        language, script = get_language_and_script(tracker)
        dispatcher.utter_message(get_template(self.name(), language, script))
        return []



class ActionDidThatHelp(Action):

    def name(self) -> Text:
        return "action_did_that_help"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        language, script = get_language_and_script(tracker)
        dispatcher.utter_message(get_template(self.name(), language, script))

        return []


class ActionHappy(Action):

    def name(self) -> Text:
        return "action_happy"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        language, script = get_language_and_script(tracker)
        dispatcher.utter_message(get_template(self.name(), language, script))

        return []


class ActionGoodbye(Action):

    def name(self) -> Text:
        return "action_goodbye"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        language, script = get_language_and_script(tracker)
        dispatcher.utter_message(get_template(self.name(), language, script))

        return []



class ActionLanguageSearch(Action):

    def name(self) -> Text:
        return "action_lang_search"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        data_path = os.path.join("data", "cldf-datasets-wals-014143f", "cldf", "languages.csv")
        wals_data = pd.read_csv(data_path)
        entities = list(tracker.get_latest_entity_values("language"))
        
        if len(entities) > 0:
            query_lang = entities.pop()
            query_lang = translator.translate(query_lang,lang_tgt='en')
            query_lang = query_lang.lower().capitalize()
            print(query_lang)

            
            out_row = wals_data[wals_data["Name"] == query_lang].to_dict("records")

            if len(out_row) > 0:
                out_row = out_row[0]
                out_text = "Language %s belongs to the Family %s\n with Genus as %s\n and has ISO code %s" % (out_row["Name"], out_row["Family"], out_row["Genus"], out_row["ISO_codes"])
                dispatcher.utter_message(text = out_text)
            else:
                dispatcher.utter_message(text = "Sorry! We don't have records for the language %s" % query_lang)

        return []