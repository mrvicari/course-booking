from flask import render_template, request, url_for, flash, redirect, g, abort
from app import app, models, db, login_manager
from .forms import RoomForm, TrainerForm, CourseForm, RegisterForm, LogInForm, ScheduleForm, NewPasswordForm, NewEmailForm, DeleteAccountForm
from .models import Course, Trainer, Room, Schedule
import bcrypt, logging
from flask_login import login_user, login_required, current_user, logout_user
import os
from werkzeug import secure_filename
from datetime import datetime, timedelta, date
from flask_mail import Message, Mail
import json

mail = Mail(app)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static/uploads')
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

'''
********************************************************************************
**                                                                            **
**                               BOTH                                         **
**                                                                            **
********************************************************************************
'''

'''
Show map with available cities as homepage
'''
@app.route('/')
def homepage():
    return render_template("userHomepage.html")

'''
Register a new user to the database
'''
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        userUsername = models.User.query.filter_by(username=form.username.data).first()
        userEmail = models.User.query.filter_by(email=form.email.data).first()
        if userUsername is None and userEmail is None:
            if form.password.data == form.repeatPassword.data:
                password_hash = bcrypt.hashpw(form.password.data.encode('utf-8'), bcrypt.gensalt())
                newUser = models.User(firstName=form.firstName.data,
                                      surname=form.surname.data,
                                      username=form.username.data,
                                      email=form.email.data,
                                      password=password_hash,
                                      admin=False)
                db.session.add(newUser)
                db.session.commit()
                return redirect(url_for('login'))
            else:
                flash("Passwords do not match!")
        else:
            flash("Username or email already exists!")
            form.username.data=""
            form.email.data=""
    return render_template('register.html', title = 'Register', form=form)

'''
Check username and password against db, and log user in if success
'''
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LogInForm()
    if form.validate_on_submit():
        user = models.User.query.filter_by(username=form.usernameOrEmail.data).first()
        if user:
            if user.enabled == False:
                flash("Acount was disabled!")
                return redirect(url_for('login'))
            if bcrypt.checkpw(form.password.data.encode('utf-8'), user.password):
                login_user(user)
                if current_user.admin:
                    return redirect(url_for('administrator'))
                else:
                    return redirect(url_for('homepage'))
            else:
                flash("Wrong Password!")
        else:
            user = models.User.query.filter_by(email=form.usernameOrEmail.data).first()
            if user:
                if user.enabled == False:
                    flash("Acount was disabled!")
                    return redirect(url_for('login'))
                if bcrypt.checkpw(form.password.data.encode('utf-8'), user.password):
                    login_user(user)
                    if current_user.admin:
                        return redirect(url_for('administrator'))
                    else:
                        return redirect(url_for('homepage'))
                else:
                    flash("Wrong Password!")
            else:
                flash("Wrong Username!")
                form.usernameOrEmail.data=""
    return render_template('login.html', title = 'Log In', form=form)

'''
End user session
'''
@app.route('/logout')
@login_required
def logout():
    logout_user();
    return redirect(url_for('login'))

'''
Before every request check if there are any users with courses starting 2 days
from now and send them a reminderSent
'''
@app.before_request
def before_request():
    for schedule in models.Schedule.query.all():
        for user in schedule.users:
            if user not in schedule.usersReminded:
                if (schedule.startDate - timedelta(days=2)) == date.today():
                    try:
                        msg = Message(schedule.course.title + " reminder",
                                     sender="comp2221@gmail.com",
                                     recipients=[user.email])
                        msg.body = "Hello " + user.firstName + ",\n\nYour course " + schedule.course.title + " starts in two days, on " + str(schedule.startDate)
                        mail.send(msg)
                    except Exception as e:
                        print(str(e))
                    schedule.usersReminded.append(user)
                    db.session.commit()

    g.user = current_user

'''
More information about a specific schedule
'''
@app.route('/courses/<int:id>/info')
@login_required
def userSchedulesInfo(id):
    schedule = models.Schedule.query.get(id)
    return render_template('userScheduleDetail.html',schedule=schedule)

