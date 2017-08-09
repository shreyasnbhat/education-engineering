### Description
This repository is dedicated for the Design Project of Data Mining/Analysis in Education Research for the Semester I 2018-19. The project aims to predcit the direction of a student's performance according to his/her past performances.

### Project Technology Stack
- Flask
- MaterializeCSS
- Local DB - (PostrgreSQL/SQLAlchemy) (To-do)
- Online DB - Firebase (To-do)
- Tensorflow (To-do)
- Vagrant

#### Vagrant machine setup(Under developement)
1. Install vagrant prerequisites first that is Virtual Box.
2. Then install vagrant in your Ubuntu machine by `sudo apt-get install vagrant`.
3. Then in the directory where the repo was cloned run `vagrant up`
4. This will spawn an instance of the vagrant machine which would be used to host our web server.
5. To run the webserver type `vagrant ssh` to ssh into the virtual instance.
6. Then run `cd flask-app` and `python server.py`
7. Now open `localhost:500/` in the browser to view the running `flask app`.  

#### Contribution Guidelines
1. Pull requests to be sent from any branch of the fork except `master`
2. Commit messages should be descriptive. For example `feat:Added templates for Prediction Pages`

#### Pull Request Creation Help
1. `git add *`
2. `git commit -m "Descriptive Commit Message`
3. `git push -u origin branchname`

#### Fork Master Synchronization
1. Assuming main repo has been added as a remote named `upstream`
2. `git fetch upstream`
3. `git reset --hard upstream/master`
 
#### Fork Branch updation with master
1. Assuming `feature-branch` is checked out.
2. Run `git rebase master` to update your branch if it is behind `master`(local)
3. If conflicts arise fix them and run `git add *` and then `git rebase --continue`

