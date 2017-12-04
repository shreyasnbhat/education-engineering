from flask import render_template, request, redirect, url_for, abort, flash, session, g, send_from_directory
from flask.globals import session as session_obj
from flask.ext.login import login_user, login_required, logout_user, current_user
from sqlalchemy.orm import exc
from sqlalchemy import and_
import json, os, time, smtplib, bcrypt, hashlib
from collections import OrderedDict
from app import *
from random import choice
from string import ascii_uppercase
from logger import logger
from db.samplev2 import generate_sample_db
from werkzeug.utils import secure_filename
from grader.grader import get_predicted_grade, genGrade


# General Function
def process_student_data(db_session, course_id, student_id):
    course = db_session.query(Course). \
        filter_by(id=course_id).one()

    scores = db_session.query(Score). \
        filter(Score.student_id == student_id). \
        filter(Score.course_id == course_id). \
        filter(Score.course_id == MaxScore.course_id). \
        filter(Score.name == MaxScore.name). \
        order_by(MaxScore.priority.asc()).all()

    max_scores = db_session.query(MaxScore). \
        filter_by(course_id=course_id). \
        order_by(MaxScore.priority.asc()).all()

    student = db_session.query(Student). \
        filter_by(id=student_id).one()

    course_total = db_session.query(MaxScore.maxscore).filter_by(course_id=course_id,
                                                                 name='Total').one()[0]

    average_query_unsorted = db_session.query(Score.name, func.avg(Score.score).label('Sums')). \
        filter_by(course_id=course_id). \
        group_by(Score.name). \
        subquery()

    average_query_sorted = db_session.query(average_query_unsorted.c.name,
                                            average_query_unsorted.c.Sums.label('average')). \
        filter(average_query_unsorted.c.name == MaxScore.name). \
        filter(MaxScore.course_id == course_id). \
        order_by(MaxScore.priority.asc()). \
        all()

    course_averages = OrderedDict(average_query_sorted)

    # Course Average Pre processing
    for key in course_averages:
        course_averages[key] = round(course_averages[key], 2)

    # Get Mid Term Average and Final Average
    try:
        course_final_average = course_averages['Total']
    except KeyError:
        course_final_average = 'Average Pending'
    try:
        course_mid_term_average = course_averages['Mid Term Total']
    except KeyError:
        course_mid_term_average = 'Average Pending'

    logger(course_mid_term_average=course_mid_term_average,
           course_final_average=course_final_average)

    # Scores with Total in their score name are stripped
    scores_actual_json = json.dumps(
        [scores[i].score for i in range(len(scores)) if 'tal' not in str(scores[i].name).lower()])
    scores_percentages = json.dumps(
        [round(float(scores[i].score) * 100 / float(max_scores[i].maxscore), 2) for i in range(len(scores))
         if 'tal' not in str(scores[i].name).lower()])
    scores_names = json.dumps([i.name for i in scores if 'tal' not in str(i.name).lower()])
    scores_distribution_percentages = json.dumps([i.maxscore for i in max_scores if 'tal' not in str(i.name).lower()])
    course_averages_for_plot = json.dumps(course_averages)

    return scores, \
           course, \
           scores_distribution_percentages, \
           course_total, \
           student, \
           scores_names, \
           scores_percentages, \
           scores_actual_json, \
           course_averages, \
           course_averages_for_plot, \
           course_mid_term_average, \
           course_final_average


