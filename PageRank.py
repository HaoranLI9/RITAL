import random
import numpy as np

class PageRankModel:
    def __init__(self):

        self.V_Q = []
        self.E_Q = []
        self.seed = []

    def getSubGraph(self, indexer, query, base_model, n_seed=10, incom_link=5):
        """
        Cette fonction permet de renvoyer le graphe correspondant à une requête donnée et pour un modele donné
        """
        tmpV = set()
        tmpE = set()
        self.seed = [item[0] for item in base_model.getRanking(query)] # ajout des documents repondant au contenu demandé
        self.seed = self.seed if len(self.seed)<=n_seed else self.seed[:n_seed]
        
        for idDoc in self.seed:
            tmpV.add(idDoc)
            # ajout des documents vers qui pointent le document courant
            for otherDoc in indexer.getHyperlinksFrom(idDoc):
                # ajout du document
                tmpV.add(otherDoc)
                # ajout du lien entre les documents
                tmpE.add((idDoc, otherDoc))
            
            # ajout de k documents choisis aléatoirement et qui pointent tous vers idDoc
            incoming_links = indexer.getHyperlinksTo(idDoc)
            incoming_links = incoming_links if len(incoming_links)<=incom_link else random.sample(incoming_links, incom_link)
            for otherDoc in incoming_links:
                tmpV.add(otherDoc)
                tmpE.add((otherDoc, idDoc))

        # on a notre sous graphe correspondant à la requête    
        self.V_Q = list(sorted(tmpV))
        self.E_Q = list(tmpE)
        
    def getAdjacencyMatrix(self):
        A = np.zeros((len(self.V_Q), len(self.V_Q)))
        for i,j in self.E_Q:
            A[self.V_Q.index(i)][self.V_Q.index(j)] = 1
        return A
    
    def getTransitionMatrix(self, adjacency_matrix):
        return adjacency_matrix/adjacency_matrix.sum(axis=1, keepdims=True)


    def runPageRank(self, damping_factor=0.85, priori=None):
        # get A
        A = self.getAdjacencyMatrix()
        P = self.getTransitionMatrix(A)
        if priori is None:
            priori = np.ones((1, A.shape[0])) / A.shape[0] # dans le cours il a été dit que le a priori est une probabilité que la page "i" soit importante a priori et somme des a priori donne 1
        s = np.random.dirichlet(np.ones(A.shape[0]),size=1) # initialisation de s. La somme des s donne 1 comme indiqué dans le cours
        eps = 1e-3

        for i in range(5000):
            s_new = damping_factor * s@P + (1-damping_factor)*priori
            if np.abs(np.subtract(s_new, s)).all()<eps:
                print("\nConvergé à l'itération: ", i+1)
                break
            s = s_new
        # classement des scores
        rank = np.argsort(s, axis=1)[0]
        # reverse array
        rank = rank[::-1]
        return [(self.V_Q[i], s[0][i]) for i in rank if self.V_Q[i] in self.seed] # retourne le page rank de document seeds (document retourné auparavant par le modèle de la requête)