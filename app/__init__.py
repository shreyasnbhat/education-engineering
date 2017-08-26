from flask import Flask
from flask.ext.login import LoginManager

app = Flask(__name__)
app.secret_key = 'secret_key'


'''
The login manager contains the code that lets your application and Flask-Login work together, 
such as how to load a user from an ID, where to send users when they need to log in etc.
'''
login_manager = LoginManager(app)
login_manager.init_app(app)

### Login Manager Config ###
login_manager.login_view = "getHomePage"

from models import session,AuthStore

@login_manager.user_loader
def load_user(user_id):
    return session.query(AuthStore).filter_by(id = str(user_id)).first()

from app import views