def get_grading(db_session, course_id):
    maxscore_by_subject = db_session.query(MaxScore).filter_by(course_id=course_id).all()

    score_names = [i.name for i in maxscore_by_subject]
    name = score_names[-1]

    maximum_scores_unsorted = db_session.query(Score.name, func.max(Score.score).label('Maxs')). \
        filter_by(course_id=course_id). \
        group_by(Score.name). \
        subquery()

    maximum_scores_sorted = db_session.query(maximum_scores_unsorted.c.name,
                                             maximum_scores_unsorted.c.Maxs.label('Maximum')). \
        filter(maximum_scores_unsorted.c.name == MaxScore.name). \
        filter(MaxScore.course_id == course_id). \
        order_by(MaxScore.priority.asc()). \
        all()

    minimum_scores_unsorted = db_session.query(Score.name, func.min(Score.score).label('Mins')). \
        filter_by(course_id=course_id). \
        group_by(Score.name). \
        subquery()

    minimum_scores_sorted = db_session.query(minimum_scores_unsorted.c.name,
                                             minimum_scores_unsorted.c.Mins.label('Minimum')). \
        filter(minimum_scores_unsorted.c.name == MaxScore.name). \
        filter(MaxScore.course_id == course_id). \
        order_by(MaxScore.priority.asc()). \
        all()

    course_total = db_session.query(MaxScore.maxscore).filter_by(course_id=course_id,
                                                                 name=name).one()[0]

    average_query_unsorted = db_session.query(Score.name, func.avg(Score.score).label('Sums')). \
        filter_by(course_id=course_id). \
        group_by(Score.name). \
        subquery()

    average_query_sorted = db_session.query(average_query_unsorted.c.name,
                                            average_query_unsorted.c.Sums.label('average')). \
        filter(average_query_unsorted.c.name == MaxScore.name). \
        filter(MaxScore.course_id == course_id). \
        order_by(MaxScore.priority.asc()). \
        all()

    course_averages = OrderedDict(average_query_sorted)

    course_maximums = OrderedDict(maximum_scores_sorted)

    course_minimums = OrderedDict(minimum_scores_sorted)

    # Course Maximum Preprocessing
    for key in course_maximums:
        course_maximums[key] = round(course_maximums[key], 2)
    try:
        course_final_maximum = float(course_maximums[name])
    except KeyError:
        course_final_maximum = 'Maximum Pending'

    # Course Minimum Preprocessing
    for key in course_minimums:
        course_minimums[key] = round(course_minimums[key], 2)
    try:
        course_final_minimum = float(course_minimums[name])
    except KeyError:
        course_final_minimum = 'Minimum Pending'

    # Course Average Pre processing
    for key in course_averages:
        course_averages[key] = round(course_averages[key], 2)

    # Get Mid Term Average and Final Average
    try:
        course_final_average = course_averages[name]
    except KeyError:
        course_final_average = 'Average Pending'

    course_maximum, a, a_minus, b, b_minus, c, c_minus = get_predicted_grade(course_final_average, course_final_minimum,
                                                                             course_final_maximum)
    return course_maximum, a, a_minus, b, b_minus, c, c_minus


def get_last_column(db_session, course_id):
    maxscore_by_subject = db_session.query(MaxScore).filter_by(course_id=course_id).all()

    score_names = [i.name for i in maxscore_by_subject]
    name = score_names[-1]
    course_total = db_session.query(MaxScore.maxscore).filter_by(course_id=course_id,
                                                                 name=name).one()[0]
    return name, course_total


"""
Views Start Here
"""


@app.before_request
def make_session_permanent():
    """
    Session timeout is defined as 15 minutes and timeout is after inactivity
    """
    session.permanent = True
    app.permanent_session_lifetime = datetime.timedelta(minutes=15)
    session.modified = True
    g.user = current_user


def login_prepocess(db_session, user_credentials):
    """
    This pre processor is used to identify if a user exists in the faculty or the student table
    :param db_session: Database session for the db
    :param user_credentials: User credentials of the user logging in
    """

    session_obj['userid'] = user_credentials.id.encode('utf-8')
    session_obj['isAdmin'] = db_session.query(AuthStore.isAdmin).filter_by(id=session_obj['userid']).one()[0]

    try:
        session_obj['isSuper'] = db_session.query(Admin.isSuper).filter_by(id=session_obj['userid']).one()[0]
    except exc.NoResultFound:
        session_obj['isSuper'] = False

    # Check is user is faculty or student
    isStudent = False
    isFaculty = False

    try:
        db_session.query(Student).filter_by(id=session_obj['userid']).one()
        isStudent = True
    except exc.NoResultFound:
        pass

    try:
        db_session.query(Faculty).filter_by(id=session_obj['userid']).one()
        isFaculty = True
    except exc.NoResultFound:
        pass

    session_obj['isStudent'] = isStudent
    session_obj['isFaculty'] = isFaculty


