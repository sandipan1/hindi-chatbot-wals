from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

import os
import pandas as pd
import random

from langdetect import detect
from google_trans_new import google_translator  
from newick import read
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
            query_lang_en = translator.translate(text=query_lang, lang_tgt='en')
            query_lang_en = query_lang_en.strip()
            query_lang_en = query_lang_en.lower().capitalize()
            if len(query_lang_en.split(' ')) > 1:
                f = [x.capitalize() for x in query_lang_en.split(' ')]

                query_lang_en = list(set(f).intersection(set(wals_data["Name"])))[0]
            print(query_lang_en)
            
            out_row = wals_data[wals_data["Name"] == query_lang_en].to_dict("records")
            print(len(out_row))
            if len(out_row) > 0:
                out_row = out_row[0]
                out_text = "Language %s belongs to the Family %s\n with Genus as %s\n and has ISO code %s" % (out_row["Name"], out_row["Family"], out_row["Genus"], out_row["ISO_codes"])
                out_text = translator.translate(text=out_text, lang_tgt='hi')
                print(out_text)
                dispatcher.utter_message(text = out_text)
            else:
                # dispatcher.utter_message(text="Sorry, we do not have records for the language %s"%query_lang_en)
                dispatcher.utter_message(text = "क्षमा करें, हमारे पास %s भाषा के रिकॉर्ड नहीं हैं"%query_lang)

        return []

class ActionLanguageSearchFromCountry(Action):
    def name(self) -> Text:
        return "action_lang_search_from_country"

    def print(self, text):
        print('[' + self.name() + ']: ' + text)

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        country = pd.read_csv(os.path.join("data", "cldf-datasets-wals-014143f", "raw", "country.csv"))
        country_language = pd.read_csv(os.path.join("data", "cldf-datasets-wals-014143f", "raw", "countrylanguage.csv"))
        language = pd.read_csv(os.path.join("data", "cldf-datasets-wals-014143f", "raw", "language.csv"))

        entities = list(tracker.get_latest_entity_values("country"))
        if len(entities) > 0:
            query_country = entities.pop()
            query_country_en = translator.translate(text=query_country, lang_tgt='en')
            query_country_en = query_country_en.strip()
            query_country_en = query_country_en.lower().capitalize()
            if len(query_country_en.split(' ')) > 1:
                query_country_en = ' '.join([x.capitalize() for x in query_country_en.split()])

            self.print(query_country_en)
            
            cpk = list(country[country['name'] == query_country_en]['pk'])
            if len(cpk) == 0:
                out_text = 'क्षमा करें, मुझे मेरे डेटासेट में %s देश नहीं मिला'%query_country
            else:
                cpk = cpk[0]
                lpks = list(country_language[country_language['country_pk'] == cpk]['language_pk'])
                if len(lpks) == 0:
                    out_text = 'क्षमा करें, मुझे %s देश के अनुरूप कोई भी भाषा नहीं मिली'%query_country
                else:
                    languages = list(language[language['pk'].isin(lpks)]['name'])
                    if len(languages) > 10:
                        languages = random.sample(languages, 10)
                    out_text = "%s में बोली जाने वाली भाषाएँ इस प्रकार हैं - "%query_country + translator.translate(text=", ".join(languages), lang_tgt='hi')
        else:
            out_text = 'क्षमा करें, मुझे समझ नहीं आया'

        self.print(out_text)
        dispatcher.utter_message(text=out_text)
        return []

class ActionCountrySearchFromLanguage(Action):
    def name(self) -> Text:
        return "action_country_search_from_language"

    def print(self, text):
        print('[' + self.name() + ']: ' + text)

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        country = pd.read_csv(os.path.join("data", "cldf-datasets-wals-014143f", "raw", "country.csv"))
        country_language = pd.read_csv(os.path.join("data", "cldf-datasets-wals-014143f", "raw", "countrylanguage.csv"))
        language = pd.read_csv(os.path.join("data", "cldf-datasets-wals-014143f", "raw", "language.csv"))

        entities = list(tracker.get_latest_entity_values("language"))
        if len(entities) > 0:
            query_language = entities.pop()
            query_language_en = translator.translate(text=query_language, lang_tgt='en')
            query_language_en = query_language_en.strip()
            query_language_en = query_language_en.lower().capitalize()
            if len(query_language_en.split(' ')) > 1:
                f = [x.capitalize() for x in query_lang_en.split(' ')]
                query_lang_en = list(set(f).intersection(set(language["name"])))[0]

            self.print(query_language_en)
            
            lpk = list(language[language['name'] == query_language_en]['pk'])
            if len(lpk) == 0:
                out_text = 'क्षमा करें, मुझे मेरे डेटासेट में %s भाषा नहीं मिली'%query_language
            else:
                lpk = lpk[0]
                cpks = list(country_language[country_language['language_pk'] == lpk]['country_pk'])
                if len(cpks) == 0:
                    out_text = 'क्षमा करें, मुझे ऐसा कोई देश नहीं मिला जहाँ %s भाषा बोली जाती है'%query_language
                else:
                    countries = list(country[country['pk'].isin(cpks)]['name'])
                    if len(countries) > 10:
                        countries = random.sample(countries, 10)
                    out_text = "%s भाषा बोलने वाले देश इस प्रकार हैं - "%query_language + translator.translate(text=", ".join(countries), lang_tgt='hi')
        else:
            out_text = 'क्षमा करें, मुझे समझ नहीं आया'

        self.print(out_text)
        dispatcher.utter_message(text=out_text)
        return []

