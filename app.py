from flask import Flask
from flask_mysqldb import MySQL

app = Flask(__name__)
# app.config.from_pyfile('config.py')
# init MYSQL
app.config['SECRET_KEY']="jasbdi3i5h452345!#!afasd"
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'flaskdb'
mysql = MySQL(app)
from views import *

if __name__ == '__main__':
	app.run()
