#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Imports
import smtplib

# pandas
import pandas as pd
import csv
import pymongo
import time
import math


#coneccion con base de datos
con = pymongo.MongoClient()
con.database_names()
db = con.pruebas
coleccion = db.contratos

# numpy, matplotlib, seaborn
import numpy as np

# machine learning
from sklearn.ensemble import RandomForestClassifier

train = pd.read_csv('train.csv',dtype={"dep_municipio": np.float64},)
test= pd.read_csv('test.csv',dtype={"dep_municipio": np.float64},)

cols = ['Proceso','num_cuantia','dep_municipio']
colsRes = ['clase']
trainArr = train.as_matrix(cols)    # training array
trainRes = train.as_matrix(colsRes) # training results

## Training!

rf = RandomForestClassifier(n_estimators=100)    # 100 decision trees is a good enough number
rf.fit(trainArr, trainRes.ravel())# ajuste del modelo
# verificando la precisión
print("precisión del modelo: {0: .2f}".format((trainRes.ravel() == rf.predict(trainArr)).mean()))
precision=("{0: .2f}".format((trainRes.ravel() == rf.predict(trainArr)).mean()))
print precision

testArr = test.as_matrix(cols)
results = rf.predict(testArr)

submission = pd.DataFrame({
        "prediccion": results,
        "Identificador":test["Identificador"],
        "clase": test["clase"],
        "Proceso": test["Proceso"],
        "num_cuantia":test["num_cuantia"],
        "dep_municipio":test["dep_municipio"]

    })
submission.to_csv('predicciones.csv', index=False)

def loadCsv(filename):
    lines = csv.reader(open(filename, "rb"))
    dataset_train = list(lines)
    for i in range(len(dataset_train)):
        if i == 0:
            dataset_train[i] = [0, 0, 0, 0, 0, 0]
        else:
            coleccion.update({"Identificador":dataset_train[i][0]},{"$set":{"clasificacion":dataset_train[i][5]}})
            coleccion.update({"Identificador":dataset_train[i][0]},{"$set":{"fecha":time.strftime("%c")}})
            dataset_train[i] = [float(x) for x in dataset_train[i][1:6]]
    coleccion.update_many({"clasificacion":"0"},{"$set":{"grupo":"RECOMENDABLE"}})
    coleccion.update_many({"clasificacion":"1"},{"$set":{"grupo":"NO RECOMENDABLE"}})
    return dataset_train


filename='predicciones.csv'

data_train=loadCsv(filename)


fn=0
fp=0
tn=0
tp=0
ppv=0
npv=0
mmc=0
sensibilidad=0
especificidad=0
aciertos=0
correct = 0
uno=1
cero=0
for i in range(len(data_train)):
    if data_train[i][1] == data_train[i][4]:
        correct += 1
        if data_train[i][1] == uno:
            tn+=1
        if data_train[i][1] == cero:
            tp+=1
    else:
        if (int(data_train[i][1]) == cero):
            if (int(data_train[i][4])== uno):
                fn+=1
        if (int(data_train[i][1]) == uno):
            if (int(data_train[i][4])== cero):
                fp+=1


total=0
falsos=0
falsosP=0
total=len(data_train)
print ("total:"),len(data_train)
print("correctos:"),correct
falsos=total-correct
falsosP=fn+fp

if(falsosP>falsos):
    fp=fp-1

accuracy= (correct/float(len(data_train))) * 100.0
print ("porcentaje de aciertos:{0: .1f}%".format(accuracy))
print("falsos negativos:"),fn
print("falsos positivos:"),fp
print("verdaderos negativos:"),tn
print("verdaderos positivos:"),tp


if(tn!=0 & tp!=0):
    mmc= float (tp*tn-fp*fn)/(math.sqrt((tp+fp)*(tp+fn)*(tn+fp)*(tn+fn)))
    sensibilidad=float(tp)/(fn+tp)
    especificidad=float(tn)/(fp+tn)
if(tn!=0):
    npv= (float(tn)/(tn+fn))*100
if(tp!=0):
    ppv=(float(tp)/(tp+fp))*100


aciertos=float (tp+tn)/(tp+fp+fn+tn)


coleccion.update_many({"fecha":{"$gte": time.strftime("%x")}},{"$set":{"precision":precision}})
coleccion.update_many({"fecha":{"$gte": time.strftime("%x")},"clasificacion":"0"},{"$set":{"npv":npv}})
coleccion.update_many({"fecha":{"$gte": time.strftime("%x")},"clasificacion":"1"},{"$set":{"ppv":ppv}})
coleccion.update_many({"fecha":{"$gte": time.strftime("%x")},"clasificacion":"0"},{"$set":{"ppv":ppv}})
coleccion.update_many({"fecha":{"$gte": time.strftime("%x")},"clasificacion":"1"},{"$set":{"npv":npv}})

print("sensibilidad:"),sensibilidad
print("especificidad:"),especificidad
print("aciertos:"),aciertos
print("precision:"),precision
print("prediccion de valor negativo:"),npv
print("prediccion de valor positivo:"),ppv
print("coeficiente de correlacion de Matthews:"),mmc


usuarios=[]
for testy in coleccion.find().distinct('Usuario'):
    print(testy)
    usuarios.append(testy)
    to = testy
    gmail_user = 'jessikapull'
    gmail_pwd = '*******'
    smtpserver = smtplib.SMTP("smtp.gmail.com",587)
    smtpserver.ehlo()
    smtpserver.starttls()
    smtpserver.ehlo
    smtpserver.login(gmail_user, gmail_pwd)
    header = 'To:' + to + '\n' + 'From: ' + gmail_user + '\n' + 'Subject: Procesos de contratacion \n'
    print header
    msg = header + '\nPor favor revisar la seccion de Preferencias de la pagina de procesos de contratacion \n\n'
    smtpserver.sendmail(gmail_user, to, msg)
    print 'Correo enviado!'
    smtpserver.close()




