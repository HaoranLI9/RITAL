#!/usr/bin/env python3

import re
from utils.Document import Document
import shelve
import time

class Parser:
    

    def parse_doc(self, file_path):
        """ Fonction pour parser une collection stockée et renvois un dictionnaire de Documents """
        # définition des fonction regex
        reg1 = re.compile(r'\.T(\n|\r\n?)(?P<Title>(.*|(\n|\r\n?))*)(\n|\r\n?)+\.[BANWX]') # Title
        reg2 = re.compile(r'\.W(\n|\r\n?)(?P<Content>(.*|(\n|\r\n?))*)(\n|\r\n?)+\.[BANX]') # Contenu du document
        reg3 = re.compile(r'\.X[\n\r](.|[\n\r])*[\n\r]')

        # lecture du fichier
        #file = open(filename, "r")
        file = open(file_path, "r")
        content = file.read()
        file.close()
        # Split le contenu du fichier selon la balise I(identifiant)
        content_split = re.split(r'\.I\s+(\d+)', content)
        #content_split = re.split(r'\s*.I\s+(\d+)', content)
        data = dict()
        
        for i in range(1, len(content_split), 2): # indice pour parcourir les documents, i représente l'indice de la valeur de la balise .I
            # constituer un dictionnaire des regex et les appliquer sur chaque item
            t = ""
            c = ""
            match = reg1.search(content_split[i+1])
            if match:
                t = match.group('Title')
            match = reg2.search(content_split[i+1])
            if match:
                c = match.group('Content')
            match = reg3.search(content_split[i+1])
            # ajout des liens
            if match:
                l = re.findall(r"(\d+).*[\n\r]", match.group(0))
            data[int(content_split[i])] = Document(content_split[i], t, c, set(map(int, l)))
            if i%500==0:
                print("TAille de la collection traité: ", len(data))
        return data

    def parse_single_doc(self, idDoc, raw_doc):
        """ Fonction permettant de parser un seul document passé en paramètre(utilisé par la fonction parse_huge_collection) """
        reg1 = re.compile(r'\.T(\n|\r\n?)(?P<Title>(.*|(\n|\r\n?|\s))*)(\n|\r\n?)+\.[BANWX]') # Title
        reg2 = re.compile(r'\.W(\n|\r\n?)(?P<Content>(.*|(\n|\r\n?|\s))*)(\n|\r\n?)+\.[BANX]') # Contenu du document
        reg3 = re.compile(r'\.X[\n\r](.|[\n\r])*[\n\r]')

        t = ""
        c = ""
        match = reg1.search(raw_doc)
        if match:
            t = match.group('Title')
        match = reg2.search(raw_doc)
        if match:
            c = match.group('Content')
        match = reg3.search(raw_doc)
        # ajout des liens
        if match:
            l = re.findall(r"(\d+).*[\n\r]", match.group(0))
        return Document(idDoc, t, c, set(map(int, l)))


    def parse_huge_collection(self, file_path):
        """ 
            Fonction pour parser une très grande collection de documents très rapidement 

            Fait moins d'une seconde pour parser environ 4200 documents du fichier cacm.txt

            Cette fonction se charge également de stocker les documents parsés dans un fichier 
            binaire(cela permet de ne pas tout garder en mémoire) et on peut
            accéder à tout document en O(1) grâce au module "shelve" intégré à python
        """
        # définition des fonction regex
        reg1 = re.compile(r"^\s*\.I\s*(?P<Identifier>\d+)")

        # lecture du fichier
        buffer = ""
        #docs = dict()
        ident = None
        i = 0
        parsed_file_path = "./data/collection_parsed.dat"
        parser_file = shelve.open(parsed_file_path, "c")
        stt = time.time()
        with open(file_path, "r") as file:
            for line in file:
                match = reg1.search(line)
                
                if match: # vérifer si on tombe sur un identifiant de document
                    i+=1
                    if buffer=="": # si on n'a pas de document en cours dans la mémoire tampon, là on fait pas de traitement          
                        ident = match.group("Identifier")
                        continue
                    else:
                        parser_file[ident] = self.parse_single_doc(int(ident), buffer)
                        # docs[ident] = parse_single_doc(ident, buffer) # Faire un traitement sur le document en mémoire
                        ident = match.group("Identifier")
                        buffer = ""
                        continue
                    if i>500:
                        print("\n"+str(i), end="D ")
                
                buffer += line
    
            # Rajouter le dernier document qui reste dans le buffer
            #docs[ident] = parse_single_doc(ident, buffer)
            print("Données traitées: "+str(i)+" en "+str(time.time()-stt)+" (sec)")
            print("Collection traitée et enrégistrer sous : "+parsed_file_path)
            parser_file[ident] = self.parse_single_doc(int(ident), buffer)
            parser_file.close()
        #return docs
    