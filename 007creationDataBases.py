#!/usr/bin/python
#-*- coding:utf-8 -*-

#--------------START-IMPORTATIONS-------------------

import codecs, re, glob, os, uuid, string, requests
import nltk, pickle, many_stop_words
from nltk.stem.snowball import SnowballStemmer
from nltk.stem import WordNetLemmatizer
from bs4 import BeautifulSoup
from pattern.fr import parsetree

#--------------END-IMPORTATIONS-------------------

#--------------START-PARAMETRES-------------------

langueDuTexte = 'english'#'french'

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


def tokeniseur(texteASegmenter, motsOuPhrase="mot"):
	#la fonction tokeniseur segmente une txt en un dictionnaire de ses mots, si ceux-ci sont segmentables par les moyens traditionnels, aucune exception n'est prise en compte
	
	texteASegmenter = re.sub('\d+', '', texteASegmenter)
	texteDejaSegmenteMot = re.findall(r"[\w']+", texteASegmenter)
	#ou texteDejaSegmenteMot = re.compile("\W+", re.UNICODE)

	texteSegmentePhrase = re.compile("[。\.\?\!\n\r\t\;\(\)\:\[\]]+", re.UNICODE)
	texteDejaSegmentePhrase = texteSegmentePhrase.split(texteASegmenter)
	#ou texteDejaSegmentePhrase = enleveurDeMotsVides(re.split(u"[。\.\?\!\;\:\n]+", texteASegmenter))

	motsOuPhrase = str(motsOuPhrase)
	if motsOuPhrase.lower() == "mot" or motsOuPhrase.lower() == "mots" or motsOuPhrase.lower() == "m" or motsOuPhrase == "1":
		return texteDejaSegmenteMot
	if motsOuPhrase.lower() == "phrase" or motsOuPhrase.lower() == "phrases" or motsOuPhrase.lower() == "p" or motsOuPhrase == "2":
		return texteDejaSegmentePhrase


def enleveurDeVides(listeTexteTokenise):
	return [token for token in listeTexteTokenise if token != ""]


def enleveurDeStopWords(listeTexteTokenise, listeStopList):
	return [token for token in listeTexteTokenise if token not in listeStopList]


def enleveurStopWordsTuples(tupleTP, listeStopList):
	if tupleTP[0] not in listeStopList:
		return tupleTP 


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


def lemmatiseur(token):
	if langueDuTexte == 'english':
		lemmatizer = WordNetLemmatizer()
		lemma = lemmatizer.lemmatize(token)
	elif langueDuTexte == 'french':
		#parsetree déjà parametré pr francais
		lemma = parsetree(token, lemmata=True)
	return lemma

def posTagger(tokenOuListeTokens):
	######################################
	#chchr pos tag dans autres lang nltk.standford ptet
	######################################
	tokenOuListeTokens = list(tokenOuListeTokens)
	listeTP = nltk.pos_tag(tokenOuListeTokens)
	return listeTP

def generateurCodesUniques(lemmaInscrire, pos):
	"""
	generateur de codes id uniques base 64 à 5 caracteres
	"""
	#chargement dico
	try:
		fichierDico = open("dicoGlossaireCodesID.p", "rb")
		dicoGlossaireCodesID = pickle.load(fichierDico)
		fichierDico.close()
	except IOError:
		dicoGlossaireCodesID = {}
	#generateur
	verifieur = False
	while verifieur == False:
		codeIdUniqueRandom = uuid.uuid4().bytes.encode("base64")[:5]
		codeIdUniqueRandom = string.replace(codeIdUniqueRandom, '/', '_')
		codeIdUniqueRandom = string.replace(codeIdUniqueRandom, '+', '-')
		if codeIdUniqueRandom not in dicoGlossaireCodesID.values():
			verifieur = True	
	#verification que le code id n'existe pas encore
	#et ne correspond pas a un token deja existant
	cleVerif = lemmaInscrire + '_' + pos
	if cleVerif not in dicoGlossaireCodesID:
		dicoGlossaireCodesID[cleVerif] = codeIdUniqueRandom
	else:
		codeIdUniqueRandom = dicoGlossaireCodesID[cleVerif]
	#pickle dump
	fichierDico = open("dicoGlossaireCodesID.p", "wb")
	pickle.dump(dicoGlossaireCodesID, fichierDico)
	fichierDico.close()
	return codeIdUniqueRandom


