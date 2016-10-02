#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pyquery import PyQuery as pq
from pyExcelerator import *
import pymongo

con = pymongo.MongoClient()
con.database_names()
db = con.pruebas
coleccion = db.scraping

diccionario = dict()
keys = ['Indicador', 'Num_proceso', 'Tipo_proceso', 'Estado', 'Entidad',
'Objeto', 'Departamento_municipio', 'Cuantia', 'Fecha']
aux = ""
aux1 = 0
urls=[]

archivo = open('direcciones.txt', 'r')
for line in archivo:
    urls.append(line)


cont2 = 0
coleccion.drop()

for line in urls:
    tablas = pq(urls[cont2])(".tablaslistOdd, .tablaslistEven")
    cont2 = cont2 + 1
    for x in tablas:
        if aux1 < 9:
            aux = pq(x).text()
            if aux1 == 7:
                aux = aux.replace('$', '').replace(',', '')
                aux = int(aux)
            diccionario[keys[aux1]] = aux
            if aux1 == 8:
                coleccion.insert(diccionario)
                diccionario = dict()
            aux1 = aux1 + 1
        else:
            aux1 = 1
            aux = ""

coleccion.remove({"Estado": "Celebrado"})
coleccion.remove({"Estado": "Adjudicado"})
coleccion.remove({"Estado": "Liquidado"})
coleccion.remove({"Estado": "Descartado"})
coleccion.remove({"Tipo_proceso": "Lista Multiusos"})
coleccion.remove({"Cuantia":0})
coleccion.remove({"Cuantia":{"$exists":False}})

procesos = list(enumerate(coleccion.aggregate([{'$group': {'_id': "$Tipo_proceso"}}]), start=1))
for num, proce in procesos:
    coleccion.update_many({'Tipo_proceso': proce['_id']}, {'$set': {'Proceso': num}})

coleccion.update_many({"Cuantia":{"$gte":0,"$lte":50000000}},{"$set":{"num_cuantia":1}})
coleccion.update_many({"Cuantia":{"$gte":50000001,"$lte":200000000}},{"$set":{"num_cuantia":2}})
coleccion.update_many({"Cuantia":{"$gte":200000001,"$lte":500000000}},{"$set":{"num_cuantia":3}})
coleccion.update_many({"Cuantia":{"$gte":500000001,"$lte":2000000000}},{"$set":{"num_cuantia":4}})
coleccion.update_many({"Cuantia":{"$gte":2000000001}},{"$set":{"num_cuantia":5}})

#se le agrega una columna de clasificacion
coleccion.update_many({"Estado":"Finalizado el plazo para manifestaciones de interés"},{"$set": {"clase":1}})
coleccion.update_many({"Estado":"Terminado sin Liquidar"},{"$set": {"clase":1}})
coleccion.update_many({"Estado":"Terminado Anormalmente después de Convocado"},{"$set": {"clase":1}})
coleccion.update_many({"clase": {"$exists":False}},{"$set": {"clase":0}})
coleccion.update_many({"$or":[{"Indicador": {"$exists":True}},{"Indicador": {"$exists":False}}]},{"$unset": {"Indicador":""}})
coleccion.remove({"Proceso":0})


listado = list(enumerate(coleccion.aggregate([{'$group': {'_id': "$Departamento_municipio"}}]), start=1))
for numero, municipio in listado:
    coleccion.update_many({'Departamento_municipio': municipio['_id']}, {'$set': {'dep_municipio': numero}})

