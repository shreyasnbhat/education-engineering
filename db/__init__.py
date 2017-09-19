from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


def id_format(unformatted_id):
    """
    This function is used to the format any student ID that is present
    :param unformatted_id: This would contain an alphanumeric student id
    :return: formatted id
    """
    if len(unformatted_id) < 13:
        return unformatted_id[0:8] + str(0) + unformatted_id[8:12]
    else:
        return unformatted_id
