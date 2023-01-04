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
    """Asynchronously get the data in MongoDB for Word

    Args:
        word (str): the word to get the data for

    Returns:
        dict: a dictionary of data for the word from MongoDB
    """
    word_data = await collection.find_one({'word': f"{word}\n"})
    return word_data


async def get_word_definition_words(word_data: dict) -> list:
    """Takes a word dictionary data and gets all the word data dictionaries for all the words in its definition

    Args:
        word_data (dict): A word data dictionary from MongoDB which contains the full text definition of that word

    Returns:
        list: The list of word data for all words in the original words definition
    """
    tasks = []
    words_data_in_definition = []
    definition_text = word_data["dictionary_definitions"]
    if definition_text:
        words_in_definition = prep_definition_text(
            basic_parser(word_data["dictionary_definitions"]))
        for word in words_in_definition:
            tasks.append(async_get_word_data(word))
        words_data_in_definition = await asyncio.gather(*tasks)
    return words_data_in_definition

# First Attempt


async def recursive_hyponyms(depth: int, starting_word: str):
    graph_list = []
    layers_dict = {starting_word: 0}
    starting_word_data = await async_get_word_data(starting_word)

    async def entity_hyponyms(n: int, max_depth: int, word_data: dict):
        if n < max_depth:
            n += 1
            words_in_definition = await get_word_definition_words(word_data)
            for definition_word_data in words_in_definition:
                graph_list.append(
                    (word_data["word"], definition_word_data["word"]))
                layers_dict[definition_word_data["word"]] = n
                entity_hyponyms(n, max_depth, definition_word_data)
        return 0

    entity_hyponyms(0, depth, starting_word_data)
    return graph_list, layers_dict

# Second Attempt


async def get_word_data(depth: int, starting_word: str):
    graph_list = []
    layers_dict = {starting_word: 0}
    starting_word_data = await async_get_word_data(starting_word)
    tasks = []

    async def recursive_word_data(n: int, max_depth: int, word_data: dict):
        print(
            f"Current Depth: {n}, until Max Depth {max_depth} for Word: {word_data['word']}")
        if n < max_depth and word_data:
            n += 1
            words_in_definition = await get_word_definition_words(word_data)
            for definition_word_data in words_in_definition:
                if definition_word_data:
                    graph_list.append(
                        (word_data["word"], definition_word_data["word"]))
                    layers_dict[definition_word_data["word"]] = n
                    word_task = asyncio.create_task(recursive_word_data(
                        n, max_depth, definition_word_data))
                    tasks.append(word_task)
    initial_word_task = asyncio.create_task(
        recursive_word_data(0, depth, starting_word_data))
    tasks.insert(0, initial_word_task)
    await asyncio.gather(*tasks)
    return graph_list, layers_dict


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
    graph, layers = await get_word_data(3, "run")
    print(len(graph))

if __name__ == "__main__":
    asyncio.run(main())
