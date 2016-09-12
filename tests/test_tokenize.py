# coding: utf-8

from ujsonpath import tokenize


class TestTokenize:
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

        query = 'level1.level2["level3"]'
        expected_tokens = ['level1', 'level2', '[level3]']
        assert list(tokenize(query)) == expected_tokens

    def test_tokenize_union(self):
        query = 'level1.level2[4,2][level3a,level3b]'
        expected_tokens = ['level1', 'level2', '[4,2]', '[level3a,level3b]']
        assert list(tokenize(query)) == expected_tokens

        query = 'level1.level2["level3a","level3b"]'
        expected_tokens = ['level1', 'level2', '[level3a,level3b]']
        assert list(tokenize(query)) == expected_tokens

    def test_tokenize_quoted_identifiers(self):
        query = 'level1.level2["$.level3[0,1]\\[:-1]"]'
        expected_tokens = ['level1', 'level2', '[$.level3[0\\,1]\\\\[\\:-1]]']
        assert list(tokenize(query)) == expected_tokens

    def test_tokenize_escaped_union(self):
        query = 'level1.level2[level3\\,1]'
        expected_tokens = ['level1', 'level2', '[level3\\,1]']
        assert list(tokenize(query)) == expected_tokens

    def test_tokenize_quoted_union(self):
        query = 'level1.level2["level3,1"]'
        expected_tokens = ['level1', 'level2', '[level3\\,1]']
        assert list(tokenize(query)) == expected_tokens

    def test_tokenize_quotes(self):
        query = 'level1.level2["level3 \':)\'"]'
        expected_tokens = ['level1', 'level2', '[level3 \'\\:)\']']
        assert list(tokenize(query)) == expected_tokens

        query = "level1.level2['level3 \":)\"'']"
        expected_tokens = ['level1', 'level2', '[level3 "\\:)"]']
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