@app.route('/', methods=['GET', 'POST'])
def getHomePage():
    if request.method == 'GET':
        return render_template('homepage.html')

    elif request.method == 'POST':

        db_session = DBSession()

        ''' Password can either be an existing password or a token to be used for password resets '''
        userid = request.form['bits-id'].encode('utf-8')
        password = request.form['password'].encode('utf-8')

        logger(userid=userid, password=password)

        try:
            user_credentials = db_session.query(AuthStore).filter_by(id=userid).one()
            user_credential_salt = user_credentials.salt.encode('utf-8')
            user_credential_phash = user_credentials.phash.encode('utf-8')
            user_credential_token_hash = user_credentials.tokenHash

            logger(Password=password,
                   Salt=user_credential_salt,
                   Phash_DB=user_credential_phash,
                   Phash_gen=bcrypt.hashpw(password, user_credential_salt))

            if bcrypt.hashpw(password, user_credential_phash) == user_credential_phash:
                login_user(user_credentials)
                login_prepocess(db_session,
                                user_credentials)
                return redirect(url_for('getCourses'))

            elif user_credential_token_hash is not None:
                sha256object = hashlib.sha256(password)
                tokenHash_obtained = sha256object.hexdigest()

                token_existence_time = str(db_session.query(func.now()).scalar() - user_credentials.tokenTimeStamp)

                logger(tokenHash_actual=user_credential_token_hash,
                       tokenHash_obtain=tokenHash_obtained,
                       token_existence_time=token_existence_time)

                # Handle token expiry and validity
                if tokenHash_obtained == user_credential_token_hash:
                    if TOKEN_LIFETIME > token_existence_time:
                        login_user(user_credentials)
                        login_prepocess(db_session,
                                        user_credentials)
                        return redirect(url_for('getDashboard'))
                    else:
                        error = "Token Expired! Get new token"
                        return render_template('homepage.html',
                                               error=error)

            else:
                error = "Wrong username or Password!"
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
        if session_obj['isAdmin']:
            return render_template('upload.html')
        else:
            return redirect(url_for('getHomePage'))

    elif request.method == 'POST':
        if session_obj['isAdmin']:
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


def download(filename):
    uploads = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    print uploads
    return send_from_directory(directory=uploads, filename=filename)


@app.route('/grade/<string:course_id>', methods=['GET', 'POST'])
@login_required
def grade(course_id):
    if request.method == 'GET':
        if session_obj['isAdmin']:
            db_session = DBSession()
            a_max, a, a_minus, b, b_minus, c, c_minus = get_grading(db_session, course_id=course_id)
            course_data = db_session.query(Course).filter_by(id=course_id).one()
            course_name = course_data.name
            course_name = '.'.join(course_name.split(' '))
            filename = course_id + '_' + course_name + '_' + course_data.semester + '_' + course_data.year + '.csv'
            db_session.close()
            return render_template('grade.html', course_id=course_id, a_max=a_max, a_min=a, a_minus_max=a,
                                   a_minus_min=a_minus, b_max=a_minus, b_min=b, b_minus_max=b, b_minus_min=b_minus,
                                   c_max=b_minus, c_min=c, c_minus_max=c, c_minus_min=c_minus, filename=filename)
        else:
            return redirect(url_for('getHomePage'))
    elif request.method == 'POST':
        print request.form
        if session_obj['isAdmin']:
            a_max = float(request.form['A_max'])
            a_min = float(request.form['A_min'])
            a_minus_max = float(request.form['A-_max'])
            a_minus_min = float(request.form['A-_min'])
            b_max = float(request.form['B_max'])
            b_min = float(request.form['B_min'])
            b_minus_max = float(request.form['B-_max'])
            b_minus_min = float(request.form['B-_min'])
            c_max = float(request.form['C_max'])
            c_min = float(request.form['C_min'])
            c_minus_max = float(request.form['C-_max'])
            c_minus_min = float(request.form['C-_min'])
            db_session = DBSession()
            course_data = db_session.query(Course).filter_by(id=course_id).one()
            course_name = course_data.name
            course_name = '.'.join(course_name.split(' '))
            filename = course_id + '_' + course_name + '_' + course_data.semester + '_' + course_data.year + '.csv'
            name, total = get_last_column(db_session, course_id)
            column = name + '-' + str(total)
            db_session.close()
            genGrade(filename=filename, column=column, a_min=a_min, a_minus_min=a_minus_min, b_min=b_min,
                     b_minus_min=b_minus_min, c_min=c_min)
            print 'hi'
            uploads = os.path.join(app.config['UPLOAD_FOLDER'])
            print uploads
            return send_from_directory(directory=uploads, filename=filename, as_attachment=True)
        else:
            print request.path
            abort(400)


