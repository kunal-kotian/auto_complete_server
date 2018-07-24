"""Unit test to check that the normalize_responses module 
produces the expected signature for responses.
"""


import sys
sys.path.append("..")   # add the dir one level up to the modules path

import unittest
import warnings

from normalize_responses import get_signature_to_text_map


class testNormalizeResponses(unittest.TestCase):
    def test_signature_to_text_map(self):
        """Test that normalization produces expected result."""
        # suppress warnings to declutter output
        warnings.simplefilter("ignore")
        responses = ["We've gotta resolve these 5 issues!"]
        signature_to_text = get_signature_to_text_map(responses)
        expected = eval("""{'-PRON- have get to resolve these NUM issue':
                           ['we have got to resolve these NUM issues']}""")
        self.assertEqual(signature_to_text, expected)
