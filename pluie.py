#!/usr/bin/env python3

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
switch = etatSw(IDX_switch)
level = int(etatAl(IDX_alerte))

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

# print("Alerte finale : ",alerte)


#########
# Envoi des alertes
#########

## Mise à jour du switch

if (alerte > 1) and (switch == "Off"):
  requests.get(domobox+'type=command&param=switchlight&idx='+IDX_switch+'&switchcmd=On&level=1', verify=False)
elif (alerte == 1) and (switch == "On"):
  requests.get(domobox+'type=command&param=switchlight&idx='+IDX_switch+'&switchcmd=Off&level=0', verify=False)

## Mise à jour de l'alerte avec le niveau exact d'alerte

if (alerte == 1) and ( level != 0):
  requests.get(domobox+'type=command&param=udevice&idx='+IDX_alerte+'&nvalue=0&svalue=RAS',verify=False)
elif (alerte == 2) and ( level != 1):
  requests.get(domobox+'type=command&param=udevice&idx='+IDX_alerte+'&nvalue=1&svalue=Faible',verify=False)
elif (alerte == 3) and ( level != 3):
  requests.get(domobox+'type=command&param=udevice&idx='+IDX_alerte+'&nvalue=3&svalue=Modéré',verify=False)
elif (alerte == 4) and ( level != 4):
  requests.get(domobox+'type=command&param=udevice&idx='+IDX_alerte+'&nvalue=4&svalue=Fort',verify=False)


