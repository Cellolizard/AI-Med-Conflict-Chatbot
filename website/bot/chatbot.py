# © Copyright 2018 Mitchell Rudoll and Oliver Whittlef

# Inspiration drawn from NLTK Eliza, https://github.com/lizadaly/brobot/blob/master/broize.py,
# and https://github.com/parulnith/Building-a-Simple-Chatbot-in-Python-using-NLTK/blob/master/chatbot.py

# This product uses publicly available data from the U.S. National Library of Medicine (NLM), National
# Institutes of Health, Department of Health and Human Services; NLM is not responsible for the product
# and does not endorse or recommend this or any other product.

# This uses the abovementioned data through the use of API calls in interaction.py and rxnorm.py

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
import os.path as path
import warnings
warnings.filterwarnings("ignore")
from textblob import TextBlob
from .config import *
from .interaction import findDrugInteractions
from .rxnorm import rxNormId
from nltk.corpus import stopwords
from nltk.corpus import wordnet
# from nltk.corpus import punkt
# from nltk_data.corpora import stopwords
# from nltk_data.corpora import wordnet
# from nltk_data.tokenizers import punkt
# DATA LOADING

p = path.abspath(path.join(__file__, "../.."))

os.environ['NLTK_DATA'] = p + '/nltk_data/'
nltk.data.path.append(p + '/nltk_data/')
# make sure required files are downloaded, but don't print to console
# download_dir='/opt/python/current/app'
# nltk.download('punkt', quiet=True)
# nltk.download('wordnet', quiet=True)
# nltk.download('stopwords', quiet=True)

module_dir = os.path.dirname(__file__)
file_path = os.path.join(module_dir, 'corpora.txt')
f=open(file_path, 'r', errors= 'ignore')
raw=f.read()
raw=raw.lower()

sent_tokens = nltk.sent_tokenize(raw)
word_tokens = nltk.word_tokenize(raw)

stop_words = set(stopwords.words('english'))

# Dictionary of drug names used

# dictionary of form RxNormId : {UserName : OfficialName}
client_drug_names = {}

remove_punct_dict = dict((ord(punct), None) for punct in string.punctuation)

lemmer = nltk.stem.WordNetLemmatizer()

# API CALLS

# CLASSES

class NoNoWordsException(Exception):
    """Response triggered blacklist"""
    pass
1
# FUNCTIONS

def add_to_client_drug_names(rxNormId, dictPair):
    client_drug_names[rxNormId] = dictPair
    return True

def get_from_client_drug_names(rxNormId):
    return client_drug_names[rxNormId]

def starts_with_vowel(word):
    # check for 'a' versus 'an'
    return True if word[0] in 'aeiou' else False

def find_pronoun(sent):
    # find's preferred pronoun to respond with
    pronoun = None

    for word, part_of_speech in sent.pos_tags:
        # Disambiguate pronouns
        if part_of_speech == 'PRP' and word.lower() == 'you':
            pronoun = 'I'
        elif part_of_speech == 'PRP' and word.lower() == 'your':
            pronoun = 'my'
        elif part_of_speech == 'PRP' and word == 'I':
            # If the user mentioned themselves
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
    # attempt to find the best noun in the sentence
    noun = None

    if not noun:
        for w, p in sent.pos_tags:
            if p == 'NN':  # This is a noun
                noun = w
                break

    return noun

def find_adjective(sent):
    # attempt to find the best adjective in the sentence
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
        if verb_word in ('be', 'am', 'is', "'m"):
            resp.append(verb_word)
    if noun:
        pronoun = "an" if starts_with_vowel(noun) else "a"
        resp.append(pronoun + " " + noun)

    return " ".join(resp)

def check_for_comment_about_bot(pronoun, noun, adjective, verb):
    # checks if the user's response is about the bot
    resp = ""
    # if pronoun == 'I':
    #     resp = "You're talking about me."
    if pronoun == 'I' and verb == 'are':
        resp = random.choice(SELF_VERBS_WITH_ADJECTIVE).format(**{'adjective' : adjective })
    elif pronoun == 'I' and (noun or adjective):
        if noun:
            if random.choice((True, False)):
                resp = random.choice(SELF_VERBS_WITH_NOUN_CAPS_PLURAL).format(**{'noun': noun.pluralize().capitalize()})
            else:
                resp = random.choice(SELF_VERBS_WITH_NOUN_LOWER).format(**{'noun': noun})
        else:
            resp = random.choice(SELF_VERBS_WITH_ADJECTIVE).format(**{'adjective': adjective})
    return resp

def check_for_greeting(input):
    # checks for if the user has greeted the bot
    resp = ""
    input_parsed = input.lower().split(" ")
    if("whats up" in input.lower() or "what's up" in input.lower()):
        resp = "The sky <span class='emoji'>🙄</span>"
    elif resp == "":
        for word in GREETING_INPUTS_MULTIWORD:
            if resp != "":
                break
            if word in input.lower():
                resp = random.choice(GREETING_RESPONSES).capitalize()
    for word in GREETING_INPUTS:
        if resp != "":
            break
        if word in input_parsed:
            resp = random.choice(GREETING_RESPONSES).capitalize()
    return resp

def check_for_goodbye(input):
    # checks for if the user has bid the bot goodbye
    resp = ""
    input_parsed = input.lower().split(" ")
    for word in GOODBYE_INPUTS:
        if resp != "":
            break
        if word in input_parsed:
            resp = random.choice(GOODBYE_RESPONSES).capitalize()
    for word in GOODBYE_INPUTS:
        if resp != "":
            break
        if word in input.lower():
            resp = random.choice(GOODBYE_RESPONSES).capitalize()
    return resp

