"""Contains functions to normalize customer service agents' response text.
Primary function here is get_signature_to_text_map.  It employs the rest 
of the functions defined in this module.
"""

__author__ = 'Kunal Kotian'

import spacy


def get_signature_to_text_map(responses):
    """Returns a dict mapping a sentence-signature to multiple sentences 
    matching the signature.  
    A signature is constructed for each sentence in the responses corpus.
    The idea here is that sentences with the same signature must be very similar
    and can be treated as repeated occurrences of the same sentence.
    Multiple sentences matching a signature are each represented as repeated 
    occurrences of a normalized version of the sentence.
    
    Arguments
    ---------
    responses: list
        A list of strings, each representing a customer service agent response.
        Each individual response string may consist of one or more sentences.
        
    Example:
        Agent response: "What problems are you experiencing?"
        Normalized: "what problems are you experiencing"
        Signature: "what problem be -PRON- experience"
    """
    nlp = spacy.load('en')  # load SpaCy's default NLP model for English
    signature_to_text = {}
    for parsed_response in nlp.pipe(responses):
        for sent in parsed_response.sents:
            signature, normalized = get_signature_n_normalized(sent)
            # ignore sentences with signature being a single character 
            # and sentences with an empty string as signature
            if len(signature) <= 1:
                continue
            if not signature in signature_to_text:
                signature_to_text[signature] = [normalized]
            elif signature in signature_to_text:
                # add a copy of its first value, i.e. treat current 
                # sentence as a repeated occurrence of the existing sentence.
                signature_to_text[signature].append(signature_to_text[signature][0])
    return signature_to_text


def get_signature_n_normalized(sent):
    """Returns a tuple of 2 strings representing the signature and 
    the normalized form of the input sentence. 
    The signature is constructed from the lemmatized word tokens in the sentence. 
    The normalized form is obtained from SpaCy's token.norm_ attribute which stores 
    a lower-cased form of the word token, unifies differences in spellings 
    ('colour' -> 'color'), and replaces some common slang ('gotta' -> 'got to').
    Numbers are replaced by 'NUM' in the signature as well as the normalized form.
    
    Arguments
    ---------
    sent: a SpaCy span object
        A span object representing a sentence.
    """
    signature = []
    normalized = []
    for token in sent:
        if satisfies_conditions(token):
            # replace numbers in the text with 'NUM'
            if token.pos_ == 'NUM':
                signature.append('NUM')
                normalized.append('NUM')
            else:
                signature.append(token.lemma_)
                if get_norm(token) == 'moment' and normalized and normalized[-1] == 'NUM':
                    # 'one moment' is a common phrase used in customer service.
                    # Here, replacement of 'one' with 'NUM' must be undone.
                    normalized[-1] = 'one'
                normalized.append(get_norm(token))
    signature = ' '.join(signature)
    normalized = ' '.join(normalized)
    return signature, normalized


def satisfies_conditions(token):
    """Return a boolean indicating whether the token satisfies the following conditions:
    The token must not represent any of these: 
    1. space, 2. punctuation, 3. an interjection, 4. proper noun
    
    Arguments
    ---------
    token: a SpaCy token object
        A word token.
    """
    conditions = [token.is_space, token.is_punct, token.pos_ in ('INTJ', 'PROPN')]
    match_status = not any(conditions)
    return match_status


def get_norm(token):
    """Returns a string representing the normalized form of a word token 
    using SpaCy's tokenizer.  The tokenizer returns inappropriate normal 
    forms for a few words. These are overriden manually in this function.
    
    Arguments
    ---------
    token: a SpaCy token object
        A word token.
    """
    norm = token.norm_
    if token.text == 'a':
        norm = 'a'
    elif token.text == 'am':
        norm = 'am'
    return norm