@app.route('/courses')
@login_required
def getCourses():
    db_session = DBSession()

    try:
        # If session is not created by an admin user then load student courses else load all courses
        if not session_obj['isAdmin']:

            course_ids = db_session.query(Score.course_id).filter_by(student_id=session_obj['user_id']).distinct()
            courses = db_session.query(Course).filter(Course.id.in_(course_ids)).all()

            return render_template('courses.html',
                                   courses=courses,
                                   user_id=session_obj['userid'],
                                   admin=False, super=False)
        elif session_obj['isSuper']:
            courses = db_session.query(Course).all()

            return render_template('courses.html',
                                   courses=courses,
                                   user_id=session_obj['userid'],
                                   admin=True,
                                   super=True)

        elif session_obj['isAdmin']:
            courses = db_session.query(Course).all()

            return render_template('courses.html',
                                   courses=courses,
                                   user_id=session_obj['userid'],
                                   admin=True,
                                   super=False)

    except exc.NoResultFound:
        return render_template('courses.html')

    finally:
        db_session.close()


# Need this for admin only
@app.route('/courses/<string:course_id>')
@login_required
def getStudentsByCourse(course_id):
    if session_obj['isAdmin']:
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


@app.route('/courses/<string:course_id>/<string:student_id>')
@login_required
def getScoresByStudent(course_id, student_id):
    db_session = DBSession()

    scores, \
    course, \
    scores_distribution_percentages, \
    course_total, \
    student, \
    scores_names, \
    scores_percentages, \
    scores_actual_json, \
    course_averages, \
    course_averages_for_plot, \
    course_mid_term_average, course_final_average = process_student_data(db_session, course_id, student_id)

    db_session.close()

    return render_template('studentScore.html',
                           scores=scores,
                           course=course,
                           max_scores=scores_distribution_percentages,
                           course_total=course_total,
                           student=student,
                           x_=scores_names,
                           y_percentages=scores_percentages,
                           y_actual=scores_actual_json,
                           course_averages=course_averages,
                           course_averages_for_plot=course_averages_for_plot,
                           course_mid_term_average=course_mid_term_average,
                           course_final_average=course_final_average,
                           isAdmin=session_obj['isAdmin'])


@app.route('/predictions')
@login_required
def getPredictions():
    return "<h1>Predictions</h1>"


@app.route('/admins')
@login_required
def getAllAdmins():
    if request.method == 'GET':
        if session_obj['isSuper']:
            db_session = DBSession()

            admins = db_session.query(Admin).all()
            users_non_admin = db_session.query(AuthStore.id).filter_by(isAdmin=False)
            students_non_admin = db_session.query(Student).filter(Student.id.in_(users_non_admin)).all()
            faculty_non_admin = db_session.query(Faculty).filter(Faculty.id.in_(users_non_admin)).all()
            db_session.close()

            return render_template('admins.html',
                                   admins=admins,
                                   students=students_non_admin,
                                   faculty=faculty_non_admin)
        else:
            abort(404)


@app.route('/admins/grant/<string:admin_id>', methods=['GET', 'POST'])
@login_required
def grantAdminPermissions(admin_id):
    logger(method='Grant',
           admin_id=admin_id)

    if admin_id is not session_obj['userid']:
        db_session = DBSession()
        admin_credentials_status = db_session.query(AuthStore).filter_by(id=admin_id).first()
        admin_credentials_status.isAdmin = True

        new_admin = None
        is_student = False

        try:
            new_admin = db_session.query(Student).filter_by(id=admin_id).one()
            is_student = True
            print "Success!"
        except exc.NoResultFound:
            print "Doesn't belong to Student table!"

        if not is_student:
            try:
                new_admin = db_session.query(Faculty).filter_by(id=admin_id).one()
                print "Success"
            except exc.NoResultFound:
                print "Doesn't belong to Faculty table!"

        if new_admin:
            db_session.add(Admin(id=new_admin.id,
                                 name=new_admin.name,
                                 gender=new_admin.gender,
                                 isSuper=False))
            db_session.commit()

        db_session.close()
        return redirect(url_for('getAllAdmins'))

    else:
        flash("Invalid Permission upgrade request!")
        return redirect(url_for('getAllAdmins'))


