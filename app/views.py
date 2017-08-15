from flask import render_template

from app import app


@app.route('/')
def getHomePage():
    return render_template('homepage.html')


@app.route('/scores')
def getScores():
    return "<h1>Scores</h1>"


@app.route('/prediction')
def getPredictions():
    return "<h1>Predictions</h1>"
