from app import db
from datetime import datetime
from flask_admin.contrib.sqla import ModelView

ScheduleUser = db.Table('ScheduleUser', db.Model.metadata,
    db.Column('scheduleId', db.Integer, db.ForeignKey('schedule.id')),
    db.Column('userId', db.Integer, db.ForeignKey('user.id'))
)

ScheduleUser2 = db.Table('ScheduleUser2', db.Model.metadata,
    db.Column('scheduleId', db.Integer, db.ForeignKey('schedule.id')),
    db.Column('userId', db.Integer, db.ForeignKey('user.id'))
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(50), unique=False)
    surname = db.Column(db.String(50), unique=False)
    username = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.Unicode(50), unique=False)
    admin = db.Column(db.Boolean, unique=False)
    enabled = db.Column(db.Boolean, unique=False)
    # Add further fields and relationships
    schedules = db.relationship('Schedule', secondary=ScheduleUser)
    schedulesWaiting = db.relationship('Schedule', secondary=ScheduleUser2)
    scheduleId = db.Column(db.Integer, db.ForeignKey('schedule.id'))

    def is_active(self):
        return True

    def get_id(self):
        return str(self.id)

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), unique=True)
    description = db.Column(db.String(200), unique=False)
    capacity = db.Column(db.Integer, unique=False)
    duration = db.Column(db.Integer, unique=False)
    # Add further fields and relationships
    schedules = db.relationship('Schedule', backref='course', lazy='dynamic')
    preRequisiteCourses = db.Column(db.String(200), unique=False)
    bookingRate = db.Column(db.Integer, unique=False)
    enabled = db.Column(db.Boolean, unique=False)

class Trainer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=False)
    address = db.Column(db.String(50), unique=False)
    email = db.Column(db.String(50), unique=True)
    mobile = db.Column(db.String(50), unique=False)
    # Add further fields and relationships
    schedules = db.relationship('Schedule', backref='trainer', lazy='dynamic')
    enabled = db.Column(db.Boolean, unique=False)

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    city = db.Column(db.String(50), unique=False)
    address = db.Column(db.String(50), unique=False)
    roomType = db.Column(db.String(50), unique=False)
    capacity = db.Column(db.Integer, unique=False)
    facilities = db.Column(db.String(50), unique=False)
    accessibility = db.Column(db.Boolean, unique=False)
    # Add further fields and relationships
    schedules = db.relationship('Schedule', backref='room', lazy='dynamic')
    roomImage = db.Column(db.String(300))
    enabled = db.Column(db.Boolean, unique=False)

class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    courseId = db.Column(db.Integer, db.ForeignKey('course.id'))
    trainerId = db.Column(db.Integer, db.ForeignKey('trainer.id'))
    roomId = db.Column(db.Integer, db.ForeignKey('room.id'))
    startDate = db.Column(db.Date, unique=False)
    startTime = db.Column(db.Integer, unique=False)
    seatsAvailable = db.Column(db.Integer, unique=False)
    waitingList = db.Column(db.Integer, unique=False)
    reminderSent = db.Column(db.Boolean, unique=False)
    users = db.relationship('User', secondary=ScheduleUser)
    usersWaiting = db.relationship('User', secondary=ScheduleUser2)
    usersReminded = db.relationship('User', backref='room', lazy='dynamic')
    enabled = db.Column(db.Boolean, unique=False)