@app.route('/admins/revoke/<string:admin_id>', methods=['GET', 'POST'])
@login_required
def revokeAdminPermissions(admin_id):
    logger(method='Revoke',
           admin_id=admin_id)

    if admin_id is not session_obj['userid']:
        db_session = DBSession()

        admin_credentials_status = db_session.query(AuthStore).filter_by(id=admin_id).one()
        admin_details = db_session.query(Admin).filter_by(id=admin_id).one()

        if admin_details.isSuper is False:
            admin_credentials_status.isAdmin = False

            # Remove Admin from system only if not a superuser
            db_session.delete(admin_details)
            db_session.commit()

        else:
            flash("Removal of Superuser is disallowed!")
            db_session.close()
            return redirect(url_for('getAllAdmins'))

        db_session.close()
        return redirect(url_for('getAllAdmins'))

    else:
        flash("Can't revoke permissions of user in session!")
        return redirect(url_for('getAllAdmins'))


@login_required
@app.route('/dashboard', methods=['GET', 'POST'])
def getDashboard():
    if request.method == 'GET':
        db_session = DBSession()

        user = None

        if session_obj['isStudent']:
            user = db_session.query(Student).filter_by(id=session_obj['userid']).one()
        elif session_obj['isFaculty']:
            user = db_session.query(Faculty).filter_by(id=session_obj['userid']).one()

        db_session.close()

        if user:
            return render_template('dashboard.html',
                                   user=user)
        else:
            abort(404)

    else:
        # Process new password and change user password
        new_password = request.form['password'].encode('utf-8')
        if len(new_password) >= 6:
            db_session = DBSession()
            user_salt_new = bcrypt.gensalt()
            user_phash_new = bcrypt.hashpw(new_password, user_salt_new)
            user_credentials = db_session.query(AuthStore).filter_by(id=session_obj['userid']).one()
            user_credentials.salt = user_salt_new
            user_credentials.phash = user_phash_new
            user_credentials.tokenHash = None
            db_session.commit()
            db_session.close()

            flash("Password Successfully Changed!")
        else:
            flash("Password must have more than 6 characters")

        return redirect(url_for('getDashboard'))


@app.route('/forgotpassword', methods=['GET', 'POST'])
def forgotPassword():
    if request.method == 'GET':
        return render_template('forgotpassword.html')
    elif request.method == 'POST':
        user_id = request.form['user-id'].encode('utf-8')

        ''' Store newly SHA256 hash of the generated token in the column token hash '''
        db_session = DBSession()

        user_credentials = db_session.query(AuthStore).filter_by(id=user_id).one()
        token = ''.join([choice(ascii_uppercase) for i in range(16)])
        logger(new_password=token)

        sha256object = hashlib.sha256(token)
        tokenHash = sha256object.hexdigest()
        logger(tokenHash=tokenHash)

        user_credentials.tokenHash = tokenHash
        user_credentials.tokenTimeStamp = func.now()

        user_email = ""
        if session_obj['isStudent']:
            user = db_session.query(Student).filter_by(id=user_id).one()
            user_email = user.email
        elif session_obj['isFaculty']:
            user = db_session.query(Faculty).filter_by(id=user_id).one()
            user_email = user.email

        db_session.commit()
        db_session.close()

        # Send Mail Task to Celery
        if user_email and '@' in user_email:
            sendmail.delay(user_email, user_id, token)
        else:
            flash('Default Recovery Email not set!')
            return redirect(url_for('forgotPassword'))

        return redirect(url_for('forgotPassword'))


@login_required
@app.route('/dashboard/recoverymail', methods=['GET', 'POST'])
def passwordRecoveryMail():
    if request.method == 'POST':

        db_session = DBSession()

        password_recovery_mail = request.form['email'].encode('utf-8')
        logger(password_recovery_mail=password_recovery_mail)

        if session_obj['isStudent'] and '@' in password_recovery_mail:
            user = db_session.query(Student).filter_by(id=session_obj['userid']).one()
            user.email = password_recovery_mail
            db_session.commit()
        elif session_obj['isFaculty'] and '@' in password_recovery_mail:
            user = db_session.query(Faculty).filter_by(id=session_obj['userid']).one()
            user.email = password_recovery_mail
            db_session.commit()

        db_session.close()

    return redirect(url_for('getDashboard'))