'''
Display more details about courses, trainers or rooms
'''
@app.route('/<cmd>/<int:id>/info')
@login_required
def infoItem(cmd,id):
    if cmd == 'course':
        return render_template('adminCourseDetail.html',course=models.Course.query.get(id))
    elif cmd == 'trainer':
        return render_template('adminTrainerDetail.html',trainer=models.Trainer.query.get(id))
    elif cmd == 'room':
        roomItem = models.Room.query.get(id)
        image = roomItem.roomImage
        imageList = image.split()
        numOfImages = len(imageList)
        imagePaths = []
        for i in range(numOfImages):
            imagePath = '../../static/uploads/'+imageList[i]
            imagePaths.append(imagePath)
        return render_template('adminRoomDetail.html',room=models.Room.query.get(id),item = numOfImages,img = imagePaths)

'''
View a month long calendar for a specific room showing when room is busy
'''
@app.route('/room/<int:id>/schedule')
@login_required
def roomSchedule(id):
    totalSchedule=[]
    filename=(os.path.join(APP_ROOT, 'static/calendar/roomSchedule.json'))
    dir = os.path.dirname(filename)
    schedule=models.Schedule.query.filter_by(roomId=id)
    roomName=models.Room.query.get(id).name
    with open(filename, "w") as outfile:
        if schedule != None:
            for x in schedule:
                roomSchedule={'title':'','start':'','end':'','url':''}
                if x.startTime < 10:
                    startTime='0'+str(x.startTime)
                    endTime='0'+str(x.startTime+1)
                else:
                    startTime=str(x.startTime)
                    endTime=str(x.startTime+1)
                roomSchedule['title']=startTime+':00 '+x.course.title
                roomSchedule['start']=str(x.startDate)
                roomSchedule['end']=str(x.startDate + timedelta(days=x.course.duration))
                roomSchedule['url']='/courses/'+str(x.id)+'/info'
                totalSchedule.append(roomSchedule)
            json.dump(totalSchedule, outfile, indent=4)
        else:
            json.dump(totalSchedule, outfile, indent=4)

    return render_template('adminScheduleCalendar.html',roomName=roomName)

'''
********************************************************************************
**                                                                            **
**                                  USER                                      **
**                                                                            **
********************************************************************************
'''

'''
View all available courses in the future. Organised by city and sorted by date
'''
@app.route('/courses/<city>')
@login_required
def userCoursePage(city):
    if city != 'Leeds' and city != 'London' and city != 'Glasgow':
        abort(404)

    allSchedules = models.Schedule.query.all()
    leedsSchedules = []
    londonSchedules = []
    glasgowSchedules = []

    for sch in allSchedules:
        if sch.room.city == 'Leeds' and sch.startDate >= date.today():
            leedsSchedules.append(sch)
        if sch.room.city == 'London' and sch.startDate >= date.today():
            londonSchedules.append(sch)
        if sch.room.city == 'Glasgow' and sch.startDate >= date.today():
            glasgowSchedules.append(sch)

    return render_template('userCourseLists.html', city=city,
                                                   leedsSchedules=sorted(leedsSchedules, key=lambda x: x.startDate),
                                                   londonSchedules=sorted(londonSchedules, key=lambda x: x.startDate),
                                                   glasgowSchedules=sorted(glasgowSchedules, key=lambda x: x.startDate))

'''
Check whether a user should be allowed to book a course (pre-reqs, timetable clash, etc.)
'''
@app.route('/book/<city>/<scheduleID>/<userID>/check')
@login_required
def bookCheck(scheduleID, userID, city):
    user = models.User.query.get(userID)
    schedule = models.Schedule.query.get(scheduleID)
    userCourses = []

    if user in schedule.users:
        flash("You have already booked a place in this course!")
        return redirect(url_for('userCoursePage', city=city))

    PRCs = schedule.course.preRequisiteCourses
    if PRCs is not None:
        PRClist = PRCs.split(", ")
    else:
        PRClist = []

    for userSch in user.schedules:
        if userSch.startDate + timedelta(days=userSch.course.duration) < date.today():
            userCourses.append(userSch.course.title)

    if PRClist is not None:
        for course in PRClist:
            if course not in userCourses:
                flash('You need to complete ' + course + ' first!!')
                return redirect(url_for('userCoursePage', city=city))

    for userSch in user.schedules:
        if (userSch.startDate <= schedule.startDate <= (userSch.startDate + timedelta(days=userSch.course.duration))):
            flash('You are busy during this course!')
            return redirect(url_for('userCoursePage', city=city))
        elif (userSch.startDate <= (schedule.startDate + timedelta(days=schedule.course.duration)) <= (userSch.startDate + timedelta(days=userSch.course.duration))):
            flash('You are busy during this course!')
            return redirect(url_for('userCoursePage', city=city))
        elif (schedule.startDate <= userSch.startDate <= (schedule.startDate + timedelta(days=schedule.course.duration))):
            flash('You are busy during this course!')
            return redirect(url_for('userCoursePage', city=city))
        elif (schedule.startDate <= (userSch.startDate + timedelta(days=userSch.course.duration)) <= (schedule.startDate + timedelta(days=schedule.course.duration))):
            flash('You are busy during this course!')
            return redirect(url_for('userCoursePage', city=city))

    return redirect(url_for('book', city=city, scheduleID=scheduleID, userID=userID))

