# Mitchell Rudoll and Oliver Whittlef

# Inspiration drawn from NLTK Eliza and https://github.com/lizadaly/brobot/blob/master/broize.py

# IMPORTS

from __future__ import print_function, unicode_literals
import nltk
import numpy as np
import random
import string
import sys
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
import io
from textblob import TextBlob
from config import FILTER_WORDS, GREETING_INPUTS, GREETING_RESPONSES, NONE_RESPONSES, COMMENTS_ABOUT_SELF, SELF_VERBS_WITH_ADJECTIVE, SELF_VERBS_WITH_NOUN_LOWER, SELF_VERBS_WITH_NOUN_CAPS_PLURAL, GOODBYE_INPUTS, GOODBYE_RESPONSES
from interaction import findDrugInteractions
from rxnorm import rxNormId

# DATA LOADING

os.environ['NLTK_DATA'] = os.getcwd() + '/nltk_data'

nltk.download('punkt')
nltk.download('wordnet')

# Dictionary of drug names used

# dictionary of form RxNormId : {UserName : OfficialName}
user_drug_names = {}

# API CALLS

# CLASSES

class NoNoWordsException(Exception):
    """Response triggered blacklist"""
    pass
1
# FUNCTIONS

def add_to_client_drug_names(rxNormId, dictPair):
    user_drug_names[rxNormId] = dictPair
    return True

def get_from_client_drug_names(rxNormId):
    return user_drug_names[rxNormId]

def starts_with_vowel(word):
    """Check for pronoun compability -- 'a' vs. 'an'"""
    return True if word[0] in 'aeiou' else False

def find_pronoun(sent):
    """Given a sentence, find a preferred pronoun to respond with. Returns None if no candidate
    pronoun is found in the input"""
    pronoun = None

    for word, part_of_speech in sent.pos_tags:
        # Disambiguate pronouns
        if part_of_speech == 'PRP' and word.lower() == 'you':
            pronoun = 'I'
        elif part_of_speech == 'PRP' and word == 'I':
            # If the user mentioned themselves, then they will definitely be the pronoun
            pronoun = 'You'
    return pronoun

def find_verb(sent):
    """Pick a candidate verb for the sentence."""
    verb = None
    pos = None
    for word, part_of_speech in sent.pos_tags:
        if part_of_speech.startswith('VB'):  # This is a verb
            verb = word
            pos = part_of_speech
            break
    return verb, pos


def find_noun(sent):
    """Given a sentence, find the best candidate noun."""
    noun = None

    if not noun:
        for w, p in sent.pos_tags:
            if p == 'NN':  # This is a noun
                noun = w
                break

    return noun

def find_adjective(sent):
    """Given a sentence, find the best candidate adjective."""
    adj = None
    for w, p in sent.pos_tags:
        if p == 'JJ':  # This is an adjective
            adj = w
            break
    return adj

def preprocess_text(sentence):
    """Handle some weird edge cases in parsing, like 'i' needing to be capitalized
    to be correctly identified as a pronoun"""
    cleaned = []
    words = sentence.split(' ')
    for w in words:
        if w == 'i':
            w = 'I'
        if w == "i'm":
            w = "I'm"
        cleaned.append(w)

    return ' '.join(cleaned)

def construct_response(pronoun, noun, verb):
    """No special cases matched, so we're going to try to construct a full sentence that uses as much
    of the user's input as possible"""
    resp = []

    if pronoun:
        resp.append(pronoun)
    if verb:
        verb_word = verb[0]
        if verb_word in ('be', 'am', 'is', "'m"):  # This would be an excellent place to use lemmas!
            resp.append(verb_word)
    if noun:
        pronoun = "an" if starts_with_vowel(noun) else "a"
        resp.append(pronoun + " " + noun)

    return " ".join(resp)

def check_for_comment_about_bot(pronoun, noun, adjective):
    """Check if the user's input was about the bot itself, in which case try to fashion a response
    that feels right based on their input. Returns the new best sentence, or None."""
    resp = None
    if pronoun == 'I' and (noun or adjective):
        if noun:
            if random.choice((True, False)):
                resp = random.choice(SELF_VERBS_WITH_NOUN_CAPS_PLURAL).format(**{'noun': noun.pluralize().capitalize()})
            else:
                resp = random.choice(SELF_VERBS_WITH_NOUN_LOWER).format(**{'noun': noun})
        else:
            resp = random.choice(SELF_VERBS_WITH_ADJECTIVE).format(**{'adjective': adjective})
    return resp

def check_for_greeting(input):
    resp = None
    for word in GREETING_INPUTS:
        if word in input.lower():
            resp = random.choice(GREETING_RESPONSES).capitalize()
    return resp

def check_for_goodbye(input):
    resp = None
    for word in GOODBYE_INPUTS:
        if word in input.lower():
            resp = random.choice(GOODBYE_RESPONSES).capitalize()
    return resp