class ActionGenderSearch(Action):
    def name(self) -> Text:
        return "action_gender_search"

    def print(self, text):
        print('[' + self.name() + ']: ' + text)

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        values = pd.read_csv(os.path.join("data", "cldf-datasets-wals-014143f", "cldf", "values.csv"))
        languages = pd.read_csv(os.path.join("data", "cldf-datasets-wals-014143f", "cldf", "languages.csv"))

        entities = list(tracker.get_latest_entity_values("language"))
        if len(entities) > 0:
            query_language = entities.pop()
            query_language_en = translator.translate(text=query_language, lang_tgt='en')
            query_language_en = query_language_en.strip()
            query_language_en = query_language_en.lower().capitalize()
            if len(query_language_en.split(' ')) > 1:
                f = [x.capitalize() for x in query_lang_en.split(' ')]
                query_lang_en = list(set(f).intersection(set(languages["Name"])))[0]

            self.print(query_language_en)
            
            language_code = list(languages[languages['Name'] == query_language_en]['ID'])
            if len(language_code) == 0:
                out_text = 'क्षमा करें, मुझे मेरे डेटासेट में %s भाषा नहीं मिली'%query_language
            else:
                language_code = language_code[0]
                gender_value = values[values['ID'] == '30A-' + language_code]['Value']
                gender_value = gender_value.iloc[0]
                if gender_value == 1:
                    out_text = '%s भाषा लिंग अज्ञेयवादी है'%query_language
                elif gender_value == 2:
                    out_text = '% भाषा के दो लिंग मूल्य हैं'%query_language
                elif gender_value == 3:
                    out_text = '%s भाषा तीन लिंग मूल्यों का उपयोग करती है'%query_language
                elif gender_value == 4:
                    out_text = '%s भाषा में चार लिंग हैं'%query_language
                else:
                    out_text = '%s भाषा में पाँच लिंग हैं'%query_language
        else:
            out_text = 'क्षमा करें, मुझे समझ नहीं आया'

        self.print(out_text)
        dispatcher.utter_message(text=out_text)
        return []


class ActionAncestorTree():
    def name(self) -> Text:
        return "action_ancestor_search"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        trees= read("data/tree.txt",strip_comments=True)
        entities = list(tracker.get_latest_entity_values("language"))
        data_path = os.path.join("data", "cldf-datasets-wals-014143f", "cldf", "languages.csv")
        wals_data = pd.read_csv(data_path)
        if len(entities) > 0:
            query_lang = entities.pop()
            query_lang_en = translator.translate(text=query_lang, lang_tgt='en')
            query_lang_en = query_lang_en.strip()
            query_lang_en = query_lang_en.lower()
            if len(query_lang_en.split(' ')) > 1:
                f = [x.capitalize() for x in query_lang_en.split(' ')]

                query_lang_en = list(set(f).intersection(set(wals_data["Name"])))[0]
            print(query_lang_en)

        matched_leaves = [] 
        for i, node in enumerate(trees):
            s=node.get_leaves()
            r= [k for k in s if query_lang_en in k.name]
            matched_leaves.extend(r)
            print(r,node,i)

        if len(matched_leaves) > 0:
            for i in matched_leaves:
                anc = get_ancestors(i)
                out_text = "-->".join(anc)
                out_text = translator.translate(text=out_text, lang_tgt='hi')
                dispatcher.utter_message(text="वंश - वृक्ष " + out_text)
        else: 
            dispatcher.utter_message(text='क्षमा करें, मुझे समझ नहीं आया')



class ActionLanguageCousins():
    def name(self) -> Text:
        return "action_cousin_search"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        trees= read("data/tree.txt",strip_comments=True)
        entities = list(tracker.get_latest_entity_values("language"))

        if len(entities) > 0:
            query_lang = entities.pop()
            query_lang_en = translator.translate(text=query_lang, lang_tgt='en')
            query_lang_en = query_lang_en.strip()
            query_lang_en = query_lang_en.lower()
            if len(query_lang_en.split(' ')) > 1:
                f = [x.capitalize() for x in query_lang_en.split(' ')]

                query_lang_en = list(set(f).intersection(set(wals_data["Name"])))[0]
            print(query_lang_en)

        matched_leaves = [] 
        for i, node in enumerate(trees):
            s=node.get_leaves()
            r= [k for k in s if query_lang_en in k.name]
            matched_leaves.extend(r)

            print(r,node,i)

        if len(matched_leaves) > 0:
            for i in matched_leaves:
                anc = get_immediate_cousins(i)
                out_text = ','.join(anc)
                out_text = translator.translate(text=out_text, lang_tgt='hi')
                dispatcher.utter_message(text="मिलती जुलती भाषा  " + out_text)
        else: 
            dispatcher.utter_message(text='क्षमा करें, मुझे समझ नहीं आया')


def get_ancestors(node): 
    ancestors=[]
    ancestors.append(node.name)
    while(node.ancestor): 
        ancestors.append(node.ancestor.name)
        node = node.ancestor 
    return ancestors


def get_immediate_cousins(node): 
    ancestor = node.ancestor 
    return ancestor.get_leaf_names()