def check_for_request_for_self_reflection(input, pronoun, noun, adjective, verb):
    # checks for if the user has asked things of the nature 'How are you doing?' or 'How do you feel?'
    resp = ""
    adj = adjective
    n = noun
    if adj == None:
        adj = ""
    if n == None:
        n = "things"
    for word in ROBO_REFLECTIONS_OPINION_ASK:
        if resp != "":
            break
        if word in input.lower():
            resp = random.choice(ROBO_REFLECTIONS_OPINION_ANSWER).format(**{'adjective': adj, 'noun': n})
    for word in ROBO_REFLECTIONS_PERSONAL_ASK:
        if resp != "":
            break
        if word in input.lower():
            resp = random.choice(ROBO_REFLECTIONS_PERSONAL_ANSWER)
    return resp

def check_for_self_reflection(input):
    # checks for if the user has made comments about themselves of the nature 'I feel ____' or 'I am ____'
    resp = ""
    if "i like" in input.lower():
        resp = random.choice(SELF_REFLECTIONS_LIKE_RESPONSE)
    if "i feel" in input.lower():
        resp = random.choice(SELF_REFLECTIONS_FEEL_RESPONSE)
    if "i am" in input.lower():
        resp = random.choice(SELF_REFLECTIONS_AM_RESPONSE)

    return resp

def check_for_mention_of_drugs(input):
    # populates client_drug_names based on user input, then gets all of the interactions
    # and concatenates them together into a resp
    resp = ""
    stopwords_drugs = stop_words;
    stopwords_drugs.update(DRUGS_STOP_WORDS)
    client_drug_names.clear()
    for sent in input.sentences:
        print(sent)
        for word, typ in sent.pos_tags:
            print("{0}:{1} ".format(word, typ), end="", flush=True)
            if typ in ("RB", "CC", "NN", "NNP", "JJ") and word not in stopwords_drugs:
                id = rxNormId(word)
                if id:
                    add_to_client_drug_names(id, { "foo" : word })
    print(client_drug_names)
    if(len(client_drug_names) < 2):
        return resp
    drugInteractionsDict = findDrugInteractions(client_drug_names.keys())
    if(len(drugInteractionsDict) < 1):
        return resp
    resp = random.choice(INTERACTION_PREFIXES) + " "
    for i in drugInteractionsDict.values():
        resp += "<br>" + i
    return resp

def find_candidate_parts_of_speech(parsed):
    # finds best pronoun, noun, adjective, and verb to match input
    # returns tuple of above, with None in the place if no match
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
    # try to prevent blacklist words from corpora responses
    resp = resp
    tokenized = resp.split(' ')
    for word in tokenized:
        for s in FILTER_WORDS:
            if s in word.lower():
                resp = "Hmm, I almost said something I'm not supposed to."
    return resp

def LemTokens(tokens):
    return [lemmer.lemmatize(token) for token in tokens]

def LemNormalize(text):
    return LemTokens(nltk.word_tokenize(text.lower().translate(remove_punct_dict)))

def respond(sentence):
    # Parse the user's inbound sentence to find best parts of speech to match
    cleaned = preprocess_text(sentence)
    parsed = TextBlob(cleaned)

    # Loop through all the sentences, if more than one. This will help extract the most relevant
    # response text even across multiple sentences (for example if there was no obvious direct noun
    # in one sentence
    pronoun, noun, adjective, verb = find_candidate_parts_of_speech(parsed)

    resp = None
    if not resp:
        resp = check_for_mention_of_drugs(parsed)
    if not resp:
        resp = check_for_greeting(parsed)
    if not resp:
        resp = check_for_goodbye(parsed)
    if not resp:
        resp = check_for_self_reflection(parsed)
    if not resp:
        resp = check_for_request_for_self_reflection(parsed, pronoun, noun, adjective, verb)
    if not resp:
        resp = check_for_comment_about_bot(pronoun, noun, adjective, verb)

    # if we get through our rules, just respond using a corpora
    if not resp:
        resp = converse_normal(sentence)
        if resp != None:
            resp = resp.capitalize()

    # will just say it doesn't know what's going on as an absolute last check to make sure there's a response
    if not resp:
        if not pronoun:
            resp = random.choice(NONE_RESPONSES)
        elif not resp:
            resp = construct_response(pronoun, noun, verb)
        else:
            resp = random.choice(NONE_RESPONSES)
    # make sure we don't say anything obviously offensive
    resp = filter_response(resp)

    return resp

def respond_normal(sentence):
    resp = ''
    sent_tokens.append(sentence)
    TfidVec = TfidfVectorizer(tokenizer=LemNormalize, stop_words='english')
    tfidf = TfidVec.fit_transform(sent_tokens)
    vals = cosine_similarity(tfidf[-1], tfidf)
    idx = vals.argsort()[0][-2]
    flat = vals.flatten()
    flat.sort()
    req_tfidf = flat[-2]
    if(req_tfidf==0):
        resp = resp + "I apologize, but I don't understand what you're saying."
    else:
        resp = resp + sent_tokens[idx]
        return resp

#DRIVER

def converse(sentence):
    resp = respond(sentence)
    return resp

def converse_normal(sentence):
    resp = respond_normal(sentence)
    return resp

if __name__ == '__main__':
    # main driver if we run from the console. Very primitive version compared to UI web implementation.
    print("Bot: Welcome, user! What can I help you with today?")
    while(True):
        resp = input('> ')
        print(converse(resp))
