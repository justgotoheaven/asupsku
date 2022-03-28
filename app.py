from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

database_config = dict(host='192.168.16.2',
                       user='root',
                       password='t513t5130',
                       database='pkz')

app = Flask(__name__)
app.config['SECRET_KEY'] = 't513t513t513t513t513t513t513t513t513t513'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://{}:{}@{}/{}'.format(database_config['user'],
                                                                              database_config['password'],
                                                                              database_config['host'],
                                                                              database_config['database'])

# Database migration
db = SQLAlchemy(app)
migrate = Migrate(app, db)