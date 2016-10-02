#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Imports
import sys
import smtplib

contrase= sys.argv[1]
usuario= sys.argv[2]


to = usuario
gmail_user = 'jessikapull'
gmail_pwd = '*******'
smtpserver = smtplib.SMTP("smtp.gmail.com",587)
smtpserver.ehlo()
smtpserver.starttls()
smtpserver.ehlo
smtpserver.login(gmail_user, gmail_pwd)
header = 'To:' + to + '\n' + 'From: ' + gmail_user + '\n' + 'Subject: Procesos de contratacion, Cambio de Clave \n'
print header
msg = header + '\nSu nueva clave es: \n\n'+contrase
smtpserver.sendmail(gmail_user, to, msg)
print 'Correo enviado!'
smtpserver.close()
