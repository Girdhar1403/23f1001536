from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
db = SQLAlchemy()

app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///placementportal.db'
app.secret_key='GIRDHAR'
# have to fire a secret key while using session.
db.init_app(app)

# trublent ORM is class
# @func1(func2)
''' create table sponsor (id primary key, name varchar (20))
   adsf
'''


class Company(db.Model):
    company_id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String, unique = True, nullable = False)
    password = db.Column(db.String, nullable = False)
    Company_name = db.Column(db.String, nullable = False)
    hr_contact = db.Column(db.String, nullable = False)
    sector = db.Column(db.String, nullable = False)
    c_address = db.Column(db.String, nullable = False)
    Website = db.Column(db.String)
    status = db.Column(db.Boolean, default = False)
    status2 = db.Column(db.Boolean, default = True)
    drives = db.relationship('Drive', backref='company', lazy = True, cascade = 'all, delete-orphan')

class Student(db.Model):
    student_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique = True, nullable = False)
    password = db.Column(db.String, nullable = False)  
    name = db.Column(db.String) 
    status = db.Column(db.Text, default = "Pending")
    Father_name = db.Column(db.String) 
    qualifications = db.Column(db.String)
    stream = db.Column(db.String)
    CGPA = db.Column(db.Float)
    Experience = db.Column(db.String)
    applications = db.relationship('Application', backref = 'student', lazy = True, cascade = 'all, delete-orphan')


class Drive(db.Model):
    drive_id = db.Column(db.Integer, primary_key = True)
    job_title = db.Column(db.String, nullable = False)
    job_description = db.Column(db.String)
    eligibility_criteria = db.Column(db.String, nullable = False)
    start_date = db.Column(db.Date)
    deadline = db.Column(db.Date)
    status = db.Column(db.String, default = 'Pending')
    status_open = db.Column(db.String, default = 'Open')
    company_id = db.Column(db.Integer, db.ForeignKey(Company.company_id))
    applications = db.relationship('Application', backref = 'drive', lazy = True, cascade = 'all, delete-orphan')

class Admin(db.Model):
    admin_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique = True, nullable = False)
    password = db.Column(db.String, nullable = False)  

class Application(db.Model):
    application_id = db.Column(db.Integer, primary_key=True)
    payment = db.Column(db.Integer)
    application_date = db.Column(db.Date)
    drive_id = db.Column(db.Integer, db.ForeignKey(Drive.drive_id))
    student_id = db.Column(db.Integer, db.ForeignKey(Student.student_id))
    status = db.Column(db.String, default = 'Applied')

    
with app.app_context():
    db.create_all()
    if not Admin.query.first():
        admin = Admin(username="admin",password="1234")
        db.session.add(admin)
        db.session.commit()
    
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    pending_company = Company.query.filter_by(status = False).all()
    print(pending_company)
    approved_company = Company.query.filter_by(status = True, status2 = True).all()
    print(approved_company)
    blacklisted_company = Company.query.filter_by(status = True, status2 = False).all()

    no_company = Company.query.count()
    no_student = Student.query.count()
    no_application = Application.query.count()
    no_drive = Drive.query.count()
    return render_template('admin_dashboard.html', pending_company = pending_company, approved_company = approved_company,
                           no_company = no_company, 
                           no_application = no_application,
                           no_student = no_student,
                           no_drive = no_drive,
                           blacklisted_company =blacklisted_company)

@app.route('/registerstudent', methods = ['GET','POST'])
def registerstudent():
    if request.method == 'GET':
        return render_template('registerstudent.html')
    #else
    if request.method == 'POST':
        usrname = request.form.get('username')
        pswd = request.form.get('password')
        name = request.form.get('name')
        F_name = request.form.get('F_name')
        qualifications = request.form.get('qualifications')
        stream = request.form.get('stream')
        CGPA = request.form.get('CGPA')
        Experience = request.form.get('Experience')

        # insert into student (username, password) values ('girdhar','girdhar')
        student = Student(username = usrname, password = pswd, name = name,
                          Father_name = F_name,
                          qualifications = qualifications,
                          stream = stream,
                          CGPA = CGPA,
                          Experience = Experience)
        db.session.add(student)
        db.session.commit()
        return redirect('/login')
        
        # Student = 
