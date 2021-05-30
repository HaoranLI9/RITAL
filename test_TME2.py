#%%
from collections import Counter
from utils.TextRepresenter import PorterStemmer
from math import log
import numpy as np
import pickle
import shelve
import utils.porter as p

import re
from utils.Document import Document
from utils.Parser import Parser
from utils.IndexerSimple import IndexerSimple
from utils.PageRank import PageRankModel
import time

from utils.Weighter import *
from utils.IRmodel import IRModel, Vectoriel, ModeleLangue, Okapi

#%%
cacm = Parser().parse_doc("data/cacm/cacm.txt")
indexer_cacm=IndexerSimple(cacm)
indexer_cacm.indexation()

# %%
x = [Weighter1(indexer_cacm), Weighter2(indexer_cacm), Weighter3(indexer_cacm), Weighter4(indexer_cacm), Weighter5(indexer_cacm)]
t=1
for i in x:
    print("weight", t)
    print(i.getWeightsForDoc(10))
    #print(i.getWeightsForStem("comput"))
    #print(i.getWeightsForQuery("compute programme"))
    t += 1
# %%
weight_cacm = Weighter1(indexer_cacm)
model_v = Vectoriel(weight_cacm)
modelOkapi = Okapi(indexer_cacm)
modelLangue = ModeleLangue(indexer_cacm)
models = [model_v, modelOkapi, modelLangue]
names = ["Vectoriel", "Okapi", "Langue"]
# %%
for m, n in zip(models, names):
    print(n + ":")
    print("10 premier rank:", m.getRanking("compute")[:10])
    print("--------------------------------")
# %%