'''
Book a user in a course or place on waiting list if full
'''
@app.route('/book/<city>/<scheduleID>/<userID>/')
@login_required
def book(scheduleID, userID, city):
    user = models.User.query.get(userID)
    schedule = models.Schedule.query.get(scheduleID)

    if schedule.seatsAvailable > 0:
        schedule.users.append(user)
        user.schedules.append(schedule)

        schedule.seatsAvailable = schedule.course.capacity - len(schedule.users)

        try:
            msg = Message(schedule.course.title + " booking",
                         sender="comp2221@gmail.com",
                         recipients=[user.email])
            msg.body = "Hello " + current_user.firstName + ",\n\nYou have booked a place in " + schedule.course.title + ". Which starts on " + str(schedule.startDate)
            mail.send(msg)
        except Exception as e:
            print(str(e))

        db.session.commit()

    elif schedule.seatsAvailable <= 0 and user not in schedule.users:
        if user not in schedule.usersWaiting:
            schedule.usersWaiting.append(user)
            user.schedulesWaiting.append(schedule)

            schedule.waitingList = 0 + len(schedule.usersWaiting)

            try:
                msg = Message(schedule.course.title + " waiting list",
                             sender="comp2221@gmail.com",
                             recipients=[user.email])
                msg.body = "Hello " + current_user.firstName + ",\n\nYou have been placed in the waiting list for " + schedule.course.title + ". Which starts on " + str(schedule.startDate)
                mail.send(msg)
            except Exception as e:
                print(str(e))

            db.session.commit()
    return redirect(url_for('userCoursePage', city=city))

'''
View all courses a user has completed or has booked for the future. Organised by city or waiting list and sorted by date
'''
@app.route('/my_courses/<city>/<time>')
@login_required
def userCourses(city, time):
    if city == 'Leeds' or city == 'London' or city == 'Glasgow' or city == 'All' or city == 'Waiting':
        user = models.User.query.get(current_user.id)

        bookedCoursesPast = []
        waitingCoursesPast = []
        leedsSchedulesPast = []
        londonSchedulesPast = []
        glasgowSchedulesPast = []

        bookedCoursesFuture = []
        waitingCoursesFuture = []
        leedsSchedulesFuture = []
        londonSchedulesFuture = []
        glasgowSchedulesFuture = []

        for sch in user.schedules:
            if (sch.startDate+ timedelta(days=sch.course.duration)) < date.today():
                bookedCoursesPast.append(sch)
                if sch.room.city == 'Leeds':
                    leedsSchedulesPast.append(sch)
                elif sch.room.city == 'London':
                    londonSchedulesPast.append(sch)
                elif sch.room.city == 'Glasgow':
                    glasgowSchedulesPast.append(sch)

            elif (sch.startDate+ timedelta(days=sch.course.duration)) >= date.today():
                bookedCoursesFuture.append(sch)
                if sch.room.city == 'Leeds':
                    leedsSchedulesFuture.append(sch)
                elif sch.room.city == 'London':
                    londonSchedulesFuture.append(sch)
                elif sch.room.city == 'Glasgow':
                    glasgowSchedulesFuture.append(sch)


        for schW in user.schedulesWaiting:
            if schW.startDate < date.today():
                waitingCoursesPast.append(schW)
            elif schW.startDate >= date.today():
                waitingCoursesFuture.append(schW)


        return render_template('userBookedCourses.html', time=time,
                                                         city=city,
                                                         bookedCoursesPast=bookedCoursesPast,
                                                         waitingCoursesPast=waitingCoursesPast,
                                                         leedsSchedulesPast=leedsSchedulesPast,
                                                         londonSchedulesPast=londonSchedulesPast,
                                                         glasgowSchedulesPast=glasgowSchedulesPast,
                                                         bookedCoursesFuture=bookedCoursesFuture,
                                                         waitingCoursesFuture=waitingCoursesFuture,
                                                         leedsSchedulesFuture=leedsSchedulesFuture,
                                                         londonSchedulesFuture=londonSchedulesFuture,
                                                         glasgowSchedulesFuture=glasgowSchedulesFuture)

    else:
        abort(404)