@app.route('/registercompany', methods = ['GET','POST'])
def registercompany():
    if request.method == 'GET':
        return render_template('registercompany.html')
    #else
    if request.method == 'POST':
        usrname = request.form.get('username')
        pswd = request.form.get('password')
        cname = request.form.get('cname')
        website = request.form.get('website')
        hr_contact = request.form.get('hr_contact')
        sector = request.form.get('sector')
        address = request.form.get('address')


# insert into student (username, password) values ('girdhar','girdhar')
        company = Company(username = usrname, password = pswd,
                          Company_name = cname,
                          Website = website,
                          hr_contact = hr_contact,
                          sector = sector,
                          c_address = address)
        db.session.add(company)
        db.session.commit()
        return redirect('/login')

# @ is Deocratro take function as an argument
@app.route('/login', methods = ["GET", "POST"])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        user = request.form.get('user')
        usrname = request.form.get('username')
        pswd = request.form.get('password')
        # print(user)
        # print(type(Student.query.filter_by(username = usrname)))
    # Select * from student where username = 'girdhar'
        if user == 'admin':
            admin = Admin.query.filter_by(username = usrname,).first()# .first() will get the first row with same entry
            if admin:
                #record.column
                if admin.password == pswd:
                    session['admin_id'] = admin.admin_id # record.column name
                    return redirect('/admin_dashboard')
                else:
                    return "Incorrect Password"
            else:
                return "You are not registered as Admin"
        if user == 'student':
            student = Student.query.filter_by(username = usrname).first()# .first() will get the first row with same entry
            print(student)
            if student:
                if student.status == "Pending":
                    return "You are still not approved by Admin, Please wait till approval"
                if student.status == "Blacklisted":
                    return "You are rejected or Blacklisted by the admin"
                #record.column
                if student.password == pswd:
                    session['student_id'] = student.student_id # record.column name
                    return redirect('/student_dashboard')
                else:
                    return "Incorrect Password"
            else:
                return "Please register"
        if user == 'company':
            # print('133')
            company = Company.query.filter_by(username = usrname).first()
            print(company)
            if company:
                #record.column
                if company.status == False:
                    return "Your application status is pending"
                if company.status2 == False:
                    return "You have been Blocked by the admin"
                if company.password == pswd:
                    session['company_id'] = company.company_id # record.column name
                    return redirect('/company_dashboard')
                else:
                    return "Incorrect Password"
            else: 
                return "Please register"
            
# first username is column name and 2nd one is variable (value you entered)
@app.route('/student_dashboard')
def student_dashboard():
    id=session['student_id']
    student = Student.query.get(id)
    print('hiiii')
    appl = Application.query.filter_by(student_id = id).all()
    applied_drives = []
    for app in appl:
        drive = Drive.query.get(app.drive_id)
        applied_drives.append(drive)
        applied_drives
    print(applied_drives)
    req_applicaitos=[]
    drives = Drive.query.filter_by(status = 'Approved', status_open = 'Open').all()
    print('kiiii')
    for drive in drives:
        if drive.drive_id not in applied_drives:
            req_applicaitos.append(drive)
            print(drive)
    print(req_applicaitos)
    approved_drives = Drive.query.filter_by(status = 'Approved', status_open = 'Open').all()


    return render_template('student_dashboard.html', student = student, approved_drives = approved_drives, applied_drives=applied_drives, req_applicaitos = req_applicaitos)