def generateurCodeCtxt(listeCtxt, nbCtxtAPrendreEnCompte=5):
	"""
	la fonction generateurCodeCtxt fournit un complement
	de code id unique supplementaire pour le dico final
	correspondant au contexte
	"""
	#pickle
	fichierDico = open("dicoGlossaireCodesID.p", "rb")
	dicoGlossaireCodesID = pickle.load(fichierDico)
	fichierDico.close()
	#verif qu'il y a assez de contexte
	if len(listeCtxt) < nbCtxtAPrendreEnCompte:
		nbCtxtAPrendreEnCompte = len(listeCtxt)

	codeIdCtxt = ['*']
	compteur = 0
	while compteur < nbCtxtAPrendreEnCompte:
		ctxt = listeCtxt[compteur]
		#vérification que la cle existe
		try:
			code = dicoGlossaireCodesID[ctxt]
		except KeyError:
			listeClesCtxt = dicoGlossaireCodesID.keys()
			for cleCtxt in listeClesCtxt:
				lemPos = '_'.split(ctxt)
				print(ctxt, lemPos)
				lemma = lemPos[0]
				pos = lemPos[1]
				lemma = lemmatiseur(lemma)
				#verification que le token est bien lemmatisé
				try:
					ctxtLemmatise = lemma + '_' + pos
					code = dicoGlossaireCodesID[ctxtLemmatise]
				except KeyError:
					#sinon, on prend une instance du token au hasard
					#sans regarder son pos
					regex = '^' + lemma + '_' + '*'
					ctxtRegex = re.search(regex, cleCtxt)
					if ctxtRegex != None:
						print('eureka : ', ctxtRegex)
						code = dicoGlossaireCodesID[ctxtRegex]
						break
					else:
						print('#####rien#####', ctxt, type(ctxt))
			codeReduit = code[:2]
			codeIdCtxt.append(codeReduit)
		compteur +=1

	codeIdCtxt = ''.join(codeIdCtxt)
	return codeIdCtxt


def contexteurLetGo(listeContexteTokenEtPos):
	"""
	la fonction contexteurLetGo prend en argument une liste 
	de contexte, lemmatise tous les elements et les 
	enregistre dans un dictionnaire externe ou les
	tokens du contexte sont comptabilisés selon leur 
	rapprochement et la recursivité
	"""
	#pickle load le dico
	try:
		fichierDico = open("dicoContexte.p", "rb")
		dicoContexte = pickle.load(fichierDico)
		fichierDico.close()
	except IOError:
		dicoContexte = {}
	#remplacer token par lemma
	#ATTENTION! on n'a pas supprimé les stopwords gramm
	#pour tester leur importance syntaxique contextuelle
	for index in range(len(listeContexteTokenEtPos)):
		lemma = lemmatiseur(listeContexteTokenEtPos[index][0])
		pos = listeContexteTokenEtPos[index][1]
		#génération au premier tour d'un code unique pour chaque token
		generateurCodesUniques(lemma, pos)

		listeTP = list(listeContexteTokenEtPos[index])
		listeContexteTokenEtPos[index] = listeTP
	#enregistrer lemma+pos en cle et en valeur les mots
	#du contexte immediat et ajout avec get d'une valeur
	#correspondant a position et recursivité
	nbIndexCtxt = 1
	for indexLemma in range(len(listeContexteTokenEtPos)):
		lemmaAnalyser = listeContexteTokenEtPos[indexLemma][0]
		posAnaliser = listeContexteTokenEtPos[indexLemma][1]
		#contexte gch et drt
		indexCtxtGch = indexLemma - nbIndexCtxt
		if indexCtxtGch < 0:
			ctxtGch = None
		else: 
			ctxtGch = listeContexteTokenEtPos[indexCtxtGch]
			ctxtGch = ctxtGch[0] + '_' + ctxtGch[1]
		try:
			ctxtDrt = listeContexteTokenEtPos[indexLemma+nbIndexCtxt]
			ctxtDrt = ctxtDrt[0] + '_' + ctxtDrt[1]
		except IndexError:
			ctxtDrt = None
		#cle du dico
		lemmaEtPos = lemmaAnalyser + '_' + posAnaliser
		#dico dans dico
		try:
			dico2lemma = dicoContexte[lemmaEtPos]
		except KeyError:
			dicoContexte[lemmaEtPos] = {}
		#dico dans dico dans dico
		try: 
			dico3index0 = dicoContexte[lemmaEtPos]['0']
			dico3index1 = dicoContexte[lemmaEtPos][str(nbIndexCtxt)]
		except KeyError:
			dicoContexte[lemmaEtPos]['0'] = {}
			dicoContexte[lemmaEtPos][str(nbIndexCtxt)] = {}
		#transformation du contexte en liste avec un poids
		#ATTENTION!
		#la position du lemma dans la phrase a ete pris en compte
		#dans la deuxieme cle [nbIndexCtxt] mais on peut
		#ne requerir qu'un contexte général avec la cle [0]
		divise = nbIndexCtxt + 1
		poids = 1.0 / divise
		if ctxtGch != None:
			dicoContexte[lemmaEtPos]['0'][ctxtGch] = dicoContexte[lemmaEtPos]['0'].get(ctxtGch, 0.0)+poids
			dicoContexte[lemmaEtPos][str(nbIndexCtxt)][ctxtGch] = dicoContexte[lemmaEtPos][str(nbIndexCtxt)].get(ctxtGch, 0.0)+poids
		if ctxtDrt != None:
			dicoContexte[lemmaEtPos]['0'][ctxtDrt] = dicoContexte[lemmaEtPos]['0'].get(ctxtDrt, 0.0)+poids
			dicoContexte[lemmaEtPos][str(nbIndexCtxt)][ctxtDrt] = dicoContexte[lemmaEtPos][str(nbIndexCtxt)].get(ctxtDrt, 0.0)+poids
		nbIndexCtxt += 1
	#picle dump le dico
	fichierDico = open("dicoContexte.p", "wb")
	pickle.dump(dicoContexte, fichierDico)
	fichierDico.close()
	return None


