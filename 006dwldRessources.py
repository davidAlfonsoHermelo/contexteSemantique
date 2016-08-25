#!/usr/bin/python
#-*- coding:utf-8 -*-

#--------------START-IMPORTATIONS-------------------

import codecs, re, glob, os, uuid, string, requests
from bs4 import BeautifulSoup

#--------------END-IMPORTATIONS-------------------

#--------------START-PARAMETRES-------------------


#--------------END-PARAMETRES-------------------

#--------------START-FONCTIONS-------------------

def ouvrirFichier(fichier): 
	texteFichier = codecs.open(fichier, 'r', encoding='utf8').read()
	return texteFichier.lower()


def ecrireFichier(texte, nomDeFichier='essai'): 
	nomDeFichier = str(nomDeFichier)
	fichier = './' + nomDeFichier + '.txt'
	fichierATexte = codecs.open(fichier, 'w', encoding='utf8')
	fichierATexte.write(texte)
	fichierATexte.close()
	return None


def deURLATexte(url):
	"""
	la fonction deURLATexte aspire le texte d'une page web
	et retourne le texte brut
	"""
	contenuURL = requests.get(url.encode("UTF8"))
	texteURL = contenuURL.text
	soup = BeautifulSoup(texteURL)
	texte = []
	for title in soup.select('h1[class="content-headline"]'):
		title = (title.get_text()).encode('UTF8')
		title = title.decode('utf-8')
		texte.append(title)
	for paragraphe in soup.select('p'):
		paragraphe = (paragraphe.get_text()).encode('UTF8')
		paragraphe = paragraphe.decode('utf-8')
		texte.append(paragraphe)
	toutLeTexte = '\n'.join(texte)
	return toutLeTexte


#--------------END-FONCTIONS-------------------

#--------------START-DECLARATIONS-------------------

#Liste des pages web a aspirer
listeUrls = ['https://en.wikipedia.org/wiki/Marketing',
'https://en.wikipedia.org/wiki/Cargo',
'https://en.wikipedia.org/wiki/Computer_network',
'https://en.wikipedia.org/wiki/Customs',
'https://en.wikipedia.org/wiki/Tax']

#ASPIRER PAGE WEB ET ENREGISTRER DANS UN FICHIER RESSOURCE
compteur = 001
for url in listeUrls:
	textePageWeb = deURLATexte(url)
	ecrireFichier(textePageWeb, 'ressource/'+str(compteur))
	compteur += 1

#--------------END-DECLARATIONS-------------------

#--------------START-COMMANDES-------------------





#--------------END-COMMANDES-------------------

#--------------START-REFERENCES-------------------

###Tuto: 

#--------------END-REFERENCES-------------------