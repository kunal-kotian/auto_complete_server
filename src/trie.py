from collections import defaultdict


class TrieNode:
    """A node of a trie (prefix tree).
    
    Parameters
    ----------
    label: str
        A single character representing the node.
    
    Attributes
    ----------
    label: str
        A single character representing the node.
    children: dict
        Maps the label of each child node to the node object itself.
    has_single_child: bool
        Flag indicating whether the node has only one child.
    response_count: defaultdict
        Maps each agent response (sentence string) to the number of times 
        it was inserted into the trie containing this node.
    suggestions: list
        A list of autocomplete suggestions applicable upon traversing to this node in a trie.
    """
    def __init__(self, label):
        self.label = label
        self.children = {}  # key = node label, value = node object
        self.has_single_child = True
        self.response_count = defaultdict(int)
        self.suggestions = []


class Trie:
    """A Trie (prefix tree).
    
    Parameters
    ----------
    max_suggestions: int, default: 3
        The maximum number of suggestions to return to the customer service agent.
    """
    def __init__(self, max_suggestions=3):
        self.root = TrieNode(label='/')
        self.max_suggestions = max_suggestions  # maximum number of suggestions to show