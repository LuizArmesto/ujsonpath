# coding: utf-8

import json
from collections import namedtuple


# Symbols
ROOT_SYMBOL = '$'
SELF_SYMBOL = '@'
ESCAPE_SYMBOL = '\\'
WILDCARD_SYMBOL = '*'
DESCENDANT_SYMBOL = '..'
QUOTES_SYMBOL = '"\''
SPACE_SYMBOL = ' '
BRACKET_START_SYMBOL = '['
BRACKET_END_SYMBOL = ']'
EXPRESSION_START_SYMBOL = '('
EXPRESSION_END_SYMBOL = ')'
SLICE_OPERATOR_SYMBOL = ':'
UNION_OPERATOR_SYMBOL = ','
OR_OPERATOR_SYMBOL = '|'
FILTER_OPERATOR_SYMBOL = '?'
IDENTIFIER_SYMBOL = '.'


# Node types
class BaseNodeType(object):
    @classmethod
    def process_value(cls, value):
        return None

    @classmethod
    def evaluate(cls, node, data, root):
        raise NotImplementedError()

class RootNodeType(BaseNodeType):
    @classmethod
    def evaluate(cls, node, data, root):
        return [root]


class SelfNodeType(BaseNodeType):
    pass


class WildcardNodeType(BaseNodeType):
    @classmethod
    def evaluate(cls, node, data, root):
        # wildcard should work for lists and dicts
        data = data.value
        if isinstance(data, list):
            value = [Match(val, None) for val in data]
        elif isinstance(data, dict):
            value = [Match(val, None) for val in data.values()]
        else:
            value = [MatchNotFound()]
        return value


class DescendantNodeType(BaseNodeType):
    pass


class SliceNodeType(BaseNodeType):
    @classmethod
    def process_value(cls, value):
        return slice(*[int(i) for i in value.split(SLICE_OPERATOR_SYMBOL) if i])

    @classmethod
    def evaluate(cls, node, data, root):
        try:
            value = [Match(val, None) for val in data.value[node.value]]
        except (KeyError, TypeError):
            value = [MatchNotFound()]
        return value


class ExpressionNodeType(BaseNodeType):
    @classmethod
    def process_value(cls, value):
        return value[1:-1]

class FilterNodeType(BaseNodeType):
    @classmethod
    def process_value(cls, value):
        return value[2:-1]

class IndexNodeType(BaseNodeType):
    @classmethod
    def process_value(cls, value):
        # try to split unions
        value = escaped_split(value, UNION_OPERATOR_SYMBOL)
        if len(value) > 1:
            operator = UnionOperator
        else:
            value = escaped_split(value[0], OR_OPERATOR_SYMBOL)
            if len(value) > 1:
                operator = OrOperator
            else:
                operator = list

        value = clean_list(value)
        # unescape union and slide operators
        value = [val.replace(
            ESCAPE_SYMBOL + ESCAPE_SYMBOL, ESCAPE_SYMBOL).replace(
            ESCAPE_SYMBOL + UNION_OPERATOR_SYMBOL, UNION_OPERATOR_SYMBOL).replace(
            ESCAPE_SYMBOL + OR_OPERATOR_SYMBOL, OR_OPERATOR_SYMBOL).replace(
            ESCAPE_SYMBOL + SLICE_OPERATOR_SYMBOL, SLICE_OPERATOR_SYMBOL).replace(
            ESCAPE_SYMBOL + ROOT_SYMBOL, ROOT_SYMBOL
        ) for val in value]

        value = operator(value)
        return value

    @classmethod
    def evaluate(cls, node, data, root):
        # both, identifier and index, can be accessed as a key
        value = []
        for val in node.value:
            try:
                # try to access directly
                value.append(Match(data.value[val], None))
            except (IndexError, KeyError, TypeError):
                try:
                    # try to convert key to integer
                    value.append(Match(data.value[int(val)], None))
                except (ValueError, IndexError, KeyError, TypeError):
                    # Match not found... try next
                    pass
        if isinstance(node.value, Operator):
            value = node.value.transform(value)
        return value


IdentifierNodeType = IndexNodeType


Node = namedtuple('Node', 'type, value')


class Operator(object):
    def __init__(self, identifiers):
        self.identifiers = identifiers

    def __eq__(self, other):
        return self.identifiers == other.identifiers

    def __getitem__(self, i):
        return self.identifiers[i]

    def transform(self, value):
        raise NotImplementedError()


class UnionOperator(Operator):
    def transform(self, value):
        return value


class OrOperator(Operator):
    def transform(self, value):
        try:
            value = [value[0]]
        finally:
            return value


class MatchNotFound(object):
    value = None

    def __repr__(self):
        return u'MatchNotFound'


class Match(object):
    def __init__(self, value, path):
        self.path = path
        try:
            # value can be an instance of Match
            self.value = value.value
        except AttributeError:
            self.value = value

    def __repr__(self):
        return u'Match(value={value}, path={path})'.format(value=json.dumps(self.value), path=self.path)


