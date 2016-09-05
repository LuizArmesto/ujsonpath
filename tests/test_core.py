# coding: utf-8

import pytest

from jsonpath.core import tokenize, parse
from jsonpath.core import ROOT_NODE, WILDCARD_NODE, DESCENDANT_NODE, SLICE_NODE, INDEX_NODE, IDENTIFIER_NODE


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
                }
            ],
            "bicycle": {
                "color": "red",
                "price": 19.95
            }
        },
        "expensive": 10
    }


class TestTokenizer:
    def test_tokenize_root(self):
        query = '$'
        expected_tokens = ['$']
        assert list(tokenize(query)) == expected_tokens

    def test_tokenize_fieldnames_one_level(self):
        query = 'level1'
        expected_tokens = ['level1']
        assert list(tokenize(query)) == expected_tokens

    def test_tokenize_fieldnames_one_level_using_root(self):
        query = '$.level1'
        expected_tokens = ['$', 'level1']
        assert list(tokenize(query)) == expected_tokens

    def test_tokenize_fieldnames_two_levels(self):
        query = 'level1.level2'
        expected_tokens = ['level1', 'level2']
        assert list(tokenize(query)) == expected_tokens

    def test_tokenize_fieldnames_multiple_levels(self):
        query = 'level1.level2.level3'
        expected_tokens = ['level1', 'level2', 'level3']
        assert list(tokenize(query)) == expected_tokens

    def test_tokenize_fieldnames_escaped_separator(self):
        query = 'level1.level\\.2.level3'
        expected_tokens = ['level1', 'level.2', 'level3']
        assert list(tokenize(query)) == expected_tokens

    def test_tokenize_fieldnames_escaped_backslash(self):
        query = 'level1.level\\\\2.level3'
        expected_tokens = ['level1', 'level\\2', 'level3']
        assert list(tokenize(query)) == expected_tokens

    def test_tokenize_descendant_first_level(self):
        query = '..fieldname'
        expected_tokens = ['..', 'fieldname']
        assert list(tokenize(query)) == expected_tokens

    def test_tokenize_descendant_second_level(self):
        query = 'level1..fieldname'
        expected_tokens = ['level1', '..', 'fieldname']
        assert list(tokenize(query)) == expected_tokens

    def test_tokenize_index(self):
        query = 'level1.level2[42].level3'
        expected_tokens = ['level1', 'level2', '[42]', 'level3']
        assert list(tokenize(query)) == expected_tokens

        query = 'level1.level2[42]'
        expected_tokens = ['level1', 'level2', '[42]']
        assert list(tokenize(query)) == expected_tokens

    def test_tokenize_index_nested(self):
        query = 'level1.level2[4][2].level3'
        expected_tokens = ['level1', 'level2', '[4]', '[2]', 'level3']
        assert list(tokenize(query)) == expected_tokens

        query = 'level1.level2[4][2]'
        expected_tokens = ['level1', 'level2', '[4]', '[2]']
        assert list(tokenize(query)) == expected_tokens

    def test_tokenize_wildcard(self):
        query = 'level1.level2[*].level3'
        expected_tokens = ['level1', 'level2', '[*]', 'level3']
        assert list(tokenize(query)) == expected_tokens

        query = 'level1.level2[*]'
        expected_tokens = ['level1', 'level2', '[*]']
        assert list(tokenize(query)) == expected_tokens

    def test_tokenize_slice_start_only(self):
        query = 'level1.level2[1:].level3'
        expected_tokens = ['level1', 'level2', '[1:]', 'level3']
        assert list(tokenize(query)) == expected_tokens

        query = 'level1.level2[1:]'
        expected_tokens = ['level1', 'level2', '[1:]']
        assert list(tokenize(query)) == expected_tokens

    def test_tokenize_slice_end_only(self):
        query = 'level1.level2[:3].level3'
        expected_tokens = ['level1', 'level2', '[:3]', 'level3']
        assert list(tokenize(query)) == expected_tokens

        query = 'level1.level2[:3]'
        expected_tokens = ['level1', 'level2', '[:3]']
        assert list(tokenize(query)) == expected_tokens

    def test_tokenize_slice_start_and_end(self):
        query = 'level1.level2[1:3].level3'
        expected_tokens = ['level1', 'level2', '[1:3]', 'level3']
        assert list(tokenize(query)) == expected_tokens

        query = 'level1.level2[1:3]'
        expected_tokens = ['level1', 'level2', '[1:3]']
        assert list(tokenize(query)) == expected_tokens