def contexteurGiveMe(token, pos=None, lemma=None, contexteEnListeTokenPos=None):
	"""
	la fonction contexteurGiveMe prend en argument un
	token qu'il lemmatise et pour lequel il retourne 
	son contexte. Optimalement, on fournira aussi le POS
	du token (part of speech) selon le modele utilisé par
	nltk. Pour une précision du contexte prennant en compte
	la position du mot dans la phrase on fournira aussi
	une liste tokenisée de la phrase où se trouve le token
	dont on souhaite avoir le contexte
	"""
	#pickle load le dico
	fichierDico = open("dicoContexte.p", "rb")
	dicoContexte = pickle.load(fichierDico)
	fichierDico.close()
	if lemma == None:
		#remplacer token par lemma
		lemma = lemmatiseur(token)
	#POS et clé dicoContexte
	if pos == None:
		pos = posTagger([token])[1]
	cle1erDico = lemma + '_' + pos
	#pioche dans le dico
	if contexteEnListeTokenPos==None:
		cle2eDico = '0'
	else:
		cle2eDico = str(contexteEnListeTokenPos.index([token, pos])+1)
	dicoContexteExact = dicoContexte[cle1erDico][cle2eDico]
	#au cas où le contexte par position syntaxique serait insuffisant 
	if len(dicoContexteExact) < 9:
		dicoContexteExact = dicoContexte[cle1erDico]['0']
	#selection du contexte
	listeContexteOrdonnee = sorted(dicoContexteExact, key=dicoContexteExact.get, reverse=True)
	listeContexteSelect = listeContexteOrdonnee[:9]
	return listeContexteSelect


def premierTourTokenContexte(texteASegmenter, supprimerChiffres = 'yes'):
	"""
	la fonction premierTourTokenContexte doit produire
	un contexte de tout le texte fourni avant de passer
	au second tour
	Attention!!! : le lemma (et le stem) sont dépendants
	de la langue du texte par rapport aux modules nltk et
	pattern
	"""
	#suppression optionnelle des chiffres
	if supprimerChiffres == 'yes' or supprimerChiffres == 'y' or supprimerChiffres == 'oui':
			texteASegmenter = re.sub(r'[\d]+', '', texteASegmenter)
	#formatage du texte
	mots = re.compile(r"[\W]+", re.UNICODE)

	texteSegmentePhrase = re.compile(u"[。\.\?\!\n\r\t\;\(\)\:\[\]\§\¶\¿\¡\·]+")
	texteDejaSegmentePhrase = texteSegmentePhrase.split(texteASegmenter)
	texteDejaSegmentePhraseSansDoublon = list(set(texteDejaSegmentePhrase))
	texteDejaSegmentePhraseSansDoublon = enleveurDeVides(texteDejaSegmentePhraseSansDoublon)
	#division du txt en phrases et tokenisation mots et POS tag
	compteur = 0
	dicoTokensPosParPhrase = {}
	for phrase in texteDejaSegmentePhraseSansDoublon:
		phrase = phrase.lower()
		listeTokenise = mots.split(phrase)
		listeTokenise = enleveurDeVides(listeTokenise)
		listeTokenise = posTagger(listeTokenise)
		#contexteur pour ajouter au dico general
		contexteurLetGo(listeTokenise)
		dicoTokensPosParPhrase[str(compteur)] = listeTokenise
		compteur += 1
	return dicoTokensPosParPhrase


