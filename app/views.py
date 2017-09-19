from flask import render_template, request, redirect, url_for
from flask.globals import session
from sqlalchemy.orm import exc
from app import app
from sqlalchemy import and_
import json
from models import Student, Course, Score, AuthStore, session as dbSession
import bcrypt
from flask.ext.login import login_user, login_required, logout_user

'''Logging utility for all views'''
def logger(**kwargs):
    print "-----------------------------------------------------------------------"
    print "----------------------------Logger-------------------------------------"
    print "-----------------------------------------------------------------------"
    for key in kwargs:
        print key + str(':'), kwargs[key]
    print "-----------------------------------------------------------------------"
    print "-----------------------------------------------------------------------"
    print "-----------------------------------------------------------------------"


@app.route('/', methods=['GET', 'POST'])
def getHomePage():
    if request.method == 'GET':
        return render_template('homepage.html')
    elif request.method == 'POST':
        userid = request.form['bits-id']
        password = request.form['password'].encode('utf-8')

        try:
            user_credentials = dbSession.query(AuthStore).filter_by(id=userid).one()

            user_credential_salt = user_credentials.salt.encode('utf-8')
            user_credential_phash = user_credentials.phash.encode('utf-8')

            logger(Password=password,
                   Salt=user_credential_salt,
                   Phash_DB=user_credential_phash,
                   Phash_gen=bcrypt.hashpw(password, user_credential_salt))

            if bcrypt.hashpw(password, user_credential_phash) == user_credential_phash:
                login_user(user_credentials)
                session['userid'] = user_credentials.id
                return redirect(url_for('getCourses'))
            else:
                error = "Wrong username or Password"
                return render_template('homepage.html', error=error)


        except exc.NoResultFound:
            error = "No such user exists!"
            return render_template('homepage.html', error=error)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('getHomePage'))


@app.route('/courses')
@login_required
def getCourses():
    try:
        logger(User_id=session['userid'])

        course_ids = dbSession.query(Score.course_id).filter_by(student_id=session['user_id']).distinct()
        courses = dbSession.query(Course).filter(Course.id.in_(course_ids)).all()

        return render_template('courses.html',
                               courses=courses,
                               user_id=session['userid'])
    except exc.NoResultFound:
        return render_template('courses.html')


#### Need this for admin only
@app.route('/courses/<string:course_id>')
@login_required
def getStudentsByCourse(course_id):
    students = dbSession.query(Student).filter(
        and_(Student.id == Score.student_id, Score.course_id == Course.id, Course.id == course_id)).all()
    return render_template('students.html',
                           students=students,
                           course_id=course_id)


@app.route('/courses/<string:course_id>/<string:student_id>')
@login_required
def getScoresByStudent(course_id, student_id):
    course = dbSession.query(Course).filter_by(id=course_id).one()
    scores = dbSession.query(Score).filter_by(student_id=student_id).all()
    student = dbSession.query(Student).filter_by(id=student_id).one()

    ### For graphing need to pass the objects in JSON so that they are parsed in Javascript
    scores_num = json.dumps([i.score for i in scores])
    scores_names = json.dumps([i.name for i in scores])
    return render_template('studentScore.html',
                           scores=scores,
                           course=course,
                           student=student,
                           x_=scores_names,
                           y_=scores_num)


@app.route('/predictions')
@login_required
def getPredictions():
    return "<h1>Predictions</h1>"
