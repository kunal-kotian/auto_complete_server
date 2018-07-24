"""Contains the Trie and TrieNode classes that are used to build the 
auto-complete data model.
"""

__author__ = 'Kunal Kotian'

import sys
import pickle
from collections import defaultdict


class TrieNode:
    """A node of a trie (prefix tree).
    
    Arguments
    ---------
    label: str
        A single character representing the node.
    
    Attributes
    ----------
    label: See the input parameter description.
    children: dict
        Maps the label of each child node to the node object itself.
    has_single_child: bool
        Flag indicating whether the node has only one child.
    response_count: defaultdict
        Maps each agent response (sentence string) to the number of 
        times it was inserted into the trie containing this node.
    suggestions: list
        A list of autocomplete suggestions applicable upon traversing
        to this node in a trie.
    """
    def __init__(self, label):
        self.label = label
        self.children = {}  # key = node label, value = node object
        self.has_single_child = True
        self.response_count = defaultdict(int)
        self.suggestions = []
        
    def generate_suggestions(self, max_suggestions):
        """Store a list of autocomplete suggestions at this node in 
        the suggestions attribute.  Suggested auto-complete responses 
        are first sorted by counts (descending order) and then by 
        string length (ascending order).

        Arguments
        ---------
        max_suggestions: int
            Maximum no. of auto-complete suggestions to generate.
        """
        if max_suggestions < 0:
            raise ValueError('max_suggestions must be > 0.')
        self.suggestions = sorted(self.response_count, 
                                  key=lambda x: (self.response_count[x],
                                                 -len(x)), 
                                  reverse=True)[:max_suggestions]


