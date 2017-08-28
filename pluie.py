import requests,json

###################
# Variables
###################

#### Meteo France 

# Site de Meteofrance, "va-t-il pleuvoir dans l'heure"
meteofrance = "http://www.meteofrance.com/mf3-rpc-portlet/rest/pluie/"

# Code INSEE de la ville à surveiller, avec un 0 en plus à la fin
ville = "593920"


#### Domobox

domobox = "https://domobox.maison.lan/json.htm?"
IDX_switch = "34"
IDX_alerte = "33"

##################
# Fonctions
##################

### Récupération de l'état du switch de pluie

def etatSw(id):
  id = str(id)
  urlDomo = domobox+"type=devices&rid="+id
  r = requests.get(urlDomo,verify=False)
  dataDB = r.json()
  for i in dataDB["result"]:
    etat = i["Status"]
  return(etat)

### Récupération de l'état d'alerte actuel
def etatAl(id):
  id = str(id)
  urlDomo = domobox+"type=devices&rid="+id
  r = requests.get(urlDomo,verify=False)
  dataDB = r.json()
  for i in dataDB["result"]:
    etat = i["Level"]
  return(etat)


### Récuperation des infos de MF au format JSON


def meteoVille(insee):
  url = meteofrance+insee
  r = requests.get(url)
  data = r.json()
  return (data)


#### Etat Domobox

# On récupère l'état actuel de l'interrupteur (une fois pour toute plutot qu'a chaque appel de fonction)
etat = etatSw(IDX_switch)

########
# Process des données récupérées
########

# On initialise l'alerte à 1 par defaut
alerte = int(1)
print("Initial alerte ",alerte)

dataMF = meteoVille(ville)

# On va regarder dans les resultats le niveau d'alerte par tranche horaire et stocker la plus grosse alerte
for i in dataMF['dataCadran']:
  print("Niveau de pluie : ",i['niveauPluie'])
  if (i['niveauPluie'] != 1) and (i['niveauPluie'] > alerte):
    alerte = i['niveauPluie']

# print("Alerte finale : ",alerte,type(alerte))


#########
# Envoi des alertes
#########

# On met à jour le device Alerte avec le niveau exact d'alerte
# On met également à jour le switch alerte pluie (qui enverra les notifications)



if (alerte == 1) and ( etat == "On") :
  requests.get('https://domobox.maison.lan/json.htm?type=command&param=udevice&idx=33&nvalue=0&svalue=RAS',verify=False)
  requests.get('https://domobox.maison.lan/json.htm?type=command&param=switchlight&idx=34&switchcmd=Off&level=0', verify=False)
  print("Envoi 0")

elif (alerte == 2) and ( etat == "Off") :
  requests.get('https://domobox.maison.lan/json.htm?type=command&param=udevice&idx=33&nvalue=1&svalue=Faible',verify=False)
  requests.get('https://domobox.maison.lan/json.htm?type=command&param=switchlight&idx=34&switchcmd=On&level=1', verify=False)
  print("Envoi 1")
elif (alerte == 3) and ( etat == "Off") :
  requests.get('https://domobox.maison.lan/json.htm?type=command&param=udevice&idx=33&nvalue=3&svalue=Modéré',verify=False)
  requests.get('https://domobox.maison.lan/json.htm?type=command&param=switchlight&idx=34&switchcmd=On&level=1', verify=False)
  print("Envoi 3")
elif (alerte == 4) and ( etat == "Off") :
  requests.get('https://domobox.maison.lan/json.htm?type=command&param=udevice&idx=33&nvalue=4&svalue=Fort',verify=False)
  requests.get('https://domobox.maison.lan/json.htm?type=command&param=switchlight&idx=34&switchcmd=On&level=1', verify=False)
  print("Envoi 4")

