from flask import Flask, render_template, url_for, redirect, request ,session,flash
from flask_mysqldb import MySQL
import mysql.connector
from passlib.hash import sha256_crypt
from functools import wraps # extra 
import threading
import time

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'tmc'
app.config['SECRET_KEY'] = '5rfkgxeui56465edtyfyugkgyfyry'


mysql = MySQL(app)


    
ctime = time.time()
cur = mysql.connection.cursor()
cur.execute("SELECT time AND ticket FROM advance ")
time = cur.fetchall()
cur.close()
for x in time:
            print(time)
