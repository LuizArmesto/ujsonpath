# coding: utf-8

from collections import namedtuple

ROOT_NODE = 'ROOT'
WILDCARD_NODE = 'WILDCARD'
DESCENDANT_NODE = 'DESCENDANT'
SLICE_NODE = 'SLICE'
INDEX_NODE = 'INDEX'
IDENTIFIER_NODE = 'IDENTIFIER'


Node = namedtuple('Node', 'type, value')


class ValueNotFound(object):
    pass


class JsonPath(object):
    def __init__(self, nodes):
        self.nodes = nodes

    def find(self, data):
        parent = None
        root = data
        values = []

        nodes = self.nodes
        while nodes:
            node = nodes[0]
            try:
                nodes = nodes[1:]
            except IndexError:
                nodes = []

            node_value = self._get_node_value(node, data, parent, root)

            parent = data
            data = node_value

            if not nodes:
                values = node_value

        if not isinstance(values, list):
            values = [values]

        return values

    def _get_node_value(self, node, data, parent, root, scope=None):
        if node.type == ROOT_NODE:
            value = root
        if node.type == IDENTIFIER_NODE and isinstance(data, list):
            value = [self._get_node_value(node, datum, parent, root) for datum in data]
        elif node.type in (IDENTIFIER_NODE, INDEX_NODE, SLICE_NODE):
            try:
                value = data[node.value]
            except KeyError:
                value = ValueNotFound
        elif node.type == WILDCARD_NODE:
            if isinstance(data, list):
                value = data
            elif isinstance(data, dict):
                value = data.values()
            else:
                value = ValueNotFound
        elif node.type == DESCENDANT_NODE:
            raise NotImplementedError('Descendant is not implemented')
        return value


def tokenize(query):
    """
    Extract a list of tokens from query.
    :param query: string
    :return: list
    """

    root = '$'
    separator = '.'
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
        elif char in separator:
            if previous_char and previous_char in separator:
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
    wildcard = '[*]'
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
        elif token == wildcard:
            node_type = WILDCARD_NODE
            value = None
        elif token == descendant:
            node_type = DESCENDANT_NODE
            value = None
        elif token[0] == slice_l and token[-1] == slice_r:
            if slice_separator in token:
                node_type = SLICE_NODE
                value = slice(*[int(i) for i in token[1:-1].split(':') if i])
            else:
                node_type = INDEX_NODE
                try:
                    value = int(token[1:-1])
                except ValueError:
                    node_type = IDENTIFIER_NODE
                    value = token[1:-1].strip()
        else:
            node_type = IDENTIFIER_NODE
            value = token.strip()
            if value == '*':
                node_type = WILDCARD_NODE
                value = None

        if node_type == IDENTIFIER_NODE:
            value = value.strip(quotes)

        nodes.append(Node(type=node_type, value=value))

    return JsonPath(nodes)

