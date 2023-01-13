import time
import csv
from motor.motor_asyncio import AsyncIOMotorClient
from utils import definition_word_counter, basic_parser
from collections import Counter
import asyncio
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def find_and_prep_async(word: str) -> Counter:
    definition = ""
    word_document = await collection.find_one({"word": word})
    definition = word_document["dictionary_definitions"]
    if not definition:
        return None
    cleaned_definition = basic_parser(definition)
    definition_counter = definition_word_counter(
        cleaned_definition, remove_stopwords=False)
    return definition_counter


async def prep_rows_async(word: str) -> list[list]:
    rows = []
    definition_counter = await find_and_prep_async(word)
    if definition_counter:
        rows = [[word.strip(), sub_word, count]
                for sub_word, count in definition_counter.items()]
        return rows
    else:
        return None


async def make_tasks(words: list[str]):
    list_of_rows = []
    tasks = []
    for word in words:
        rows_to_write = asyncio.create_task(prep_rows_async(word))
        tasks.append(rows_to_write)
    list_of_rows = await asyncio.gather(*tasks)
    return list_of_rows


async def main(words: list[str]):
    all_rows = await make_tasks(words)
    return all_rows

if __name__ == "__main__":
    start = time.time()
    with open("./word_sample.txt", "r+", encoding="utf-16") as f:
        words = f.readlines()

    client = AsyncIOMotorClient()
    db = client.MerriamWebster
    collection = db.UpdatedMerriamWebsterDictionary
    all_rows = asyncio.run(main(words))
    non_null_rows = [row for row in all_rows if row != None]
    with open("test_graph_items.csv", "w+", encoding="utf-16", newline="") as f:
        csvwriter = csv.writer(f)
        csvwriter.writerow(["word", "word_in_definition", "word_count"])
        for rows_of_rows in non_null_rows:
            csvwriter.writerows(rows_of_rows)
    print(time.time() - start)
