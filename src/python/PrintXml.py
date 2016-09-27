#!/usr/bin/env python

"""
Script to transform the pickle representation of posts into an XML file that
can be loaded into Carrot2. Both the title and the text of the post need to be
included for grouping.
"""

import pandas as pd
import pickle
import sys

__author__    = "Anika Oellrich"
__copyright__ = "King's College London, 2016"
__license__   = "BSD-2-Clause"
__email__     = "anika.oellrich@kcl.ac.uk"


def writePartXml(row):
    row.fillna("", inplace=True)
    title = row['title'].encode('ascii', 'ignore')
    text = row['text'].encode('ascii', 'ignore')
    print "<document id=\"" + str(row['id']) + "\">"
    print "<title>"
    print str(title)
    print "</title><url>"
    print "http://www.reddit.com/r/" + str(row['subreddit']) + "/" + str(row['id'])
    print "</url><snippet>"
    print text
    print "</snippet></document>"
    return None

filePath = sys.argv[1]

print "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
print "<searchresult><query>dementia</query>"

df = pickle.load( open( filePath, "rb" ) )
df.apply(writePartXml, axis=1)

print "</searchresult>"
