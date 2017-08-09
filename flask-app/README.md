### Description
This repository is dedicated for the Design Project of Data Mining/Analysis in Education Research for the Semester I 2018-19. The project aims to predcit the direction of a student's performance according to his/her past performances.

### Project Technology Stack
- Flask
- MaterializeCSS
- Local DB - (PostrgreSQL/SQLAlchemy) (To-do)
- Online DB - Firebase (To-do)
- Tensorflow (To-do)
- Vagrant (To-do)

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

