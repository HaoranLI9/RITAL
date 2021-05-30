#from utils.Weight import Weighter, Weighter1, Weighter2, Weighter3, Weighter4, Weighter5


class IRModel():
    """
    un modèle de Recherche d'Information.
    """
    def __init__(self, indexersimple):
        """
        :para poid considere utilisant classe Weighter

        :type indexersimple: indexersimle(la classe de indexersimple)
        """

        self.indexersimple = indexersimple
    
    def getScores(self, query):
        """
        :para query: La requete considéreree

        :type query: string
        
        :return: les scores des documents pour une requete
        :rtype: dict[int: number]
        """
        pass
    
    def getRanking(self, query):
        """
        :param query: La requete considéreree
        :type query: string

        :return: retourne une liste de coupes (document-score) ordonnee par score decroissante.
        :rtype tuple[(docid, score).....]
        """
         #ici, vscode dit il y a une faute, mais ca marche, parce que Child class existe fonction qui va récrire celle de parent class
        scores = self.getScores(query)
        
        doc_scores = {}
        
        doc_scores = sorted(scores.items(), reverse=True, key=lambda x: x[1])

        return doc_scores

class Vectoriel(IRModel):
    """
    modèle de Vectoriel EN IRmodel
    """
    def __init__(self, weighter, normalise = True):
        """
        :para weighte
        si normalise True, on utilise socre cos
        sinon produit scalaire

        :para normalise booleen
        """
        #super().__init__(weighter)#utilise initialisation de father
        self.weighter = weighter
        self.normalise = normalise
    
    def getScores(self, query):
        """
        :para requete
        :rtype dic(int : double) / docid : score 
        """
        if self.normalise == True :
            return self.scores_normalised(query)
        else:
            return self.scores_notnormalised(query)

    def scores_notnormalised(self, query):
        """
        scores notnormalised CAD produit scalaire
        :para query
        :rtype dic(int : double) / docid : score 
        """
        res = {}
        weight_query = self.weighter.getWeightsForQuery(query)
        for stem, weightQuery in weight_query.items():
            weight_stem = self.weighter.getWeightsForStem(stem)
            for docid, weightStem in weight_stem.items():
                if docid not in res:
                    res[docid] = weightQuery * weightStem
                else:
                    res[docid] += weightQuery * weightStem
        return res

    def scores_normalised(self, query):
        """
        scores normalised CAD scores-cos
        :para query
        :rtype dic(int : double) / docid : score 
        """
        res = {}
        produit_sca = self.scores_notnormalised(query)
        ##ici pour optimiser notre code, on cree fonctions dans classe Weight pour calculer les normes de weight_DOC et QUERY
        for docid, prod_sca in produit_sca.items():
            res[docid] = prod_sca/(self.weighter.getNormeforDoc(docid)*self.weighter.getNormeforquery(query))
        return res
 
# on cherchera à optimiser 
class ModeleLangue(IRModel):
    """
     Classe ModeleLangue héritant de IRModel
    """

    def __init__(self, indexer, v_lambda=0.8):
        super().__init__(indexer)
        self.v_lambda = v_lambda

    def getScores(self, query):
        """ Calcule le score d'une requête avec le Modele de Langue : (lissage Jelinek-Merce) """
        # passer la chaine de caractère query à Porter pour la lemmatisation
        queryStems = self.indexersimple.tr.getTextRepresentation(query)
        
        pTcByStem = self._getCollectionQueryScore(queryStems)
        scores = dict()
        for idDoc in self.indexersimple.indexes.keys():
            # eliminer les docs qui ne contiennent aucun des termes de la requêtes
            if set(queryStems.keys()).intersection(self.indexersimple.getTfsForDoc(idDoc).keys()):
                scores[idDoc] = self._getQueryScoreByDoc(idDoc, pTcByStem)
        return scores
        
    
    def _getQueryScoreByDoc(self, idDoc, pTcByStem):
        """ 
        Renvoi le score par terme
        """
        queryScore = 1
        for stem, tfCollection in pTcByStem.items():
            if stem not in self.indexersimple.getTfsForDoc(idDoc):
                pTD = 0
            else: 
                pTD =  self.indexersimple.getTfsForDoc(idDoc)[stem]/sum(self.indexersimple.getTfsForDoc(idDoc).values()) # probabilité d'un terme s'achant le modele de langue du document
            queryScore *= (1*self.v_lambda)*pTD + self.v_lambda*tfCollection

        return queryScore
    
    def _getCollectionQueryScore(self, queryStems):
        """
        Retourne pour tous les termes de la requête la probabilité d'un terme sachant le modele de langue de la Collection.
        Si un terme n'est pas présent dans la collection on renvoie une valeur faible
        """
        pTcByStem = dict()
        tfCollection = sum([sum(v.values()) for v in self.indexersimple.reverse_indexes.values()]) # Tf des termes de la collection
        for stem in queryStems.keys():
            if stem not in self.indexersimple.reverse_indexes:
                pTcByStem[stem] = 1/tfCollection # cas où le terme n'existerai carrement pas dans notre collection
                continue
            pTcByStem[stem] = sum(self.indexersimple.getTfsForStem(stem).values())/tfCollection
        return pTcByStem


class Okapi(IRModel):
    """
     Classe héritant de IRModel et basant sur les modèles probabiliste
    """
    def __init__(self, indexer, k1=1.2, b=0.75):
        super().__init__(indexer)
        self.k1 = k1
        self.b = b

    def getScores(self, query):
        scores = dict()
        # passer la chaine de caractère query à Porter pour la lemmatisation
        queryStems = self.indexersimple.tr.getTextRepresentation(query)
        # longueur moyenne des documents
        avgd = sum([sum(v.values()) for v in self.indexersimple.indexes.values()])/len(self.indexersimple.indexes)
        for idDoc in self.indexersimple.indexes.keys():
            # eliminer les docs qui ne contiennent aucun des termes de la requêtes
            if set(queryStems.keys()).intersection(self.indexersimple.getTfsForDoc(idDoc).keys()):
                scores[idDoc] = self._getQueryScoreByDoc(idDoc, queryStems, avgd)
        return scores

    def _getQueryScoreByDoc(self, idDoc, queryStems, avgd):
        docQueryScore = 0

        for stem, nbOccur in queryStems.items():
            if stem in self.indexersimple.getTfsForDoc(idDoc):
                tfStemForDoc = self.indexersimple.getTfsForDoc(idDoc)[stem]
                stemScore = self.indexersimple.getidfsForStem(stem)*tfStemForDoc/(tfStemForDoc+self.k1*(1-self.b+self.b*sum(self.indexersimple.indexes[idDoc].values())/avgd))
                docQueryScore += nbOccur * stemScore
        
        return docQueryScore