@app.route('/company_dashboard')
def company_dashboard():

    id=session['company_id']
    company = Company.query.get(id)
    drives = Drive.query.filter_by(company_id = id)
    upcoming_drives = Drive.query.filter_by(company_id = id, status_open = 'Open' )
    closed_drives = Drive.query.filter_by(company_id = id, status_open = 'Closed' )

    for drive in drives:
        drive.count = Application.query.filter_by(drive_id = drive.drive_id).count()

    count_drives = Drive.query.filter_by(company_id = id).count()
    return render_template('company_dashboard.html', company = company, count_drives = count_drives,
                            drives=drives,
                            upcoming_drives = upcoming_drives,
                            closed_drives = closed_drives)

@app.route('/create_drive', methods = ['GET', 'POST'])
def create_drive():
    if request.method == 'GET':
        return render_template('/company_dashboard')
    else:   
        id = session['company_id']
        jobtitle = request.form.get('job_title')
        deadline = request.form.get('deadline')
        job_description = request.form.get('job_description')
        eligibilitycriteria = request.form.get('eligibility_criteria')
        print(type(deadline))
        deadline = datetime.strptime(deadline, '%Y-%m-%d').date()
        company_id = session['company_id']


        drive = Drive(job_title = jobtitle, start_date = datetime.now(),
                      deadline = deadline,
                      eligibility_criteria = eligibilitycriteria,
                      company_id = id,
                      job_description = job_description)
        
        db.session.add(drive)
        db.session.commit()
        return redirect('/company_dashboard')
    
@app.route('/edit_drive/<int:id>', methods=['GET', 'POST'])
def edit_drive(id):
    print(id)
    drive = Drive.query.get(id)
    if request.method == "GET":
        return render_template('edit_drive.html', drive = drive)
    else:
        drive.job_title = request.form.get('job_title')
        deadlinestr = request.form.get('deadline')
        drive.job_description = request.form.get('job_description')
        deadline = datetime.strptime(deadlinestr, '%Y-%m-%d').date()
        drive.deadline = deadline
        db.session.commit()
        return redirect('/company_dashboard')   
    
        # start_date = date

@app.route('/delete_drive/<int:id>')
def delete_drive(id):
    drive = Drive.query.get(id)
    db.session.delete(drive)
    db.session.commit()
    return redirect('/company_dashboard')

@app.route('/approve_company?/<int:id>',)
def approve_company(id):
    company = Company.query.get(id)
    company.status = True
    db.session.commit()
    return redirect('/admin_dashboard')

@app.route('/blacklist_company?/<int:id>', )
def blacklist_company(id):
    company = Company.query.get(id)
    company.status2 = False
    db.session.commit()
    return redirect('/admin_dashboard')

@app.route('/reactivate_company?/<int:id>',)
def reactivate_company(id):
    company = Company.query.get(id)
    company.status2 = True
    db.session.commit()
    return redirect('/admin_dashboard')

@app.route('/reject_company/<int:id>' )
def reject_company(id):
    company = Company.query.get(id)
    db.session.delete(company)
    db.session.commit()
    return redirect('/admin_dashboard')

@app.route('/admin_drives')
def admin_drives():
    pending_drives = Drive.query.filter_by(status = 'Pending').all()
    print(pending_drives)
    approved_drives = Drive.query.filter_by(status = 'Approved').all()
    rejected_drives = Drive.query.filter_by(status = 'Rejected').all()
    return render_template('admin_drives.html', pending_drives = pending_drives, approved_drives = approved_drives, rejected_drives = rejected_drives) 

@app.route('/approve_drives/<int:id>')
def approve_drives(id):
    drive = Drive.query.get(id)
    drive.status = "Approved"
    db.session.commit()
    return redirect('/admin_drives')

@app.route('/reject_drives/<int:id>')
def reject_drives(id):
    drive = Drive.query.get(id)
    drive.status = "Rejected"
    db.session.commit()
    return redirect('/admin_drives')

