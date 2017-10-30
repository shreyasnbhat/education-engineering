import bcrypt
import os
import pandas as pd
from db import id_format
from sqlalchemy.orm import sessionmaker
from models import *
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError


def generate_sample_db(path, course_id, course_name, db_session):
    """
    This function is used to populate the database with a csv file
    :param path: This consists the path of the .csv file to add to the db
    :param course_id: This consists of the course id for the csv file passed
    :param course_name: This consists the name of the course wrt to the course_id given
    :param db_session: This consists of the database session for db operations
    """

    # Read data from the file specified in path
    sample_marks = pd.read_csv(path)
    sample_mark_frame = pd.read_csv(path)
    sample_mark_frame.drop(['Name', 'ID Number'], axis=1, inplace=True)

    # Any mark column must be of the type mark_name-max_marks
    sample_mark_columns = sample_mark_frame.columns

    for i in sample_mark_columns:
        score_name, score_max = i.strip().split('-')

        # Add score_max to table MaxScores if not present else update
        try:
            db_session.add(MaxScore(course_id=course_id,
                                    name=score_name,
                                    maxscore=score_max))
            db_session.commit()
        except IntegrityError:
            db_session.rollback()

            # Update the Max Score
            temp = db_session.query(MaxScore).filter_by(course_id=course_id,
                                                        name=score_name)
            temp.maxscore = score_max
            db_session.commit()

    # Format Student ID's and other details to put in the db if the student is not already present
    for i in range(len(sample_marks)):
        name = sample_marks.loc[i]['Name']
        student_id = sample_marks.loc[i]['ID Number']
        formatted_student_id = id_format(student_id)

        # Student Entry Addition to db
        try:
            db_session.add(Student(name=name,
                                   id=formatted_student_id,
                                   gender='Male'))
            db_session.commit()
            print "Added ", name, formatted_student_id
        except IntegrityError:
            db_session.rollback()

        # Add scores of the student
        #If you want the entries to be displayed in order in DB Browser then use this otherwise comment it.
        if(db_session.query(Score).filter_by(student_id = formatted_student_id).first() != None):
            db_session.query(Score).filter_by(student_id = formatted_student_id, course_id = course_id).delete(synchronize_session = 'evaluate')
            db_session.commit()

        for mark_column in sample_mark_columns:
            score_name, score_max = mark_column.strip().split('-')
            score = sample_mark_frame.loc[i][mark_column]
            try:
                db_session.add(Score(student_id=formatted_student_id,
                                     course_id=course_id,
                                     name=score_name,
                                     score=score))
                db_session.commit()
            except IntegrityError:
                db_session.rollback()
                old_score = db_session.query(Score).filter_by(student_id=formatted_student_id,
                                                              name=score_name,
                                                              course_id=course_id).one()
                old_score.score = score
                db_session.commit()

    # Add authentication credentials for users. Default password set.
    ids = [i.id for i in db_session.query(Student).all()]
    passwords = ['student']

    for i in range(len(ids)):
        generated_salt = bcrypt.gensalt()
        phash = bcrypt.hashpw(passwords[0], generated_salt)
        try:
            db_session.add(AuthStore(id=ids[i],
                                     phash=phash,
                                     salt=generated_salt,
                                     isAdmin=False))
            db_session.commit()
        except IntegrityError:
            db_session.rollback()

    # Add admin login credentials
    admin_ids = ['admin', 'pkd', 'abaskar', 'bmd']
    admin_names = ['Shreyas', 'Dr Prasant Kumar Das', 'A Baskar', 'Bharat Deshpande']
    admin_passwords = ['admin']

    for i in range(len(admin_ids)):
        name = admin_names[i]
        id = admin_ids[i]
        try:
            db_session.add(Faculty(id=id,
                                   name=name,
                                   gender='Male'))
            db_session.commit()
        except IntegrityError:
            db_session.rollback()

    print "Added Faculty Details!"

    for i in range(len(admin_ids)):
        generated_salt = bcrypt.gensalt()
        phash = bcrypt.hashpw(admin_passwords[0], generated_salt)
        try:
            db_session.add(AuthStore(id=admin_ids[i],
                                     phash=phash,
                                     salt=generated_salt,
                                     tokenHash=None,
                                     isAdmin=True))

            if i is 0 or i is 1:
                db_session.add(Admin(id=admin_ids[i],
                                     name=admin_names[i],
                                     gender='Male',
                                     isSuper=True))
            else:
                db_session.add(Admin(id=admin_ids[i],
                                     name=admin_names[i],
                                     gender='Male',
                                     isSuper=False))

            db_session.commit()

        except IntegrityError:
            db_session.rollback()

    print "Added Authentication credentials"

    # Add course data
    try:
        db_session.add(Course(id=course_id, name=course_name))
        db_session.commit()
    except IntegrityError:
        db_session.rollback()


if __name__ == '__main__':

    print "Choose database name"
    print "--------------------"
    db_name = str(raw_input().strip())

    # Setup database with given input
    engine = create_engine('sqlite:///../' + db_name + '.db')
    Base.metadata.create_all(engine)
    DBSession = sessionmaker(bind=engine)
    db_session = DBSession()

    print "Choose which file to populate"
    print "-----------------------------"
    list_of_files = os.listdir('../data')

    file_id = 0

    for file in list_of_files:
        print str(file_id) + str('.'), file
        file_id += 1

    chosen_file_id = int(raw_input().strip())

    path = str('../data/') + list_of_files[chosen_file_id]

    """
    The file name for the .csv file is defined in FILEFORMAT.md
    :param course_id: Course ID for the course
    :param course_name: Course name for the course
    :param semester: Semester for the course. Can be either 1 or 2
    :param year: Year of conduction of the course
    """
    course_id, course_name_unformatted, semester, year = list_of_files[chosen_file_id].split('_')
    course_name = " ".join(course_name_unformatted.split('.'))

    # Generate the sample here
    generate_sample_db(path,
                       course_id,
                       course_name,
                       db_session)

    db_session.close()