def check_for_mention_of_drugs(input):
	resp = None
	resp = []
	drugs = []
	if "medicine" in input.lower() or "drug" in input.lower() or "medication" in input.lower():
		# The drugs I'm currently taking are . . .
		if input.find("are") >= 0:
			drugs = [str(d).strip() for d in input[input.index("are"):].split()]
		# Here's a list of the drugs I'm taking: . . .
		elif input.find("taking") >= 0:
			drugs = [str(d).strip() for d in input[input.index("taking"):].split()]
		# Please check these drugs for me . . .
		elif input.find("check") >= 0:
			drugs = [str(d).strip() for d in input[input.index("check"):].split()]
		# [Some complicated way to give list of drugs] . . . Thanks!/Thank you!
		elif input.find("thank") >= 0:
			drugs = [str(d).strip() for d in input[:input.index("thank")].split()]
		if(len(drugs) > 0):
			drugInteractionsDict = str(findDrugInteractions(map(rxNormId, drugs)))
			resp = str(drugInteractionsDict)
			if not resp:
				resp = "I couldn't find anything. Would you like me to ask Siri?"
	return resp

def check_for_comment_about_drugs(pronoun, noun, adjective):
    """Check if the user's input was about drugs, in which case try to fashion a response
    that feels right based on their input. Returns the new best sentence, or None."""
    resp = None
    if noun and noun.lower() in ["drugs", "medicine", "medication"]:
        names = ('tylenol', 'ibuprofen', 'viagra')
        resp = str(findDrugInteractions(map(rxNormId, names)))
    return resp

def find_candidate_parts_of_speech(parsed):
    """Given a parsed input, find the best pronoun, direct noun, adjective, and verb to match their input.
    Returns a tuple of pronoun, noun, adjective, verb any of which may be None if there was no good match"""
    pronoun = None
    noun = None
    adjective = None
    verb = None
    for sent in parsed.sentences:
        pronoun = find_pronoun(sent)
        noun = find_noun(sent)
        adjective = find_adjective(sent)
        verb = find_verb(sent)
    return pronoun, noun, adjective, verb

def filter_response(resp):
    """Don't allow any words to match our filter list"""
    tokenized = resp.split(' ')
    for word in tokenized:
        for s in FILTER_WORDS:
            if word.lower().startswith(s):
                raise NoNoWordsException()

lemmer = nltk.stem.WordNetLemmatizer()

def LemTokens(tokens):
    return [lemmer.lemmatize(token) for token in tokens]

remove_punct_dict = dict((ord(punct), None) for punct in string.punctuation)

def LemNormalize(text):
    return LemTokens(nltk.word_tokenize(text.lower().translate(remove_punct_dict)))

def greeting(sentence):
    # TODO: change split to .words
    for word in sentence.words:
        if word.lower() in GREETING_INPUTS:
            return random.choice(GREETING_RESPONSES)

def respond(sentence):
    """Parse the user's inbound sentence and find candidate terms that make up a best-fit response"""
    cleaned = preprocess_text(sentence)
    parsed = TextBlob(cleaned)

    # Loop through all the sentences, if more than one. This will help extract the most relevant
    # response text even across multiple sentences (for example if there was no obvious direct noun
    # in one sentence
    pronoun, noun, adjective, verb = find_candidate_parts_of_speech(parsed)

    # If we said something about the bot and used some kind of direct noun, construct the
    # sentence around that, discarding the other candidates

    # resp = check_for_comment_about_bot(pronoun, noun, adjective)
    resp = None
    if not resp:
        resp = check_for_mention_of_drugs(parsed)
    if not resp:
        resp = check_for_comment_about_drugs(pronoun, noun, adjective)
    if not resp:
        resp = check_for_greeting(parsed)
    if not resp:
        resp = check_for_goodbye(parsed)
    # If we just greeted the bot, we'll use a return greeting
    # if not resp:
    #     resp = respond(parsed)

    if not resp:
        # If we didn't override the final sentence, try to construct a new one:
        if not pronoun:
            resp = random.choice(NONE_RESPONSES)
        elif pronoun == 'I' and not verb:
            resp = random.choice(COMMENTS_ABOUT_SELF)
        else:
            resp = construct_response(pronoun, noun, verb)

    # If we got through all that with nothing, use a random response
    if not resp:
        resp = random.choice(NONE_RESPONSES)

    # Check that we're not going to say anything obviously offensive
    filter_response(resp)

    return resp

#DRIVER

def converse(sentence):
    resp = respond(sentence)
    return resp

if __name__ == '__main__':
    print("Bot: Hello, my name is Dr. Web MD. Please feel free to ask me any questions you may have regarding the medicines you're taking.")
    while(True):
        resp = input('> ')
        print(converse(resp))