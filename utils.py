from typing import Union
from spacy import load
import re
from collections import Counter
# Importing DataFrame for typing purposes
from pandas import DataFrame
# Loading english stopwords
from nltk.corpus import stopwords
eng_stopwords = set(stopwords.words('english'))
# NLP object for lemmatization
nlp = load("en_core_web_sm")


def basic_parser(full_definition: str) -> str:
    """Parses a Word's full definition, removes unwanted characters and parts such as example usage.

    Args:
        full_definition (str): The full definition text of a Word, to be parsed

    Returns:
        str: a basic parsed string, removes the tags for splitting definitions as well as some special characters
    """
    cleaned = ""
    cleaned = re.findall(":.+\\n", full_definition)
    cleaned = ''.join([definition.strip() for definition in cleaned])
    # cleaned = re.sub(":|,|\.|\(|\)", "", cleaned).strip()
    cleaned = cleaned.replace(':', '').replace(',', '').replace(
        '.', '').replace('(', '').replace(')', '').replace(';', '').replace("/", " ").strip()
    if not cleaned:
        cleaned = full_definition.replace(':', '').replace(',', '').replace(
            '.', '').replace('(', '').replace(')', '').replace(';', '').replace("/", " ").strip()
    return cleaned.lower()


def prep_definition_text(cleaned_definition: str, remove_stopwords: bool = True) -> set:
    """Prepares the definition text for graphing by removing all stopwords and returning a set of the words in the definition

    Args:
        cleaned_definition (str): A clean definition of the word. No unwanted parts or special characters
        remove_stopwords (bool, optional): If true, then the function removes all stopwords. Defaults to True.

    Returns:
        set: A set of words in the definition text
    """
    return set(cleaned_definition.split()) - eng_stopwords if remove_stopwords else set(cleaned_definition.split())


def definition_word_counter(cleaned_definition: str, remove_stopwords: bool = True) -> Counter:
    """Returns a Counter object representing the number of times each word in the definition text appears in the definition

    Args:
        cleaned_definition (str): A clean definition of the word. No unwanted parts or special characters
        remove_stopwords (bool, optional): If true, then the function removes all stopwords. Defaults to True.

    Returns:
        Counter: A Counter object representing the number of times each word in the definition text appears in the definition
    """
    if remove_stopwords:
        words = [word for word in cleaned_definition.lower().split()
                 if word not in eng_stopwords]
        return Counter(words)
    else:
        return Counter(cleaned_definition.lower().split())


def complexity_index(df: DataFrame, text: str) -> str:
    """Calculates an index for the complexity of the given text

    Args:
        df (_type_): The Pandas Dataframe containing the values used in calculating the index
        text (str): The text to be calculated

    Returns:
        str: The average of the index values for each word,
        or a message warning the user that there are no words and therefore a division by zero was attempted
    """
    index = 0
    count = 0
    # Cleaning the text provided, returning a list of all the words
    cleaned_text = prep_complexity_index_text(text)
    # Looping through all the words
    for word in cleaned_text:
        try:
            # Trying to get the value for the word as is
            index += float(df.frequency[df.word == word])
            count += 1
        except TypeError:  # Errors occur when the word is not in the dictionary
            # Lemmatizing the word and trying again
            word_lemma = get_lemma(word)
            if word_lemma and word_lemma != word:
                try:
                    index += float(df.frequency[df.word == word_lemma])
                    count += 1
                except TypeError:
                    print(word)
            else:
                print(word)
    # Returning the average value of all the words
    return str(index / count) if count != 0 else "Error, Attempted Division by Zero"


def get_lemma(word: str) -> Union[str, None]:
    """Getting the lemma of the given word

    Args:
        word (str): Word to be lemmatized

    Returns:
        Union[str, None]: Lemmatized word or None if no lemma was found
    """
    doc = nlp(word)
    return doc[0].lemma_ if doc else None


def prep_complexity_index_text(text: str) -> list[str]:
    """Removes all unwanted characters and splits the text into words, lowercases everything
    then removes all stopwords

    Args:
        text (str): Text to be cleaned and preped

    Returns:
        list[str]: List of words to be passed to the complexity index calculator
    """
    # Remove unwanted characters
    no_special_characters = re.sub(":|,|\.|\(|\)|[|]|\"", "", text).strip()
    # Split, lower, and remove stopwords
    no_stopwords = [word.lower() for word in no_special_characters.split()
                    if word not in eng_stopwords]
    return no_stopwords

# if __name__ == "__main__":
#     run = Word('run')
#     cleaned_run = basic_parser(run.full_definition)
#     print(prep_definition_text(cleaned_run))
#     print(definition_word_counter(cleaned_run))


if __name__ == "__main__":
    pass
