#!/usr/bin/env python3

class Document:
    """ Classe Document nous permettant de stocker un document avec ses métadonnées """
    def __init__(self, ident, title, text, links):
        self.id = ident
        self.title = title.strip()
        self.text = text.strip()
        self.links = links
    
    def __str__(self):
        links = " ".join(list(map(str, self.links)))
        return f"Identifiant: {self.id}\n\nTitle: {self.title}\n\nText: {self.text}\n\nLiens: {links}"