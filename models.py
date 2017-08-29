from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.exc import IntegrityError, InvalidRequestError
import os
import bcrypt

### For testing only ###
import pandas as pd

MuPMarks = pd.read_csv('./test_data.csv')
markFrame = pd.read_csv('./test_data.csv')
markFrame.drop(['Name', 'ID Number', 'Mid Term Grade', 'Pre Compre Grade'], axis=1, inplace=True)
markColumns = markFrame.columns

### Database Setup ###
Base = declarative_base()

'''Table Information along with Mappers'''


class Student(Base):
    __tablename__ = 'students'

    name = Column(String(80), nullable=False)
    id = Column(String(20), primary_key=True)
    gender = Column(String(20))
    scores = relationship('Score')


class Score(Base):
    __tablename__ = 'scores'

    student_id = Column(String(20), ForeignKey('students.id'), primary_key=True)
    course_id = Column(String(10), primary_key=True)
    name = Column(String(20), primary_key=True)
    score = Column(Integer)


class Course(Base):
    __tablename__ = 'courses'

    id = Column(String(10), ForeignKey('scores.course_id'), primary_key=True)
    name = Column(String(30), nullable=False)
    score = relationship('Score')


class AuthStore(Base):
    __tablename__ = 'authstore'

    id = Column(String(10), primary_key=True)
    salt = Column(String(50))
    phash = Column(String(50))

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id.encode('utf-8')


'''Final Configuration
   Needs to moved into __init__.py later
   This class should only contain models
'''
engine = create_engine('sqlite:///app.db')
Base.metadata.create_all(engine)
DBSession = sessionmaker(bind=engine)
session = DBSession()


def databsePurge():
    os.remove('./app.db')
    print "Database purged Successfully"


def generateMarkList(i):
    scoreList = []

    for l in markColumns:
        try:
            id = MuPMarks.loc[i]['ID Number']
            id = idFormat(id)
            scoreList.append(Score(student_id=id, name=l, course_id='CS F241', score=markFrame.loc[i][l]))
        except KeyError:
            return scoreList

    return scoreList


def idFormat(id):
    if (len(id) < 13):
        return id[0:8] + str(0) + id[8:12]
    else:
        return id


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
                session.add(Student(id=id, name=name, gender=gender))
                session.commit()
                id = idFormat(id)
                print "------------------Added------------------- "
                print "ID :", id
                print "Name :", name
                print "Scores:", generateMarkList(id)
                print "------------------------------------------ "
            except IntegrityError:
                print "Unique Constraint failed!"
                errors += 1
                print "Errors found: ", errors
                session.rollback()
            except InvalidRequestError:
                print "Invalid Request at", id, name
                errors += 1
                print "Errors found: ", errors

    for i in range(len(MuPMarks)):
        name = MuPMarks.loc[i]['Name']
        id = MuPMarks.loc[i]['ID Number']
        f_id = idFormat(id)
        try:
            print "User present"
            resultCheck = session.query(Student).filter_by(id=f_id).first()
            resultCheck.scores = generateMarkList(i)
            session.commit()
        except:
            print "User not present"
            print f_id
            student = Student(id=f_id, name=name, gender=gender, scores=generateMarkList(i))
            session.add(student)
            session.commit()
            print "Added ", id, " ", name


def addCourses():

    ### Add some additional Courses
    session.add(Course(id='CS F241', name='Microprocessors and Interfacing'))
    session.add(Course(id='MATH F211', name='Mathematics III'))
    session.add(Course(id='ECON F211', name='Principle Of Economics'))
    session.add(Course(id='CS F215', name='Digital Design'))
    session.commit()

    print "Added Courses"


def addAuthenticationData():
    ### Add some AuthStore data
    ids = ['2015A7PS0033G', '2015A7PS0029G', '2015A7PS0030G', '2015A7PS0031G', '2015A7PS0032G']
    passwords = ['shreyas123', 'gmn0105', 'watchdogs', 'qwerty123', 'fakeaccent']
    for i in range(len(passwords)):
        generated_salt = bcrypt.gensalt()
        phash = bcrypt.hashpw(passwords[i], generated_salt)
        session.add(AuthStore(id=ids[i], phash=phash, salt=generated_salt))
        print "ID: ", ids[i], " salt:", generated_salt, " hash:", phash, "was added!"

    session.commit()

    print "Added Authentication data!"

def populateDB():

    addUsers()
    addCourses()
    addAuthenticationData()
    sample()

def sample():

    session.add(Score(student_id='2015A7PS0033G',
                      course_id='ECON F211',
                      name='T2',
                      score=20))
    session.add(Score(student_id='2015A7PS0033G',
                      course_id='ECON F211',
                      name='T1',
                      score=18))
    session.add(Score(student_id='2015A7PS0033G',
                      course_id='ECON F211',
                      name='Quiz',
                      score=20))
    session.add(Score(student_id='2015A7PS0033G',
                      course_id='ECON F211',
                      name='Compre',
                      score=36))
    session.commit()


if __name__ == '__main__':

    populateDB()
