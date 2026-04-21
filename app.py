import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# --- Configuration ---
# The database file must be exactly "week7_database.sqlite3" [cite: 84]
# The database URI must be precisely as specified [cite: 87]
current_dir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///week7_database.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- Models ---
# Table and column names must strictly match the assignment schema [cite: 85, 88, 89, 90]

class Student(db.Model):
    __tablename__ = 'student'
    student_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    roll_number = db.Column(db.String, unique=True, nullable=False)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String)

class Course(db.Model):
    __tablename__ = 'course'
    course_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_code = db.Column(db.String, unique=True, nullable=False)
    course_name = db.Column(db.String, nullable=False)
    course_description = db.Column(db.String)

class Enrollments(db.Model):
    __tablename__ = 'enrollments'
    enrollment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    estudent_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False)
    ecourse_id = db.Column(db.Integer, db.ForeignKey('course.course_id'), nullable=False)

# --- Student Routes ---

@app.route("/")
def index():
    students = Student.query.all()
    # All successful endpoints must return 200 status code 
    return render_template("index.html", students=students)

@app.route("/student/create", methods=["GET", "POST"])
def create_student():
    if request.method == "GET":
        return render_template("create_student.html")
    
    roll = request.form.get("roll")
    f_name = request.form.get("f_name")
    l_name = request.form.get("l_name")

    # Redirect to error page if roll number already exists [cite: 151]
    if Student.query.filter_by(roll_number=roll).first():
        return render_template("already_exists.html")

    new_student = Student(roll_number=roll, first_name=f_name, last_name=l_name)
    db.session.add(new_student)
    db.session.commit()
    return redirect("/")

@app.route("/student/<int:student_id>/update", methods=["GET", "POST"])
def update_student(student_id):
    student = Student.query.get(student_id)
    if request.method == "GET":
        courses = Course.query.all()
        return render_template("update_student.html", student=student, courses=courses)
    
    student.first_name = request.form.get("f_name")
    student.last_name = request.form.get("l_name")
    
    # Handle enrollment update [cite: 182]
    selected_course_id = request.form.get("course")
    if selected_course_id:
        # Assignment notes previous enrollments must persist [cite: 183]
        new_enrollment = Enrollments(estudent_id=student_id, ecourse_id=int(selected_course_id))
        db.session.add(new_enrollment)
    
    db.session.commit()
    return redirect("/")

@app.route("/student/<int:student_id>/delete")
def delete_student(student_id):
    student = Student.query.get(student_id)
    # Delete student and all corresponding enrollments [cite: 184]
    Enrollments.query.filter_by(estudent_id=student_id).delete()
    db.session.delete(student)
    db.session.commit()
    return redirect("/")

@app.route("/student/<int:student_id>")
def student_details(student_id):
    student = Student.query.get(student_id)
    # Fetch enrollment details for the specific student [cite: 185]
    enrollments = db.session.query(Course).join(Enrollments).filter(Enrollments.estudent_id == student_id).all()
    return render_template("student_details.html", student=student, enrollments=enrollments)

@app.route("/student/<int:student_id>/withdraw/<int:course_id>")
def withdraw_course(student_id, course_id):
    # Remove specific course from student's enrollments [cite: 241]
    enrollment = Enrollments.query.filter_by(estudent_id=student_id, ecourse_id=course_id).first()
    if enrollment:
        db.session.delete(enrollment)
        db.session.commit()
    return redirect("/")

# --- Course Routes ---

@app.route("/courses")
def courses():
    all_courses = Course.query.all()
    return render_template("courses.html", courses=all_courses)

@app.route("/course/create", methods=["GET", "POST"])
def create_course():
    if request.method == "GET":
        return render_template("create_course.html")
    
    code = request.form.get("code")
    name = request.form.get("c_name")
    desc = request.form.get("desc")

    # Redirect to error page if course code already exists [cite: 303]
    if Course.query.filter_by(course_code=code).first():
        return render_template("course_exists.html")

    new_course = Course(course_code=code, course_name=name, course_description=desc)
    db.session.add(new_course)
    db.session.commit()
    return redirect("/courses")

@app.route("/course/<int:course_id>/update", methods=["GET", "POST"])
def update_course(course_id):
    course = Course.query.get(course_id)
    if request.method == "GET":
        return render_template("update_course.html", course=course)
    
    course.course_name = request.form.get("c_name")
    course.course_description = request.form.get("desc")
    db.session.commit()
    return redirect("/courses")

@app.route("/course/<int:course_id>/delete")
def delete_course(course_id):
    course = Course.query.get(course_id)
    # Delete course and all corresponding enrollments 
    Enrollments.query.filter_by(ecourse_id=course_id).delete()
    db.session.delete(course)
    db.session.commit()
    # Redirects back to home page after course deletion 
    return redirect("/")

@app.route("/course/<int:course_id>")
def course_details(course_id):
    course = Course.query.get(course_id)
    # Show students enrolled in this course [cite: 328]
    enrolled_students = db.session.query(Student).join(Enrollments).filter(Enrollments.ecourse_id == course_id).all()
    return render_template("course_details.html", course=course, enrollments=enrolled_students)

if __name__ == "__main__":
    # Ensure no code except the run() call is inside the main block [cite: 79]
    # Note: Do not include db.create_all() as instructed 
    app.run()