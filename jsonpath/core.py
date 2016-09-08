# coding: utf-8

import json
from collections import namedtuple

# Node types
ROOT_NODE = 'ROOT'
WILDCARD_NODE = 'WILDCARD'
DESCENDANT_NODE = 'DESCENDANT'
SLICE_NODE = 'SLICE'
INDEX_NODE = 'INDEX'
IDENTIFIER_NODE = 'IDENTIFIER'


Node = namedtuple('Node', 'type, value')


class MatchNotFound(object):
    value = None

    def __repr__(self):
        return u'MatchNotFound'


class Match(object):
    def __init__(self, value):
        try:
            # value can be an instance of Match
            self.value = value.value
        except AttributeError:
            self.value = value

    def __repr__(self):
        return u'Match(value={value})'.format(value=json.dumps(self.value))


class JsonPath(object):
    def __init__(self, nodes):
        self.nodes = nodes

    def find(self, data):
        data = Match(data)
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

        if not isinstance(values, list):
            values = [values]

        return [value for value in values if not isinstance(value, MatchNotFound)]

    def _get_node_value(self, node, data, root):
        if node.type == ROOT_NODE:
            value = root
        # data can be a Match object or a list of Match objects
        elif isinstance(data, list):
            value = [self._get_node_value(node, datum, root) for datum in data]
        elif node.type in (IDENTIFIER_NODE, INDEX_NODE):
            try:
                value = Match(data.value[node.value])
            except (IndexError, KeyError, TypeError):
                value = MatchNotFound()
        elif node.type == SLICE_NODE:
            try:
                value = [Match(val) for val in data.value[node.value]]
            except (KeyError, TypeError):
                value = MatchNotFound()
        elif node.type == WILDCARD_NODE:
            data = data.value
            if isinstance(data, list):
                value = [Match(val) for val in data]
            elif isinstance(data, dict):
                value = [Match(val) for val in data.values()]
            else:
                value = MatchNotFound()
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

    root = '$'
    identifier_separator = '.'
    escape = '\\'
    slice_l = '['
    slice_r = ']'

    previous_char = ''
    token = ''
    escaped = False

    query = query.strip()
    for char in query:
        if escaped:
            token += char
            escaped = False
        elif char in escape:
            escaped = True
        elif char in root:
            yield char
            token = ''
        elif char in identifier_separator:
            if previous_char and previous_char in identifier_separator:
                yield char + char
            elif token:
                yield token
            token = ''
        elif char in slice_l:
            if token:
                yield token
            token = char
        elif char in slice_r:
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

    root = '$'
    wildcard = '*'
    descendant = '..'
    quotes = '"\''
    slice_l = '['
    slice_r = ']'
    slice_separator = ':'

    tokens = tokenize(query)
    nodes = []

    for token in tokens:
        if token == root:
            node_type = ROOT_NODE
            value = None
        elif token == descendant:
            node_type = DESCENDANT_NODE
            value = None
        elif token[0] == slice_l and token[-1] == slice_r:
            # token have slice delimiter, let's check if it is really a slice
            if slice_separator in token:
                # it is slice if we found the slice separator
                node_type = SLICE_NODE
                value = slice(*[int(i) for i in token[1:-1].split(':') if i])
            elif wildcard in token:
                # but it can also be a wildcard
                node_type = WILDCARD_NODE
                value = None
            else:
                try:
                    # or an index. let's check if the value is numeric
                    node_type = INDEX_NODE
                    value = int(token[1:-1])
                except ValueError:
                    # it's not numeric, so it's an identifier
                    node_type = IDENTIFIER_NODE
                    value = token[1:-1].strip()
        else:
            # everything els is an identifier
            node_type = IDENTIFIER_NODE
            value = token.strip()
            if value == wildcard:
                # except if it is a wildcard
                node_type = WILDCARD_NODE
                value = None

        if node_type == IDENTIFIER_NODE:
            # we don't want the identifier value to be surrounded by quotes
            value = value.strip(quotes)

        nodes.append(Node(type=node_type, value=value))

    return JsonPath(nodes)