class TestParser:
    def test_parse_root(self):
        query = '$'
        expected_nodes = [(ROOT_NODE, None)]
        assert parse(query).nodes == expected_nodes

    def test_parse_fieldnames_one_level(self):
        query = 'level1'
        expected_nodes = [(IDENTIFIER_NODE, 'level1')]
        assert parse(query).nodes == expected_nodes

    def test_parse_fieldnames_one_level_using_root(self):
        query = '$.level1'
        expected_nodes = [(ROOT_NODE, None), (IDENTIFIER_NODE, 'level1')]
        assert parse(query).nodes == expected_nodes

    def test_parse_fieldnames_two_levels(self):
        query = 'level1.level2'
        expected_nodes = [(IDENTIFIER_NODE, 'level1'), (IDENTIFIER_NODE, 'level2')]
        assert parse(query).nodes == expected_nodes

    def test_parse_fieldnames_multiple_levels(self):
        query = 'level1.level2.level3'
        expected_nodes = [(IDENTIFIER_NODE, 'level1'), (IDENTIFIER_NODE, 'level2'), (IDENTIFIER_NODE, 'level3')]
        assert parse(query).nodes == expected_nodes

    def test_parse_fieldnames_escaped_separator(self):
        query = 'level1.level\\.2.level3'
        expected_nodes = [(IDENTIFIER_NODE, 'level1'), (IDENTIFIER_NODE, 'level.2'), (IDENTIFIER_NODE, 'level3')]
        assert parse(query).nodes == expected_nodes

    def test_parse_fieldnames_escaped_backslash(self):
        query = 'level1.level\\\\2.level3'
        expected_nodes = [(IDENTIFIER_NODE, 'level1'), (IDENTIFIER_NODE, 'level\\2'), (IDENTIFIER_NODE, 'level3')]
        assert parse(query).nodes == expected_nodes

    def test_parse_descendant_first_level(self):
        query = '..fieldname'
        expected_nodes = [(DESCENDANT_NODE, None), (IDENTIFIER_NODE, 'fieldname')]
        assert parse(query).nodes == expected_nodes

    def test_parse_descendant_second_level(self):
        query = 'level1..fieldname'
        expected_nodes = [(IDENTIFIER_NODE, 'level1'), (DESCENDANT_NODE, None), (IDENTIFIER_NODE, 'fieldname')]
        assert parse(query).nodes == expected_nodes

    def test_parse_index(self):
        query = 'level1.level2[42].level3'
        expected_nodes = [(IDENTIFIER_NODE, 'level1'), (IDENTIFIER_NODE, 'level2'), (INDEX_NODE, 42), (IDENTIFIER_NODE, 'level3')]
        assert parse(query).nodes == expected_nodes

        query = 'level1.level2[42]'
        expected_nodes = [(IDENTIFIER_NODE, 'level1'), (IDENTIFIER_NODE, 'level2'), (INDEX_NODE, 42)]
        assert parse(query).nodes == expected_nodes

    def test_parse_index_nested(self):
        query = 'level1.level2[4][2].level3'
        expected_nodes = [(IDENTIFIER_NODE, 'level1'), (IDENTIFIER_NODE, 'level2'), (INDEX_NODE, 4), (INDEX_NODE, 2), (IDENTIFIER_NODE, 'level3')]
        assert parse(query).nodes == expected_nodes

        query = 'level1.level2[4][2]'
        expected_nodes = [(IDENTIFIER_NODE, 'level1'), (IDENTIFIER_NODE, 'level2'), (INDEX_NODE, 4), (INDEX_NODE, 2)]
        assert parse(query).nodes == expected_nodes

    def test_parse_index_string(self):
        query = 'level1.level2[level3].level4'
        expected_nodes = [(IDENTIFIER_NODE, 'level1'), (IDENTIFIER_NODE, 'level2'), (IDENTIFIER_NODE, 'level3'), (IDENTIFIER_NODE, 'level4')]
        assert parse(query).nodes == expected_nodes

        query = 'level1[level2][level3][level4]'
        expected_nodes = [(IDENTIFIER_NODE, 'level1'), (IDENTIFIER_NODE, 'level2'), (IDENTIFIER_NODE, 'level3'), (IDENTIFIER_NODE, 'level4')]
        assert parse(query).nodes == expected_nodes

        query = 'level1["level2"]["level3"]["level4"]'
        expected_nodes = [(IDENTIFIER_NODE, 'level1'), (IDENTIFIER_NODE, 'level2'), (IDENTIFIER_NODE, 'level3'), (IDENTIFIER_NODE, 'level4')]
        assert parse(query).nodes == expected_nodes

        query = "level1['level2']['level3']['level4']"
        expected_nodes = [(IDENTIFIER_NODE, 'level1'), (IDENTIFIER_NODE, 'level2'), (IDENTIFIER_NODE, 'level3'), (IDENTIFIER_NODE, 'level4')]
        assert parse(query).nodes == expected_nodes

    def test_parse_wildcard(self):
        query = 'level1.level2[*].level3'
        expected_nodes = [(IDENTIFIER_NODE, 'level1'), (IDENTIFIER_NODE, 'level2'), (WILDCARD_NODE, None), (IDENTIFIER_NODE, 'level3')]
        assert parse(query).nodes == expected_nodes

        query = 'level1.level2[*]'
        expected_nodes = [(IDENTIFIER_NODE, 'level1'), (IDENTIFIER_NODE, 'level2'), (WILDCARD_NODE, None)]
        assert parse(query).nodes == expected_nodes

    def test_parse_slice_start_only(self):
        query = 'level1.level2[1:].level3'
        expected_nodes = [(IDENTIFIER_NODE, 'level1'), (IDENTIFIER_NODE, 'level2'), (SLICE_NODE, slice(1)), (IDENTIFIER_NODE, 'level3')]
        assert parse(query).nodes == expected_nodes

        query = 'level1.level2[1:]'
        expected_nodes = [(IDENTIFIER_NODE, 'level1'), (IDENTIFIER_NODE, 'level2'), (SLICE_NODE, slice(1))]
        assert parse(query).nodes == expected_nodes

    def test_parse_slice_end_only(self):
        query = 'level1.level2[:3].level3'
        expected_nodes = [(IDENTIFIER_NODE, 'level1'), (IDENTIFIER_NODE, 'level2'), (SLICE_NODE, slice(None, 3)), (IDENTIFIER_NODE, 'level3')]
        assert parse(query).nodes == expected_nodes

        query = 'level1.level2[:3]'
        expected_nodes = [(IDENTIFIER_NODE, 'level1'), (IDENTIFIER_NODE, 'level2'), (SLICE_NODE, slice(None, 3))]
        assert parse(query).nodes == expected_nodes

    def test_parse_slice_start_and_end(self):
        query = 'level1.level2[1:3].level3'
        expected_nodes = [(IDENTIFIER_NODE, 'level1'), (IDENTIFIER_NODE, 'level2'), (SLICE_NODE, slice(1, 3)), (IDENTIFIER_NODE, 'level3')]
        assert parse(query).nodes == expected_nodes

        query = 'level1.level2[1:3]'
        expected_nodes = [(IDENTIFIER_NODE, 'level1'), (IDENTIFIER_NODE, 'level2'), (SLICE_NODE, slice(1, 3))]
        assert parse(query).nodes == expected_nodes


