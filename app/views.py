from flask import render_template, request, redirect, url_for, abort, flash
from flask.globals import session as session_obj
from flask.ext.login import login_user, login_required, logout_user
from sqlalchemy.orm import exc
from sqlalchemy import and_
import json
import os
import time
from app import *
import bcrypt
from logger import logger
from db.samplev2 import generate_sample_db
from werkzeug.utils import secure_filename


@app.route('/', methods=['GET', 'POST'])
def getHomePage():
    if request.method == 'GET':
        return render_template('homepage.html')

    elif request.method == 'POST':

        db_session = DBSession()

        userid = request.form['bits-id'].encode('utf-8')
        password = request.form['password'].encode('utf-8')

        try:
            user_credentials = db_session.query(AuthStore).filter_by(id=userid).one()
            user_credential_salt = user_credentials.salt.encode('utf-8')
            user_credential_phash = user_credentials.phash.encode('utf-8')

            logger(Password=password,
                   Salt=user_credential_salt,
                   Phash_DB=user_credential_phash,
                   Phash_gen=bcrypt.hashpw(password, user_credential_salt))

            if bcrypt.hashpw(password, user_credential_phash) == user_credential_phash:
                login_user(user_credentials)
                session_obj['userid'] = user_credentials.id.encode('utf-8')
                return redirect(url_for('getCourses'))
            else:
                error = "Wrong username or Password"
                return render_template('homepage.html', error=error)

        except exc.NoResultFound:
            error = "No such user exists!"
            return render_template('homepage.html', error=error)

        finally:
            db_session.close()


@login_required
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('getHomePage'))


@celery.task
def upload_async(upload_file_filename_secure):
    """
    Celery task to upload files and populate database asynchronously
    :param upload_file_filename_secure: Secure file name to load filename
    :return:
    """
    with app.app_context():
        print "Started"
        db_session = DBSession()

        path = os.path.join(app.config['UPLOAD_FOLDER'], upload_file_filename_secure)
        course_id, course_name_unformatted, semester, year = upload_file_filename_secure.split('_')
        course_name = " ".join(course_name_unformatted.split('.'))
        print "The path is: " + path

        while not os.path.exists(path):
            print "Waiting for file to be visible"
            time.sleep(1)

        if os.path.isfile(path):
            print "Now the file is available"
            generate_sample_db(path,
                               course_id,
                               course_name,
                               db_session)
        else:
            raise ValueError("%s isn't a file!" % path)

        db_session.close()
        print "Finished"


@login_required
@app.route('/upload', methods=['GET', 'POST'])
def upload():


    if request.method == 'GET':
        if session_obj['userid'] == 'admin':
            return render_template('upload.html')
        else:
            return redirect(url_for('getHomePage'))

    elif request.method == 'POST':
        if session_obj['userid'] == 'admin':
            if 'file' not in request.files:
                logger(request=request)
                print "No file was sent"

            upload_file = request.files['file']

            if upload_file.filename == '':
                error = "File wasn't selected!"
                print "File wasn't selected"
                return render_template('upload.html', error=error)

            elif upload_file and allowed_file(upload_file.filename):
                upload_file_filename_secure = secure_filename(upload_file.filename)
                upload_file.save(os.path.join(app.config['UPLOAD_FOLDER'], upload_file_filename_secure))
                print "Uploaded file successfully"
                flash('Upload Successfull!')

                upload_async.delay(upload_file_filename_secure)

                return redirect(url_for('upload'))

            error = "Incorrect file format was chosen!"
            return render_template('upload.html', error=error)

        else:
            print request.path
            abort(400)


@app.route('/courses')
@login_required
def getCourses():
    db_session = DBSession()

    try:
        logger(User_id=session_obj['userid'])

        # If session is not created by an admin user then load student courses else load all courses
        if session_obj['userid'] != 'admin':

            course_ids = db_session.query(Score.course_id).filter_by(student_id=session_obj['user_id']).distinct()
            courses = db_session.query(Course).filter(Course.id.in_(course_ids)).all()

            return render_template('courses.html',
                                   courses=courses,
                                   user_id=session_obj['userid'],
                                   admin=False)
        else:
            courses = db_session.query(Course).all()

            return render_template('courses.html',
                                   courses=courses,
                                   user_id=session_obj['userid'],
                                   admin=True)

    except exc.NoResultFound:
        return render_template('courses.html')

    finally:
        db_session.close()


# Need this for admin only
@app.route('/courses/<string:course_id>')
@login_required
def getStudentsByCourse(course_id):
    if session_obj['userid'] == 'admin':
        db_session = DBSession()

        students = db_session.query(Student).filter(
            and_(Student.id == Score.student_id, Score.course_id == Course.id, Course.id == course_id)).all()

        db_session.close()

        return render_template('students.html',
                               students=students,
                               course_id=course_id)
    else:
        # If not a admin raise a 404 Not Found
        abort(404)
        return redirect(url_for('getCourses'))


@app.route('/courses/<string:course_id>/<string:student_id>')
@login_required
def getScoresByStudent(course_id, student_id):
    db_session = DBSession()

    course = db_session.query(Course).filter_by(id=course_id).one()
    scores = db_session.query(Score).filter_by(student_id=student_id,course_id=course_id).all()
    student = db_session.query(Student).filter_by(id=student_id).one()

    db_session.close()

    # For graphing need to pass the objects in JSON so that they are parsed in Javascript
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
