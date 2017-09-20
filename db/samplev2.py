import bcrypt
import pandas as pd
from db import id_format
from sqlalchemy.orm import sessionmaker
from models import Student, Score, AuthStore, Course, Base, MaxScore
from sqlalchemy import create_engine

"""Sample v2.0"""
engine = create_engine('sqlite:///../sampleV2.db')
Base.metadata.create_all(engine)
DBSession = sessionmaker(bind=engine)
db_session = DBSession()


def generate_sample_db(path, course_id):
    """
    This function is used to generate sample data for testing and the .db file obtained is sampleV2.db
    :param path: This consists the path of the .csv file to add to the db
    :param course_id: This consists of the course id for the csv file passed
    """

    # Read data from the file specified in path
    sample_marks = pd.read_csv(path)
    sample_mark_frame = pd.read_csv(path)
    sample_mark_frame.drop(['Name', 'ID Number'], axis=1, inplace=True)

    # Any mark column must be of the type mark_name-max_marks
    sample_mark_columns = sample_mark_frame.columns

    for i in sample_mark_columns:

        score_name,score_max = i.strip().split('-')

        # Add score_max to table MaxScores
        db_session.add(MaxScore(course_id=course_id,
                                name=score_name,
                                maxscore=score_max))
        db_session.commit()

    # Format Student ID's and other details to put in the db
    for i in range(len(sample_marks)):
        name = sample_marks.loc[i]['Name']
        student_id = sample_marks.loc[i]['ID Number']
        formatted_student_id = id_format(student_id)

        score_list = []

        for mark_column in sample_mark_columns:
            try:
                score_name,score_max = mark_column.split('-')

                score = sample_mark_frame.loc[i][mark_column]
                score_list.append(Score(student_id=formatted_student_id,
                                        name=score_name,
                                        course_id=course_id,
                                        score=score))
            except KeyError:
                print "No such key was found!"

        db_session.add(Student(name=name,
                               id=formatted_student_id,
                               gender='Male',
                               scores=score_list))
        db_session.commit()
        print "Added", student_id, name

    # Add authentication credentials for test users
    ids = ['2017A3PS0191G', '2038A3PS0191G']
    passwords = ['student', 'student']

    for i in range(len(passwords)):
        generated_salt = bcrypt.gensalt()
        phash = bcrypt.hashpw(passwords[i], generated_salt)
        db_session.add(AuthStore(id=ids[i],
                                 phash=phash,
                                 salt=generated_salt))
    db_session.commit()
    print "Added Authentication credentials"

    # Add course data
    db_session.add(Course(id='PHY F241', name='Astronomy and Astrophysics'))
    db_session.commit()
    print "Added Course data"


if __name__ == '__main__':
    generate_sample_db('../data/astro.csv', 'PHY F241')
    db_session.close()

