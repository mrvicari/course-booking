from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

app = Flask(__name__)
app.config.from_object('config')

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://///home/csunix/sc15ggb/Desktop/SoftwareProject/koala/app.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../app.db'
app.config['SECRET_KEY'] = 'mysecret'


db = SQLAlchemy(app)

from app import views, models

admin = Admin(app)
admin.add_view(ModelView(models.User, db.session))
admin.add_view(ModelView(models.Course, db.session))
admin.add_view(ModelView(models.Trainer, db.session))
admin.add_view(ModelView(models.Room, db.session))
admin.add_view(ModelView(models.Schedule, db.session))

app.config.update(	MAIL_SERVER='smtp.gmail.com',
                	MAIL_PORT=465,
                	MAIL_USE_SSL=True,
                	MAIL_USERNAME = 'comp2221@gmail.com',
                	MAIL_PASSWORD = 'secret123')
