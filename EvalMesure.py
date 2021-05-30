from utils.Query import Query
import numpy as np

class EvalMesure():
    def evalQuery(self, liste, query):
        """
        :para liste : une liste de id_doc retourné par le modele
        :para query : requete type Query(on a déjà définit)
        """
        pass


class precision(EvalMesure):
    """
    utilisant le parametre Precision
    Precision = nb(doc_pertinent) / k(rang)
    """
    def __init__(self, k=3):
        """
        :para k rang de precision qu'on veut
        """
        self.k = k

    def evalQuery(self, liste, query):
        """
        :para liste : une liste de id_doc retourné par le modele
        :para query : requete type Query(on a déjà définit)
        """
        res = 0
        iddoc_pert = query.get_iddoc_pert()
        #if len(liste) > k
        for i in range(min(len(liste),self.k)):#si k est plus que length de liste, on prend directement len(liste)
            if liste[i] in iddoc_pert: ##list[i] presents id_doc
                res += 1 # si il y a un document pertinent on ajoute 1

        return res/self.k #Precision = nb(doc_pertinent) / k(rang)

class rappel(EvalMesure):
    """
    utilisant le parametre Rappel
    Rappel = nb(doc_pertinent) / len(Tous les doc pertinent)
    """
    def __init__(self, k=3):
        """
        :para k rang de rappel qu'on veut
        """
        #super().__init__()
        self.k = k

    def evalQuery(self, liste, query):
        """
        :para liste : une liste de id_doc retourné par le modele
        :para query : requete type Query(on a déjà définit)
        """
        res = 0
        iddoc_pert = query.get_iddoc_pert()
        #if len(liste) > k
        for i in range(min(len(liste), self.k)):
            if liste[i] in iddoc_pert:
                res += 1 
        if len(iddoc_pert)==0:
            return 0
        return res/len(iddoc_pert)


class F_mesure(EvalMesure):
    """
    return F_mesure 2*P*R/(P+R)
    """
    def __init__(self, k=3):
        """
        :para k rang de rappel qu'on veut
        """
        #super().__init__()
        self.k = k

    def evalQuery(self, liste, query):
        """
        :para liste : une liste de id_doc retourné par le modele
        :para query : requete type Query(on a déjà définit)
        """
        R = rappel(self.k).evalQuery(liste, query)

        P = precision(self.k).evalQuery(liste, query)
        if (P+R)==0:
            return 0
        return 2*P*R/(P+R)

        
class AP(EvalMesure):
    """
    AP CAD Average Precision
    """
    def evalQuery(self, liste, query):
        """
        :para liste : une liste de id_doc retourné par le modele
        :para query : requete type Query(on a déjà définit)
        """
        res = 0
        for i in range(1, len(liste)+1):
            res += precision(i).evalQuery(liste, query)
        if len(liste) == 0:
            return 0
        AP = res/len(liste)
        return AP

class reciprocal_rank(EvalMesure):
    def evalQuery(self, liste, query):
        """
        :para liste : une liste de id_doc retourné par le modele
        :para query : requete type Query(on a déjà définit)
        """
        iddoc_pert = query.get_iddoc_pert()
        for i in range(len(liste)):
            if liste[i] in iddoc_pert:
                return 1/(i+1)
        return 0


class NDCG(EvalMesure):
    """
    Utilisant NDCG = DCG / DCG_ideal
    """
    def evalQuery(self, liste, query):
        """
        :para liste : une liste de id_doc retourné par le modele
        :para query : requete type Query(on a déjà définit)
        """
        iddoc_pert = query.get_iddoc_pert()
        dcg = 0
        idcg = 0
        k = 1
        for i in range (len(liste)):
            if liste[i] in iddoc_pert:
                dcg += 1/np.log2(i+2)
                idcg += 1/np.log2(k+2)
                k += 1
        if idcg == 0:
            return 0 # on ne cherche pas doc pert pas 
        ndcg = dcg / idcg
        return ndcg 
        
            

