from app import app
import sys

if __name__ == '__main__':

    deploy_mode = str(sys.argv[1])

    if deploy_mode == 'debug':
        app.debug = True
        app.run(host='localhost', port=5000)

    elif deploy_mode == 'production':
        app.run(host='0.0.0.0', port=5000)

    else :
        print "Usage: python run.py <debug/production>"
