from utils.IndexerSimple import *
from utils.EvalIRModel import *
from utils.EvalIRModel import *
from utils.Query import *
import matplotlib.pyplot as plt
class GridSearch ():
    def __init__(self, filename, percent_train = 0.7, step=0.1, size = 1):
        """
        :para percent pour séparer train et test; step, size pour 0 à 1 par pas de 0.1
        """
        self.step = step
        self.size = size
        self.filename = filename
        self.percent_train = percent_train
        self.docs_train = {}
        self.docs_test = {}
        self.indexer_train = None
        self.indexer_test = None
        self.querys_train = {}
        self.querys_test = {}

    def fit(self):
        docs = Parser().parse_doc("./data/"+str(self.filename)+"/"+str(self.filename)+".txt")
        len_train = int(len(docs)*self.percent_train)
        #print(len_train)
        k = 0
        for i, j in docs.items():
            if k < len_train:
                self.docs_train[i] = j
            else:
                self.docs_test[i] = j
            k += 1
        self.indexer_train = IndexerSimple(self.docs_train)
        self.indexer_train.indexation()
        self.indexer_test = IndexerSimple(self.docs_test)
        self.indexer_test.indexation()

        querys = QueryParser().parseQry(self.filename)
        QueryParser().parseRel(self.filename, querys)

        for id, query in querys.items():
            query_train = Query(id)
            query_train.texte = query.texte

            query_test = Query(id)
            query_test.texte = query.texte

            for iddoc in query.iddoc_pert :
                if iddoc in self.docs_train:
                    query_train.iddoc_pert.append(iddoc)
                else :
                    query_test.iddoc_pert.append(iddoc)

            self.querys_train[id] = query_train
            self.querys_test[id] = query_test
    def evaluation(self, name_model, mesure):
        evalIRModel_train = EvalIRModel(self.filename)
        evalIRModel_train.indexer = self.indexer_train
        evalIRModel_train.query = self.querys_train

        evalIRModel_test = EvalIRModel(self.filename)
        evalIRModel_test.indexer = self.indexer_test
        evalIRModel_test.query = self.querys_test

        grille = np.arange(0, self.size, self.step) - self.size/2
        if "ModeleLangue" in str(name_model):
            res = []
            lambdas = 0.8 + grille

            for l in lambdas :
                print(l)
                evalue = evalIRModel_train.evaluation_simple(ModeleLangue(self.indexer_train, v_lambda=l), mesure)
                res.append (np.mean(evalue))
            """
            plt.figure()
            plt.plot(lambdas, res)
            plt.show()
            """
            optimal = lambdas[np.argmax(res)]
            print ("ModeleLangue : lambda optimal = ", optimal, "MAP est :", np.max(res))
            evalue_test = evalIRModel_test.evaluation_simple(ModeleLangue(self.indexer_test, v_lambda=optimal), mesure)
            print ("Appliquer pour Test, MAP est :", np.mean(evalue_test))

        if "Okapi" in str(name_model):
            res = []

            k1s = 1.2 + grille
            bs = 0.75 + grille

            for k1, b in zip(k1s, bs) :
                print(k1, b)
                evalue = evalIRModel_train.evaluation_simple(Okapi(self.indexer_train, k1=k1, b=b), mesure)
                res.append (np.mean(evalue))

            k1_optimal, b_optimal = k1s[np.argmax(res)], bs[np.argmax(res)]
            print ("Okapi : k1 optimal = ", k1_optimal," b optimal =", b_optimal, "MAP est :", np.max(res))
            evalue_test = evalIRModel_test.evaluation_simple(Okapi(self.indexer_test, k1=k1_optimal, b=b_optimal), mesure)
            print ("Appliquer pour Test, MAP est :", np.mean(evalue_test))


class Kfold():
    """
    On teste Modele de languge pour Kfold
    """
    def __init__(self, filename, kfois=3, step=0.1, size = 1):
        self.filename = filename
        self.kfois = kfois
        self.step = step
        self.size = size

    def evaluation(self, indexer_train, indexer_test, querys_train, querys_test,name_model="ModeleLangue", mesure=AP()):
        evalIRModel_train = EvalIRModel(self.filename)
        evalIRModel_train.indexer = indexer_train
        evalIRModel_train.query = querys_train

        evalIRModel_test = EvalIRModel(self.filename)
        evalIRModel_test.indexer = indexer_test
        evalIRModel_test.query = querys_test

        grille = np.arange(0, self.size, self.step) - self.size/2

        if "ModeleLangue" in str(name_model):
            res = []
            lambdas = 0.8 + grille

            for l in lambdas :
                evalue = evalIRModel_train.evaluation_simple(ModeleLangue(indexer_train, v_lambda=l), mesure)
                res.append (np.mean(evalue))

            """
            optimal = lambdas[np.argmax(res)]
            #print ("ModeleLangue : lambda optimal = ", optimal, "MAP est :", np.max(res))
            evalue_test = evalIRModel_test.evaluation_simple(ModeleLangue(indexer_test, v_lambda=optimal), mesure)
            """

            return lambdas, res


        if "Okapi" in str(name_model):
            res = []

            k1s = 1.2 + grille
            bs = 0.75 + grille

            for k1, b in zip(k1s, bs) :
                print(k1, b)
                evalue = evalIRModel_train.evaluation_simple(Okapi(indexer_train, k1=k1, b=b), mesure)
                res.append (np.mean(evalue))

            return k1s, bs, res

    def fit(self):
        docs = Parser().parse_doc("./data/"+str(self.filename)+"/"+str(self.filename)+".txt")
        len_test = int(len(docs)/self.kfois)
        res1 = []
        for f in range(self.kfois):   
            print("*")     
            k = 0
            docs_test={}
            docs_train={}
            for i, j in docs.items():
                if  k> f*len_test and k<(f+1)*len_test:
                    docs_test[i] = j
                else:
                    docs_train[i] = j
                k += 1
            indexer_train = IndexerSimple(docs_train)
            indexer_train.indexation()
            indexer_test = IndexerSimple(docs_test)
            indexer_test.indexation()

            querys = QueryParser().parseQry(self.filename)
            QueryParser().parseRel(self.filename, querys)

            querys_test = {}
            querys_train = {}
            for id, query in querys.items():
                #print(id)
                query_train = Query(id)
                query_train.texte = query.texte

                query_test = Query(id)
                query_test.texte = query.texte

                for iddoc in query.iddoc_pert :
                    if iddoc in docs_train:
                        query_train.iddoc_pert.append(iddoc)
                    else :
                        query_test.iddoc_pert.append(iddoc)

                querys_train[id] = query_train
                querys_test[id] = query_test

            #print(query_train, query_test)
            a, b = self.evaluation(indexer_train, indexer_test, querys_train, querys_test)
            #print(a)
            lambdas = a
            res1.append(b)
        res1 = np.array(res1)
        res = res1.mean(axis = 0)
        optimal = lambdas[np.argmax(res)]
        print ("ModeleLangue : lambda optimal = ", optimal, "MAP est :", np.max(res))
        evalIRModel = EvalIRModel(self.filename)
        evalIRModel.set_indexer()
        evalIRModel.set_query()
        evalue = evalIRModel.evaluation_simple(ModeleLangue(evalIRModel.indexer, v_lambda=optimal), mesure=AP())
        print ("Appliquer pour Tout, MAP est :", np.mean(evalue))




