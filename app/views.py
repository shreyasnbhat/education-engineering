from flask import render_template,request,redirect,url_for
from sqlalchemy.orm import exc
from app import app
from sqlalchemy import and_
import json
from models import Student,Course,Score,AuthStore,session
import bcrypt
from flask.ext.login import login_user,login_required,logout_user

@app.route('/',methods=['GET','POST'])
def getHomePage():
    if request.method == 'GET':
        return render_template('homepage.html')
    elif request.method == 'POST':
        userid = request.form['bits-id']
        password = request.form['password'].encode('utf-8')

        try:
            user_credentials = session.query(AuthStore).filter_by(id=userid).one()

            user_credential_salt = user_credentials.salt.encode('utf-8')
            user_credential_phash = user_credentials.phash.encode('utf-8')

            print "-----------------------------------------------------------------------"
            print "--------------------Security Check-------------------------------------"
            print "-----------------------------------------------------------------------"
            print "Password: ",password
            print "Salt: ",user_credential_salt
            print "Phash DB: ",user_credential_phash
            print "Phash gen:",bcrypt.hashpw(password,user_credential_salt)
            print "-----------------------------------------------------------------------"
            print "-----------------------------------------------------------------------"
            print "-----------------------------------------------------------------------"


            if bcrypt.hashpw(password,user_credential_phash) == user_credential_phash:
                login_user(user_credentials)
                return redirect(url_for('getCourses'))
            else:
                error = "Wrong username or Password"
                return render_template('homepage.html',error=error)


        except exc.NoResultFound:
            error = "No such user exists!"
            return render_template('homepage.html',error=error)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('getHomePage'))

@app.route('/courses')
@login_required
def getCourses():
    courses = session.query(Course).all()
    return render_template('courses.html', courses = courses)

@app.route('/courses/<string:course_id>')
@login_required
def getStudentsByCourse(course_id):
    students = session.query(Student).filter(and_(Student.id == Score.student_id,Score.course_id == Course.id,Course.id == course_id)).all()
    return render_template('students.html',students=students,course_id=course_id)

@app.route('/courses/<string:course_id>/<string:student_id>')
@login_required
def getScoresByStudent(course_id,student_id):
    course = session.query(Course).filter_by(id=course_id).one()
    scores = session.query(Score).filter_by(student_id=student_id).all()
    student = session.query(Student).filter_by(id=student_id).one()

    ### For graphing
    scores_num = json.dumps([i.score for i in scores ])
    scores_names = json.dumps([i.name for i in scores])
    return render_template('studentScore.html',scores=scores,course=course,student=student, x_ = scores_names , y_=scores_num)

@app.route('/predictions')
@login_required
def getPredictions():
    return "<h1>Predictions</h1>"
