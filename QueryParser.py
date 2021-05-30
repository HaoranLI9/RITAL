from utils.Query import Query
import re

class QueryParser():
    """
    permettant de lire les fichiers de tests de requetes et de jugements de pertinence
    """
    def parseQry(self, filename):
        """ 
        Fonction pour parser une query stockée et renvois un dictionnaire
        """
        # définition des fonction regex
        if filename == "cacm":
            reg = re.compile(r'\.W((.|\n)*)\n\.[ABNXW]') # Contenu du query
        if filename == "cisi":
            reg = re.compile(r'\.W((.|\n)*)\n\.[ABNXW]')
            reg2 = re.compile(r'\.W((.|\n)*)\n')
        # lecture du fichier
        file = open("./data/"+str(filename)+"/"+str(filename)+".qry", "r")
        #file = open(filename, "r")
        content = file.read()
        file.close()
        # Split le contenu du fichier selon la balise I(identifiant)
        content_split = re.split(r'.I\s(\d+)', content)
        res = {}
        for i in range(1, len(content_split), 2): # indice pour parcourir les query, i représente l'indice de la valeur de la balise .I
            # constituer un dictionnaire des regex et les appliquer sur chaque item
            id = int(content_split[i])
            query = Query(id)
            t = ""
            match = reg.search(content_split[i+1])
            if match:
                t = match.group(1)
            else:
                match = reg2.search(content_split[i+1])
                if match:
                    t = match.group(1)
            query.savetexte(t)
            res[id] = query
            del query
        return res

    def parseRel(self, filename, query):
        """
        Fonction pour compléter un requete avec jugement
        """
        # lecture du fichier
        #file = open(filename, "r")
        file = open("./data/"+str(filename)+"/"+str(filename)+".rel", "r")
        content = file.read()
        file.close()
        # Split le contenu du fichier selon chacune ligne
        content_split = re.split(r'\n', content)
        #if filename == "cacm":
        #    reg = re.compile(r'(\d+)\s(\d+)') # Contenu du jugement
        #if filename == "cisi":
        #   reg = 
        if filename == "cacm":
            reg = re.compile(r'(\d+)\s(\d+)') # Contenu du jugement
        if filename == "cisi":
            reg = re.compile(r'(\d+)\s+(\d+)') # Contenu du jugement
        res = {}
        for i in range(len(content_split)):
            match = reg.search(content_split[i])
            if match:
                id = int(match.group(1))
                iddoc_pertinent = int(match.group(2))
                res.setdefault(id,[]).append(iddoc_pertinent)
            for i in res:
                query[i].saveiddocpert(res[i])
            
