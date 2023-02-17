import time
import logging
import base64
from itertools import pairwise, chain
from collections import Counter

import requests
from neo4j import GraphDatabase
from neo4j import Record
import neo4j
from msgspec.json import decode

from settings import URI, AUTH
from msgspec_custom_structs import *

from nltk.corpus import stopwords
eng_stopwords = set(stopwords.words('english'))


class Neo4jDriverManager:

    def __init__(self, uri: str, authentication: tuple[str, str]):
        self.driver = GraphDatabase.driver(uri, auth=authentication)
        self.session = self.driver.session(
            database='neo4j', default_access_mode=neo4j.READ_ACCESS)
        self.tx = self.session.begin_transaction()

    def reset_transaction(self):
        '''Close the Transaction if not already closed, and begin a new transaction'''
        if not self.tx.closed():
            self.tx.close()
        self.tx = self.session.begin_transaction()

    def close(self):
        '''Close the Transaction, Session, and Driver Connections'''
        self.tx.close()
        self.session.close()
        self.driver.close()

    def get_word_result(self, word: str) -> list[tuple[str, str]]:
        sub_start = time.time()
        result = self.tx.run(
            f"MATCH (w:Word) USING TEXT INDEX w:Word(value) WHERE w.value = '{word}' MATCH p = (w)-[:HAS_WORD*1..3]->(:Word) RETURN p;")
        print(time.time() - sub_start)
        word_result = [record for record in result]
        graph_tuples = self.parse_records(word_result)
        return graph_tuples

    def parse_records(self, query_record: list[Record]) -> list[tuple[str, str]]:
        word_records = [word_record.data()['p']
                        for word_record in query_record]
        graph_tuples = [(word_data[-3]['value'], word_data[-1]['value'])
                        for word_data in word_records]
        return graph_tuples


class Neo4jHTTPManager:
    """
    A Class that manages the connection to, and queries to the Neo4j database, 
    along with the parsing of the data for visualization
    """

    def __init__(self):
        # TODO: Make this part, regarding passwords, much more secure
        username, password = AUTH
        credentials = f"{username}:{password}"
        credentials_b64 = base64.b64encode(credentials.encode()).decode()
        self.headers = {
            "Authorization": f"Basic {credentials_b64}"
        }
        self.endpoint = "http://localhost:7474/db/data/transaction/commit"

    def spec_word_rows(self, spec_response: bytes) -> list[tuple[str, str]]:
        return [(data.row[0][-3]['value'], data.row[0][-1]['value']) for data in spec_response.results[0].data]

    def get_word_rows(self, spec_response: Result, include_stopwords: bool) -> Counter[tuple[str, str]]:
        """Parses the msgspec response object into a Counter object of word, word tuples 

        Args:
            spec_response (bytes): The parsed json object from msgspec
            include_stopwords (bool): Whether or not to inlude stopwords in the result

        Returns:
            Counter[tuple[str, str]]: Counter object of each tuple of word, word
        """
        if not include_stopwords:
            # Create list of tuples containing the word, word relationships, removing all empty nodes
            paths = [tuple(pairwise([d['value'] for d in data.row[0] if d]))
                     for data in spec_response.results[0].data]
            # Removing paths that contain any stopwords
            no_stopword_paths = [path for path in paths if not bool(
                eng_stopwords & set(chain.from_iterable(path)))]
            # Chaining the unique relationships into a set of node, node
            return Counter(chain.from_iterable(no_stopword_paths))
        else:
            return Counter(chain.from_iterable([tuple(pairwise([d['value'] for d in data.row[0] if d])) for data in spec_response.results[0].data]))

    def spec_word_rows_with_length(self, spec_response: bytes) -> list[tuple[str, str, int]]:
        return [(data.row[0][-3]['value'], data.row[0][-1]['value'], (len(data.row[0]) / 2 + 0.5)) for data in spec_response.results[0].data]

    def get_word_paths_raw(self, value: str, path_length: int) -> bytes:
        with requests.Session() as session:
            # Define the Neo4j query
            query = {
                "statements": [
                    {
                        "statement": f"MATCH (w:Word) USING TEXT INDEX w:Word(value) WHERE w.value = '{value}' MATCH p = (w)-[:HAS_WORD*1..{path_length}]->(:Word) RETURN p;",
                        "resultDataContents": ["row"]
                    }
                ]
            }

            # Send the request to the Neo4j endpoint
            response = session.post(
                self.endpoint, json=query, headers=self.headers)
            return response.content

    def get_two_word_paths_raw(self, first_word: str, second_word: str, max_path_length: int) -> bytes:
        with requests.Session() as session:
            # Define the Neo4j query
            query = {
                "statements": [
                    {
                        "statement": f"MATCH p=(start:Word)-[:HAS_WORD*1..{max_path_length}]->(end:Word) WHERE start.value = '{first_word}' AND end.value = '{second_word}' RETURN p ORDER BY length(p) ASC",
                        "resultDataContents": ["row"]
                    }
                ]
            }

            # Send the request to the Neo4j endpoint
            response = session.post(
                self.endpoint, json=query, headers=self.headers)
            return response.content

    def get_word_data(self, value: str, path_length: int, include_stopwords: bool) -> Counter[tuple[str, str]]:
        """Gets the words connected to the starting word up to a depth specified by path_length

        Args:
            value (str): The word value to start the search from
            path_length (int): The maximum depth/path length of definitions to get the words of

        Returns:
            Counter[tuple[str, str]]: Node, Node relationships representing the network of words connected to the starting word
        """
        word_path = self.get_word_paths_raw(value, path_length)
        raw_data = decode(word_path, type=Result)
        return self.get_word_rows(raw_data, include_stopwords)

    def get_two_word_data(self, first_word: str, second_word: str, path_length: int, include_stopwords: bool) -> Counter[tuple[str, str]]:
        """Gets the word paths that connect two words, and parses the data into a list of tuples representing the nodes and relationships

        Args:
            first_word (str): The word to connect to the second word
            second_word (str): The second word to be connected to
            path_length (int): The maximum path length to search for when attempting to connect both words

        Returns:
            Counter[tuple[str, str]]: Node, Node relationships representing the paths between both words
        """
        # Get the JSON Path bytes from the HTTP api
        word_path = self.get_two_word_paths_raw(
            first_word, second_word, path_length)
        # Decode the bytes using MsgSpec and the Result Struct
        raw_data = decode(word_path, type=Result)
        # Return the rows of the decoded data
        return self.get_word_rows(raw_data, include_stopwords)


if __name__ == "__main__":
    database = Neo4jHTTPManager()
    start = time.time()
    word_result = database.get_word_data("defenestration", 2)
    print(time.time() - start)
    print(len(word_result))
    print(word_result[:100])
