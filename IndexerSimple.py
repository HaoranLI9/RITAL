#!/usr/bin/env python3
import numpy as np
from utils.TextRepresenter import PorterStemmer
from math import log
import pickle
import shelve
from utils.Document import Document
from utils.Parser import Parser

class IndexerSimple():
    def __init__(self, data={}):
        """
        :para data dict(int(idDoc): string(Doc))
        """
        self.indexes = dict()
        self.reverse_indexes = dict()
        self.docs = data.copy()
        self.collection_size = len(self.docs)
        self.tr = PorterStemmer()

    
    def indexation(self, normalise = False):
        """ Méthode permettant d'indexer une collection (représenter sous forme de dictionnaire)"""
        
        for key,value in self.docs.items():
            self.indexes[key] = self.tr.getTextRepresentation(value.title+" "+value.text) # on applique l'indexation sur le titre et le texte 
            if normalise:
                s = sum(self.indexes[key].values()) # nombre total de terme dans le document
                self.indexes[key] = dict((k, v/s) for k,v in self.indexes[key].items())
            for i in self.indexes[key].keys():
                if i not in self.reverse_indexes:
                    self.reverse_indexes[i] = {key:self.indexes[key][i]}
                else:
                    self.reverse_indexes[i].update({key:self.indexes[key][i]})
        #self.reverse_indexes = IndexerSimple.add_or_update_dict_values(self.reverse_indexes, i, {key:self.indexes[key][i]})
        #return self.indexes, self.reverse_indexes

    def getTfsForDoc(self, idDoc):
        """ retourne la représentation (stem-tf) d'un document à partir de l'index """
        if idDoc in self.indexes:
            return self.indexes[idDoc]
        return {}#False
    
    def getTfIDFsForDoc(self, idDoc):
        """ retourne la représentation (stem-TFIDF) d'un document à partir de l'index """
        if idDoc in self.indexes:
            return dict((k, v*log((self.collection_size+1)/(1+len(self.reverse_indexes[k])))) for k, v in self.indexes[idDoc].items())
        return {} #False
    
    def getidfsForStem(self, stem):
        """
        Permet de récupérer idf (index document frequency) d'une terme dans le corpus considéré.
        
        :param stem: Le terme dont idf doit être calculé
 
        :type stem: string
        
        :return: idf
        :rtype: float
        """
        
        if stem not in self.reverse_indexes:
            df = 0
        else:
            df = len(self.reverse_indexes[stem])

        return np.log((1+len(self.indexes)) / (1+df))

    def getTfsForStem(self, stem):
        """ retourne la représentation (doc-TF) d'un stem à partir de l'index inversé """
        if stem in self.reverse_indexes:
            return self.reverse_indexes[stem]
        return None #False
    
    def getTfIDFsForStem(self, stem):
        """ retourne la représentation (doc-TFIDF) d'un stem à partir de l'index inversé """
        if stem in self.reverse_indexes:
            return dict((k, v*log((self.collection_size+1)/(1+len(self.reverse_indexes[stem])))) for k, v in self.reverse_indexes[stem].items())
        return {}#False

    def saveIndexes(self, dir="../data/"):
        """ Sauvegarder les indexes dans un fichier en utilisant pickle """
        file = open(dir+"indexes.data", "wb")
        pickle.dump(self.indexes, file)
        file.close()
        # save reverse_indexes
        file = open(dir+"reverse_indexes.data", "wb")
        pickle.dump(self.reverse_indexes, file)
        file.close()
        return True
    
    def loadIndexes(self, dir="../data/"):
        file = open(dir+"indexes.data", "rb")
        self.indexes = pickle.load(file)
        file.close()
        # load reverse_indexes
        file = open(dir+"reverse_indexes.data", "rb")
        self.reverse_indexes = pickle.load(file)
        file.close()
        return True
    
    def getStrDoc(self, idDoc):
        return self.docs[idDoc].__str__()
    
    def getHyperlinksTo(self, idDoc):
        """ 
            Méthode permettant de récupérer tous les documents qui citent le document passé en paramètre
            
            param idDoc: identifiant du document
            type idDoc: int
            return: Liste des documents
            rtype: list(Document)
        """
        listdocs = []
        if idDoc in self.docs:
            listdocs = []
            for key,value in self.docs.items():
                if idDoc in value.links:
                    listdocs.append(key)
        else:
            print("L'identifiant du document n'est pas dans la collection.")
        
        return listdocs


    def getHyperlinksFrom(self, idDoc):
        """ 
            Méthode permettant de récupérer tous les documents cités par le document passé en paramètre
            
            param idDoc: identifiant du document
            type idDoc: int
            return: Liste des documents
            rtype: list(Document)
        """
        listdocs = set()
        if idDoc in self.docs:
            for link_id in self.docs.get(idDoc).links:
                if link_id in self.docs:
                    listdocs.add(link_id)
        else:
            print("L'identifiant du document n'est pas dans la collection.")
        
        return list(listdocs)


