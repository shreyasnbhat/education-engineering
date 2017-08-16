from flask import render_template
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app import app
from db_models import Base, Student,engine

'''Final Configuration'''
DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
def getHomePage():
    return render_template('homepage.html')


@app.route('/users')
def getScores():
    users = session.query(Student).all()
    print users
    return render_template('users.html', users = users)


@app.route('/predictions')
def getPredictions():
    return "<h1>Predictions</h1>"
