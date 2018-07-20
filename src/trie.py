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
        
    def generate_suggestions(self, max_suggestions):
        """set the list of autocomplete suggestions at this node"""
        responses_sorted_by_count = sorted(self.response_count, key=self.response_count.get, reverse=True)
        try:
            self.suggestions = responses_sorted_by_count[:max_suggestions]
        except TypeError:
            raise SystemExit('Error: max_suggestions used to instantiate the Trie must of type int.')


class Trie:
    """A Trie (prefix tree).
    
    Arguments
    ---------
    max_suggestions: int, default: 3
        The maximum number of suggestions to return to the customer service agent.

    Attributes (Public Interface)
    ----------
    max_suggestions: See the input parameter description.
    root: TrieNode object, default label '/'
        The root node of the trie.
    """
    def __init__(self, max_suggestions=3):
        self.max_suggestions = max_suggestions  # maximum number of suggestions to show
        self.root = TrieNode(label='/')

    def insert_response(self, response):
        """Insert a response string to the trie as a key."""
        self._current_node = self.root          # start insertion from the root node
        # initialize response_count dict to be updated along node traversal path:
        self._response_count_along_path = None
        self._response = response
        for char in self._response:
            self._visit_next_node(char)
        # create additional node with empty string label to signify end of response string
        self._visit_next_node(char='')

    def generate_completions(self, prefix):
        """Return a list of auto-complete suggestions"""
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
            Path of the pickled file to be saved, relative to current directory.
        """
        with open(filepath, 'wb') as output_file:
            pickle.dump(self, output_file)

    @classmethod
    def load(cls, filepath):
        """Load an instance of a Trie from a pickled file.
        An object can be instantiated from a saved file in a single step, e.g.:
        myTrie = Trie().load('saved_trie_data_model.pkl')

        Arguments
        ---------
        filepath: str
            Path of the pickled file to be saved, relative to current directory.
        """
        trie_obj = cls()
        with open(filepath, 'rb') as input_file:
            trie_obj = pickle.load(input_file)
        return trie_obj
        
    def _visit_next_node(self, char):
        """Move to the node with label char from the current node, creating it first if it doesn't exist."""
        # update path response counter if the response counter was stored at current node
        if self._current_node.response_count:
            self._response_count_along_path = self._current_node.response_count.copy()
        if not self._current_node.children:
            # no child nodes exist; create new child node for char
            self._current_node.children[char] = TrieNode(char)
        elif char not in self._current_node.children:
            self._create_new_branch(char) # create new branch to insert rest of the response
        next_node = self._current_node.children[char]
        self._store_response_next_node(next_node)
        self._current_node = next_node  # set current node to node with .label == char
        
    def _create_new_branch(self, char):
        """Create a new branch for inserting the rest of the response since the current node
        has no child node with .label == char.
        """
        if self._current_node.has_single_child:  # path upto current node has not branched yet
            single_child = next(iter(self._current_node.children.values()))
            self._store_response_single_child(single_child)
        self._current_node.children[char] = TrieNode(char)  # create new node
        self._current_node.has_single_child = False

    def _store_response_single_child(self, single_child):
        """single_child is the sole existing child node for the current_node.
        Store all response strings matching current path (.response_count 
        and .suggestions) at single_child, after removing current response.
        """
        del self._response_count_along_path[self._response]
        single_child.response_count = self._response_count_along_path
        single_child.generate_suggestions(self.max_suggestions)

    def _store_response_next_node(self, next_node):
        """Information on the response is stored in .response_count and .suggestions attributes 
        which are set only for a next_node whose *parent* is 
        (1) the root node: at root, all inserted responses are stored or 
        (2) a node with multiple children: this indicates that multipe different response matches exist 
        beyond parent node, hence we update autocomplete suggestions beyond parent node"""
        if (self._current_node is self.root) or (not self._current_node.has_single_child):
            # create or update a counter of response strings added to the trie that passed through this node
            next_node.response_count[self._response] += 1
            next_node.generate_suggestions(self.max_suggestions)

    def _reset_for_auto_complete(self):
        """Resets the trie to a state in which it expects the next char passed to its auto_complete()
        method to be part of a new input string to be matched.  This method must be called before the start 
        of streaming a new string to auto_complete().
        """
        self._current_node = self.root
        # initialize a suggestions list to be updated along node traversal path:
        self._suggestions_along_path = []
        self._no_match = False  # flag indicating if no matching response exists
        
    def _generate_completions_by_char(self, char):
        """Returns a list of auto-complete suggestions for char. char is assumed to be a character 
        in the input prefix which is streamed to this method one character at a time.
        """
        try:
            next_node = self._current_node.children[char]
            if next_node.suggestions:   # check if next_node has updated suggestions
                self._suggestions_along_path = next_node.suggestions
            self._current_node = next_node
        except KeyError:
            self._no_match = True
            self._suggestions_along_path = []
