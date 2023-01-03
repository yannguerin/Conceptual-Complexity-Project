from utils import prep_definition_text, basic_parser
from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient
import spacy
import asyncio
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


client = AsyncIOMotorClient()
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


async def async_get_word_data(word: str) -> dict:
    word_data = await collection.find_one({'word': f"{word}\n"})
    return word_data


async def get_word_definition_words(word_data: dict) -> set:
    tasks = []
    words_data_in_definition = []
    words_in_definition = prep_definition_text(
        basic_parser(word_data["dictionary_definitions"]))
    for word in words_in_definition:
        tasks.append(async_get_word_data(word))
    words_data_in_definition = await asyncio.gather(*tasks)
    return words_data_in_definition

# Notes
# A few different approaches I could use:
#   First: An asynchronous acquisition of word and their definitions
#   Second: I could write a recursive function where the depth is the max depth of the network graph
#       Similar to my cyto_app project from dash-playground
#   Third: A combination of asynchronous and recursive
#       Though, a loop with range set to depth may just perform the same task as a recursive function, plus would be easier to implement recursively

# Code from WordsAPI Database Project


async def async_store_word(db_collection, json_word: dict):
    if isinstance(json_word, dict):
        await db_collection.insert_one(json_word)
    else:
        raise TypeError("Word Value must be of type: dict")


async def store_word_list(db_collection, list_of_word_dicts: list):
    tasks = []
    if isinstance(list_of_word_dicts, list):
        for word in list_of_word_dicts:
            tasks.append(async_store_word(db_collection, word))
        await asyncio.gather(*tasks)


async def main():
    run = await async_get_word_data("run")
    print(run)

if __name__ == "__main__":
    asyncio.run(main())
