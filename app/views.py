from flask import render_template
from sqlalchemy.orm import sessionmaker
from app import app
from sqlalchemy import and_,or_
from models import Student,engine,Course,Score

'''Final Configuration'''
DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
def getHomePage():
    return render_template('homepage.html')

@app.route('/courses')
def getCourses():
    courses = session.query(Course).all()
    return render_template('courses.html', courses = courses)

@app.route('/courses/<string:course_id>')
def getStudentsByCourse(course_id):
    students = session.query(Student).filter(and_(Student.id == Score.student_id,Score.course_id == Course.id,Course.id == course_id)).all()
    for x in students:
        print x.id
    return render_template('students.html',students=students,course_id=course_id)

@app.route('/courses/<string:course_id>/<string:student_id>')
def getMarksByStudent(course_id,student_id):
    course = session.query(Course).filter_by(id=course_id).one()
    scores = session.query(Score).filter_by(student_id=student_id).all()
    student = session.query(Student).filter_by(id=student_id).one()
    return render_template('studentScore.html',scores=scores ,course=course,student=student)

@app.route('/predictions')
def getPredictions():
    return "<h1>Predictions</h1>"
