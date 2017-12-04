from sqlalchemy import Column, Integer, String, ForeignKey, ForeignKeyConstraint, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

'''Table Information along with Mappers'''
class Student(Base):
    __tablename__ = 'students'

    name = Column(String(80), nullable=False)
    id = Column(String(20), primary_key=True)
    gender = Column(String(20))
    email = Column(String(40))
    scores = relationship('Score')


class Score(Base):
    __tablename__ = 'scores'

    student_id = Column(String(20), ForeignKey('students.id'), primary_key=True)
    course_id = Column(String(10), primary_key=True)
    name = Column(String(20), primary_key=True)
    score = Column(Integer)


class MaxScore(Base):
    __tablename__ = 'maxscores'

    course_id = Column(String(10), primary_key=True)
    name = Column(String(20), primary_key=True)
    maxscore = Column(Integer)
    priority = Column(Integer)
    ForeignKeyConstraint(['course_id', 'name'], ['scores.course_id', 'scores.name'])


class Course(Base):
    __tablename__ = 'courses'

    id = Column(String(10), ForeignKey('scores.course_id'), primary_key=True)
    year = Column(String(4), primary_key=True)
    semester = Column(String(1), primary_key=True)
    name = Column(String(30), nullable=False)
    score = relationship('Score')


"""NOTE: Need to update the overriden functions of is_authenticated() is_active() and is_anonymous()"""
class AuthStore(Base):
    __tablename__ = 'authstore'

    id = Column(String(10), primary_key=True)
    salt = Column(String(50))
    phash = Column(String(50))
    tokenHash = Column(String(50))
    tokenTimeStamp = Column(DateTime(timezone=True), server_default=func.now())
    isAdmin = Column(Boolean())

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id.encode('utf-8')


class Grade(Base):
    __tablename__ = 'grades'
    student_id = Column(String(20), primary_key=True)
    course_id = Column(String(10), primary_key=True)
    grade = Column(String(2))


class Admin(Base):
    __tablename__ = 'admins'

    id = Column(String(10), primary_key=True)
    name = Column(String(80), nullable=False)
    gender = Column(String(20))
    isSuper = Column(Boolean())


class Faculty(Base):
    __tablename__ = 'faculty'

    id = Column(String(30), primary_key=True)
    name = Column(String(80), nullable=False)
    gender = Column(String(10))
    email = Column(String(40))