class IndexerHugeCollection():
    """
    TME1: Bonus
    [classe traitant les Grandes collection de documents]
    """
    def __init__(self, docs_filename):
        """
        :param docs_filename
        """
        self.docs_filename = docs_filename
        self.tr = PorterStemmer()
        self.indexes_path = "./data/indexes.db"
        self.reverse_indexes_path = "./data/reverse_indexes.db"

    def indexationHugeCorpus(self, normalise = False):
        """ 
            Méthode permettant d'indexer une collection (représenter dans un fichier) [Idéale pour les grandes collections]
        """
        shelve_indexes = shelve.open(self.indexes_path, "c")
        shelve_reverse_indexes = shelve.open(self.reverse_indexes_path, "c")
        with shelve.open(self.docs_filename) as f:
            for key, value in f.items():        
                shelve_indexes[int(key)] = self.tr.getTextRepresentation(value.title+" "+value.text) # on applique l'indexation sur le titre et le texte     
                if normalise:
                    s = sum(shelve_indexes[int(key)].values()) # nombre total de terme dans le document
                    shelve_indexes[int(key)] = dict((k, v/s) for k,v in shelve_indexes[int(key)].items())
                for i in shelve_indexes[int(key)].keys():
                    if i not in shelve_reverse_indexes:
                        shelve_reverse_indexes[i] = {key:shelve_indexes[int(key)][i]}
                    else:
                        shelve_reverse_indexes[i].update({key:shelve_indexes[int(key)][i]})

        shelve_indexes.close()
        shelve_reverse_indexes.close()

    def getTfsForDoc(self, idDoc):
        """ retourne la représentation (stem-tf) d'un document à partir de l'index """
        with shelve.open(self.indexes_path) as indexes:
            if idDoc in indexes:
                return indexes[idDoc]
        return {}#False
    
    def getTfIDFsForDoc(self, idDoc):
        """ retourne la représentation (stem-TFIDF) d'un document à partir de l'index """
        
        with shelve.open(self.indexes_path) as indexes:
            if idDoc in indexes:
                shelve_reverse_indexes = shelve.open(self.reverse_indexes_path)
                value = dict((k, v*log((len(indexes)+1)/(1+len(shelve_reverse_indexes[k])))) for k, v in indexes[idDoc].items())
                shelve_reverse_indexes.close()
                return value
        
        return {}#False
    
    def getidfsForStem(self, stem):
        """
        Permet de récupérer idf (index document frequency) d'une terme dans le corpus considéré.
        
        :param stem: Le terme dont idf doit être calculé
 
        :type stem: string
        
        :return: idf
        :rtype: float
        """
        taille = 0
        with shelve.open(self.indexes_path) as indexes:
            taille = len(indexes)
            shelve_reverse_indexes = shelve.open(self.reverse_indexes_path)
            if stem not in shelve_reverse_indexes:
                df = 0
            else:
                df = len(shelve_reverse_indexes[stem])
            shelve_reverse_indexes.close()

        return np.log((1+taille) / (1+df))

    def getTfsForStem(self, stem):
        """ retourne la représentation (doc-TF) d'un stem à partir de l'index inversé """
        with shelve.open(self.reverse_indexes_path) as reverse_indexes:
            if stem in reverse_indexes:
                return reverse_indexes[stem]
        return {}#False
    
    def getTfIDFsForStem(self, stem):
        """ retourne la représentation (doc-TFIDF) d'un stem à partir de l'index inversé """
        with shelve.open(self.reverse_indexes_path) as reverse_indexes:
            if stem in reverse_indexes:
                indexes = shelve.open(self.indexes_path)
                value = dict((k, v*log((len(indexes)+1)/(1+len(reverse_indexes[stem])))) for k, v in reverse_indexes[stem].items())
                indexes.close()
                return value
        
        return {}#False
    
    def getStrDoc(self, idDoc):
        with shelve.open(self.docs_filename) as docs:
            return docs[str(idDoc)].__str__()
    
    def getHyperlinksTo(self, idDoc):
        """ 
            Méthode permettant de récupérer tous les documents qui citent le document passé en paramètre
            
            param idDoc: identifiant du document
            type idDoc: int
            return: Liste des documents
            rtype: list(Document)
        """
        listdocs = []
        with shelve.open(self.docs_filename) as docs:
            if str(idDoc) in docs:
                for key,value in docs.items():
                    if idDoc in value.links:
                        listdocs.append(int(key))
            else:
                print("L'identifiant du document n'est pas dans la collection.")
        
        return listdocs


    def getHyperlinksFrom(self, idDoc):
        """ 
            Méthode permettant de récupérer tous les documents cités par le document passé en paramètre
            
            param idDoc: identifiant du document
            type idDoc: int
            return: Liste des documents
            rtype: list(Document)
        """
        listdocs = set()
        with shelve.open(self.docs_filename) as docs:
            if str(idDoc) in docs:
                for link_id in docs.get(str(idDoc)).links:
                    if str(link_id) in docs:
                        listdocs.add(link_id)
            else:
                print("L'identifiant du document n'est pas dans la collection.")
        
        return list(listdocs)
