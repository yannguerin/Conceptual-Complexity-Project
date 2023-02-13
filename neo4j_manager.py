import time
import logging
import base64
from itertools import pairwise, chain

import requests
from neo4j import GraphDatabase
from neo4j import Record
import neo4j
from msgspec.json import decode

from settings import URI, AUTH
from msgspec_custom_structs import *


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
    def __init__(self):
        self.session = requests.Session()
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

    def get_word_rows(self, spec_response: bytes) -> set[tuple[str, str]]:
        return set(chain.from_iterable([tuple(pairwise([d['value'] for d in data.row[0] if d])) for data in spec_response.results[0].data]))

    def spec_word_rows_with_length(self, spec_response: bytes) -> list[tuple[str, str, int]]:
        return [(data.row[0][-3]['value'], data.row[0][-1]['value'], (len(data.row[0]) / 2 + 0.5)) for data in spec_response.results[0].data]

    def get_word_paths_raw(self, value: str, path_length: int) -> bytes:
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
        response = self.session.post(
            self.endpoint, json=query, headers=self.headers)
        return response.content

    def get_two_word_paths_raw(self, first_word: str, second_word: str, max_path_length: int) -> dict:
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
        response = self.session.post(
            self.endpoint, json=query, headers=self.headers)
        return response.content

    def get_word_data(self, value: str, path_length: int) -> list[tuple[str, str]]:
        word_path = self.get_word_paths_raw(value, path_length)
        raw_data = decode(word_path, type=Result)
        return self.spec_word_rows(raw_data)

    def get_two_word_data(self, first_word: str, second_word: str, path_length: int) -> list[tuple[str, str]]:
        word_path = self.get_two_word_paths_raw(
            first_word, second_word, path_length)
        raw_data = decode(word_path, type=Result)
        return self.get_word_rows(raw_data)


if __name__ == "__main__":
    database = Neo4jHTTPManager()
    start = time.time()
    word_result = database.get_word_data("defenestration", 2)
    print(time.time() - start)
    print(len(word_result))
    print(word_result[:100])
