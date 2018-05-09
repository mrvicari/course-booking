from flask_script import Manager
from app import app, models, db
import bcrypt
from datetime import datetime, timedelta, date
import random

manager = Manager(app)

@manager.command
def createAdmin():
    admin = models.User(firstName='admin',
                        surname='admin',
                        username='admin',
                        email='admin@fdm.com',
                        password=bcrypt.hashpw('password'.encode('utf-8'), bcrypt.gensalt()),
                        admin=True)

    db.session.add(admin)
    db.session.commit()

@manager.command
def createUsers():
    names = ['John', 'Andrew', 'George', 'Michael']
    surnames = ['Williams', 'Smith', 'Busuioc', 'White']

    for i in range(0,4):
        user = models.User(firstName=names[i],
                           surname=surnames[i],
                           username=(names[i]+surnames[i]),
                           email=names[i][0]+surnames[i]+str(89+i)+'@gmail.com',
                           password=bcrypt.hashpw('password'.encode('utf-8'), bcrypt.gensalt()),
                           admin=False)
        db.session.add(user)
        db.session.commit()

@manager.command
def createCourses():
    titles = ['Software Engineering', 'Algorithms', 'Networks', 'Artificial Intellingence', 'Numerical Computation']

    for i in range(0,5):
        course = models.Course(title=titles[i],
                               description='Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.',
                               capacity=5,
                               duration=5,
                               enabled=True)
        db.session.add(course)
        db.session.commit()

    softEng = models.Course.query.get(1)
    softEng.capacity = 2

    algorithms = models.Course.query.get(2)
    algorithms.preRequisiteCourses = 'Networks, Artificial Intellingence'

    db.session.commit()

@manager.command
def createTrainers():
    names = ['Harper', 'Caleb', 'Ella']
    surnames = ['Lewis', 'Harris', 'Clarke']
    streets = ['High Street', 'Station Road', 'Main Street']

    for i in range(0,3):
        trainer = models.Trainer(name=names[i]+' '+surnames[i],
                                 address=str(random.randrange(1,50))+' '+streets[i],
                                 email=names[i][0]+surnames[i]+'@fdm.com',
                                 mobile='07'+str(random.randrange(100000000,999999999)),
                                 enabled=True)
        db.session.add(trainer)
        db.session.commit()

@manager.command
def createRooms():
    names = ['RSLT03', 'RSLT18']
    cities = ['Glasgow', 'Leeds', 'London']
    streets = ['High Street', 'Station Road']
    types = ['Lecture Theatre', 'Seminar Room', 'Teaching Space', 'Computer Cluster']
    facilities = ['Microphone', 'DVD Player', 'Voting System', 'Interactive Monitor', 'Slide Projector', 'Laptop Connection', 'Split Screen']
    paths = ['rslt03.jpg', 'rslt18.jpg']
    boolValues = [True, False]

    for i in range(0,2):
        room = models.Room(name=names[i],
                           city=cities[i%3],
                           address=str(random.randrange(1,50))+' '+streets[i],
                           roomType=types[i%4],
                           capacity=(10+i),
                           facilities=facilities[i],
                           accessibility=boolValues[i%2],
                           roomImage=paths[i],
                           enabled=True)
        db.session.add(room)
        db.session.commit()

@manager.command
def createSchedules():
    numComp = models.Schedule(courseId=5,
                              trainerId=1,
                              roomId=1,
                              startDate=(date.today() + timedelta(days=2)),
                              startTime=8,
                              seatsAvailable=5,
                              waitingList=0,
                              reminderSent=False,
                              enabled=True)
    db.session.add(numComp)

    algorithms = models.Schedule(courseId=2,
                                 trainerId=2,
                                 roomId=2,
                                 startDate=(date.today() + timedelta(days=5)),
                                 startTime=8,
                                 seatsAvailable=5,
                                 waitingList=0,
                                 reminderSent=False,
                                 enabled=True)
    db.session.add(algorithms)

    softEng = models.Schedule(courseId=1,
                              trainerId=3,
                              roomId=1,
                              startDate=(date.today() + timedelta(days=11)),
                              startTime=8,
                              seatsAvailable=0,
                              waitingList=2,
                              reminderSent=False,
                              enabled=True)
    db.session.add(softEng)

    networks = models.Schedule(courseId=3,
                               trainerId=2,
                               roomId=2,
                               startDate=(date.today() + timedelta(days=(-7))),
                               startTime=8,
                               seatsAvailable=3,
                               waitingList=0,
                               reminderSent=False,
                               enabled=True)
    db.session.add(networks)

    artInt = models.Schedule(courseId=4,
                             trainerId=1,
                             roomId=1,
                             startDate=(date.today() + timedelta(days=(-13))),
                             startTime=8,
                             seatsAvailable=4,
                             waitingList=0,
                             reminderSent=False,
                             enabled=True)
    db.session.add(artInt)

    db.session.commit()

@manager.command
def bookUsers():
    numComp = models.Schedule.query.get(1)
    algorithms = models.Schedule.query.get(2)
    softEng = models.Schedule.query.get(3)
    networks = models.Schedule.query.get(4)
    artInt = models.Schedule.query.get(5)

    user89 = models.User.query.get(2)
    user90 = models.User.query.get(3)
    user91 = models.User.query.get(4)
    user92 = models.User.query.get(5)

    softEng.users.append(user89)
    softEng.users.append(user90)
    softEng.usersWaiting.append(user91)
    softEng.usersWaiting.append(user92)

    user89.schedules.append(softEng)
    user90.schedules.append(softEng)
    user91.schedulesWaiting.append(softEng)
    user92.schedulesWaiting.append(softEng)

    networks.users.append(user89)
    networks.users.append(user90)

    user89.schedules.append(networks)
    user90.schedules.append(networks)

    artInt.users.append(user89)

    user89.schedules.append(artInt)

    db.session.commit()

@manager.command
def populateDb():
    createAdmin()
    createUsers()
    createCourses()
    createTrainers()
    createRooms()
    createSchedules()
    bookUsers()



if __name__ == "__main__":
    manager.run()
