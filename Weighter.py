from utils.IndexerSimple import IndexerSimple
import numpy as np
import utils.porter as p
from collections import Counter

class Weighter():
    """
    classe représentant le structure d'une pondération.
    """
    def __init__(self, indexersimple):
        """
        :para indexsimple on utilise classe indexsimple
        :type index: dict[int : dict[string: int]]
        :type indexInverse: dict[string : dict[int: int]]

        On utlise la fonction pour intialiser index et indexInverse
        """
        #self.indexer = IndexerSimple(docs)
        #self.indexer.indexation()
        self.indexersimple = indexersimple
        indexersimple.indexation()
        self.indexes = indexersimple.indexes
        self.reverse_indexes = indexersimple.reverse_indexes
        self.norme_doc = {}
        self.norme_query = {}

    def getWeightsForDoc(self, idDoc):
        """
        :para id de doc
        :type idDoc: int
        
        :return: Les poids des différents termes.
        :rtype: dict[string : number]
        """
        pass
    
    def getWeightsForStem(self, stem):
        """
        :para terme dans le corpus considéré.
        :type stem: string
        
        :return: Les poids du terme dans chaque document.
        :rtype: dict[int : number] id : poid
        """
        pass
    
    def getWeightsForQuery(self, query):
        """
        :para la requete consideree
        :type query: string
        
        :return: Les poids du terme dans la requete.
        :rtype: dict[string : number]
        """
        pass
    
    def getNormeforDoc(self, docId):

        if(docId not in self.norme_doc):

            #ici, vscode dit il y a faute, mais ca marche, parce que Child class existe fonction qui va récrire celle de parent class
            docweights = self.getWeightsForDoc(docId)#On trouve le poid de doc
            self.norme_doc[docId] = np.linalg.norm(list(docweights.values()))#On transforme en vecteur pour calculer la norme
        
        return self.norme_doc[docId]


    def getNormeforquery(self, query):
        
        if(query not in self.norme_query):
            #ici, vscode dit il y a faute, mais ca marche, parce que Child class existe fonction qui va récrire celle de parent class
            queryweights = self.getWeightsForQuery(query)#On trouve le poid de query
            self.norme_query[query] = np.linalg.norm(list(queryweights.values()))#On transforme en vecteur pour calculer la norme
        
        return self.norme_query[query]


#-W(t,d) = tf(t,d) et W(t,q) = 1 si t ∈ q, O sinon ;
class Weighter1(Weighter):
    """
    heritage de Weighter

    :type index: dict[int : dict[string: int]]
    :type indexInverse: dict[string : dict[int: int]]

    """
    def getWeightsForDoc(self, idDoc):

        return self.indexes[idDoc] # index montre que chaque element de doc dont tf
    
    def getWeightsForStem(self, stem):

        if stem in self.reverse_indexes:
            return self.reverse_indexes[stem] #montre tf du terme pour chaque document
        else:
            return {} 
                
    def getWeightsForQuery(self, query):
        #ici, c'est binaire
        requete = np.unique(list(map(p.stem, query.split())))# split et unique requete
        poid = {}
        for stem in requete:
            poid[stem] = 1
        return poid

#-W(t,d) = tf(t,d) et W(t,q) = tf(t,q)
class Weighter2(Weighter):
    """
    heritage de Weighter

    :type index: dict[int : dict[string: int]]
    :type indexInverse: dict[string : dict[int: int]]

    """
    def getWeightsForDoc(self, idDoc):

        return self.indexes[idDoc] # index montre que chaque element de doc dont tf
    
    def getWeightsForStem(self, stem):

        if stem in self.reverse_indexes:
            return self.reverse_indexes[stem] #montre tf du terme pour chaque document
        else:
            return {} 
    
    def getWeightsForQuery(self, query):
        #ici, c'est pas binaire, on utlise tf
        tf_requete = dict(Counter(list(map(p.stem, query.split())))) #le tf pour les termes de la requete
        poid = {}
        for stem in tf_requete:
            poid[stem] = tf_requete[stem]
        return poid

#-W(t,d) = tf(t,d) et W(t,q) = idf(t) si t ∈ q, 0 sinon
class Weighter3(Weighter):
    """
    heritage de Weighter

    :type index: dict[int : dict[string: int]]
    :type indexInverse: dict[string : dict[int: int]]

    """
    def getWeightsForDoc(self, idDoc):

        return self.indexes[idDoc] # index montre que chaque element de doc dont tf
    
    def getWeightsForStem(self, stem):
        if stem in self.reverse_indexes:
            return self.reverse_indexes[stem] #montre tf du terme pour chaque document
        else:
            return {} 
    
    def getWeightsForQuery(self, query):

        requete = np.unique(list(map(p.stem, query.split())))
        poid = {}
        for stem in requete:
            poid[stem] = self.indexersimple.getidfsForStem(stem)##utiliser getidf dans Weight pour calculer idf
        return poid

#-W(t,d) = 1 + log(tf(t,d)) si t ∈ d, 0 sinon ; et W(t,q) = idf(t) si t ∈ q, 0 sinon
class Weighter4(Weighter):
    """
    heritage de Weighter

    :type index: dict[int : dict[string: int]]
    :type indexInverse: dict[string : dict[int: int]]

    """
#-W(t,d) = 1 + log(tf(t,d)) si t ∈ d, 0 sinon 
    def getWeightsForDoc(self, idDoc):

        poid = {}
        for stem in self.indexes[idDoc]:
            poid[stem] = 1+np.log(self.indexes[idDoc][stem])
        return poid
    
    def getWeightsForStem(self, stem):
        if stem in self.reverse_indexes:
            poid = {}
            for idDoc in self.reverse_indexes[stem]:
                poid[idDoc] = 1+np.log(self.reverse_indexes[stem][idDoc])
            return poid
        else:
            return {}
#-W(t,q) = idf(t) si t ∈ q, 0 sinon
    def getWeightsForQuery(self, query):

        requete = np.unique(list(map(p.stem, query.split())))
        poid = {}
        for stem in requete:
            poid[stem] = self.indexersimple.getidfsForStem(stem)##utiliser getidf dans Weight pour calculer idf
        return poid

#W(t,d) = (1 + log(tf(t,d)))x idf(t) si t ∈ d, 0 sinon ; et W(t,q) = (1 + log(tf(t,q)))x idf(t) si t ∈ q, 0.

class Weighter5(Weighter):
    """
    heritage de Weighter

    :type index: dict[int : dict[string: int]]
    :type indexInverse: dict[string : dict[int: int]]

    """
    def getWeightsForDoc(self, idDoc):

        poid = {}
        for stem in self.indexes[idDoc]:
            poid[stem] = (1+np.log(self.indexes[idDoc][stem]))*self.indexersimple.getidfsForStem(stem)
        return poid
    
    def getWeightsForStem(self, stem):
        if stem in self.reverse_indexes :
            poid = {}
            for idDoc in self.reverse_indexes[stem]:
                poid[idDoc] = (1+np.log(self.reverse_indexes[stem][idDoc]))*self.indexersimple.getidfsForStem(stem)
            return poid
        else:
            return {}
    #W(t,q) = (1 + log(tf(t,q)))x idf(t) si t ∈ q, 0.
    def getWeightsForQuery(self, query):

        tf_requete = dict(Counter(list(map(p.stem, query.split())))) #le tf pour les termes de la requete
        poid = {}
        for stem in tf_requete:
            poid[stem] = (1+np.log(tf_requete[stem]))*self.indexersimple.getidfsForStem(stem)
        return poid