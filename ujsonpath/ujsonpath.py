# coding: utf-8

import json
from collections import namedtuple


# Symbols
ROOT_SYMBOL = '$'
SELF_SYMBOL = '@'  # TODO
ESCAPE_SYMBOL = '\\'
WILDCARD_SYMBOL = '*'
DESCENDANT_SYMBOL = '..'  # TODO
QUOTES_SYMBOL = '"\''
SPACE_SYMBOL = ' '
BRACKET_START_SYMBOL = '['
BRACKET_END_SYMBOL = ']'
EXPRESSION_START_SYMBOL = '('  # TODO
EXPRESSION_END_SYMBOL = ')'  # TODO
SLICE_OPERATOR_SYMBOL = ':'
UNION_OPERATOR_SYMBOL = ','
FILTER_OPERATOR_SYMBOL = '?'  # TODO
IDENTIFIER_SYMBOL = '.'


# Node types
ROOT_NODE = 'ROOT'
SELF_NODE = 'SELF'  # TODO
WILDCARD_NODE = 'WILDCARD'
DESCENDANT_NODE = 'DESCENDANT'  # TODO
SLICE_NODE = 'SLICE'
EXPRESSION_NODE = 'EXPRESSION'  # TODO
FILTER_NODE = 'FILTER'  # TODO
INDEX_NODE = 'INDEX'
IDENTIFIER_NODE = INDEX_NODE


Node = namedtuple('Node', 'type, value')


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
            node_value = self._get_node_value(node, data, root)
            data = node_value
            if not nodes:
                values = node_value

        return [value for value in values if not isinstance(value, MatchNotFound)]

    def _get_node_value(self, node, data, root):
        path = None
        if node.type == ROOT_NODE:
            value = root
        elif isinstance(data, list):
            # data can be a Match object or a list of Match objects
            value = [self._get_node_value(node, datum, root) for datum in data]
        elif node.type in (IDENTIFIER_NODE, INDEX_NODE):
            # both, identifier and index, can be accessed as a key
            try:
                # try to access directly
                value = [Match(data.value[val], path) for val in node.value]
            except (IndexError, KeyError, TypeError):
                try:
                    # try to convert to integer index
                    value = [Match(data.value[int(val)], path) for val in node.value]
                except (ValueError, IndexError, KeyError, TypeError):
                    # both tries failed
                    value = [MatchNotFound()]
        elif node.type == SLICE_NODE:
            try:
                value = [Match(val, path) for val in data.value[node.value]]
            except (KeyError, TypeError):
                value = [MatchNotFound()]
        elif node.type == WILDCARD_NODE:
            # wildcard should work for lists and dicts
            data = data.value
            if isinstance(data, list):
                value = [Match(val, path) for val in data]
            elif isinstance(data, dict):
                value = [Match(val, path) for val in data.values()]
            else:
                value = [MatchNotFound()]
        elif node.type == DESCENDANT_NODE:
            raise NotImplementedError('Descendant is not implemented')
        else:  # pragma: no cover
            raise ValueError('Unknown node type: {}'.format(node.type))

        if isinstance(value, list) and len(value) >= 1 and isinstance(value[0], list):
            # if the original query have more than one wildcard, we can get a list of lists
            # but we want a flat list
            value = [item for sublist in value for item in sublist]

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
    quote_used = ''

    query = query.strip()
    for char in query:
        if escaped:
            if char in UNION_OPERATOR_SYMBOL + SLICE_OPERATOR_SYMBOL:
                # don't remove escape from union symbol because unions will be evaluated later
                token += ESCAPE_SYMBOL
            escaped = False
            token += char
        elif quoted:
            if char in UNION_OPERATOR_SYMBOL + SLICE_OPERATOR_SYMBOL + ESCAPE_SYMBOL:
                # escape special symbols used inside quotation
                token += ESCAPE_SYMBOL
            if char == quote_used:
                quoted = False
            else:
                token += char
        elif char in ESCAPE_SYMBOL:
            escaped = True
        elif char in QUOTES_SYMBOL:
            quote_used = char
            quoted = not quoted
        elif char in ROOT_SYMBOL:
            yield char
            token = ''
        elif char in IDENTIFIER_SYMBOL:
            if previous_char and previous_char in IDENTIFIER_SYMBOL:
                yield char + char
            elif token:
                yield token
            token = ''
        elif char in BRACKET_START_SYMBOL:
            if token:
                yield token
            token = char
        elif char in BRACKET_END_SYMBOL:
            token += char
            yield token
            token = ''
        else:
            token += char

        previous_char = char

    if token:
        yield token


def parse(query):
    """
    Parse json path query.
    :param query: string
    :return: JsonPath object
    """

    tokens = tokenize(query)
    nodes = []

    for token in tokens:
        if token == ROOT_SYMBOL:
            node_type = ROOT_NODE
            value = None
        elif token == DESCENDANT_SYMBOL:
            node_type = DESCENDANT_NODE
            value = None
        elif token[0] == BRACKET_START_SYMBOL and token[-1] == BRACKET_END_SYMBOL:
            # token have not escaped slice delimiter, let's check if it is really a slice
            if SLICE_OPERATOR_SYMBOL in token.replace('\\' + SLICE_OPERATOR_SYMBOL, ''):
                # it is slice if we found the slice separator
                node_type = SLICE_NODE
                try:
                    value = slice(*[int(i) for i in token[1:-1].split(SLICE_OPERATOR_SYMBOL) if i])
                except ValueError:
                    node_type = IDENTIFIER_NODE
                    value = token[1:-1]
            elif WILDCARD_SYMBOL in token:
                # but it can also be a wildcard
                node_type = WILDCARD_NODE
                value = None
            else:
                try:
                    # or an index. let's check if the value is numeric
                    node_type = INDEX_NODE
                    value = [int(token[1:-1])]
                except ValueError:
                    # it's not numeric, so it's an identifier
                    node_type = IDENTIFIER_NODE
                    value = token[1:-1].strip()
        else:
            # everything else is an identifier
            node_type = IDENTIFIER_NODE
            value = token.strip()
            if value == WILDCARD_SYMBOL:
                # except if it is a wildcard
                node_type = WILDCARD_NODE
                value = None

        if node_type == IDENTIFIER_NODE:
            try:
                # try to split unions
                value = escaped_split(value, UNION_OPERATOR_SYMBOL)
                value = [val.strip(SPACE_SYMBOL) for val in value]
                # unescape union and slide operators
                value = [val.replace(
                    ESCAPE_SYMBOL + ESCAPE_SYMBOL, ESCAPE_SYMBOL).replace(
                    ESCAPE_SYMBOL + UNION_OPERATOR_SYMBOL, UNION_OPERATOR_SYMBOL).replace(
                    ESCAPE_SYMBOL + SLICE_OPERATOR_SYMBOL, SLICE_OPERATOR_SYMBOL) for val in value]
            except AttributeError:
                # failed to strip/split because value could be a list or an integer
                pass

        nodes.append(Node(type=node_type, value=value))

    return JsonPath(nodes)


def escaped_split(string, char):
    sections = string.split(char)
    if ESCAPE_SYMBOL not in string:
        return sections
    sections = [section + (char if section and section[-1] == ESCAPE_SYMBOL else '') for section in sections]
    result = ['' for _ in sections]
    idx = 0
    for section in sections:
        result[idx] += section
        idx += (1 if section and section[-1] != char else 0)
    return [val.strip() for val in result if val != '']
