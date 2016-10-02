#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pymongo
import csv
import subprocess
import sys
import time

con = pymongo.MongoClient()
con.database_names()
db = con.pruebas
coleccion = db.contratos

usuarios=[]


for testy in coleccion.find().distinct('Usuario'):
    print(testy)
    usuarios.append(testy)

cont=0

for j in usuarios:
    cursor = coleccion.find_one({"Usuario": j}, {"Proceso": 1, "num_cuantia": 1, "_id": 0})
    cursor2 =db.scraping.find({"Proceso":cursor.get("Proceso"),"num_cuantia":
        cursor.get("num_cuantia")},{"_id":0,"Tipo_proceso":1,"Entidad":1,"Estado":1,
        "Departamento_municipio":1,"Objeto":1, "Cuantia":1,"Proceso":1,"num_cuantia":1,
        "clase":1,"dep_municipio":1}).limit(12)
    coleccion.insert(cursor2)
    coleccion.update_many({"Usuario": {"$exists": False}}, {"$set": {'Usuario': j}})
    coleccion.update_many({"fecha": {"$exists": False}}, {"$set": {'fecha': time.strftime("%c")}})
    cursor21=db.scraping.find({"Proceso":cursor.get("Proceso"),"num_cuantia":cursor.get("num_cuantia")},{"_id":1}).limit(12)
    for x in cursor21:
        coleccion.update({"Usuario":j,"Identificador":{"$exists":False}},{"$set":{"Identificador":str(x.get("_id"))}})
        print (str(x.get("_id")))

cursor3 = coleccion.find({'fecha': time.strftime("%c")},{'Identificador':1,'_id':0, 'clase': 1,'Proceso':1,'num_cuantia':1,'dep_municipio':1,'Usuario':1})
with open('test.csv', 'w') as outfile:
    fields = ['clase','Proceso','num_cuantia','dep_municipio','Usuario','Identificador']
    writer = csv.DictWriter(outfile, fieldnames=fields)
    writer.writeheader()
    for x in cursor3:
        writer.writerow(x)
theproc = subprocess.Popen([sys.executable, "randomForest.py" ])
