from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

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


"""NOTE: Need to update the overriden functions of is_authenticated() is_active() and is_anonymous()"""
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








