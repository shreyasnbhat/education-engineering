import pandas as pd


def get_predicted_grade(course_final_average, course_final_minimum, course_final_maximum):
    # Final Grade
    partition1 = (float(float(course_final_maximum) - course_final_average)) / 4.0
    partition2 = (float(course_final_average - float(course_final_minimum))) / 2.0
    a = course_final_maximum - partition1
    a_minus = a - partition1
    b = a_minus - partition1
    c = course_final_average - partition2

    return course_final_maximum, a, a_minus, b, course_final_average, c, course_final_minimum


def genGrade(filename, column, a_min, a_minus_min, b_min, b_minus_min, c_min):
    grades = []
    df = pd.read_csv('data/' + filename)
    for i in df[column]:
        if i >= a_min:
            grades.append('A')
        elif i >= a_minus_min:
            grades.append('A-')
        elif i >= b_min:
            grades.append('B')
        elif i >= b_minus_min:
            grades.append('B-')
        elif i >= c_min:
            grades.append('C')
        else:
            grades.append('C-')
    df['Grade'] = grades
    df.to_csv('data/' + filename)


def get_clustering(filename, column):
    from sklearn.cluster import KMeans
    df = pd.read_csv(filename)
    x = df[column]
    km = KMeans(n_clusters=6).fit(x.reshape(-1, 1))
    print km.cluster_centers_
