import sys
import argparse
from json import dumps
from urllib.parse import unquote_plus

from flask import Flask, request

from data_model import build_offline_data_model


# This is the main script that launches the auto-complete server.

############  Take input arguments from the command line  ############
parser = argparse.ArgumentParser()
parser.add_argument('--max_suggestions', type=int, default=3, 
    help='Max. no. of auto-complete suggestions')
parser.add_argument('--min_words_partial', type=int, default=4, 
    help='Min. no. of words in auto-complete suggestions of partial sentences')
parser.add_argument('--input_filepath', type=str, required=True, 
    help='Relative path of the JSON file with conversations')
parser.add_argument('--output_filepath', type=str, required=True, 
    help='Relative path of the pickled file to be saved')
args = parser.parse_args(sys.argv[1:])

###############  Build and save the offline data model  ###############
autocomplete_trie = build_offline_data_model(args.max_suggestions,
                                             args.min_words_partial, 
                                             args.input_filepath, 
                                             args.output_filepath)
print("""Auto-complete data model created with 
    maximum no. of suggestions set to: {}
    minimum no. of words in partial sentence suggestions set to: {}
    These parameters can be changed from the command line.
    To see how, run: python server.py""".format(args.max_suggestions, 
                                                args.min_words_partial))
# Note: build_offline_data_model() also saves the data model (trie)
# at the specified output filepath.  Once this saved data model is 
# available, the trie can be instantiated from the pickled file by:
## from trie import Trie
## autocomplete_trie = Trie().load(args.output_filepath)

###############  Launch the auto-complete HTTP server  ###############
app = Flask(__name__)

@app.route('/autocomplete')
def fetch_suggestions():
    # q is the key of URL query string with its value being the prefix
    prefix = unquote_plus(request.args.get('q')).lower()
    suggestions = {}
    suggestions['Completions'] = autocomplete_trie.generate_completions(prefix)
    return dumps(suggestions)

app.run(host='0.0.0.0', port=13000)   # launch the server
