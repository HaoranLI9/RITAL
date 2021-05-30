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
# %%
cacm = Parser().parse_doc("data/cacm/cacm.txt")
indexer_cacm=IndexerSimple(cacm)
indexer_cacm.indexation()
# %%
#On vérifier que notre indexer marche bien
print(cacm[1])
print("--------------------------------------------")
print(indexer_cacm.indexes[1])
print("--------------------------------------------")
print(indexer_cacm.reverse_indexes['report'])
# %%
#TME1_bonus
Parser().parse_huge_collection("./data/cacm/cacm.txt")
# %%
