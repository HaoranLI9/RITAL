from utils.EvalMesure import *
from utils.IndexerSimple import *
from utils.QueryParser import *
from utils.IRmodel import *
from utils.Weighter import *
import numpy as np


class EvalIRModel(object):
    """
    permettant l’evaluation de differents modeles de recherche sur un ensemble de requetes selon differentes mesures d’evaluation
    cette fonction utilise toutes les fonctions qu'on a crée, donc on essaie de tout combiner 
    """
    def __init__(self, filename):
        """
        filename qu'on veut (cacm ou cisi)
        """
        self.indexer = None
        #self.indexes = None
        #self.reverse_indexes = None
        self.query = None
        self.weighters = []
        self.models = {}
        self.mesures = {}
        self.filename = filename

    def set_indexer(self):
        """
        on utilise Class IndexerSimple
        """
        docs = Parser().parse_doc("./data/"+str(self.filename)+"/"+str(self.filename)+".txt")
        indexer=IndexerSimple(docs)
        indexer.indexation()
        self.indexer = indexer
    
    def set_query(self):
        """
        on utilise Class QueryParser pour les querys
        """
        self.query = QueryParser().parseQry(self.filename)
        #QueryParser().parseRel("./data/"+str(self.filename)+"/"+str(self.filename)+".rel", self.query)
        QueryParser().parseRel(self.filename, self.query)

    def set_weighter(self, weighters):
        """
        Para: une liste de Weighter 1-5
        """
        for weighter in weighters:
            w = weighter(self.indexer)
            self.weighters.append(w)

    def set_model(self):
        """
        pour initialiser les model
        """
        #vectoriel
        self.models["Vectoriel"] = []
        for weighter in self.weighters:
            model1 = Vectoriel(weighter)
            self.models["Vectoriel"].append(model1)

        #ModeleLangue
        model2 = ModeleLangue(self.indexer, v_lambda=0.8)
        self.models["ModeleLangue"] = model2

        #Okapi
        model3 = Okapi(self.indexer, k1=1.2, b=0.75)
        #self.models.append(model3)
        self.models["Okapi"] = model3

    def set_mesure(self, k):
        """
        para: k le rang qu'on veut quand utilisant precision ou rapel
        pour initialiser les mesures
        """
        mesure1 = precision(k)
        #self.mesures.append(mesure1)
        self.mesures["precision"] = mesure1

        mesure2 = rappel(k)
        #self.mesures.append(mesure2)
        self.mesures["rappel"] = mesure2
        
        mesure3 = F_mesure(k)
        #self.mesures.append(mesure3)
        self.mesures["F-mesure"] = mesure3

        mesure4 = AP()
        #self.mesures.append(mesure4)
        self.mesures["AP"] = mesure4

        mesure5 = NDCG()
        #self.mesures.append(mesure5)
        self.mesures["NDCG"] = mesure5

        mesure6 = reciprocal_rank()
        #self.mesures.append(mesure6)
        self.mesures["Reciprocal_rank"] = mesure6

    def set_all(self, weighters, k):
        """
        para: weighters une liste de Weighter 1-5 pour le voctoriel / k: le rang
        Une fonction sésume toutes les fonctions d'initilisation
        """
        self.set_indexer()
        self.set_query()
        self.set_weighter(weighters)
        self.set_model()
        self.set_mesure(k)
        
    def evaluation_simple(self, model, mesure):
        """
        para :model 3 types mesure 6 types
        apres on a initilisé toutes les para, on peut utiliser dictionnaire de models et mesures
        on l'evalue une seule dans cette fonctions
        """
        evals = []
        for _, query in self.query.items():
            rank = model.getRanking(query.get_texte())
            liste = []
            for i in rank:
                k, _ = i
                liste.append(k)
            eval = mesure.evalQuery(liste, query)
            evals.append(eval)
        return evals

    def evaluation_all(self):
        """
        cette fonctions test tous les models et mesures, et presente la moyenne et l’ecart-type pour chaque modele.
        """
        for name_model, model  in self.models.items():
            print(name_model, " :")
            if name_model != "Vectoriel":
                for name_mesure, mesure in self.mesures.items():
                    evals = self.evaluation_simple(model,mesure)
                    print(name_mesure," ","mean: ", np.mean(evals), "std: ", np.std(evals))
                print("\n")
            else:
                for i in range(len(model)):
                    print("Vectoriel with weighter",i+1,": ")
                    for name_mesure, mesure in self.mesures.items():
                        evals = self.evaluation_simple(model[i],mesure)
                        print(name_mesure," ","mean: ", np.mean(evals), "std: ", np.std(evals))
                    print("\n")
                
    def t_test(self, model1, model2, mesure):
        """
        pour permettre de calculer des tests de significativite entre deux
        modeles (t-test) pour tester si deux modeles sont significativement differents.
        """
        eval1 = self.evaluation_simple(model1, mesure)
        eval2 = self.evaluation_simple(model2, mesure)
        n = len(eval1)
        mean1, var1 = np.mean(eval1), np.var(eval1)
        mean2, var2 = np.mean(eval2), np.var(eval2)
        t = np.abs(mean1 - mean2)/np.sqrt((n-1)*(var1+var2)*2/(2*n*(n-1)))
        limit = 2
        print(t)
        if t < limit:
            print("significativement non-differents")
        else:
            print("significativement differents")