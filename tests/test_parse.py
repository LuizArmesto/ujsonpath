# coding: utf-8

from ujsonpath import parse
from ujsonpath import UnionOperator, OrOperator
from ujsonpath import RootNodeType, WildcardNodeType, DescendantNodeType, SliceNodeType, IndexNodeType, IdentifierNodeType, ExpressionNodeType, FilterNodeType


class TestParse:
    def test_parse_root(self):
        query = '$'
        expected_nodes = [(RootNodeType, None)]
        assert parse(query).nodes == expected_nodes

    def test_parse_fieldnames_one_level(self):
        query = 'level1'
        expected_nodes = [(IdentifierNodeType, ['level1'])]
        assert parse(query).nodes == expected_nodes

    def test_parse_fieldnames_one_level_using_root(self):
        query = '$.level1'
        expected_nodes = [(RootNodeType, None), (IdentifierNodeType, ['level1'])]
        assert parse(query).nodes == expected_nodes

    def test_parse_fieldnames_two_levels(self):
        query = 'level1.level2'
        expected_nodes = [(IdentifierNodeType, ['level1']), (IdentifierNodeType, ['level2'])]
        assert parse(query).nodes == expected_nodes

    def test_parse_fieldnames_multiple_levels(self):
        query = 'level1.level2.level3'
        expected_nodes = [(IdentifierNodeType, ['level1']), (IdentifierNodeType, ['level2']), (IdentifierNodeType, ['level3'])]
        assert parse(query).nodes == expected_nodes

    def test_parse_fieldnames_escaped_separator(self):
        query = 'level1.level\\.2.level3'
        expected_nodes = [(IdentifierNodeType, ['level1']), (IdentifierNodeType, ['level.2']), (IdentifierNodeType, ['level3'])]
        assert parse(query).nodes == expected_nodes

    def test_parse_fieldnames_escaped_backslash(self):
        query = 'level1.level\\\\2.level3'
        expected_nodes = [(IdentifierNodeType, ['level1']), (IdentifierNodeType, ['level\\2']), (IdentifierNodeType, ['level3'])]
        assert parse(query).nodes == expected_nodes

    def test_parse_descendant_first_level(self):
        query = '..fieldname'
        expected_nodes = [(DescendantNodeType, None), (IdentifierNodeType, ['fieldname'])]
        assert parse(query).nodes == expected_nodes

    def test_parse_descendant_second_level(self):
        query = 'level1..fieldname'
        expected_nodes = [(IdentifierNodeType, ['level1']), (DescendantNodeType, None), (IdentifierNodeType, ['fieldname'])]
        assert parse(query).nodes == expected_nodes

    def test_parse_union(self):
        query = 'level1.level2[4,2].level3'
        expected_nodes = [(IdentifierNodeType, ['level1']), (IdentifierNodeType, ['level2']), (IndexNodeType, UnionOperator(['4', '2'])), (IdentifierNodeType, ['level3'])]
        assert parse(query).nodes == expected_nodes

        query = 'level1.level2[4,2]'
        expected_nodes = [(IdentifierNodeType, ['level1']), (IdentifierNodeType, ['level2']), (IndexNodeType, UnionOperator(['4', '2']))]
        assert parse(query).nodes == expected_nodes

        query = 'level1.[level2a, level2b]'
        expected_nodes = [(IdentifierNodeType, ['level1']), (IdentifierNodeType, UnionOperator(['level2a', 'level2b']))]
        assert parse(query).nodes == expected_nodes

        query = 'level1.["level2a",level2b]'
        expected_nodes = [(IdentifierNodeType, ['level1']), (IdentifierNodeType, UnionOperator(['level2a', 'level2b']))]
        assert parse(query).nodes == expected_nodes

        query = "level1.['level2a',  'level2b']"
        expected_nodes = [(IdentifierNodeType, ['level1']), (IdentifierNodeType, UnionOperator(['level2a', 'level2b']))]
        assert parse(query).nodes == expected_nodes

    def test_parse_or(self):
        query = 'level1.level2[4|2].level3'
        expected_nodes = [(IdentifierNodeType, ['level1']), (IdentifierNodeType, ['level2']), (IndexNodeType, OrOperator(['4', '2'])), (IdentifierNodeType, ['level3'])]
        assert parse(query).nodes == expected_nodes

        query = 'level1.level2[4|2]'
        expected_nodes = [(IdentifierNodeType, ['level1']), (IdentifierNodeType, ['level2']), (IndexNodeType, OrOperator(['4', '2']))]
        assert parse(query).nodes == expected_nodes

        query = 'level1.[level2a | level2b]'
        expected_nodes = [(IdentifierNodeType, ['level1']), (IdentifierNodeType, OrOperator(['level2a', 'level2b']))]
        assert parse(query).nodes == expected_nodes

        query = 'level1.["level2a"|level2b]'
        expected_nodes = [(IdentifierNodeType, ['level1']), (IdentifierNodeType, OrOperator(['level2a', 'level2b']))]
        assert parse(query).nodes == expected_nodes

        query = "level1.['level2a'|  'level2b']"
        expected_nodes = [(IdentifierNodeType, ['level1']), (IdentifierNodeType, OrOperator(['level2a', 'level2b']))]
        assert parse(query).nodes == expected_nodes

    def test_parse_index(self):
        query = 'level1.level2[42].level3'
        expected_nodes = [(IdentifierNodeType, ['level1']), (IdentifierNodeType, ['level2']), (IndexNodeType, [42]), (IdentifierNodeType, ['level3'])]
        assert parse(query).nodes == expected_nodes

        query = 'level1.level2[42]'
        expected_nodes = [(IdentifierNodeType, ['level1']), (IdentifierNodeType, ['level2']), (IndexNodeType, [42])]
        assert parse(query).nodes == expected_nodes

    def test_parse_index_nested(self):
        query = 'level1.level2[4][2].level3'
        expected_nodes = [(IdentifierNodeType, ['level1']), (IdentifierNodeType, ['level2']), (IndexNodeType, [4]), (IndexNodeType, [2]), (IdentifierNodeType, ['level3'])]
        assert parse(query).nodes == expected_nodes

        query = 'level1.level2[4][2]'
        expected_nodes = [(IdentifierNodeType, ['level1']), (IdentifierNodeType, ['level2']), (IndexNodeType, [4]), (IndexNodeType, [2])]
        assert parse(query).nodes == expected_nodes

    def test_parse_index_string(self):
        query = 'level1.level2[level3].level4'
        expected_nodes = [(IdentifierNodeType, ['level1']), (IdentifierNodeType, ['level2']), (IdentifierNodeType, ['level3']), (IdentifierNodeType, ['level4'])]
        assert parse(query).nodes == expected_nodes

        query = 'level1[level2][level3][level4]'
        expected_nodes = [(IdentifierNodeType, ['level1']), (IdentifierNodeType, ['level2']), (IdentifierNodeType, ['level3']), (IdentifierNodeType, ['level4'])]
        assert parse(query).nodes == expected_nodes

        query = 'level1["level2"]["level3"]["level4"]'
        expected_nodes = [(IdentifierNodeType, ['level1']), (IdentifierNodeType, ['level2']), (IdentifierNodeType, ['level3']), (IdentifierNodeType, ['level4'])]
        assert parse(query).nodes == expected_nodes

        query = "level1['level2']['level3']['level4']"
        expected_nodes = [(IdentifierNodeType, ['level1']), (IdentifierNodeType, ['level2']), (IdentifierNodeType, ['level3']), (IdentifierNodeType, ['level4'])]
        assert parse(query).nodes == expected_nodes

    def test_parse_wildcard(self):
        query = 'level1.level2[*].level3'
        expected_nodes = [(IdentifierNodeType, ['level1']), (IdentifierNodeType, ['level2']), (WildcardNodeType, None), (IdentifierNodeType, ['level3'])]
        assert parse(query).nodes == expected_nodes

        query = 'level1.level2[*]'
        expected_nodes = [(IdentifierNodeType, ['level1']), (IdentifierNodeType, ['level2']), (WildcardNodeType, None)]
        assert parse(query).nodes == expected_nodes

    def test_parse_slice_start_only(self):
        query = 'level1.level2[1:].level3'
        expected_nodes = [(IdentifierNodeType, ['level1']), (IdentifierNodeType, ['level2']), (SliceNodeType, slice(1)), (IdentifierNodeType, ['level3'])]
        assert parse(query).nodes == expected_nodes

        query = 'level1.level2[1:]'
        expected_nodes = [(IdentifierNodeType, ['level1']), (IdentifierNodeType, ['level2']), (SliceNodeType, slice(1))]
        assert parse(query).nodes == expected_nodes

    def test_parse_slice_end_only(self):
        query = 'level1.level2[:3].level3'
        expected_nodes = [(IdentifierNodeType, ['level1']), (IdentifierNodeType, ['level2']), (SliceNodeType, slice(None, 3)), (IdentifierNodeType, ['level3'])]
        assert parse(query).nodes == expected_nodes

        query = 'level1.level2[:3]'
        expected_nodes = [(IdentifierNodeType, ['level1']), (IdentifierNodeType, ['level2']), (SliceNodeType, slice(None, 3))]
        assert parse(query).nodes == expected_nodes

    def test_parse_slice_start_and_end(self):
        query = 'level1.level2[1:3].level3'
        expected_nodes = [(IdentifierNodeType, ['level1']), (IdentifierNodeType, ['level2']), (SliceNodeType, slice(1, 3)), (IdentifierNodeType, ['level3'])]
        assert parse(query).nodes == expected_nodes

        query = 'level1.level2[1:3]'
        expected_nodes = [(IdentifierNodeType, ['level1']), (IdentifierNodeType, ['level2']), (SliceNodeType, slice(1, 3))]
        assert parse(query).nodes == expected_nodes

    def test_parse_invalid_slice(self):
        query = 'level1.level2[a:3].level3'
        expected_nodes = [(IdentifierNodeType, ['level1']), (IdentifierNodeType, ['level2']), (IdentifierNodeType, ['a:3']), (IdentifierNodeType, ['level3'])]
        assert parse(query).nodes == expected_nodes

    def test_parse_expression(self):
        query = 'level1.level2[(@.length-1)]'
        expected_nodes = [(IdentifierNodeType, ['level1']), (IdentifierNodeType, ['level2']), (ExpressionNodeType, '@.length-1')]
        assert parse(query).nodes == expected_nodes

    def test_parse_filter(self):
        query = 'level1.level2[?(@.price==8.95)]'
        expected_nodes = [(IdentifierNodeType, ['level1']), (IdentifierNodeType, ['level2']), (FilterNodeType, '@.price==8.95')]
        assert parse(query).nodes == expected_nodes