def secondTourTokenDico(dicoTokensPosParPhrase):
	"""
	la fonction secondTourTokenDico produit un dictionnaire 
	contenant comme cle un code id unique pour chaque 
	token et en valeur une liste du token, POS, lemma et
	stem (dans cet ordre).
	Attention!!! : le lemma (et le stem) sont dépendants
	de la langue du texte par rapport aux modules nltk et
	pattern
	"""
	#chargement pickle du dico final
	try:
		fichierDico = open("dicoFinalCodesID.p", "rb")
		dicoFinalCodesID = pickle.load(fichierDico)
		fichierDico.close()
	except IOError:
		dicoFinalCodesID = {}

	for cle in dicoTokensPosParPhrase:
		listeTokenPos = dicoTokensPosParPhrase[cle]
		for tokenEtPos in listeTokenPos:
			token = tokenEtPos[0]
			pos = tokenEtPos[1]
			#lemmatisation
			lemma = lemmatiseur(token)
			#stemmisation
			stemmer = SnowballStemmer(langueDuTexte)
			stem = stemmer.stem(token)
			#rendu d'une liste contenant le token, le pos, le lemma et le stem
			listeLingformatisee = [token, pos, lemma, stem]
			#contexte
			listeCtxt = contexteurGiveMe(token, pos, lemma, listeTokenPos)
			#attribution code id unique
			cleCodeId = generateurCodesUniques(lemma, pos)
			cleCodeCtxt = generateurCodeCtxt(listeCtxt)
			cleCodeDefinitif = cleCodeId + cleCodeCtxt

			#enregistrement nouvelles entrées
			dicoFinalCodesID[cleCodeDefinitif] = listeLingformatisee
	#pickle
	fichierDico = open("dicoFinalCodesID.p", "wb")
	pickle.dump(dicoFinalCodesID, fichierDico)
	fichierDico.close()
	return dicoFinalCodesID


def ajouteurDicoFinalTokenParToken(tupleOuListetokenEtPos):
	"""
	la fonction ajouteurDicoFinalTokenParToken fait
	la même fonction que moulinetteToken mais en 
	prennant un token à la fois en argument (tuple 
	ou liste de token et pos) au lieu de tout un texte.
	"""
	try:
		#pickle
		fichierDico = open("dicoFinalCodesID.p", "rb")
		dicoFinalCodesID = pickle.load(fichierDico)
		fichierDico.close()
	except IOError:
		dicoContexte = {}
	#unités
	token = tokenEtPos[0]
	pos = tokenEtPos[1]
	#lemmatisation
	lemma = lemmatiseur(token)
	#stemmisation
	stemmer = SnowballStemmer(langueDuTexte)
	stem = stemmer.stem(token)
	#rendu d'une liste contenant le token, le pos, le lemma et le stem
	listeLingformatisee = [token, pos, lemma, stem]
	#attribution code id unique
	cleCodeId = generateurCodesUniques(lemma, pos)

	#enregistrement nouvelles entrées
	dicoFinalCodesID[cleCodeId] = listeLingformatisee
	fichierDico = open("dicoFinalCodesID.p", "wb")
	pickle.dump(dicoFinalCodesID, fichierDico)
	fichierDico.close()
	return cleCodeId

def tourZeroNgram(texteASegmenter):
	"""
	la fonction tourZeroNgram segmente un txt 
	en une liste de ses phrases et 'phrasemes' les 
	plus courants et retourne un dictionnaire avec
	un code id unique pour cle et une liste avec
	le token-phraseme et son POS (PHR)
	"""
	texteASegmenter.lower()
	texteSegmentePhrase = re.compile(u"[[。\.\?\!\n\r\t\;\(\)\:\[\]\§\¶\¿\¡\·]+")
	texteDejaSegmentePhrase = texteSegmentePhrase.split(texteASegmenter)
	texteDejaSegmentePhraseSansDoublon = list(set(texteDejaSegmentePhrase))
		
	#chargement pickle du dico final
	try:
		fichierDico = open("dicoFinalCodesID.p", "rb")
		dicoFinalCodesID = pickle.load(fichierDico)
		fichierDico.close()
	except IOError:
		dicoContexte = {}

	for phraseme in texteDejaSegmentePhraseSansDoublon:
		mots = re.compile(r"[\W]+", re.UNICODE)
		listeTokenise = mots.split(phraseme)
		listeTokenise = enleveurDeVides(listeTokenise)
		lenPhraseme = len(listeTokenise)
		tailleNgramMax = lenPhraseme - 1
		#lemmatisation
		for index in range(lenPhraseme):
			listeTokenise[index] = lemmatiseur(listeTokenise[index])
		#reconstitution du phraseme
		for nbDeN in range(2, lenPhraseme):
			for index in range(tailleNgramMax):
				positionFinDeGram = index+nbDeN
				ngram = listeTokenise[index:positionFinDeGram]
				stringNgram = ' '.join(ngram)
				cleCodeId = generateurCodesUniques(stringNgram, 'PHR')
				dicoFinalCodesID[cleCodeId] = [stringNgram, 'PHR']
	fichierDico = open("dicoFinalCodesID.p", "wb")
	pickle.dump(dicoFinalCodesID, fichierDico)
	fichierDico.close()
	return dicoFinalCodesID


