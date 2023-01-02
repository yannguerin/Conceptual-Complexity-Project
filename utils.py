from database_management import Word
import re
from collections import Counter

from nltk.corpus import stopwords
eng_stopwords = set(stopwords.words('english'))


def basic_parser(full_definition: str) -> str:
    """Parses a Word's full definition, removes unwanted characters and parts
    WARNING: This is for prototyping only. This function is not an adequate parser for the complete project.
    If you see this function in the final version of the project, the Author has messed up and offers his sincerest apologies to the Code Deities

    Args:
        full_definition (str): The full definition text of a Word, to be parsed

    Returns:
        str: a basic parsed string, removes the tags for splitting definitions as well as some special characters
    """
    cleaned = ""
    # Removing all number definition tags and new line character
    cleaned = re.sub("\\n\s{0,3}[0-9]{1,3}\s{0,3}\\n",
                     " ", full_definition).replace("\n", " ")
    # Removing any number enclosed in parentheses (including parentheses)
    cleaned = re.sub("\(\d\)", " ", cleaned)
    # Removing any letter definition tags and :, (, and )
    cleaned = re.sub("\s+[a-z]\s+:+", " ", cleaned).replace(":",
                                                            " ").replace("(", " ").replace(")", " ")
    return cleaned.strip()


def prep_definition_text(cleaned_definition: str, remove_stopwords: bool = True) -> set:
    """Prepares the definition text for graphing by removing all stopwords and returning a set of the words in the definition

    Args:
        cleaned_definition (str): A clean definition of the word. No unwanted parts or special characters
        remove_stopwords (bool, optional): If true, then the function removes all stopwords. Defaults to True.

    Returns:
        set: A set of words in the definition text
    """
    return set(cleaned_definition.lower().split()) - eng_stopwords if remove_stopwords else set(cleaned_definition.split())


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


if __name__ == "__main__":
    run = Word('run')
    cleaned_run = basic_parser(run.full_definition)
    print(prep_definition_text(cleaned_run))
    print(definition_word_counter(cleaned_run))
