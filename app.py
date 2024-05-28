from flask import Flask, render_template, url_for, redirect, request, session
from flask_sqlalchemy import SQLAlchemy # type: ignore
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from flask_login import LoginManager, UserMixin
from flask_migrate import Migrate

import traceback
import random
import string
import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///:memory:'
app.config["SQLALCHEMY_BINDS"] = {
    'registration': 'sqlite:///valentina_new_student.db',
    'web_content':'sqlite:///web_contents.db',
    'SignUp' : 'sqlite:///SignUp.db'
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config["SECRET_KEY"] = "K0lade001."

# initialise the database
db = SQLAlchemy(app)
# db.init_app(app)


# initialise the migration
migrate = Migrate(app, db)


# LoginManager is needed for our application 
# to be able to log in and out users
login_manager = LoginManager()
login_manager.init_app(app)



Base = declarative_base()
# Create a model for users registration
class registration(db.Model):

    # Student ID generator
    @staticmethod
    def generate_student_id(length=4):
        character = string.digits
        id = 'VA/' + str(datetime.datetime.now().year)[-2:] + '/' + ''.join(random.choice(character) for _ in range(length))
        return id

    __bind_key__ = 'registration'
    __tablename__ = 'registration'

    # id = db.Column(db.Integer, autoincrement=True)
    Student_ID = db.Column(db.String(10), unique=True, nullable=False, default=generate_student_id(), primary_key=True)
    f_name = db.Column(db.String(80), unique=False, nullable=False)
    l_name = db.Column(db.String(80), unique=False, nullable=False)
    parent_name = db.Column(db.String(80), unique=False, nullable=False)
    address = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(80), unique=False, nullable=False)
    phone = db.Column(db.String(80), unique=False, nullable=False)

    def __repr__(self):
        return f"Student_ID:{self.Student_ID}, Surname: {self.f_name}, Last Name: {self.l_name}, Address: {self.address}, Parent Name: {self.parent_name}, Email: {self.email}, Phone: {self.phone}"
    # Student_ID:{self.Student_ID}, 

class WebContent(db.Model):
    __bind_key__ = 'web_content'
    __tablename__ = 'web_content'
    id = db.Column(db.String(50), primary_key=True)
    content = db.Column(db.Text)

class SignUp(UserMixin, db.Model):
    __bind_key__ = 'SignUp'
    __tablename__ = 'SignUp'

    # Student ID generator
    @staticmethod
    def is_admin():
        return True
    

    # id = db.Column(db.String(50), primary_key=True)
    username = db.Column(db.String(80),  unique=True, nullable=False, primary_key=True)
    email = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(80), nullable=False)
    password_again = db.Column(db.String(80), nullable=False)
    is__admin = db.Column(db.String(80), nullable=False, default=0) 

    def __repr__(self):
        return f"username:{self.username}, email: {self.email}, password: {self.password}, password_again: {self.password_again}, admin: {self.is_admin}"

# Creates a user loader callback that returns the user object given an id
@login_manager.user_loader
def loader_user(user_id):
    return SignUp.query().filter_by(username=user_id).first()


with app.app_context():
    db.create_all()


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/error')
def error():
    return render_template('404.html')

@app.route('/courses')
def courses():
    return render_template('courses.html')

@app.route('/team')
def team():
    return render_template('team.html')


@app.route('/testimonial')
def testimonial():
    return render_template('testimonial.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/login')
def login():
    return render_template('signin.html')

@app.route('/join', methods=['POST', 'GET'])
def join():
    if request.method == 'POST':
        # let's create a model for the request above 
        new_registration = registration(
            Student_ID = registration.generate_student_id(),
            f_name = request.form.get('f_name'),
            l_name = request.form.get('l_name'),
            parent_name = request.form.get('parent_name'),
            address = request.form.get('address'),
            email = request.form.get('email'),
            phone = request.form.get('phone'),
        )        

        print('Printing new application here:', new_registration)
        print('registration.Student_ID: ', registration.generate_student_id())
        # now push it to the database
        try:
            db.session.add(new_registration)
            db.session.commit()

            return redirect('login') 
        except Exception as e:
            db.session.rollback()  # Roll back the session to clean up the failed transaction
            print('Error details:', str(e))
            print(traceback.format_exc())  # Print the stack trace for more details
            return 'Issues creating registration'

    else:
        return render_template('form.html')


@app.route('/show')
def show():
    applications = registration.query.all()
    
    return render_template('show.html', applications=applications)

@app.route('/regUsers')
def regUsers():
    users = SignUp.query.all()
    greet = 'Hello, there'
    return render_template('usersDB.html',  applications=greet)
    
@app.route('/<int:Student_ID>')
def delete(Student_ID):
    data = registration.query.get(Student_ID)
    db.session.delete(data)
    db.session.commit()
    return redirect('show')


# _+============= Dashboards ======================
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')



# Sign UP
@app.route('/signup')
def signup():
    return render_template('signup.html')

# Admin Sign Up
@app.route('/adminSignUp')
def adminSignUp():
    return render_template('SignUpAdmin.html')

@app.route('/signup_now', methods=["POST", "GET"])
def signup_now():
    if request.method == 'POST':
        new_signUp = SignUp(
            username = request.form.get('username'),
            email = request.form.get('email'),
            password = request.form.get('password'),
            password_again = request.form.get('password_again'),
            is_admin = request.form.get('admin'),
        )

        # if SignUp.query.filter_by(username=SignUp.username).first():
        #     message = 'Username already existed'
        #     print(message)
        # elif SignUp.query.filter_by(username=SignUp.email).first():
        #     message = 'Email already existed'

        print('New Sign Up: ', new_signUp)
        print(SignUp.query.filter_by(username='kolade').first())

        try:
            db.session.add(new_signUp)
            db.session.commit()
            return redirect('join')
        except Exception as e:
            db.session.rollback()  # Roll back the session to clean up the failed transaction
            print('Error details:', str(e))
            print(traceback.format_exc())  # Print the stack trace for more details
            return 'Issues creating registration'



# if __name__ == '__main__':
#     app.run()