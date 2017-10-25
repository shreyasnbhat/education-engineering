from datetime import datetime


def logger(**kwargs):
    """
    This method is a logger function to log any values
    :param kwargs: Variable arguments
    """
    print
    print "============================Logger============================================================================="
    for key in kwargs:
        print str(datetime.now()) + " | " + key + str(':'), kwargs[key]
    print "==============================================================================================================="