'''
Cancel booking for a course, in case of there being someone on the waiting list: book a place for them in the course
'''
@app.route('/my_courses/<cmd>/<int:id>/remove')
@login_required
def userCoursesRemove(cmd,id):

    schedule = models.Schedule.query.get(id)
    print(schedule.course.title)
    user = models.User.query.get(current_user.id)
    if cmd == 'Leeds' or cmd == 'London' or cmd == 'Glasgow' or cmd=='All':
        user.schedules.remove(schedule)

        if schedule.usersWaiting:
            moveUser = schedule.usersWaiting.pop(0)
            schedule.users.append(moveUser)

        schedule.seatsAvailable = schedule.course.capacity - len(schedule.users)
        schedule.waitingList = 0 + len(schedule.usersWaiting)

        db.session.commit()
        try:
            msg = Message(schedule.course.title + " booking",
                         sender="comp2221@gmail.com",
                         recipients=[user.email])
            msg.body = "Hello " + current_user.firstName + ",\n\nA place has been made available in " + schedule.course.title + ". As you were first on the waiting list, this place is now yours. The course starts on " + str(schedule.startDate)
            mail.send(msg)
            print(schedule.course.title)
        except Exception as e:
            print(str(e))


        return redirect(url_for('userCourses', city=cmd, time='future'))

    elif cmd == 'Waiting':
        user.schedulesWaiting.remove(schedule)

        schedule.seatsAvailable = schedule.course.capacity - len(schedule.users)
        schedule.waitingList = 0 + len(schedule.usersWaiting)

        db.session.commit()

        return redirect(url_for('userCourses', city=cmd, time='future'))

'''
View information about user
'''
@app.route('/profile')
@login_required
def userProfile():
    return render_template('userProfile.html')

'''
Allow user to change their password or email
'''
@app.route('/profile/change/<cmd>', methods=['GET', 'POST'])
@login_required
def userChange(cmd):
    user = models.User.query.get(current_user.id)
    if cmd == "email":
        allUsers = models.User.query.all()
        form = NewEmailForm()
        if form.validate_on_submit():
            if bcrypt.checkpw(form.password.data.encode('utf-8'), user.password):
                checkUserEmail = models.User.query.filter_by(email=form.newEmail.data)
                if checkUserEmail is None:
                    user.email = form.newEmail.data
                    db.session.commit()
                    return redirect(url_for('userProfile'))
                else:
                    flash("Email is already registered!")
            else:
                flash("Incorrect password!")
    if cmd == "password":
        form = NewPasswordForm()
        if form.validate_on_submit():
            if bcrypt.checkpw(form.oldPassword.data.encode('utf-8'), user.password):
                if form.newPassword.data == form.repeatNewPassword.data:
                    user.password = bcrypt.hashpw(form.newPassword.data.encode('utf-8'), bcrypt.gensalt())
                    db.session.commit()
                    return redirect(url_for('userProfile'))
                else:
                    flash("Passwords do not match!")
            else:
                flash("Incorrect current password!")
    if cmd == "delete":
        form = DeleteAccountForm()
        if form.validate_on_submit():
            if bcrypt.checkpw(form.password.data.encode('utf-8'), user.password):
                user.enabled=False
                db.session.commit()
                logout_user()
                return redirect(url_for('homepage'))
            else:
                flash("Incorrect password!")
    return render_template('userChange.html',form=form, cmd=cmd)

'''
********************************************************************************
**                                                                            **
**                                  ADMIN                                     **
**                                                                            **
********************************************************************************
'''

'''
Redirect user to administrator course page if user is admin
'''
@app.route('/administrator')
@login_required
def administrator():
    if current_user.admin:
        return redirect(url_for('adminCourse'))
    else:
        return redirect(url_for('homepage'))

'''
List all courses with the option to add a new one or view more/edit/remove an existing one
'''
@app.route('/administrator/course')
@login_required
def adminCourse():

    allSchedules = models.Schedule.query.all()
    allCourses = models.Course.query.all()
    for course in allCourses:
        timesScheduled = 0
        totalBookings = 0
        totalAvailable = 0
        for sch in allSchedules:
            if course.title == sch.course.title:
                timesScheduled += 1

                totalBookings += ((sch.seatsAvailable + len(sch.users)) - sch.seatsAvailable + sch.waitingList)
                totalAvailable += (sch.seatsAvailable + len(sch.users))

        if totalAvailable > 0:
            course.bookingRate = round((totalBookings/totalAvailable)*100, 2)
        else:
            course.bookingRate = 0
    db.session.commit()


    if current_user.admin:
        return render_template('adminCourse.html', items = models.Course.query.filter_by(enabled=True))
    else:
        return redirect(url_for('homepage'))

