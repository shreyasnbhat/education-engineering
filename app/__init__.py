from flask import Flask
from flask.ext.login import LoginManager
from db.models import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from celery import Celery

# Environment variables for uploads
UPLOAD_FOLDER = '/home/shreyas/Projects/education-engineering/data'
ALLOWED_EXTENSIONS = {'csv', 'pdf'}

# Flask App initialization
app = Flask(__name__)
app.secret_key = 'secret_key'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Celery configuration with Redis
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

# Initialize Celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

# Final Configuration depending upon sample version
engine = create_engine('sqlite:///test.db')
Base.metadata.create_all(engine)
DBSession = sessionmaker(bind=engine)

"""
The login manager contains the code that lets your application and Flask-Login work together, 
such as how to load a user from an ID, where to send users when they need to log in etc.
"""
login_manager = LoginManager(app)
login_manager.init_app(app)

# Login Manager view definition
login_manager.login_view = "getHomePage"


@login_manager.user_loader
def load_user(user_id):
    db_session = DBSession()
    user_from_auth = db_session.query(AuthStore).filter_by(id=str(user_id)).first()
    db_session.close()
    return user_from_auth


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


from app import views
