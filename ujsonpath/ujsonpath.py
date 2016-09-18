# coding: utf-8

import json
from collections import namedtuple

# Symbols
ROOT_SYMBOL = '$'
SELF_SYMBOL = '@'
ESCAPE_SYMBOL = '\\'
WILDCARD_SYMBOL = '*'
DESCENDANT_SYMBOL = '..'
SINGLE_QUOTE_SYMBOL = '\''
DOUBLE_QUOTE_SYMBOL = '"'
QUOTES_SYMBOL = SINGLE_QUOTE_SYMBOL + DOUBLE_QUOTE_SYMBOL
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
        # unescape special chars from itentifier
        value = [unquote(val).replace(
            ESCAPE_SYMBOL + ESCAPE_SYMBOL, ESCAPE_SYMBOL).replace(
            ESCAPE_SYMBOL + UNION_OPERATOR_SYMBOL, UNION_OPERATOR_SYMBOL).replace(
            ESCAPE_SYMBOL + OR_OPERATOR_SYMBOL, OR_OPERATOR_SYMBOL).replace(
            ESCAPE_SYMBOL + SLICE_OPERATOR_SYMBOL, SLICE_OPERATOR_SYMBOL).replace(
            ESCAPE_SYMBOL + IDENTIFIER_SYMBOL, IDENTIFIER_SYMBOL).replace(
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

    def __repr__(self):
        return '{}{}'.format(self.__class__.__name__, self.identifiers)

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
        return u'JsonPath(nodes={nodes})'.format(nodes=self.nodes)

    def find(self, data):
        data = Match(data, ROOT_SYMBOL)
        root = data
        values = []

        nodes = self.nodes
        while nodes:
            node = nodes[0]
            nodes = nodes[1:]
            node_value = _evaluate_node(node, data, root)
            data = node_value
            if not nodes:
                values = node_value

        return [value for value in values if not isinstance(value, MatchNotFound)]


def _evaluate_node(node, data, root):
    try:
        value = [_evaluate_node(node, datum, root) for datum in data]
    except TypeError:
        value = node.type.evaluate(node, data, root)
    # if the original query have more than one wildcard, we can get a list of lists
    # but we want a flat list
    value = join_lists(value)
    if not value:
        value = [MatchNotFound()]
    return value

def generate_tokens(query):
    """
    Extract a list of tokens from query.
    :param query: string
    :return: list
    """

    previous_char = ''
    token = ''
    escaped = False
    quoted = False
    quote_used = ''

    quotes = {
        SINGLE_QUOTE_SYMBOL: SINGLE_QUOTE_SYMBOL,
        DOUBLE_QUOTE_SYMBOL: DOUBLE_QUOTE_SYMBOL,
        EXPRESSION_START_SYMBOL: EXPRESSION_END_SYMBOL,
    }

    query = query.strip()
    for char in query:
        if escaped:
            escaped = False
            token += char
        elif quoted:
            if char in (UNION_OPERATOR_SYMBOL, SLICE_OPERATOR_SYMBOL, OR_OPERATOR_SYMBOL, ESCAPE_SYMBOL):
                # escape special symbols used inside quotation
                token += ESCAPE_SYMBOL
            quoted = not char == quotes[quote_used]
            token += char
        elif char in ESCAPE_SYMBOL:
            escaped = True
            token += char
        elif char in quotes:
            quote_used = char
            quoted = True
            token += char
        elif previous_char + char == DESCENDANT_SYMBOL:
            yield DESCENDANT_SYMBOL
        elif char in (IDENTIFIER_SYMBOL, BRACKET_START_SYMBOL, BRACKET_END_SYMBOL):
            yield token
            token = ''
        else:
            token += char

        previous_char = char

    yield token


def tokenize(query):
    tokens = list(generate_tokens(query))
    tokens = clean_list(tokens, exclude=('', ))  # remove empty strings
    return tokens


def _get_node_type(token):
    node_types = {
        ROOT_SYMBOL: RootNodeType,
        DESCENDANT_SYMBOL: DescendantNodeType,
        FILTER_OPERATOR_SYMBOL: FilterNodeType,
        EXPRESSION_START_SYMBOL: ExpressionNodeType,
        WILDCARD_SYMBOL: WildcardNodeType,
        SINGLE_QUOTE_SYMBOL: IdentifierNodeType,
        DOUBLE_QUOTE_SYMBOL: IdentifierNodeType,
    }
    node_type = node_types.get(token.strip(), None)
    value = token
    if not node_type:
        if SLICE_OPERATOR_SYMBOL in value.replace('\\' + SLICE_OPERATOR_SYMBOL, ''):
            # it is slice if we found the slice separator
            node_type = SliceNodeType
        else:
            node_type = node_types.get(value[0], IdentifierNodeType)
    return node_type, value


def parse(query):
    """
    Parse json path query.
    :param query: string
    :return: JsonPath object
    """
    nodes = []
    tokens = tokenize(query)
    for token in tokens:
        node_type, value = _get_node_type(token)
        try:
            value = node_type.process_value(value)
        except ValueError:
            node_type = IdentifierNodeType
            value = node_type.process_value(value)

        nodes.append(Node(type=node_type, value=value))
    return JsonPath(nodes)


def join_lists(value):
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


def unquote(string):
    result = string
    try:
        if string[0] in QUOTES_SYMBOL and string[0] == string[-1]:
            result = string[1:-1]
    finally:
        return result