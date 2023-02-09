# Custom Structs to speed up parsing JSON data from Neo4j API

from msgspec import Struct


class Value(Struct):
    word: str


class RowItem(Struct):
    value: Value


class Row(Struct):
    row: list[list[dict]]


class Data(Struct):
    data: list[Row]


class Result(Struct):
    results: list[Data]
