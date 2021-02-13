from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

import os
import pandas as pd

from langdetect import detect
from google_trans_new import google_translator  

translator = google_translator()  

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
            query_lang = translator.translate(text=query_lang, lang_tgt='en')
            query_lang = query_lang.rstrip()
            query_lang = query_lang.lower().capitalize()
            print(type(query_lang))
            print(query_lang)
            
            out_row = wals_data[wals_data["Name"] == query_lang].to_dict("records")
            print(len(out_row))
            if len(out_row) > 0:
                out_row = out_row[0]
                out_text = "Language %s belongs to the Family %s\n with Genus as %s\n and has ISO code %s" % (out_row["Name"], out_row["Family"], out_row["Genus"], out_row["ISO_codes"])
                dispatcher.utter_message(text = out_text)
            else:
                dispatcher.utter_message(text = "Sorry! We don't have records for the language %s" % query_lang)

        return []