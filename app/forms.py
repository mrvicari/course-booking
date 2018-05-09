from flask_wtf import Form
from wtforms import StringField, TextAreaField, validators, PasswordField, BooleanField, StringField, IntegerField, SelectField,SelectMultipleField,widgets
from wtforms.fields.html5 import EmailField, DateField
from wtforms.validators import DataRequired, Length, Email, NumberRange
import datetime

roomTypeData = [('Lecture Theatre', 'Lecture Theatre'),
                ('Seminar Room', 'Seminar Room'),
                ('Teaching Space', 'Teaching Space'),
                ('Computer Cluster', 'Computer Cluster')]

citiesData = [('Glasgow', 'Glasgow'), ('Leeds', 'Leeds'), ('London', 'London')]

class RegisterForm(Form):
    firstName = StringField('firstName', [DataRequired()])
    surname = StringField('surname', [DataRequired()])
    username = StringField('username', [DataRequired(), Length(min=4, max=20)])
    email = EmailField('email', [DataRequired(), Length(min=4, max=35), Email()])
    password = PasswordField('password', [DataRequired(), Length(min=6, max=25)])
    repeatPassword = PasswordField('repeatPassword', [DataRequired(), Length(min=6, max=25)])

class LogInForm(Form):
    usernameOrEmail = StringField('usernameOrEmail', [DataRequired()])
    password = PasswordField('password', [DataRequired()])

class CourseForm(Form):
    title = StringField('title', [DataRequired(), Length(min=4, max=30)])
    description = TextAreaField('description', [DataRequired()])
    capacity = IntegerField('capacity', [DataRequired()])
    duration = IntegerField('duration', [DataRequired(), NumberRange(min=1, max=99)])

class TrainerForm(Form):
    name = StringField('name', [DataRequired(), Length(min=4, max=30)])
    address = StringField('address', [DataRequired(), Length(min=4, max=30)])
    email = EmailField('email', [DataRequired(), Length(min=4, max=35), Email()])
    mobile = StringField('mobile', [DataRequired(), Length(min=4, max=15)])


class RoomForm(Form):
    name = StringField('name', [DataRequired(), Length(min=4, max=30)])
    city = SelectField('city', choices=citiesData)
    address = StringField('address', [DataRequired(), Length(min=4, max=30)])
    roomType = SelectField('roomType', coerce=str, choices=roomTypeData)
    capacity = IntegerField('capacity', [DataRequired()])
    accessibility = BooleanField('accessibility')
    roomImagePath = StringField('image path')

class ScheduleForm(Form):
    course = SelectField('course', coerce=int, choices=[])
    trainer = SelectField('trainer', coerce=int, choices=[])
    room = SelectField('room', coerce=int, choices=[])
    startDate = DateField('startDate')
    startTime = SelectField('startTime', coerce=int, choices=[])

class NewPasswordForm(Form):
    oldPassword = PasswordField('password', [DataRequired(), Length(min=6, max=25)])
    newPassword = PasswordField('password', [DataRequired(), Length(min=6, max=25)])
    repeatNewPassword = PasswordField('password', [DataRequired(), Length(min=6, max=25)])

class NewEmailForm(Form):
    newEmail = EmailField('email', [DataRequired(), Length(min=4, max=35), Email()])
    password = PasswordField('password', [DataRequired(), Length(min=6, max=25)])

class DeleteAccountForm(Form):
    password = PasswordField('password', [DataRequired(), Length(min=6, max=25)])