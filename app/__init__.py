from flask import Flask
from flask.ext.login import LoginManager
from db.models import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)
app.secret_key = 'secret_key'

"""Final Configuration depending upon sample version"""
engine = create_engine('sqlite:///sampleV2.db')
Base.metadata.create_all(engine)
DBSession = sessionmaker(bind=engine)
db_session = DBSession()

'''
The login manager contains the code that lets your application and Flask-Login work together, 
such as how to load a user from an ID, where to send users when they need to log in etc.
'''
login_manager = LoginManager(app)
login_manager.init_app(app)

# Login Manager Config
login_manager.login_view = "getHomePage"

@login_manager.user_loader
def load_user(user_id):
    var = db_session.query(AuthStore).filter_by(id = str(user_id)).first()
    return var

from app import views
