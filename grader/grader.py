import pandas as pd
from db import id_format
from sqlalchemy.orm import sessionmaker
from db.models import *
from sqlalchemy import create_engine, func
from sqlalchemy.exc import IntegrityError

def get_predicted_grade(course_final_average, course_final_minimum, course_final_maximum):
    # Final Grade
    partition1 = (float(float(course_final_maximum) - course_final_average)) / 4.0
    partition2 = (float(course_final_average - float(course_final_minimum))) / 2.0
    a = course_final_maximum - partition1
    a_minus = a - partition1
    b = a_minus - partition1
    c = course_final_average - partition2

    return course_final_maximum, a, a_minus, b, course_final_average, c, course_final_minimum


def genGrade(filename, column, a_min, a_minus_min, b_min, b_minus_min, c_min, db_session):
    grades = []
    course = filename.strip().split('_')
    course_id = course[0]
    course_name = ' '.join(course[1].split('.'))
    semester = course[2]
    year = course[3].split('.')[0]
    df = pd.read_csv('data/' + filename)
    a_count = 0
    a_minus_count = 0
    b_count = 0
    b_minus_count = 0
    c_count = 0
    c_minus_count = 0
    for i in df[column]:
        if i >= a_min:
            grades.append('A')
            a_count = a_count + 1
        elif i >= a_minus_min:
            grades.append('A-')
            a_minus_count = a_minus_count + 1
        elif i >= b_min:
            grades.append('B')
            b_count = b_count + 1
        elif i >= b_minus_min:
            grades.append('B-')
            b_minus_count = b_minus_count + 1
        elif i >= c_min:
            grades.append('C')
            c_count = c_count + 1
        else:
            grades.append('C-')
            c_minus_count = c_minus_count + 1
    df['Grade'] = grades
    df.to_csv('data/' + filename, index=False)
    ids = df['ID Number']
    for i in range(len(grades)):
        try:
            db_session.add(Grade(student_id=ids[i], course_id=course_id, grade=grades[i]))
            db_session.commit()
        except IntegrityError:
            db_session.rollback()
            temp = db_session.query(Grade).filter_by(student_id=ids[i], course_id=course_id)
            temp.grade = grades[i]
            db_session.commit()

    mgpa = float(10*a_count + 9*a_minus_count + 8*b_count + 7*b_minus_count + 6*c_count + 5*c_minus_count)/float(a_count + a_minus_count + b_count + b_minus_count + c_count + c_minus_count)
    mgpa = str(round(mgpa, 2))
    try:
        temp = db_session.query(Course).filter_by(id=course_id, year=year, semester=semester, name=course_name).one()
        temp.mgpa=mgpa
        db_session.commit()
    except:
        db_session.rollback()

def get_clustering(filename, column):
    from sklearn.cluster import KMeans
    df = pd.read_csv(filename)
    x = df[column]
    km = KMeans(n_clusters=6).fit(x.reshape(-1, 1))
    print km.cluster_centers_