'''
List all trainers with the option to add a new one or view more/edit/remove an existing one
'''
@app.route('/administrator/trainer')
@login_required
def adminTrainer():
    if current_user.admin:
        return render_template('adminTrainer.html', items = models.Trainer.query.filter_by(enabled=True))
    else:
        return redirect(url_for('homepage'))

'''
List all rooms with the option to add a new one or view more/edit/remove an existing one
'''
@app.route('/administrator/room')
@login_required
def adminRoom():
    if current_user.admin:
        return render_template('adminRoom.html', items = models.Room.query.filter_by(enabled=True))
    else:
        return redirect(url_for('homepage'))

'''
List all schedules with the option to view more/edit/remove a specific one
'''
@app.route('/administrator/schedule')
@login_required
def adminSchedule():
    if current_user.admin:
        schedules = models.Schedule.query.filter_by(enabled=True)
    else:
        return redirect(url_for('homepage'))
    return render_template('adminSchedule.html', schedules=schedules)

'''
View a list of all delegates booked in a schedule or in the waiting list
'''
@app.route('/administrator/schedule/<scheduleID>/info/<users>')
@login_required
def adminSchedulesInfo(scheduleID, users):
    schedule = models.Schedule.query.get(scheduleID)
    return render_template('adminScheduleDelegates.html', schedule=schedule, delegatesToList=users)

'''
List all delegate with the option to view all courses a specific delagate is involved in
'''
@app.route('/administrator/delegate')
@login_required
def adminDelegate():
    if current_user.admin:
        return render_template('adminDelegate.html', items = models.User.query.filter_by(admin=False))
    else:
        return redirect(url_for('homepage'))

'''
Display all courses past or present that a given delegate is involved in
'''
@app.route('/administrator/delegate/<delegateID>/courses/<time>')
@login_required
def adminDelegateInfo(delegateID, time):
    delegate = models.User.query.get(delegateID)

    pastSchedules = []
    futureSchedules = []

    for sch in delegate.schedules:
        if sch.startDate < date.today():
            pastSchedules.append(sch)
        elif sch.startDate >= date.today():
            futureSchedules.append(sch)

    return render_template('adminDelegateDetail.html', delegate=delegate,
                                                       time=time,
                                                       pastSchedules=pastSchedules,
                                                       futureSchedules=futureSchedules)

'''
Create a new course with data from a form
'''
@app.route('/administrator/course/add', methods=['GET', 'POST'])
@login_required
def adminCourseAdd():
    if current_user.admin:
        form = CourseForm()
        if form.validate_on_submit():
            newCourse = models.Course.query.filter_by(title=form.title.data).first()
            listOfPreRequisiteCourses = ', '.join(request.form.getlist('preRequisite'))
            if newCourse is None:
                newCourse = models.Course(title=form.title.data,
                                          description=form.description.data,
                                          capacity=form.capacity.data,
                                          duration=form.duration.data,
                                          preRequisiteCourses=listOfPreRequisiteCourses,
                                          bookingRate=0,
                                          enabled=True)
                db.session.add(newCourse)
                db.session.commit()
                flash('New course created!')
                return redirect(url_for('adminCourseAdd'))
            elif newCourse.enabled == False:
                newCourse.enabled = True
                newCourse.description = form.description.data
                newCourse.capacity = form.capacity.data
                newCourse.duration=form.duration.data
                newCourse.preRequisiteCourses=listOfPreRequisiteCourses
                db.session.commit()
            else:
                flash(form.title.data + " already exists!")
    return render_template('adminCourseAdd.html',
                           title='Course management',
                           courses=models.Course.query.filter_by(enabled=True),
                           form=form)

