from flask import Flask
from flask_sqlalchemy import SQLAlchemy
database_config = dict(host='db4free.net',
                       user='asupsku_admin',
                       password='---',
                       database='asupsku_db_main')

app = Flask(__name__)
app.config['SECRET_KEY'] = 't513t513t513t513t513t513t513t513t513t513'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://{}:{}@{}/{}'.format(database_config['user'],
                                                                              database_config['password'],
                                                                              database_config['host'],
                                                                              database_config['database'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
