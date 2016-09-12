# coding: utf-8

from ujsonpath import parse
from ujsonpath import ROOT_NODE, WILDCARD_NODE, DESCENDANT_NODE, SLICE_NODE, INDEX_NODE, IDENTIFIER_NODE


class TestParse:
    def test_parse_root(self):
        query = '$'
        expected_nodes = [(ROOT_NODE, None)]
        assert parse(query).nodes == expected_nodes

    def test_parse_fieldnames_one_level(self):
        query = 'level1'
        expected_nodes = [(IDENTIFIER_NODE, ['level1'])]
        assert parse(query).nodes == expected_nodes

    def test_parse_fieldnames_one_level_using_root(self):
        query = '$.level1'
        expected_nodes = [(ROOT_NODE, None), (IDENTIFIER_NODE, ['level1'])]
        assert parse(query).nodes == expected_nodes

    def test_parse_fieldnames_two_levels(self):
        query = 'level1.level2'
        expected_nodes = [(IDENTIFIER_NODE, ['level1']), (IDENTIFIER_NODE, ['level2'])]
        assert parse(query).nodes == expected_nodes

    def test_parse_fieldnames_multiple_levels(self):
        query = 'level1.level2.level3'
        expected_nodes = [(IDENTIFIER_NODE, ['level1']), (IDENTIFIER_NODE, ['level2']), (IDENTIFIER_NODE, ['level3'])]
        assert parse(query).nodes == expected_nodes

    def test_parse_fieldnames_escaped_separator(self):
        query = 'level1.level\\.2.level3'
        expected_nodes = [(IDENTIFIER_NODE, ['level1']), (IDENTIFIER_NODE, ['level.2']), (IDENTIFIER_NODE, ['level3'])]
        assert parse(query).nodes == expected_nodes

    def test_parse_fieldnames_escaped_backslash(self):
        query = 'level1.level\\\\2.level3'
        expected_nodes = [(IDENTIFIER_NODE, ['level1']), (IDENTIFIER_NODE, ['level\\2']), (IDENTIFIER_NODE, ['level3'])]
        assert parse(query).nodes == expected_nodes

    def test_parse_descendant_first_level(self):
        query = '..fieldname'
        expected_nodes = [(DESCENDANT_NODE, None), (IDENTIFIER_NODE, ['fieldname'])]
        assert parse(query).nodes == expected_nodes

    def test_parse_descendant_second_level(self):
        query = 'level1..fieldname'
        expected_nodes = [(IDENTIFIER_NODE, ['level1']), (DESCENDANT_NODE, None), (IDENTIFIER_NODE, ['fieldname'])]
        assert parse(query).nodes == expected_nodes

    def test_parse_union(self):
        query = 'level1.level2[4,2].level3'
        expected_nodes = [(IDENTIFIER_NODE, ['level1']), (IDENTIFIER_NODE, ['level2']), (INDEX_NODE, ['4', '2']), (IDENTIFIER_NODE, ['level3'])]
        assert parse(query).nodes == expected_nodes

        query = 'level1.level2[4,2]'
        expected_nodes = [(IDENTIFIER_NODE, ['level1']), (IDENTIFIER_NODE, ['level2']), (INDEX_NODE, ['4', '2'])]
        assert parse(query).nodes == expected_nodes

        query = 'level1.[level2a, level2b]'
        expected_nodes = [(IDENTIFIER_NODE, ['level1']), (IDENTIFIER_NODE, ['level2a', 'level2b'])]
        assert parse(query).nodes == expected_nodes

        query = 'level1.["level2a",level2b]'
        expected_nodes = [(IDENTIFIER_NODE, ['level1']), (IDENTIFIER_NODE, ['level2a', 'level2b'])]
        assert parse(query).nodes == expected_nodes

        query = "level1.['level2a',  'level2b']"
        expected_nodes = [(IDENTIFIER_NODE, ['level1']), (IDENTIFIER_NODE, ['level2a', 'level2b'])]
        assert parse(query).nodes == expected_nodes

    def test_parse_index(self):
        query = 'level1.level2[42].level3'
        expected_nodes = [(IDENTIFIER_NODE, ['level1']), (IDENTIFIER_NODE, ['level2']), (INDEX_NODE, [42]), (IDENTIFIER_NODE, ['level3'])]
        assert parse(query).nodes == expected_nodes

        query = 'level1.level2[42]'
        expected_nodes = [(IDENTIFIER_NODE, ['level1']), (IDENTIFIER_NODE, ['level2']), (INDEX_NODE, [42])]
        assert parse(query).nodes == expected_nodes

    def test_parse_index_nested(self):
        query = 'level1.level2[4][2].level3'
        expected_nodes = [(IDENTIFIER_NODE, ['level1']), (IDENTIFIER_NODE, ['level2']), (INDEX_NODE, [4]), (INDEX_NODE, [2]), (IDENTIFIER_NODE, ['level3'])]
        assert parse(query).nodes == expected_nodes

        query = 'level1.level2[4][2]'
        expected_nodes = [(IDENTIFIER_NODE, ['level1']), (IDENTIFIER_NODE, ['level2']), (INDEX_NODE, [4]), (INDEX_NODE, [2])]
        assert parse(query).nodes == expected_nodes

    def test_parse_index_string(self):
        query = 'level1.level2[level3].level4'
        expected_nodes = [(IDENTIFIER_NODE, ['level1']), (IDENTIFIER_NODE, ['level2']), (IDENTIFIER_NODE, ['level3']), (IDENTIFIER_NODE, ['level4'])]
        assert parse(query).nodes == expected_nodes

        query = 'level1[level2][level3][level4]'
        expected_nodes = [(IDENTIFIER_NODE, ['level1']), (IDENTIFIER_NODE, ['level2']), (IDENTIFIER_NODE, ['level3']), (IDENTIFIER_NODE, ['level4'])]
        assert parse(query).nodes == expected_nodes

        query = 'level1["level2"]["level3"]["level4"]'
        expected_nodes = [(IDENTIFIER_NODE, ['level1']), (IDENTIFIER_NODE, ['level2']), (IDENTIFIER_NODE, ['level3']), (IDENTIFIER_NODE, ['level4'])]
        assert parse(query).nodes == expected_nodes

        query = "level1['level2']['level3']['level4']"
        expected_nodes = [(IDENTIFIER_NODE, ['level1']), (IDENTIFIER_NODE, ['level2']), (IDENTIFIER_NODE, ['level3']), (IDENTIFIER_NODE, ['level4'])]
        assert parse(query).nodes == expected_nodes

    def test_parse_wildcard(self):
        query = 'level1.level2[*].level3'
        expected_nodes = [(IDENTIFIER_NODE, ['level1']), (IDENTIFIER_NODE, ['level2']), (WILDCARD_NODE, None), (IDENTIFIER_NODE, ['level3'])]
        assert parse(query).nodes == expected_nodes

        query = 'level1.level2[*]'
        expected_nodes = [(IDENTIFIER_NODE, ['level1']), (IDENTIFIER_NODE, ['level2']), (WILDCARD_NODE, None)]
        assert parse(query).nodes == expected_nodes

    def test_parse_slice_start_only(self):
        query = 'level1.level2[1:].level3'
        expected_nodes = [(IDENTIFIER_NODE, ['level1']), (IDENTIFIER_NODE, ['level2']), (SLICE_NODE, slice(1)), (IDENTIFIER_NODE, ['level3'])]
        assert parse(query).nodes == expected_nodes

        query = 'level1.level2[1:]'
        expected_nodes = [(IDENTIFIER_NODE, ['level1']), (IDENTIFIER_NODE, ['level2']), (SLICE_NODE, slice(1))]
        assert parse(query).nodes == expected_nodes

    def test_parse_slice_end_only(self):
        query = 'level1.level2[:3].level3'
        expected_nodes = [(IDENTIFIER_NODE, ['level1']), (IDENTIFIER_NODE, ['level2']), (SLICE_NODE, slice(None, 3)), (IDENTIFIER_NODE, ['level3'])]
        assert parse(query).nodes == expected_nodes

        query = 'level1.level2[:3]'
        expected_nodes = [(IDENTIFIER_NODE, ['level1']), (IDENTIFIER_NODE, ['level2']), (SLICE_NODE, slice(None, 3))]
        assert parse(query).nodes == expected_nodes

    def test_parse_slice_start_and_end(self):
        query = 'level1.level2[1:3].level3'
        expected_nodes = [(IDENTIFIER_NODE, ['level1']), (IDENTIFIER_NODE, ['level2']), (SLICE_NODE, slice(1, 3)), (IDENTIFIER_NODE, ['level3'])]
        assert parse(query).nodes == expected_nodes

        query = 'level1.level2[1:3]'
        expected_nodes = [(IDENTIFIER_NODE, ['level1']), (IDENTIFIER_NODE, ['level2']), (SLICE_NODE, slice(1, 3))]
        assert parse(query).nodes == expected_nodes

    def test_parse_invalid_slice(self):
        query = 'level1.level2[a:3].level3'
        expected_nodes = [(IDENTIFIER_NODE, ['level1']), (IDENTIFIER_NODE, ['level2']), (IDENTIFIER_NODE, ['a:3']), (IDENTIFIER_NODE, ['level3'])]
        assert parse(query).nodes == expected_nodes