'''
Create a new trainer with data from a form
'''
@app.route('/administrator/trainer/add', methods=['GET', 'POST'])
@login_required
def adminTrainerAdd():
    if current_user.admin:
        form = TrainerForm()
        trainerLists = models.Trainer.query.all()
        if form.validate_on_submit():
            for trainer in trainerLists:
                if trainer.enabled == False and trainer.email == form.email.data:
                    trainer.enabled = True
                    trainer.name = form.name.data
                    trainer.mobile = form.mobile.data
                    trainer.address = form.address.data
                    db.session.commit()
                    return redirect(url_for('adminTrainer'))
                elif trainer.email == form.email.data:
                    flash('There is same trainer on list')
                    break

                else:
                    newTrainer = models.Trainer(name=form.name.data,
                                                address=form.address.data,
                                                email=form.email.data,
                                                mobile=form.mobile.data,
                                                enabled = True)
                    db.session.add(newTrainer)
                    db.session.commit()
                    flash('New Trainer registered!')
                    return redirect(url_for('adminTrainer'))

    return render_template('adminTrainerAdd.html',
                           title='Trainer management',
                           trainers=models.Trainer.query.filter_by(enabled=True),
                           form=form)

'''
Create a new room with data from a form
'''
@app.route('/administrator/room/add', methods=['GET', 'POST'])
@login_required
def adminRoomAdd():
    if current_user.admin:
        form = RoomForm()
        filenames = []
        facilities = ['Microphone', 'DVD Player', 'Voting System', 'Interactive Monitor', 'Slide Projector', 'Laptop Connection', 'Split Screen']

        if request.method == 'POST':
            uploaded_files = request.files.getlist("file[]")
            for file in uploaded_files:
                filename = secure_filename(file.filename)
                if filename == '':
                    return redirect(url_for('adminRoomAdd'))
                else:
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    filenames.append(filename)

        roomLists = models.Room.query.all()
        if form.validate_on_submit():
            listOfFaclilties = ', '.join(request.form.getlist('facilities'))
            listOfImages = ' '.join(filenames)
            for room in roomLists:
                if room.enabled == False and room.name == form.name.data:
                    room.enabled = True
                    room.city=form.city.data
                    room.address=form.address.data
                    room.roomType=form.roomType.data
                    room.capacity=form.capacity.data
                    room.facilities=listOfFaclilties
                    room.accessibility=form.accessibility.data
                    room.roomImage=listOfImages
                    db.session.commit()
                    return redirect(url_for('adminRoom'))
                elif room.name == form.name.data:
                    flash('There is same room name on list')
                    break
                else:
                    newRoom = models.Room(name=form.name.data,
                                            city=form.city.data,
                                            capacity=form.capacity.data,
                                            roomType=form.roomType.data,
                                            address=form.address.data,
                                            facilities=listOfFaclilties,
                                            accessibility=form.accessibility.data,
                                            roomImage=listOfImages,
                                            enabled=True)
                    db.session.add(newRoom)
                    db.session.commit()
                    flash('New Room registered!')
                    return redirect(url_for('adminRoom'))

    return render_template('adminRoomAdd.html',
                           title='Room management',
                           rooms=models.Room.query.filter_by(enabled=True),
                           facilities = facilities,
                           form=form)

'''
Create a new schedule by using a course, a trainer, a room and giving it a start date/time
'''
@app.route('/administrator/schedule/<city>/add', methods=['GET', 'POST'])
@login_required
def adminScheduleAdd(city):
    if current_user.admin:
        form = ScheduleForm()
        form.course.choices = [(course.id, course.title) for course in models.Course.query.filter_by(enabled=True).order_by(models.Course.title)]
        form.trainer.choices = [(trainer.id, trainer.name) for trainer in models.Trainer.query.filter_by(enabled=True).order_by(models.Trainer.name)]
        form.room.choices = [(room.id, room.name) for room in models.Room.query.filter_by(city=city,enabled=True).order_by(models.Room.name)]
        form.startTime.choices = [(time, str(time) + ':00') for time in range(8, 18)]
        if form.validate_on_submit():

            isRoomFree = True
            isTrainerFree = True

            newSchedule = models.Schedule(courseId=form.course.data,
                                          trainerId=form.trainer.data,
                                          roomId=form.room.data,
                                          startDate=form.startDate.data,
                                          startTime=form.startTime.data,
                                          seatsAvailable=models.Course.query.get(form.course.data).capacity,
                                          waitingList=0,
                                          enabled=True)

            newScheduleTrainer = models.Trainer.query.get(form.trainer.data)

            for sch in newScheduleTrainer.schedules:
                if sch.startDate <= form.startDate.data <= (sch.startDate + timedelta(days=sch.course.duration)):
                    flash("Trainer is busy!")
                    isTrainerFree = False
                elif sch.startDate <= (form.startDate.data + timedelta(days=models.Course.query.get(form.course.data).duration)) <= (sch.startDate + timedelta(days=sch.course.duration)):
                    flash("Trainer is busy!")
                    isTrainerFree = False

            newScheduleRoom = models.Room.query.get(form.room.data)

            for sch in newScheduleRoom.schedules:
                if sch.startDate <= form.startDate.data <= (sch.startDate + timedelta(days=sch.course.duration)):
                    flash("Room is busy!")
                    isRoomFree = False
                elif sch.startDate <= (form.startDate.data + timedelta(days=models.Course.query.get(form.course.data).duration)) <= (sch.startDate + timedelta(days=sch.course.duration)):
                    flash("Room is busy!")
                    isRoomFree = False

            newScheduleCourse = models.Course.query.get(form.course.data)
            if newScheduleRoom.capacity < newScheduleCourse.capacity:
                flash("The capacity of the room is less than the capacity of the course!")
                isRoomFree = False


            if isTrainerFree and isRoomFree:
                db.session.add(newSchedule)
                db.session.commit()
                return redirect(url_for('adminSchedule'))

    else:
        return redirect(url_for('homepage'))
    return render_template('adminScheduleAdd.html', form=form, pageHeader="Schedule a course")

