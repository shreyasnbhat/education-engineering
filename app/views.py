from flask import render_template
from sqlalchemy.orm import sessionmaker
from app import app
from models import Student,engine

'''Final Configuration'''
DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
def getHomePage():
    return render_template('homepage.html')


@app.route('/users')
def getScores():
    #Get all user here and display
    users = session.query(Student).all()
    return render_template('users.html', users = users)

@app.route('/predictions')
def getPredictions():
    return "<h1>Predictions</h1>"
