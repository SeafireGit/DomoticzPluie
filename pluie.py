#!/usr/bin/env python3

import requests
import json

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

#### Dictionnaire des états
# Precipitation 1 = niveau 0 et commentaire RAS
dico = {1:(0,"RAS"),2:(1,"Faible"),3:(3,"Modéré"),4:(4,"Fort")}

##################
# Fonctions
##################

def etatSw(id):
    """ Récupère l'état du Dummy switch Pluie sur Domoticz """
    id = str(id)
    urlDomo = domobox+"type=devices&rid="+id
    r = requests.get(urlDomo,verify=False)
    dataDB = r.json()
    for i in dataDB["result"]:
      etat = i["Status"]
    return(etat)

def etatAl(id):
    """ Récupère l'état du Dummy Alert Pluie sur Domoticz """
    id = str(id)
    urlDomo = domobox+"type=devices&rid="+id
    r = requests.get(urlDomo,verify=False)
    dataDB = r.json()
    for i in dataDB["result"]:
      etat = i["Level"]
    return(etat)

def meteoVille(insee):
    """ Récupération des données sur le site de MF """
    url = meteofrance+insee
    r = requests.get(url)
    data = r.json()
    return (data)

def update_switch(etat):
    """ Met à jour le switch. 1=allumé 2=éteint"""
    request.get('{0}type=command&param=switchlight&idx={1}&switchcmd=On&level={2}'.format(domobox,IDX_switch,etat),verify=False)

def update_alerte(alerte):
    """ Met à jour l'alerte, en prenant les niveaux et commentaires dans le dico"""
    requests.get('{0}type=command&param=udevice&idx={1}&nvalue={2}&svalue={3}'.format(domobox,IDX_alerte,dico[alerte][0],dico[alerte][1]), verify=False)

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
  update_switch(1)
elif (alerte == 1) and (switch == "On"):
  update_switch(0)

## Mise à jour de l'alerte avec le niveau exact d'alerte

if (alerte == 1) and ( level != 0):
    update_alerte(1)
elif (alerte == 2) and ( level != 1):
    update_alerte(2)
elif (alerte == 3) and ( level != 3):
    update_alerte(3)
elif (alerte == 4) and ( level != 4):
    update_alerte(4)