@celery.task
def sendmail(user_mail, user_id, new_password):
    # Set as environment variables
    gmail_user = 'educationengineering17@gmail.com'
    gmail_password = 'dop1718shreyas'

    # Mail Send
    sent_from = gmail_user
    to = user_mail
    subject = 'Forgot Password for Grade Predictor and Analyzer'
    body = 'Your new password for ' + user_id + ' is ' + new_password + '\n - Admin'
    email_text = """Subject: %s\n%s\n""" % (subject, body)

    logger(message=email_text)

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_password)
        server.sendmail(sent_from, to, email_text)
        server.close()

        logger(email="Email Sent Succesfully!")

    except:
        logger(email="Something went wrong!")


@login_required
@app.route('/courses/<string:course_id>/metrics')
def getCourseMetrics(course_id):
    db_session = DBSession()

    course = db_session.query(Course).filter_by(id=course_id).one()
    maxscore_by_subject = db_session.query(MaxScore).filter_by(course_id=course.id).all()

    score_names = [i.name for i in maxscore_by_subject]
    max_scores = [i.maxscore for i in maxscore_by_subject]

    list_scores_by_test_type = []
    size_of_score_names = len(score_names)

    for i in range(size_of_score_names):
        score_query = db_session.query(Score).filter_by(course_id=course_id,
                                                        name=score_names[i]).all()
        list_scores_by_test_type.append([(float(j.score) / float(max_scores[i])) * 100 for j in score_query])

    db_session.close()

    return render_template('metrics.html',
                           course_id=course_id,
                           max_score=max_scores,
                           scores=list_scores_by_test_type,
                           names=score_names)


@login_required
@app.route('/courses/<string:course_id>/<string:student_id>/<string:test_name>/edit', methods=['POST'])
def editMarks(student_id, course_id, test_name):
    db_session = DBSession()

    if session_obj['isAdmin']:
        updated_score = request.form['update-score'].encode('utf-8')
        max_score = db_session.query(MaxScore).filter_by(course_id=course_id,
                                                         name=test_name).one()
        # Max score check
        if float(updated_score) <= max_score:
            score = db_session.query(Score).filter_by(course_id=course_id,
                                                      student_id=student_id,
                                                      name=test_name).one()
            diff = float(updated_score) - score.score

            # Total and Mid Term Total Update
            try:
                mid_term_total_priority = \
                    db_session.query(MaxScore.priority).filter_by(course_id=course_id,
                                                                  name='Mid Term Total').one()[0]
                final_total_priority = \
                    db_session.query(MaxScore.priority).filter_by(course_id=course_id,
                                                                  name='Total').one()[0]

                mid_term_total = db_session.query(Score).filter_by(course_id=course_id,
                                                                   student_id=student_id,
                                                                   name='Mid Term Total').one()
                final_total = db_session.query(Score).filter_by(course_id=course_id,
                                                                student_id=student_id,
                                                                name='Total').one()
                logger(total=final_total)

                if max_score.priority < mid_term_total_priority:
                    mid_term_total.score += diff
                    final_total.score += diff
                    db_session.commit()
                elif mid_term_total_priority < max_score.priority < final_total_priority:
                    final_total.score += diff
                    db_session.commit()
            except:
                pass

            score.score = updated_score
            db_session.commit()

    scores, \
    course, \
    scores_distribution_percentages, \
    course_total, \
    student, \
    scores_names, \
    scores_percentages, \
    scores_actual_json, \
    course_averages, \
    course_averages_for_plot, \
    course_mid_term_average, course_final_average = process_student_data(db_session, course_id, student_id)

    db_session.close()

    return render_template('studentScore.html',
                           scores=scores,
                           course=course,
                           max_scores=scores_distribution_percentages,
                           course_total=course_total,
                           student=student,
                           x_=scores_names,
                           y_percentages=scores_percentages,
                           y_actual=scores_actual_json,
                           course_averages=course_averages,
                           course_averages_for_plot=course_averages_for_plot,
                           course_mid_term_average=course_mid_term_average,
                           course_final_average=course_final_average,
                           isAdmin=session_obj['isAdmin'])
