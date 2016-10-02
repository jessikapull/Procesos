#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Flask, render_template, url_for, request, session, redirect
from flask.ext.pymongo import PyMongo
import bcrypt
import random
from bson.objectid import ObjectId
from pyExcelerator import *
import csv
import subprocess
import sys
import string
import time
import pymongo

app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'mongologinexample'
app.config['MONGO_DBNAME'] = 'pruebas'
app.config["SECRET_KEY"] = "KeepThisS3cr3t"

mongo = PyMongo(app)

@app.route('/')
@app.route('/inicio')
def index():
    if 'username' in session:
        #return 'You are logged in as ' + session['username']
        contratos = mongo.db.scraping
        cursor=contratos.find().skip(random.randrange(contratos.count())).limit(20)
        return render_template('inicio.html',cursor=cursor)

    return render_template('index.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'usuario' : request.form['username']})

        if existing_user is None:
            hashpass = bcrypt.hashpw(request.form['pass'].encode('utf-8'), bcrypt.gensalt())
            users.insert({'Nombre' : request.form['nombre'],'Apellido':request.form['apellido'],'usuario' : request.form['username'], 'password' : hashpass})
            session['username'] = request.form['username']
            return redirect(url_for('index'))

        return render_template('existe.html')

    return render_template('register.html')

def cambioClave():

    return ''.join([random.choice(string.letters + string.digits) for i in range(5)])


@app.route('/recordar', methods=['POST', 'GET'])
def recordar():
    if request.method == 'POST':
        users = mongo.db.users
        existing = users.find_one({'usuario' : request.form['username']})
        usuario=request.form['username'][:]

        if existing:
            clave= cambioClave()
            hashpass = bcrypt.hashpw(clave.encode('utf-8'), bcrypt.gensalt())
            users.update({'usuario' : request.form['username']},{"$set":{'password' : hashpass}})
            subprocess.Popen([sys.executable, "correo.py",clave,usuario])
            return render_template('correoEnviado.html')

        return render_template('invalido.html')

    return render_template('recordar.html')

@app.route('/login', methods=['POST'])
def login():
    users = mongo.db.users
    login_user = users.find_one({'usuario' : request.form['username']})

    if login_user:
        if bcrypt.hashpw(request.form['pass'].encode('utf-8'), login_user['password'].encode('utf-8')) == login_user['password'].encode('utf-8'):
            session['username'] = request.form['username']
            return redirect(url_for('index'))

    return render_template('invalido.html')

@app.route('/filtros')
def filtros():
    contratos = mongo.db.scraping
    proc=int(request.args.get('proceso'))
    cuant=int(request.args.get('cuantia'))
    obj=request.args.get('objeto')
    if(obj==""):
        if(proc==0 & cuant==0):
            print 'no ha seleccionado nada'
        elif(proc!=0 & cuant==0):
            cursor=contratos.find({'Proceso':proc})
        elif(proc==0 & cuant!=0):
            cursor=contratos.find({'num_cuantia':cuant})
        elif(proc!=0 & cuant!=0):
            print('entro hacer la busqueda proceso y cuantia diferentes de 0')
            cursor=contratos.find({"$and":[{'num_cuantia':cuant},{'Proceso':proc}]})
    elif(cuant==0):
        if(proc!=0):
            cursor=contratos.find({"$and":[{'Proceso':proc},{'Objeto':{"$regex":".*obj", "$options":"i"}}]})
        else:
            cursor=contratos.find({"$and":[{'Objeto':{"$regex":".*obj", "$options":"i"}}]})
    elif(proc==0):
        cursor=contratos.find({"$and":[{'num_cuantia':cuant},{'Objeto':{"$regex":".*obj", "$options":"i"}}]})
    else:
        cursor=contratos.find({"$and":[{'num_cuantia':cuant},{'Proceso':proc},{'Objeto':{"$regex":".*obj", "$options":"i"}}]})


    if cursor:
        return render_template("contratos.html",cursor=cursor)

    return 'Los datos no coinciden'

@app.route('/notificaciones')
def notificaciones():
    if 'username' in session:
        #return 'You are logged in as ' + session['username']
        procesos=mongo.db.contratos
        precision=procesos.find_one({"Usuario":session['username'],"fecha":{"$gte": time.strftime("%x")}},{"precision":1,"_id":0})
        if precision:
            precision=float(precision.get("precision"))
            precision=precision*100

        print 'precision',precision
        cursor2 = procesos.find(
            {
                "Usuario": session['username'],
                "fecha": {"$lte": time.strftime("%x")}
            },
            {
                "grupo": 1,
                "Objeto": 1,
                "Entidad": 1,
                "Tipo_proceso": 1,
                "Cuantia": 1,
                "Estado": 1,
                "fecha":1,
                "ppv":1,
                "npv":1,
                "grupo":1
            }
        ).sort('fecha', pymongo.DESCENDING)


        cursor1=procesos.find({"Usuario":session['username'],"fecha":{"$gte": time.strftime("%x")}},{"ppv":1,"npv":1,"grupo":1,"Objeto":1,"Entidad":1,"Tipo_proceso":1,"Cuantia":1,"Estado":1,"fecha":1}).sort('fecha', pymongo.DESCENDING)

        return render_template('notificaciones.html',cursor1=cursor1,cursor2=cursor2,precision=precision)

    return redirect(url_for('index'))

@app.route('/clasificar')
def clasificar():
    procesos=mongo.db.contratos
    cursor=procesos.find({"Usuario":session['username'],"fecha":{"$gte": time.strftime("%x")}},{'_id':0,'Identificador':1, 'clase': 1,'Proceso':1,'num_cuantia':1,'dep_municipio':1,'Usuario':1})
    with open('test.csv', 'w') as outfile:
        fields = ['clase','Proceso','num_cuantia','dep_municipio','Usuario','Identificador']
        writer = csv.DictWriter(outfile, fieldnames=fields)
        writer.writeheader()
        for x in cursor:
            writer.writerow(x)

    print 'entro a ejecutar el script'
    usuario=session['username'][:]
    print 'este es el usuario', usuario
    subprocess.Popen([sys.executable, "randomForest.py",usuario ])
    return render_template('notificaciones.html')


@app.route('/guardar', methods=['POST'])
def guarda():
    if request.method=='POST':
        contratos=request.form.getlist("contratos")
        procesos=mongo.db.contratos
        usuarios=mongo.db.users
        datos=mongo.db.scraping
        existe=usuarios.find_one({'usuario' : session['username']})
        procesoExistente=procesos.find_one({'Usuario' : session['username']})


        if existe:
            for value in contratos:
                procesoExistente=procesos.find_one({'Usuario' : session['username'],"Identificador":value})


                if(procesoExistente):
                    print('ese proceso ya ha sido guardado por el usuario')
                    cursor=datos.find({"_id":ObjectId(value)},{"_id":0,"clase":1})
                    procesos.update({"Identificador":value},{"$set":{'clase':cursor.get("clase")}})
                    procesos.update({"Identificador":value},{"$set":{'fecha':time.strftime("%c")}})
                    
                elif(procesos.find_one({"Identificador":value})):

                    cursor=datos.find({"_id":ObjectId(value)},{"_id":0,"Tipo_proceso":1,"Entidad":1,"Estado":1,"Departamento_municipio":1,"Objeto":1,"Cuantia":1,"Proceso":1,"num_cuantia":1,"clase":1,"dep_municipio":1})
                    procesos.insert(cursor)
                    procesos.update({"fecha":{"$exists":False}},{"$set":{'fecha':time.strftime("%c")}})
                    procesos.update({"Usuario":{"$exists":False}},{"$set":{'Usuario':session['username']}})
                    procesos.update({"Identificador":{"$exists":False}},{"$set":{'Identificador':value}})
                else:
                    cursor=datos.find({"_id":ObjectId(value)},{"_id":0,"Tipo_proceso":1,"Entidad":1,"Estado":1,"Departamento_municipio":1,"Objeto":1,"Cuantia":1,"Proceso":1,"num_cuantia":1,"clase":1,"dep_municipio":1})
                    procesos.insert(cursor)
                    procesos.update({"fecha":{"$exists":False}},{"$set":{'fecha':time.strftime("%c")}})
                    procesos.update({"Identificador":{"$exists":False}},{"$set":{'Identificador':value}})
                    procesos.update({"Usuario":{"$exists":False}},{"$set":{'Usuario':session['username']}})
                print 'usuario',session['username'],'y contrato',value

    return redirect(url_for('clasificar'))

@app.route('/filtrar')
def filtrar():
    if 'username' in session:
        return render_template('filtrar.html')

    return redirect(url_for('index'))



@app.route('/logout')
def logout():
   session.pop('username', None)
   return redirect(url_for('index'))



if __name__ == '__main__':
    app.secret_key = 'mysecret'
    app.run(debug=True)