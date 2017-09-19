from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from models import Student, Score, AuthStore, Course
from sqlalchemy import create_engine
import pandas as pd
from db import id_format
from sqlalchemy.exc import IntegrityError, InvalidRequestError
import bcrypt

"""Sample v1.0"""
Base = declarative_base()
engine = create_engine('sqlite:///../sampleV1.db')
Base.metadata.create_all(engine)
DBSession = sessionmaker(bind=engine)
db_session = DBSession()

"""Global Variable Space"""
MuPMarks = pd.read_csv('../test_data.csv')
markFrame = pd.read_csv('../test_data.csv')
markFrame.drop(['Name', 'ID Number', 'Mid Term Grade', 'Pre Compre Grade'], axis=1, inplace=True)
markColumns = markFrame.columns


def generateMarkList(i):
    scoreList = []

    for l in markColumns:
        try:
            id = MuPMarks.loc[i]['ID Number']
            id = id_format(id)
            scoreList.append(Score(student_id=id, name=l, course_id='CS F241', score=markFrame.loc[i][l]))
        except KeyError:
            return scoreList

    return scoreList


def addUsers():
    from bs4 import BeautifulSoup
    data = open("html_doc.html", 'r').read()

    soup = BeautifulSoup(data)
    gender = 'Male'

    errors = 0

    for i in soup.find_all('tr'):
        t = [j.string for j in i.find_all('td')]
        if len(t) > 2:
            id = t[0].lstrip('\n').strip(" ")
            name = t[1].strip(" ").strip(" .").strip("\n")
            try:
                db_session.add(Student(id=id, name=name, gender=gender))
                db_session.commit()
                id = id_format(id)
                print "------------------Added------------------- "
                print "ID :", id
                print "Name :", name
                print "Scores:", generateMarkList(id)
                print "------------------------------------------ "
            except IntegrityError:
                print "Unique Constraint failed!"
                errors += 1
                print "Errors found: ", errors
                db_session.rollback()
            except InvalidRequestError:
                print "Invalid Request at", id, name
                errors += 1
                print "Errors found: ", errors

    for i in range(len(MuPMarks)):
        name = MuPMarks.loc[i]['Name']
        id = MuPMarks.loc[i]['ID Number']
        f_id = id_format(id)
        try:
            print "User present"
            resultCheck = db_session.query(Student).filter_by(id=f_id).first()
            resultCheck.scores = generateMarkList(i)
            db_session.commit()
        except:
            print "User not present"
            print f_id
            student = Student(id=f_id, name=name, gender=gender, scores=generateMarkList(i))
            db_session.add(student)
            db_session.commit()
            print "Added ", id, " ", name


def addCourses():
    ### Add some additional Courses
    db_session.add(Course(id='CS F241', name='Microprocessors and Interfacing'))
    db_session.add(Course(id='MATH F211', name='Mathematics III'))
    db_session.add(Course(id='ECON F211', name='Principle Of Economics'))
    db_session.add(Course(id='CS F215', name='Digital Design'))
    db_session.commit()

    print "Added Courses"


def addAuthenticationData():
    ### Add some AuthStore data
    ids = ['2015A7PS0033G', '2015A7PS0029G', '2015A7PS0030G', '2015A7PS0031G', '2015A7PS0032G']
    passwords = ['shreyas123', 'gmn0105', 'watchdogs', 'qwerty123', 'fakeaccent']
    for i in range(len(passwords)):
        generated_salt = bcrypt.gensalt()
        phash = bcrypt.hashpw(passwords[i], generated_salt)
        db_session.add(AuthStore(id=ids[i], phash=phash, salt=generated_salt))
        print "ID: ", ids[i], " salt:", generated_salt, " hash:", phash, "was added!"

    db_session.commit()

    print "Added Authentication data!"


def sample():
    db_session.add(Score(student_id='2015A7PS0033G',
                         course_id='ECON F211',
                         name='T2',
                         score=20))
    db_session.add(Score(student_id='2015A7PS0033G',
                         course_id='ECON F211',
                         name='T1',
                         score=18))
    db_session.add(Score(student_id='2015A7PS0033G',
                         course_id='ECON F211',
                         name='Quiz',
                         score=20))
    db_session.add(Score(student_id='2015A7PS0033G',
                         course_id='ECON F211',
                         name='Compre',
                         score=36))
    db_session.commit()


def populateDB():
    addUsers()
    addCourses()
    addAuthenticationData()
    sample()


if __name__ == '__main__':
    populateDB()
    db_session.close()
