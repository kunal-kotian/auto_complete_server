"""Contains functions to build the data model based on the normalized 
responses and the Trie class [from trie.py].
"""

__author__ = 'Kunal Kotian'

from json import load
from itertools import chain
import time

import contractions

from normalize_responses import get_signature_to_text_map
from trie import Trie


def build_offline_data_model(max_suggestions, min_words_partial, 
                             input_filepath, output_filepath):
    """Perform all offline data processing steps build the data model.
    Includes:
    1) Normalization of the agents' responses [normalize_responses.py].
    2) Building the data model [data_model.py] based on the normalized 
       responses and the Trie class [trie.py].
    3) Storage (pickled file) of the built data model at output_filepath.

    Arguments
    ---------
    max_suggestions: int
        Maximum number of auto-complete suggestions.
    min_words_partial: int
        Minimum number of words in auto-complete suggestions of 
        partial sentences.
    input_filepath: str
        Relative path of the JSON file with conversations.
    output_filepath: str
        Relative path of the pickled file to be saved.
    """
    responses = extract_responses_from_JSON(input_filepath)
    print('Read in data. Starting processing of responses now...')
    ########################   Normalization   ########################
    start = time.time()
    # A signature is constructed for each sentence in the responses using 
    # lemmatized forms of words.  signature_to_text is a dict whose values
    # are sentences with identical signatures that are grouped together 
    # and represented as repeated copies of the same normalized form.
    signature_to_text = get_signature_to_text_map(responses)
    # Next, we flatten nested lists of these normalized sentences:
    responses_processed = list(chain.from_iterable(signature_to_text.values()))
    end = time.time()
    duration  = round(end - start, 2)
    print("Finished normalizing agent responses in {} s".format(duration))
    ##############   Creating and Saving the Data Model   #############
    start = time.time()
    # A trie (prefix tree) is used here to construct a data model.
    # A trie allows efficiently (w.r.t. time) accessing all strings 
    # matching a prefix.
    autocomplete_trie = Trie(max_suggestions, min_words_partial)
    for response in responses_processed:
        # insert responses to grow the trie
        autocomplete_trie.insert_response(response)

    end = time.time()
    duration  = round(end - start, 2)
    print('Inserted normalized responses into the trie in {} s.'.format(duration))
    
    # Save the trie containing all agent responses
    start = time.time()
    autocomplete_trie.save(output_filepath)
    end = time.time()
    duration  = round(end - start, 2)
    print('Trie with normalized responses saved at: {}'.format(output_filepath))
    print('Serialization of the trie took {} s.'.format(duration))

    return autocomplete_trie


def extract_responses_from_JSON(filepath):
    """Return a list of agents' responses, with each element being a string
    after reading in conversations from the JSON file and extract agents'.

    Arguments
    ---------
    filepath: str
        Relative path of the JSON file with conversations.
    """
    with open(filepath) as file:
        data = load(file)

    responses = []
    for issue in data['Issues']:
        for message in issue['Messages']:
            # only include messages from agents
            if not message['IsFromCustomer']:
                agent_response = message['Text'].strip()
                # expand contractions 
                # (e.g. don't -> do not); normalizes sentences
                agent_response = contractions.fix(agent_response)
                responses.append(agent_response)
    return responses
