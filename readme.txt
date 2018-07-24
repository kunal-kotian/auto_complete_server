ASAPP NLP / ML Engineering Challenge
====================================

Kunal Kotian, July 23, 2018


Introduction
------------
I wrote this auto-complete server code based on the 'Trie' or 'Prefix tree' data structure.  I chose this data structure because:
 1. It allows for very fast lookup of matching auto-complete suggestions.  
    The modified version of the Trie I implemented here performs this lookup in O(k) time, with k being the number of characters in the prefix input.
 2. I had already written my own Python implementation of a Trie for a recent (June '18) graduate school project. 
    The Trie was required to generate auto-complete predictions with the inputs consisted of single words.
    I used this as a starting point and modified the code to make the Trie I implemented for this work more space efficient.

I estimate that it took me about 10 hours (excluding writing this readme file) to complete the work.


Goals and Outcomes:
------------------
1: Offline data processing   
   This includes the following 2 steps which are wrapped in a single function called build_offline_data_model() [data_model.py]:
     1) Normalization of the agents' responses [normalize_responses.py].
     2) Building the data model [data_model.py] based on the normalized responses and the Trie class [trie.py].
   The data model built is serialized (pickled) and saved at the location specified by the user.
   (Offline data processing takes a 1 - 2 minutes on my MacBook with 8 GB RAM and a 2.7 GHz Intel Core i5 processor.)

2: Realtime autocomplete
   This is implemented in a method of the Trie class called generate_completions() [trie.py].
   
3: Autocomplete server
   The auto-complete server is launched by the script launch_auto_complete.py.
   launch_auto_complete.py is the main script - it must be run to build and save the offline data model and launch the server.
   Detailed instructions for running this script using command line arguments are provided in one of the sections below.

4: Follow-up questions
   My answers to the follow-up questions are in the answers_to_follow_up_questions.pdf file.

Side note: The normalization code replaces numbers with by 'NUM'.  
The idea behind this was that perhaps the front-end of the application providing an interface for typing for the customer service agents might be able to allow agents to type in a number replacing 'NUM' if they select any auto-complete suggestion containing 'NUM'.


Directory structure:
-------------------

ASAPP_auto_complete
 |
 |--readme.txt
 |
 |--src
 |   |
 |   |--launch_auto_complete.py
 |   |--data_model.py
 |   |--trie.py
 |   |--normalize_responses.py
 |   |
 |   |--tests
 |       |
 |       |--test_normalize_responses.py
 |       |--test_trie.py
 |
 |--data
 |   |
 |   |--sample_conversations.json
 |
 |--answers_to_follow_up_questions.pdf


Required Python Packages:
------------------------
The following external python packages are required to be installed to launch the auto-complete server:
1. Flask
   Installation: 
      pip install Flask

2. SpaCy
   Installation and download of the English language model:
      pip install spacy
      python -m spacy download 'en'

3. contractions
   Installation: 
      pip install contractions


Launching the Auto-Complete Server:
----------------------------------
To launch the auto-complete server, from the home directory, run the launch_auto_complete.py file.
The auto-complete server (Flask) can be pinged with a url query string like:
curl http://localhost:13000/autocomplete?q=What+is+y

The above request will result in the server returning the following JSON (or something similar, depending on the auto-complete system's input parameters):
{"Completions": ["what is your account number", "what is your order number", "what is your new address"]}

This launch_auto_complete.py script accepts command line options to control some aspects of the auto-complete server.
To get help on the command line options, run:
python src/launch_auto_complete.py -h

An example of the command line arguments that can be passed to launch the server is:
python src/launch_auto_complete.py --max_suggestions 3 --min_words_partial 4 --input_filepath ./data/sample_conversations.json --output_filepath ./data/autocomplete_trie.pkl

The line above launches the auto-complete server, generating a list of 3 auto-complete suggestions for each prefix sent to the server via the URL query string, with the auto-complete suggestions of partial sentences having a minimum of 4 words.


Running Unit Tests:
------------------
First, CD into the tests directory inside src:
cd src/tests

From the tests folder, to run unit tests, run:
python -m unittest -v