'''
Allow admins to edit details for existing courses, trainers or rooms
'''
@app.route('/administrator/<cmd>/<int:id>/edit', methods=['GET','POST'])
@login_required
def editItem(cmd,id):
    if current_user.admin:
        if cmd == 'course':
            courseItem = models.Course.query.get(id)
            form = CourseForm(obj=courseItem)

            if courseItem.preRequisiteCourses != None:
                checkedPreRequisiteCourse = courseItem.preRequisiteCourses.split(", ")
            else:
                checkedPreRequisiteCourse = ""

            if form.validate_on_submit():
                courseItem.title = form.title.data
                courseItem.description = form.description.data
                courseItem.duration = form.duration.data
                courseItem.capacity = form.capacity.data
                listOfPreRequisiteCourses = ', '.join(request.form.getlist('preRequisite'))
                courseItem.preRequisiteCourses = listOfPreRequisiteCourses
                db.session.add(courseItem)
                db.session.commit()
                return redirect(url_for('adminCourse'))
            return render_template('adminCourseEdit.html', courses=models.Course.query.all(),
                                                           checkedPreRequisiteCourse=checkedPreRequisiteCourse,
                                                           course=models.Course.query.get(id),
                                                           form=form)
        elif cmd == 'trainer':
            oneTrainer = models.Trainer.query.get(id)
            form = TrainerForm(obj=oneTrainer)
            if form.validate_on_submit():
                oneTrainer.name=form.name.data
                oneTrainer.address=form.address.data
                oneTrainer.email=form.email.data
                oneTrainer.mobile=form.mobile.data
                db.session.add(oneTrainer)
                db.session.commit()
                return redirect(url_for('adminTrainer'))
            return render_template('adminTrainerEdit.html',
                                   trainer=models.Trainer.query.get(id),
                                   form=form)
        elif cmd == 'room':
            roomItem = models.Room.query.get(id)
            form = RoomForm(obj=roomItem)
            image = roomItem.roomImage
            imageList = image.split()
            numOfImages = len(imageList)
            imagePaths = []
            removeImgPath = ""
            filenames = []
            facilities = ['Microphone', 'DVD Player', 'Voting System', 'Interactive Monitor', 'Slide Projector', 'Laptop Connection', 'Split Screen']

            if models.Course.query.get(id).preRequisiteCourses != None:
                currentFacilities = roomItem.facilities.split(", ")
            else:
                currentFacilities=[]

            print(currentFacilities)

            if form.validate_on_submit():
                if imagePaths != []:
                    for i in range(numOfImages):
                        removeImgPath = secure_filename(imageList[i])
                        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], removeImgPath))
                uploaded_files = request.files.getlist("file[]")
                for file in uploaded_files:
                    filename = secure_filename(file.filename)
                    if filename != '':
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                        filenames.append(filename)
                    else:
                        for i in range(0,numOfImages):
                            filenames.append(secure_filename(imageList[i]))

                listOfImages = ' '.join(filenames)
                roomItem.name=form.name.data
                roomItem.city=form.city.data
                roomItem.address=form.address.data
                roomItem.roomType=form.roomType.data
                roomItem.capacity=form.capacity.data
                listOfFaclilties = ', '.join(request.form.getlist('facilities'))
                roomItem.facilities=listOfFaclilties
                roomItem.accessibility=form.accessibility.data
                roomItem.roomImage = listOfImages
                db.session.add(roomItem)
                db.session.commit()
                return redirect(url_for('adminRoom'))
            return render_template('adminRoomEdit.html',
                                   room=models.Room.query.get(id),
                                   form=form,
                                   items=len(currentFacilities),
                                   currentFacilities = currentFacilities,
                                   facilities = facilities)
        elif cmd == 'schedule':
            form = ScheduleForm()
            scheduleItem = models.Schedule.query.get(id)
            form.course.choices = [(course.id, course.title) for course in models.Course.query.order_by(models.Course.title)]
            form.trainer.choices = [(trainer.id, trainer.name) for trainer in models.Trainer.query.order_by(models.Trainer.name)]
            form.room.choices = [(room.id, room.name) for room in models.Room.query.order_by(models.Room.name)]
            form.startTime.choices = [(time, str(time) + ':00') for time in range(8, 18)]

            # form = ScheduleForm(obj=scheduleItem)
            if request.method == 'GET':
                form.course.data = scheduleItem.course.id
                form.trainer.data = scheduleItem.trainer.id
                form.room.data = scheduleItem.room.id
                form.startDate.data = scheduleItem.startDate
                form.startTime.data = scheduleItem.startTime

            if form.validate_on_submit():
                scheduleItem.courseId = form.course.data
                scheduleItem.trainerId = form.trainer.data
                scheduleItem.roomId = form.room.data
                scheduleItem.startDate = form.startDate.data
                scheduleItem.startTime = form.startTime.data

                db.session.commit()
                return redirect(url_for('adminSchedule'))
            return render_template('adminScheduleAdd.html',
                                   schedule=models.Schedule.query.get(id),
                                   form=form,
                                   pageHeader="Edit a scheduled course")
    else:
        flash("You don't have any permission to edit.")
        return redirect(url_for('administrator'))

    return redirect(url_for('administrator'))

