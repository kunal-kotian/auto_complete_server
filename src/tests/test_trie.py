import sys
sys.path.append("..")   # add the dir one level up to the modules path

import unittest

from trie import TrieNode, Trie


class testTrieNode(unittest.TestCase):
    def test_no_label(self):
        """Test creation of node with no label."""
        with self.assertRaises(TypeError):
            no_label_node = TrieNode()

    def test_max_suggestions_negative(self):
        """Test use of negative integer max_suggestions."""
        node = TrieNode(label='')
        with self.assertRaises(ValueError):
            node.generate_suggestions(max_suggestions=-5)

    def test_max_suggestions_float(self):
        """Test use of float max_suggestions."""
        node = TrieNode(label='')
        with self.assertRaises(TypeError):
            node.generate_suggestions(max_suggestions=5.0)


class testTrie(unittest.TestCase):
    def test_max_suggestions_negative(self):
        """Test use of negative integer max_suggestions."""
        trie = Trie(max_suggestions=-5)
        with self.assertRaises(ValueError):
            trie.insert_response(' ')

    def test_max_suggestions_float(self):
        """Test use of float max_suggestions."""
        trie = Trie(max_suggestions=5.0)
        with self.assertRaises(TypeError):
            trie.insert_response(' ')

    def test_insert_response_completions(self):
        """Test if the completions are generated include the expected 
        strings in the expected order.
        """
        trie = Trie(max_suggestions=5, min_words_partial=3)
        trie.insert_response('what is your account number and address')
        trie.insert_response('what is your account number')
        trie.insert_response('what is the account number')
        trie.insert_response('what is the issue you are facing')
        trie.insert_response('what is the issue you are facing')
        trie.insert_response('what is your account number please')
        completions = trie.generate_completions('w')
        expected = eval("""['what is the',
            'what is your account number',
            'what is the issue you are facing',
            'what is the account number',
            'what is your account number please']""")
        self.assertEqual(completions, expected)

    def test_insert_response_counts(self):
        """Test if the response_count is being calculated as expected."""
        trie = Trie(max_suggestions=6, min_words_partial=1)
        trie.insert_response('what is your account number and address')
        trie.insert_response('what is your account number')
        trie.insert_response('what is the account number')
        trie.insert_response('what is the issue you are facing')
        trie.insert_response('what is the issue you are facing')
        response_count = dict(trie.root.children['w'].response_count)
        expected = eval("""{'what is your account number and address': 1, 
            'what is your account number': 1, 
            'what is the account number': 1, 
            'what is': 5, 'what is the issue you are facing': 2, 
            'what is the': 3}""")
        self.assertEqual(response_count, expected)
