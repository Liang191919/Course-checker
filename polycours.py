import requests

def parse(text, left_delim, right_delim):
    start = text.find(left_delim)
    end = text.find(right_delim, start)
    if start != -1 and end != -1:
        return text[start + len(left_delim):end]
    return None

def getSessionId(user, password, birth):
    login_url = 'https://dossieretudiant.polymtl.ca/WebEtudiant7/ValidationServlet'
    login_headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    data = f'code={user}&nip={password}&naissance={birth}'
    response = requests.post(login_url, headers=login_headers, data=data, allow_redirects=False)
    if response.cookies.__contains__('JSESSIONID'):
        print(response.headers['set-cookie'][:44])
        return response.headers['set-cookie'][:44]
    else:
        raise Exception('Mauvais utilisateur, mot de passe ou annee de naissance')

def sendApiNotice(cours, nbPlaces, api_url, c_datetime):
    if (api_url == ""):
        return
    coursdispo_headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
        'pragma': 'no-cache',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.8',
    }
    if(cours[9] == "T"):
        data = f'CONTENT &text=Le cours {cours[0:7]} groupe {cours[8:9]} section Théorie a {nbPlaces} place disponible. {c_datetime}'
    else:
        data = f'CONTENT &text=Le cours {cours[0:7]} groupe {cours[8:9]} section Labo a {nbPlaces} place disponible. {c_datetime}'
    response = requests.post(api_url, headers=coursdispo_headers, data=data )

def find_class(sessionToken):
    coursdispo_url = "https://dossieretudiant.polymtl.ca/WebEtudiant7/ChoixCoursServlet"

    cookie = f"{sessionToken} _ga=GA1.1.253545233.1703907429; __gsas=ID=256d9d049bcfcbc8:T=1723211511:RT=1723211511:S=ALNI_MYcvr4AiSJR74-_n15lgxjvs4QtRw; _hjSessionUser_4333=eyJpZCI6IjdhOTVjNzVlLTcyZTgtNWVmOC05OWI3LWY5OTUxOTI2YjE5ZCIsImNyZWF0ZWQiOjE3MjkzOTA5NzQxMjUsImV4aXN0aW5nIjp0cnVlfQ==; SERVERID=de-1-2022; _ga_4693C2BZE0=GS1.1.1732256167.5.1.1732256420.0.0.0; _gcl_au=1.1.1942866019.1733285221; _ga_59DLH8GF4Z=GS1.1.1733906748.10.0.1733906755.0.0.0; cookie-agreed=2; _ga_E7F431GGN8=GS1.1.1733954475.42.1.1733955318.60.0.0; _ga_VNNZF6GB5Z=GS1.1.1734132302.580.1.1734132319.0.0.0"

    coursdispo_headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 OPR/114.0.0.0',
        'pragma': 'no-cache',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.8',
        'Cookie' : cookie,
        'referer' : 'https://dossieretudiant.polymtl.ca/WebEtudiant7/ValidationServlet',
    }
    data = 'selProgInscrit=01&selProgBulletinCumulatif=01&selProgHorPers=01&selTrimHorPers=20251&numDossierHoraire=01&trimHoraire=20251&selProgModif=01&selProgAttestation=&selTrimestreAttestation=&stProgRensPers=&stProgResAcad=&stProgHorPers=&stTrimHorPers=&stProgPropo=&stProgModif=&stProgStage=&stProgPlan=&token=&matricule=2290577&choixProgramme=&dateDebutTrimestre=&choixProgrammeDates=&codeDossier=01&dateFinTrimestre=+&trimestreActuel=+&choixTrimestre=+&messagePasOK=+&trimestreModif=20251&trimestreProp=20251&anneeCollation=&codeProgrammesBulletin=01&codeProgrammesNotes=&codeProgrammesHoraire=01&codeProgrammeInsc=1&trimestre=20251&codeProgrammesProposition=&codeProgrammesPlan=&codeProgrammesModification=01&nbreDoss=1&nbreDossES=0&nbreDossStage=&nbreDossActif=1&nbreTrim=5&trimestreAttestation=&dateRelAnt=Choisir&trimestreInscription=20251&codeStatutActuel=NINS&chaineTrimInsc=hiver+2025&chaineTrimModifChoixCours=hiver+2025&nbInscRecherche=0&selectionMandat=+&selectionMandat1=+&selectionMandat2=+&selectionMandat3=+&selectionMandat4=+&selectionMandat5=+&selectionMandat6=+&selectionMandat7=+&selectionMandat8=+&selectionMandat9=+&selectionMandat10=+&messagePopup=&conflits10=&conflits11=&conflits12=&conflits13=&conflits14=&conflits15=&conflits16=&conflits17=&conflits18=&conflits19=&conflits20=&conflits21=&conflits22=&conflits23=&conflits24=&conflits25=&conflits26=&conflits27=&conflits28=&conflits29=&conflits30=&conflits31=&conflits32=&conflits33=&conflits34=&conflits35=&conflits36=&conflits37=&conflits38=&conflits39=&conflits40=&conflits41=&conflits42=&conflits43=&conflits44=&conflits45=&conflits46=&conflits47=&conflits48=&conflits49=&conflits50=&conflits51=&conflits52=&conflits53=&conflits54=&conflits55=&conflits56=&conflits57=&conflits58=&conflits59=&conflits60=&conflits61=&conflits62=&conflits63=&conflits64=&conflits65=&conflits66=&conflits67=&conflits68=&conflits69=&conflits70=&conflits71=&conflits72=&conflits73=&conflits74=&conflits75=&conflits76=&conflits77=&conflits78=&conflits79=&conflits80=&conflits81=&conflits82=&conflits83=&conflits84=&conflits85=&conflits86=&conflits87=&conflits88=&conflits89=&conflits90=&conflits91=&conflits92=&conflits93=&conflits94=&conflits95=&conflits96=&conflits97=&conflits98=&conflits99=&conflits00=&conflits01=&conflits02=&conflits03=&conflits04=&conflits05=&conflits06=&conflits07=&conflits08=&conflits09='
    response = requests.post(coursdispo_url, headers=coursdispo_headers, data = data)
    classe = requests.get(coursdispo_url, headers=coursdispo_headers).text
    return classe

def getNbPlaceDisponible(classes, cours):
    return int(parse(classes, f'{cours}"]="', ' ";')[0:3])
