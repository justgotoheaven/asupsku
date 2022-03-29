import models
from app import db, app
from flask_migrate import Migrate

migrate = Migrate(app, db)

