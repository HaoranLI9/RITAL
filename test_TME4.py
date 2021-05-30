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
from utils.QueryParser import QueryParser

from utils.EvalIRModel import *
from utils.EvalMesure import *

import numpy as np
#%%
np.seterr(divide='ignore', invalid='ignore')
# %%
cacm = Parser().parse_doc("data/cacm/cacm.txt")
indexer_cacm=IndexerSimple(cacm)
indexer_cacm.indexation()

weight_cacm = Weighter1(indexer_cacm)
model = Vectoriel(weight_cacm)
# %%
pr = PageRankModel()
modelOkapi = Okapi(indexer_cacm)
pr.getSubGraph(indexer_cacm, "computer science enginneering", modelOkapi)
# %%
print("Vertex(sommets): ", pr.V_Q)
docs = pr.runPageRank()
print(docs)
print("-----------------------------------------------------------------------------------------------------------")
for idDoc, ranked in docs:
    print(indexer_cacm.getStrDoc(idDoc))
    print("=======================================================================================================")
# %%