'''
Remove a specific course, trainer, room or schedule
'''
@app.route('/administrator/<cmd>/<int:id>/remove')
@login_required
def removeItem(cmd,id):
    if current_user.admin:
        if cmd == 'course':
            scheduled = False
            allSchedules = models.Schedule.query.all()
            course = models.Course.query.get(id)
            for sch in allSchedules:
                if sch.course.title == course.title:
                    scheduled = True
            if scheduled:
                course.enabled = False
                db.session.commit()
            else:
                db.session.delete(course)
                db.session.commit()
            return redirect(url_for('adminCourse'))
        elif cmd == 'trainer':
            scheduled = False
            allSchedules = models.Schedule.query.all()
            trainer = models.Trainer.query.get(id)
            for sch in allSchedules:
                if sch.trainer.email == trainer.email:
                    scheduled = True
            if scheduled:
                trainer.enabled = False
                db.session.commit()
            else:
                db.session.delete(trainer)
                db.session.commit()
            return redirect(url_for('adminTrainer'))
        elif cmd == 'room':
            scheduled = False
            allSchedules = models.Schedule.query.all()
            room = models.Room.query.get(id)
            for sch in allSchedules:
                if sch.room.name == room.name:
                    scheduled = True
            if scheduled:
                room.enabled = False
                db.session.commit()
            else:
                deleteItem = models.Room.query.get(id)
                originalImgPath = deleteItem.roomImage
                tempImgPath = ""
                if originalImgPath != "":
                    tempImgPath = secure_filename(originalImgPath)
                    if "_" in tempImgPath:
                        imgFiles = tempImgPath.split("_")
                        for imgFile in imgFiles:
                            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], imgFile))
                    else:
                        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], tempImgPath))
                db.session.delete(deleteItem)
                db.session.commit()
            return redirect(url_for('adminRoom'))
        elif cmd =='schedule':
            deleteItem = models.Schedule.query.get(id)
            db.session.delete(deleteItem)
            db.session.commit()
            return redirect(url_for('adminSchedule'))
    else:
        flash("You don't have any permission to delete.")
        return redirect(url_for('administrator'))

'''
********************************************************************************
**                                                                            **
**                                  EXTRA                                     **
**                                                                            **
********************************************************************************
'''

'''
Login user and get its data from database
'''
@login_manager.user_loader
def load_user(id):
    return models.User.query.get(int(id))

'''
Specify allowed file extensions for uploads
'''
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

'''
Save uploaded files to server side folder
'''
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)
