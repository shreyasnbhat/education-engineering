import sys
from sqlalchemy import Column,ForeignKey,Integer,String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import random

Base = declarative_base()

'''Table Information along with Mappers'''
class Student(Base):
    __tablename__ = 'Student'
    name = Column(String(80),nullable=False)
    id = Column(Integer,primary_key=True)
    gender = Column(String(10))


'''Final Configuration'''
engine = create_engine('sqlite:///app.db')
Base.metadata.create_all(engine)
DBSession = sessionmaker(bind=engine)
session = DBSession()

if __name__ == '__main__':

    id = [random.randint(1, 1000) for i in range(10)]
    name = 'Lorem ipsum'
    gender = 'male'
    students = []
    for i in range(10):
        st = Student(name = name, id = id[i], gender = gender)
        session.add(st)
        session.commit()

    result = session.query(Student).all()
    print result

