import spacy
from motor import MotorClient
from pymongo import MongoClient

client = MongoClient()
db = client.MerriamWebster
collection = db.UpdatedMerriamWebsterDictionary

nlp = spacy.load("en_core_web_sm")


class Word:

    def __init__(self, word: str):
        self.word = word
        self.word_info = collection.find_one({"word": f"{self.word}\n"})

        # Properties
        if not self.word_info:
            suffix = self.suffix()
            lemma = self._lemma()
            if lemma and suffix:
                self.word_info = collection.find_one({"word": f"{(lemma)}\n"})
            else:
                raise ValueError(
                    "Word {self.word} is not in the Merriam Webster Dictionary.")

        # Add appending of syllables and pronunciation if lemma was used in search
        self.syllables = self.word_info["syllables"]
        self.part_of_speech = self.word_info["part_of_speech"]
        self.pronunciation = self.word_info["pronunciation"]
        self.full_definition = self.word_info["dictionary_definitions"]

    def _lemma(self) -> str:
        doc = nlp(self.word)
        return doc[0].lemma_ if doc else None

    def suffix(self) -> str:
        lemma = self._lemma()
        if self.word.startswith(lemma):
            return lemma, self.word[len(lemma):]
        else:
            return None


def get_single_word_data(word: str) -> dict:
    pass


async def get_word_definition_definitions(word: Word) -> set:
    pass

# Notes
# A few different approaches I could use:
#   First: An asynchronous acquisition of word and their definitions
#   Second: I could write a recursive function where the depth is the max depth of the network graph
#       Similar to my cyto_app project from dash-playground
#   Third: A combination of asynchronous and recursive
#       Though, a loop with range set to depth may just perform the same task as a recursive function, plus would be easier to implement recursively