class TestFinder:
    def test_find_bicycle_color(self, store_json):
        query = 'store.bicycle.color'
        expected_values = ['red']
        assert parse(query).find(store_json) == expected_values

    def test_find_bicycle_color_using_root(self, store_json):
        query = '$.store.bicycle.color'
        expected_values = ['red']
        assert parse(query).find(store_json) == expected_values

    def test_find_first_book_author(self, store_json):
        query = 'store.book[1].author'
        expected_values = ['Evelyn Waugh']
        assert parse(query).find(store_json) == expected_values

    def test_find_books_author_except_first_and_last(self, store_json):
        query = '$.store.book[1:-1].author'
        expected_values = ['Evelyn Waugh', 'Herman Melville']
        assert parse(query).find(store_json) == expected_values

    def test_find_authors(self, store_json):
        query = 'store.book[*].author'
        expected_values = ['Nigel Rees', 'Evelyn Waugh', 'Herman Melville', 'J. R. R. Tolkien']
        assert parse(query).find(store_json) == expected_values

    def test_find_all_things_in_store(self, store_json):
        query = 'store.*'
        expected_values = [store_json['store']['book'], store_json['store']['bicycle']]
        assert parse(query).find(store_json) == expected_values
        assert parse(query).find(store_json) == expected_values

    def test_find_all_prices(self, store_json):
        query = '$.store..price'
        with pytest.raises(NotImplementedError):
            parse(query).find(store_json)