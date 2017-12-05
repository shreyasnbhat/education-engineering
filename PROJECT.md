### Project Goals
The project aimed to work upon ideas presented by various people in the field
of Education Engineering. 

A webapp was developed as a part of the project which allowed
faculty to analyze student performance over time, review their progress,
and also grade their work. It would also help the students to analyze their 
course wise metrics and see where they could do better.

#### WebApp v0.5 Feature List
- User Authentication using BITS-ID
- Forgot Password Emails Supported
- User roles of Student, Admin and SuperAdmin
- .csv file upload to generate wepapp content
- Metrics that allow Faculty members to grade their courses
- Metrics that allow student to view his performance over the duration of the course
- User Dashboard to change recovery email
- Ability to change marks of students quickly upon request
- Grade course according to the ranges specified by the faculty


### Project Setup
1) Make sure that you have python2 and git installed by checking `which python`
2) Install `virtualenv` first using `sudo apt-get install python-virtualenv`
3) Clone the project directory in any directory of you choice.
4) Clone project using `git clone https://github.com/shreyasnbhat/education-engineering.git`
5) Assuming the the folder of `education-engineering` is now under a folder called `WebApp`.
6) In the terminal and then use `virtualenv ~/path/WebApp/flask_app`
7) Now use `cd WebApp/flask_app/bin` and use `source activate` to start you virtual environement
8) Now the terminal should say something like `(flask-app) $user@bits: ` instead of `$user@bits`
9) Now to setup all the project requirements run `sh setup.sh`. This script exists inside the project folder of `education-engineering`
10) Check if redis-server is running by `service redis-server status`. If it is not running then use `service redis-server start`
11) Now run the Celery Server by  `celery -A app.celery worker -D`
12) Run main server locally by `python run.py d 5000`.
13) For server deploy use `python run.py p 500`

### Tutorial
1) Setup the webapp server at `localhost:5000`
2) Setup Celery Server using `celery -A app.celery worker -D`  in the project root directoy `~/path/education-engineering/`
3) Make sure the service `redis` is running at port `6379`. If not use `service redis-server start`
2) Go to `localhost:5000/`
3) Use default Admin UserID as `admin` and Admin Password as `admin`    
4) If you don't see any courses listed you can use the upload feature to update the webapp
5) Before using the upload feature make sure that a `Celery Server` is running. 
6) Choose the file you want to upload. FILEFORMAT.md specifies the way in which you are supposed to upload the file.
7) Other formats of the file will yield incorrect results.
8) In the course page if you click on any course, as you are an admin you will be redirected to the list of registered stduents in the course.
9) If you are not admin and click on the course you will be redirected to your marks directly.
10) The student list page has a button `Grade` which would allow you to grade students according to the ranges that you specify. A default range has been already provided.
11) For further help in grading you could also go to the Metrics tab and view histograms of various components.
12) If you would click on any student listed in the student list you would be redirected to the metrics for that student. These metrics would help you analyze a student's performance.
13) The metrics here include course component distribution, performance in various tests, relative performance wrt average.
14) Here you could also change the course marks directly.