def encrypteur(texte):
	"""
	la fonction encrypteur associe les tokens en langage
	naturel d'un texte à leur représentation cryptee
	sémantiquement-contextuellement
	"""
	fichierDico = open("dicoFinalCodesID.p", "rb")
	dicoFinalCodesID = pickle.load(fichierDico)
	fichierDico.close()
	
	#segmentation phrases
	texteASegmenter.lower()
	texteSegmentePhrase = re.compile(u"[[。\.\?\!\n\r\t\;\(\)\:\[\]\§\¶\¿\¡\·\•]+")
	listePhrases = texteSegmentePhrase.split(texte)
	
	#segmentation mots
	for phrase in listePhrases:
		mots = re.compile(r"[\W]+", re.UNICODE)
		listeTokenisee = mots.split(phrase)
		listeTokenisee = enleveurDeVides(listeTokenisee)
		listeTokenOriginale = listeTokenisee
		#POS
		listeTokenisee = posTagger(listeTokenisee)
		for tokenEtPos in listeTokenisee:
			token = tokenEtPos[0]
			pos = tokenEtPos[1]
			try:
				for code, liste in dicoFinalCodesID.iteritems():
					if liste[0]==token and liste[1]==pos:
						listeTokenOriginale[token] = code
			except KeyError:
				code = ajouteurDicoFinalTokenParToken(tokenEtPos)
				listeTokenOriginale[token] = code
			phraseCodee = ' '.join(listeTokenOriginale)
		listePhrases[phrase] = phraseCodee
	texteCode = '. '.join(listePhrases)
	return texteCode

def decrypteur(texteCrypte):
	"""
	la fonction decrypteur associe les tokens codifiés 
	d'un texte à leur représentationn en langage naturel
	"""
	fichierDico = open("dicoFinalCodesID.p", "rb")
	dicoFinalCodesID = pickle.load(fichierDico)
	fichierDico.close()
	
	listePhrasesCodees = '. '.split(texteCrypte)
	for phraseCodee in listePhrasesCodees:
		listeCodes = ' '.split(phraseCodee)
		for code in listeCodes:
			listeCodes[code] = dicoFinalCodesID[code][1]
		phrase = ' '.join(listeCodes)
		listePhrasesCodees[phraseCodee] = phrase
	texte = '. '.join(listePhrasesCodees)
	return texte

#--------------END-FONCTIONS-------------------

#--------------START-DECLARATIONS-------------------

#STOPLIST
#il faudra trouver mieux que many_stop_words car
#nb stopwords en anglais: 894
#mais en francais: 334 et en chinois: 119
if langueDuTexte == 'english':
	listeStopList = many_stop_words.get_stop_words('en')
elif langueDuTexte == 'french':
	listeStopList = many_stop_words.get_stop_words('fr')
elif langueDuTexte == 'chinese':
	listeStopList = many_stop_words.get_stop_words('zh')


#OUVRIR RESSOURCES
listeFichiersRessource = glob.glob('./ressource/*.txt')

#--------------END-DECLARATIONS-------------------

#--------------START-COMMANDES-------------------


for fichierRessource in listeFichiersRessource:
	texteASegmenter = ouvrirFichier('./'+fichierRessource)
	#texteASegmenter = texteASegmenter.encode('utf8')
	#creation des bases de donnees
	#creation des dictionnaires auxiliaires
	dicoTokensPosParPhrase = premierTourTokenContexte(texteASegmenter)
	#creation du dictionnaire final
	dicoFinal = secondTourTokenDico(dicoTokensPosParPhrase)



#--------------END-COMMANDES-------------------

#--------------START-REFERENCES-------------------

###Tuto: 

#--------------END-REFERENCES-------------------