class JsonPath(object):
    def __init__(self, nodes):
        self.nodes = nodes

    def __repr__(self):
        return u'JsonPath(nodes={nodes})'.format(nodes=json.dumps(self.nodes))

    def find(self, data):
        data = Match(data, ROOT_SYMBOL)
        root = data
        values = []

        nodes = self.nodes
        while nodes:
            node = nodes[0]
            nodes = nodes[1:]
            node_value = get_node_value(node, data, root)
            data = node_value
            if not nodes:
                values = node_value

        return [value for value in values if not isinstance(value, MatchNotFound)]


def get_node_value(node, data, root):
    try:
        value = [get_node_value(node, datum, root) for datum in data]
    except TypeError:
        value = node.type.evaluate(node, data, root)
    # if the original query have more than one wildcard, we can get a list of lists
    # but we want a flat list
    value = _join_lists(value)
    if not value:
        value = [MatchNotFound()]
    return value


def tokenize(query):
    """
    Extract a list of tokens from query.
    :param query: string
    :return: list
    """

    previous_char = ''
    token = ''
    escaped = False
    quoted = False
    bracketed = False
    expression = False
    quote_used = ''

    query = query.strip()
    for char in query:
        if escaped:
            if char in UNION_OPERATOR_SYMBOL + SLICE_OPERATOR_SYMBOL + OR_OPERATOR_SYMBOL:
                # don't remove escape from union symbol because unions will be evaluated later
                token += ESCAPE_SYMBOL
            escaped = False
            token += char
        elif quoted:
            if char in UNION_OPERATOR_SYMBOL + SLICE_OPERATOR_SYMBOL + OR_OPERATOR_SYMBOL + ESCAPE_SYMBOL + ROOT_SYMBOL:
                # escape special symbols used inside quotation
                token += ESCAPE_SYMBOL
            if char == quote_used:
                quoted = False
                if expression:
                    token += char
            else:
                token += char
        elif char in ESCAPE_SYMBOL:
            escaped = True
        elif char in QUOTES_SYMBOL:
            quote_used = char
            quoted = not quoted
            if expression:
                token += char
        elif char in BRACKET_START_SYMBOL:
            if token:
                yield token
            bracketed = True
            token = char
        elif char in BRACKET_END_SYMBOL:
            token += char
            yield token
            token = ''
            bracketed = False
        elif char in EXPRESSION_START_SYMBOL:
            expression = True
            token += char
        elif char in EXPRESSION_END_SYMBOL:
            expression = False
            token += char
        elif bracketed:
            token += char
        elif char in ROOT_SYMBOL:
            yield char
            token = ''
        elif char in IDENTIFIER_SYMBOL:
            if previous_char and previous_char in IDENTIFIER_SYMBOL:
                yield char + char
            elif token:
                yield token
            token = ''
        else:
            token += char

        previous_char = char

    if token:
        yield token


class Parser(object):
    def __init__(self, tokens):
        self.tokens = tokens

    def _get_node_type(self, token):
        node_types = {
            ROOT_SYMBOL: RootNodeType,
            DESCENDANT_SYMBOL: DescendantNodeType,
            FILTER_OPERATOR_SYMBOL: FilterNodeType,
            EXPRESSION_START_SYMBOL: ExpressionNodeType,
            WILDCARD_SYMBOL: WildcardNodeType
        }
        node_type = node_types.get(token.strip(), None)
        value = token
        if not node_type:
            if token[0] == BRACKET_START_SYMBOL and token[-1] == BRACKET_END_SYMBOL:
                value = token[1:-1]
                # token have not escaped slice delimiter, let's check if it is really a slice
                if SLICE_OPERATOR_SYMBOL in value.replace('\\' + SLICE_OPERATOR_SYMBOL, ''):
                    # it is slice if we found the slice separator
                    node_type = SliceNodeType
                else:
                    node_type = node_types.get(value[0], IdentifierNodeType)
            else:
                # everything else is an identifier
                node_type = IdentifierNodeType
        return node_type, value

    def parse(self):
        nodes = []
        for token in self.tokens:
            node_type, value = self._get_node_type(token)
            try:
                value = node_type.process_value(value)
            except ValueError:
                node_type = IdentifierNodeType
                value = node_type.process_value(value)

            nodes.append(Node(type=node_type, value=value))
        return nodes


def parse(query):
    """
    Parse json path query.
    :param query: string
    :return: JsonPath object
    """
    tokens = list(tokenize(query))
    nodes = Parser(tokens).parse()
    return JsonPath(nodes)


def _join_lists(value):
    try:
        value = [item for sublist in value for item in sublist]
    except TypeError:
        pass
    return value


def clean_list(data, exclude=tuple(), strip=SPACE_SYMBOL):
    cleanned_list = []
    for val in data:
        if val not in exclude:
            try:
                val = val.strip(strip)
            finally:
                cleanned_list.append(val)
    return cleanned_list


def escaped_split(string, char):
    sections = [section + (char if section.endswith(ESCAPE_SYMBOL) else '') for section in string.split(char)]
    result = [''] * len(sections)
    idx = 0
    for section in sections:
        result[idx] += section
        idx += int(not section.endswith(char))
    return clean_list(result, exclude=('',))
