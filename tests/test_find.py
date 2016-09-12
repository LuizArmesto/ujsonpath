# coding: utf-8

import pytest

from ujsonpath import parse


@pytest.fixture
def store_json():
    return {
        "store": {
            "book": [
                {
                    "category": "reference",
                    "author": "Nigel Rees",
                    "title": "Sayings of the Century",
                    "price": 8.95
                },
                {
                    "category": "fiction",
                    "author": "Evelyn Waugh",
                    "title": "Sword of Honour",
                    "price": 12.99
                },
                {
                    "category": "fiction",
                    "author": "Herman Melville",
                    "title": "Moby Dick",
                    "isbn": "0-553-21311-3",
                    "price": 8.99
                },
                {
                    "category": "fiction",
                    "author": "J. R. R. Tolkien",
                    "title": "The Lord of the Rings",
                    "isbn": "0-395-19395-8",
                    "price": 22.99
                },
                {
                    "category": "fiction",
                    "title": "The Hobit",
                    "isbn": "0-395-19395-9",
                    "price": 22.99
                }
            ],
            "bicycle": {
                "color": "red",
                "price": 19.95
            }
        },
        "expensive": 10
    }


class TestFind:
    def test_find_bicycle_color(self, store_json):
        query = 'store.bicycle.color'
        expected_values = ['red']
        assert [match.value for match in parse(query).find(store_json)] == expected_values

    def test_find_bicycle_color_using_root(self, store_json):
        query = '$.store.bicycle.color'
        expected_values = ['red']
        assert [match.value for match in parse(query).find(store_json)] == expected_values

    def test_find_first_book_author(self, store_json):
        query = 'store.book[1].author'
        expected_values = ['Evelyn Waugh']
        assert [match.value for match in parse(query).find(store_json)] == expected_values

    def test_find_first_book_author_bracket_notation(self, store_json):
        query = "$['store']['book'][1]['author']"
        expected_values = ['Evelyn Waugh']
        assert [match.value for match in parse(query).find(store_json)] == expected_values

    def test_find_first_book_author_list_index_as_string(self, store_json):
        query = "$['store']['book']['1']['author']"
        expected_values = ['Evelyn Waugh']
        assert [match.value for match in parse(query).find(store_json)] == expected_values

    def test_find_books_author_except_first_and_last_two(self, store_json):
        query = '$.store.book[1:-2].author'
        expected_values = ['Evelyn Waugh', 'Herman Melville']
        assert [match.value for match in parse(query).find(store_json)] == expected_values

    def test_find_slice_a_map(self, store_json):
        query = '$.store[1:-2]'
        expected_values = []
        assert [match.value for match in parse(query).find(store_json)] == expected_values

    def test_find_books_author_union(self, store_json):
        query = '$.store.book[1,2,3].author'
        expected_values = ['Evelyn Waugh', 'Herman Melville', 'J. R. R. Tolkien']
        assert [match.value for match in parse(query).find(store_json)] == expected_values

    def test_find_books_author_and_price_union(self, store_json):
        query = '$.store.book[1,2,3][author, price]'
        expected_values = ['Evelyn Waugh', 12.99, 'Herman Melville', 8.99, 'J. R. R. Tolkien', 22.99]
        assert [match.value for match in parse(query).find(store_json)] == expected_values

    def test_find_authors(self, store_json):
        query = 'store.book[*].author'
        expected_values = ['Nigel Rees', 'Evelyn Waugh', 'Herman Melville', 'J. R. R. Tolkien']
        assert [match.value for match in parse(query).find(store_json)] == expected_values

    def test_find_wildcard_a_value(self, store_json):
        query = 'store.book[0].author[*]'
        expected_values = []
        assert [match.value for match in parse(query).find(store_json)] == expected_values

    def test_find_all_things_in_store(self, store_json):
        query = 'store.*'
        expected_values = [store_json['store']['book'], store_json['store']['bicycle']]
        values = [match.value for match in parse(query).find(store_json)]
        assert len(values) == len(expected_values)
        assert all(el in values for el in expected_values)

    def test_find_all_prices(self, store_json):
        query = '$.store..price'
        with pytest.raises(NotImplementedError):
            parse(query).find(store_json)

    def test_find_multiple_wildcard(self):
        data = {
            "level1": [
                {"level2": [
                    {"level3": "A"},
                    {"level3": "B"}
                ]},
                {"level2": [
                    {"level3": "C"}
                ]}
            ]
        }
        query = 'level1[*].level2[*].level3'
        expected_values = ['A', 'B', 'C']
        assert [match.value for match in parse(query).find(data)] == expected_values

        data = {
            "level1": [
                {"level2": [
                    {"level3": [
                        {"level4": "A"}
                    ]},
                    {"level3": [
                        {"level4": "B"}
                    ]}
                ]},
                {"level2": [
                    {"level3": [
                        {"level4": "C"},
                        {"level4": "D"}
                    ]}
                ]}
            ]
        }
        query = 'level1[*].level2[*].level3[*].level4'
        expected_values = ['A', 'B', 'C', 'D']
        assert [match.value for match in parse(query).find(data)] == expected_values

    def test_find_special_identifiers(self):
        data = {
            "$.level1": [
                {
                    "level2[:-1]": {
                        "level3\\a[0,1]": "A"
                    },
                    "level2[:-2]": {
                        "level3\\b[0,1]": "B"
                    }
                }
            ]
        }
        query = '["$.level1"][*]["level2[:-1]"]["level3\\a[0,1]"]'
        expected_values = ['A']
        assert [match.value for match in parse(query).find(data)] == expected_values