import re
from collections import Counter

from nltk.corpus import stopwords
eng_stopwords = set(stopwords.words('english'))


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
        '.', '').replace('(', '').replace(')', '').strip()
    if not cleaned:
        cleaned = full_definition.replace(':', '').replace(',', '').replace(
            '.', '').replace('(', '').replace(')', '').strip()
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


# if __name__ == "__main__":
#     run = Word('run')
#     cleaned_run = basic_parser(run.full_definition)
#     print(prep_definition_text(cleaned_run))
#     print(definition_word_counter(cleaned_run))


if __name__ == "__main__":
    print(eng_stopwords)
