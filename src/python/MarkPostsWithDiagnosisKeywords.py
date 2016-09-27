'''
Script to extract posts that mention on of the keywords (e.g. suffers or
diagnosed) to indicate a diagnosis. The processed pickle file is then saved
with keywords and potential subjects and objects for the diagnosis are stored.
'''

import pickle
import pandas as pd
import sys
from spacy.en import English

__author__    = "Anika Oellrich"
__copyright__ = "King's College London, 2016"
__license__   = "BSD-2-Clause"
__email__     = "anika.oellrich@kcl.ac.uk"


parser = English()
keywords = ["diagnosed", "suffers", "suffer", "suffered"]

# function to see whether token is in the subtree of one of the identified
# keywords
def child_of_keyword(token, keywords):
    while (token.head is not token):
        if (str(token.head.orth_) in keywords):
            return True
        token = token.head
    return False

# function to convert special characters as contained in some of the posts
def character_converter(row):
    row.fillna("", inplace=True)
    return row['text'].encode('ascii', 'ignore')

# function to screen text for keywords
def find_keyword(row):
    row.fillna("", inplace=True)
    if (row['text'] != ""):
        text = row['text'].encode('ascii', 'ignore')
        doc = parser(unicode(text))

        for sent in doc.sents:
            foundKeyword = False
            for keyword in keywords:
                if (str(sent.text).find(keyword) != -1):
                    return True
                    break

    return False

# instead of extracting single tokens, the aim is to also pick up the surrounding
# noun phrases so that things like "early stage Alzheimers" can be picked up
# not only "stage" or "Alzheimer"
def collectNounPhrase(token):
    counter = 1
    nounPhrase = str(token.orth_)

    while (True):
        try:
            if ((str(token.nbor(counter).pos_) == "NOUN") | (str(token.nbor(counter).pos_) == "ADJ")): #| (str(token.nbor(counter).pos_) == "ADJ")):
                nounPhrase = nounPhrase + " " + str(token.nbor(counter).orth_)
                counter += 1
            else:
                break
        except IndexError:
            break

    counter = -1
    while (True):
        try:
            if ((str(token.nbor(counter).pos_) == "NOUN") | (str(token.nbor(counter).pos_) == "ADJ")): # | (str(token.nbor(counter).pos_) == "ADJ")):
                nounPhrase = str(token.nbor(counter).orth_) + " " + nounPhrase
                counter -= 1
            else:
                break
        except IndexError:
            break

    return nounPhrase

def process_text(row):
    subjects = []
    objects = []
    row.fillna("", inplace=True)

    if (row['text'] != ""):
        text = row['text'].encode('ascii', 'ignore')
        doc = parser(unicode(text))

        for sent in doc.sents:

            foundKeyword = False
            for keyword in keywords:
                if (str(sent.text).find(keyword) != -1):
                    foundKeyword = True
                    break

            if (foundKeyword):
                for token in sent:
                    if (token.orth_ in keywords):
                        counter = 1
                        # search right from keyword for closest object
                        while (True):
                            try:
                                if ( (str(token.nbor(counter).dep_).find("obj") != -1) & (token.nbor(counter).pos_ == "NOUN")):
                                    objects.append(collectNounPhrase(token.nbor(counter)))
                                    break
                                counter += 1
                            except IndexError:
                                break

                        counter = -1
                        # search right from keyword for closest subject
                        while (True):
                            try:
                                if ( (str(token.nbor(counter).dep_).find("subj") != -1) & (token.nbor(counter).pos_ == "NOUN")):
                                    subjects.append(collectNounPhrase(token.nbor(counter)))
                                    break
                                counter -= 1
                            except IndexError:
                                break

    return pd.Series({'subjects':subjects, 'objects':objects})

filePath = sys.argv[1]
df = pickle.load( open( filePath, "rb" ) )

df['text'] = df.apply(character_converter, axis=1)
df['keywordExists'] = df.apply(find_keyword, axis=1)
df[['objects','subjects']] = df.apply(process_text, axis=1)

df.to_pickle(sys.argv[2])
