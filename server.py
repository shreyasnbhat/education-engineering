from flask import Flask,render_template

app = Flask(__name__)

@app.route('/')
def getHomePage():
    return render_template('homepage.html')

@app.route('/scores')
def getScores():
    return "<h1>Scores</h1>"

@app.route('/prediction')
def getPredictions():
    return "<h1>Predictions</h1>"

if __name__ == '__main__':

    app.debug = True
    app.run()