@app.route('/apply_drive/<int:id>',methods = ['GET', 'POST'])
def apply_drive(id):
    student_id = session['student_id']
    student = Student.query.get(student_id)
    if request.method == 'GET':
        drive = Drive.query.get(id)
        return render_template('apply_drive.html', drive = drive, student = student)
    else:
        payment = request.form.get('payment')

        qualification = request.form.get('qualifications')
        experience = request.form.get('Experience')
        CGPA = request.form.get('CGPA')

        student.qualifications = qualification
        student.Experience = experience
        student.CGPA = CGPA

        ap = Application(payment = payment,
            drive_id=id,    
            student_id =  student_id,

            application_date=datetime.now().date()
        )
        db.session.add(ap)
        db.session.commit()
        return redirect('/student_dashboard')
    
    
@app.route('/company_applications')
def company_applicaiton():
    company_id = session['company_id']
    company = Company.query.get(company_id)
    drives = company.drives
    app = Application.query.first()
    print(app.drive.company_id)
    print(333, drives)
    drive_ids = []
    for drive in drives:
        drive_ids.append(drive.drive_id)
    apps = Application.query.all()
    all_applicaitons = []
    for ap in apps:
        if ap.drive_id in drive_ids:
            all_applicaitons.append(ap)
    
    pending_applications = []
    approved_applications = []
    rejected_applications = []
    for ap in all_applicaitons:
        if ap.status == "Applied":
            pending_applications.append(ap)
        elif ap.status == "Approved":
            approved_applications.append(ap)
        else:
            rejected_applications.append(ap)
        print(pending_applications)
    return render_template('company_applications.html', pending_applications=pending_applications,
        approved_applications = approved_applications,
        rejected_applications = rejected_applications,
        company = company)
    
@app.route('/cancel_application/')
def cancel_application():
    return redirect ('/student_dashboard')


@app.route('/approve_application/<int:id>')
def approve_application(id):
    application = Application.query.get(id)
    application.status = "Approved"
    db.session.commit()
    return redirect('/company_applications')

@app.route('/reject_application/<int:id>')
def reject_application(id):
    application = Application.query.get(id)
    application.status = "Rejected"
    db.session.commit()
    return redirect('/company_applications')

@app.route('/view_application/<int:id>')
def view_application(id):
    application = Application.query.get(id)
    return render_template('view_application.html', application = application)

@app.route('/view_drive_applications/<int:id>')
def view_drive_applications(id):
    drive = Drive.query.get(id)
    
    drive_applications = Application.query.filter_by(drive_id = id)
    
    pending_applications = []
    approved_applications = []
    rejected_applications = []
    for ap in drive_applications:
        if ap.status == "Applied":
            pending_applications.append(ap)
        elif ap.status == "Approved":
            approved_applications.append(ap)
        else:
            rejected_applications.append(ap)
    return render_template('view_drive_applications.html', drive = drive,
                           pending_applications = pending_applications,
                           approved_applications = approved_applications,
                           rejected_applications =rejected_applications)

@app.route('/view_resume/<int:id>')
def view_resume(id):
    application = Application.query.get(id)
    return render_template('view_resume.html', application = application)

@app.route('/approve_student/<int:id>')
def approve_student(id):
    student = Student.query.get(id)
    student.status = "Approved"
    db.session.commit()
    return redirect('/admin_students')

@app.route('/blacklist_student/<int:id>')
def blacklist_student(id):
    student = Student.query.get(id)
    student.status = "Blacklisted"
    db.session.commit()
    return redirect('/admin_students')

@app.route('/admin_students')
def admin_students():
    pending_students = Student.query.filter_by(status = 'Pending').all()
    approved_students = Student.query.filter_by(status = 'Approved').all()
    blacklisted_students = Student.query.filter_by(status = 'Blacklisted').all()
    return render_template('admin_students.html', pending_students=pending_students,
        approved_students=approved_students,
        blacklisted_students=blacklisted_students)

@app.route('/close_drive/<int:id>')
def close_drive(id):
    drive = Drive.query.get(id)
    drive.status_open = 'Closed'
    db.session.commit()
    return redirect('/company_dashboard')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == "__main__":
    with app.app_context():
          db.create_all()
    app.run(debug=True)