class Trie:
    """A Trie (prefix tree).
    
    Arguments
    ---------
    max_suggestions: int, default: 3
        Maximum no. of auto-complete suggestions to return.
    min_words_partial: int, default: 4
        Minimum no. of words in partial auto-complete suggestions. 
        When the auto-complete suggestions are fullsentences, 
        any no. of words is allowed.
    is_loaded: bool, default: False
        Flag indicating whether the trie object is being instantiated
        from a serialized (pickled) trie using its .load() method.

    Attributes (Public Interface)
    ----------
    max_suggestions: See the input argument description.
    min_words_partial: See the input argument description.
    root: TrieNode object
        The root node of the trie.
    """
    def __init__(self, max_suggestions=3, min_words_partial=4, 
                 is_loaded=False):
        # avoid over-writing attributes when loading saved trie
        if not is_loaded:
            self.max_suggestions = max_suggestions
            self.min_words_partial = min_words_partial
            self.root = TrieNode(label='/')

    def insert_response(self, response):
        """Insert a response string into the trie as a key.
        Auto-complete suggestions can be generated from 
        inserted responses using generate_completions().

        Arguments
        ---------
        response: str
            A string representing an agent's response (sentence).
        """
        self._response = response
        self._current_node = self.root    # start from the root node
        # initialize response_count dict updated along traversal path:
        self._response_count_along_path = None
        self._inserted_chars = '' # chars from response inserted so far
        # Track nodes *along current path* having response stored:
        self._nodes_with_response = []
        for char in self._response:
            self._visit_next_node(char)
            self._inserted_chars += char
        # create additional node to signify end of response string
        self._visit_next_node(char='')

    def generate_completions(self, prefix):
        """Return a list of auto-complete suggestions

        Arguments
        ---------
        prefix: str
            The input prefix for which auto-complete suggestions
            are to be generated.
        """
        self._reset_for_auto_complete()
        for char in prefix:
            if self._no_match:
                break
            self._generate_completions_by_char(char)
        return self._suggestions_along_path

    def save(self, filepath):
        """Serialize and save the Trie object as a pickle file.

        Arguments
        ---------
        filepath: str
            Path of the pickled file to be saved, relative to current dir.
        """
        LIMIT = 10000  # maximum depth of the Python interpreter stack
        sys.setrecursionlimit(LIMIT)  # required for pickling the trie
        with open(filepath, 'wb') as output_file:
            pickle.dump(self, output_file)

    @classmethod
    def load(cls, filepath):
        """Load an instance of a Trie from a pickled file.
        An object can be instantiated from a saved file directly, e.g.:
        myTrie = Trie().load('saved_trie_data_model.pkl')

        Arguments
        ---------
        filepath: str
            Path of the pickled file to be saved, relative to current dir.
        """
        trie_obj = cls(is_loaded=True)
        with open(filepath, 'rb') as input_file:
            trie_obj = pickle.load(input_file)
        return trie_obj
        
    def _visit_next_node(self, char):
        """Move to the node with label char from the current node, 
        creating it first if it doesn't exist.
        """
        if self._current_node.response_count:
            # update path response counter if a response counter was 
            # stored (in a previous traversal) at current node
            self._response_count_along_path = self._current_node.response_count.copy()
        if not self._current_node.children:
            # no child nodes exist; create new child node for char
            self._current_node.children[char] = TrieNode(char)
        elif char not in self._current_node.children:
            # create new branch to insert rest of the response:
            self._create_new_branch(char)
        next_node = self._current_node.children[char]
        self._store_response_next_node(next_node)
        if self._current_node.response_count:
            self._nodes_with_response.append(self._current_node)
        self._current_node = next_node  # set current node to next node
        
    def _create_new_branch(self, char):
        """Create a new branch for inserting the rest of the response. 
        Update attributes of the trie, the current node and its other child
        (if needed) to prepare for creating a new branch beyond current node.
        """
        if self._current_node.has_single_child:
            # path upto current node has not branched yet
            # the only child node that exists under _current_node is:
            single_child = next(iter(self._current_node.children.values()))
            self._store_response_single_child(single_child)
        self._current_node.children[char] = TrieNode(char)  # create new node
        self._current_node.has_single_child = False
        
    def _store_substring(self):
        """Store response substring up to current char.
        When a new branch is created, it indicates that the substring 
        in ._inserted_chars is a common prefix for multiple response 
        strings.This method adds this common substring prefix to each 
        node at which response was saved along the insertion path.
        """
        if self._current_node.label != ' ':
            # condition above ensures stored substrings contain whole words
            # avoids prefixes like 'when w', 
            # allows 'when was', 'when will', etc.
            return
        inserted_words = self._inserted_chars.strip().split(' ')
        if len(inserted_words) < self.min_words_partial:
            return
        if self._inserted_chars.strip() in self._response_count_along_path:
            add_count = 1
        else:
            # summing the counts of strings that were inserted along the
            # current path gives the count of response string that share 
            # the substring ._inserted_chars
            add_count = sum(self._response_count_along_path.values())
        for node in self._nodes_with_response:
            node.response_count[self._inserted_chars.strip()] += add_count
            node.generate_suggestions(self.max_suggestions)
        
    def _store_response_single_child(self, single_child):
        """Store all response strings, along current path at single_child, 
        after removing current response.  These will serve as the basis 
        for auto-complete suggestions when a prefix traversal reaches 
        single_child.  Note: When the current node is the root node, then 
        since every child of the root always has the response string 
        stored already, this method is bypassed.

        single_child is the sole existing child node for the current_node.
        """
        if self._current_node is self.root:
            return
        single_child.response_count = self._response_count_along_path.copy()
        del single_child.response_count[self._response]
        single_child.generate_suggestions(self.max_suggestions)

    def _store_response_next_node(self, next_node):
        """Information on the response is stored in response_count and 
        suggestions attributes which are set only for a next_node whose
         *parent* is:
        (1) the root node: at root, all inserted responses are stored, or 
        (2) a node with multiple children: this indicates that multiple 
            different response matches exist beyond parent node, hence 
            we update autocomplete suggestions beyond parent node
            """
        if ((self._current_node is not self.root) and 
            (self._current_node.has_single_child)):
            return
        self._store_substring()   # store shared prefix substrings
        # create or update a counter of response strings added to the 
        # trie that passed through this node
        next_node.response_count[self._response] += 1
        next_node.generate_suggestions(self.max_suggestions)

    def _reset_for_auto_complete(self):
        """Resets the trie to a state in which it expects the next char 
        passed to its auto_complete() method to be part of a new input 
        string to be matched.  This method must be called before the 
        start of streaming a new string to auto_complete().
        """
        self._current_node = self.root
        # initialize suggestions list updated along node traversal path:
        self._suggestions_along_path = []
        self._no_match = False  # flag indicating no matching response
        
    def _generate_completions_by_char(self, char):
        """Sets _suggestions_along_path to a list of auto-complete 
        suggestions for char. char is a character in the input prefix 
        which is streamed to this method sequentially in the order it 
        appears in the response string.
        """
        try:
            next_node = self._current_node.children[char]
            # check if next_node has updated suggestions
            if next_node.suggestions:
                self._suggestions_along_path = next_node.suggestions
            self._current_node = next_node
        except KeyError:
            self._no_match = True
            self._suggestions_along_path = []
