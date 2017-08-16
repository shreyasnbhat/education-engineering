from sqlalchemy import Column,Integer,String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

'''Table Information along with Mappers'''
class Student(Base):
    __tablename__ = 'student'

    name = Column(String(80),nullable=False)
    id = Column(Integer,primary_key=True)
    gender = Column(String(10))

'''Final Configuration'''
engine = create_engine('sqlite:///app.db')
Base.metadata.create_all(engine)
DBSession = sessionmaker(bind=engine)
session = DBSession()

if __name__ == '__main__':

    #Fake Data Population
    name = ['Shreyas N Bhat','Gautam M Naik','Archit Patke','Aditya Asgaonkar','Pranav Palande','Manas Mulay','Sudeep Katakol','Atharva Vaidya','Pankaj Kumar','Sai Avinash']
    gender = 'Male'
    students = []
    for i in range(len(name)):
        student = Student(name = name[i], id = i, gender = gender)
        session.add(student)
        session.commit()

    result = session.query(Student).all()
    print result
