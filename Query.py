class Query():
    def __init__(self, id_query):
        """
        permet de initialiser id, texte et ids des documents pertinents.
        """
        self.id = int(id_query)
        self.texte = ""
        self.iddoc_pert = []

    #retourner
    def get_identifiant(self):
        """
        :rtype : int
        """
        return self.id
    
    def get_texte(self):
        """
        :rtype : string
        """
        return self.texte

    def get_iddoc_pert(self):
        """
        liste des identifiants des documents pertinents.
        :rtype : liste
        """
        return self.iddoc_pert

    #stocker

    def savetexte(self, texte):
        self.texte = texte

    def saveiddocpert(self, iddoc_pertinent):
        """
        :para iddoc liste de iddoc_pertinent
        """
        self.iddoc_pert = iddoc_pertinent
        