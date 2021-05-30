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

from utils.TME23_bonus import *
# %%
querys_cacm = QueryParser().parseQry("cacm")
QueryParser().parseRel("cacm", querys_cacm)
n = len(querys_cacm)
print("len total:", n)
print("--------------")
for i in np.random.choice(n, 5):
    print("id :", querys_cacm[i].get_identifiant())
    print("text :", querys_cacm[i].get_texte())
    print("iddoc_pertinent :", querys_cacm[i].get_iddoc_pert())
    print("--------------")
# %%
querys_cisi = QueryParser().parseQry("cisi")
QueryParser().parseRel("cisi", querys_cisi)
n = len(querys_cisi)
print("len total:", n)
print("--------------")
for i in np.random.choice(n, 5):
    print("id :", querys_cisi[i].get_identifiant())
    print("text :", querys_cisi[i].get_texte())
    print("iddoc_pertinent :", querys_cisi[i].get_iddoc_pert())
    print("--------------")
# %%
eval1 = EvalIRModel("cacm")
Weighters = [Weighter1, Weighter2, Weighter3, Weighter4, Weighter5]
eval1.set_all(Weighters, k = 5)
# %%
print("Tous les models :")
print(eval1.models)
print("-------------------------------------")
print("Tous les mesures :")
print(eval1.mesures)
print("-------------------------------------")
# %%
print("toutes les evaluations de cacm :")
eval1.evaluation_all()
# %%
print("toutes les evaluations de cisi :")
eval2 = EvalIRModel("cisi")
Weighters = [Weighter1, Weighter2, Weighter3, Weighter4, Weighter5]
eval2.set_all(Weighters, k = 5)
eval2.evaluation_all()

#%%
#Bonus t-test
print("t-test sur cacm :")
model1 = eval1.models["Vectoriel"][0]
model2 = eval1.models["Vectoriel"][1]
model3 = eval1.models["Okapi"]
print("t-test entre Vectoriel(Weighter1) et Vectoriel(Weighter2) :")
eval1.t_test(model1, model2, rappel(k=5))
print("--------------------------------------------")
print("t-test entre Vectoriel(Weifhter1) et Okapi :")
eval1.t_test(model1, model3, rappel(k=5))

# %%
#Bonus Gridsearch
ggg = GridSearch("cacm",size=1, step = 0.1)
ggg.fit()
ggg.evaluation("ModeleLangue", AP())
# %%
#Bonus Kfold
kkk = Kfold("cacm", kfois=3, size=1, step=0.2)
kkk.fit()
# %%
