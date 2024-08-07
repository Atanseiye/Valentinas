from flask import Flask, render_template, url_for, redirect, request, session
from flask_sqlalchemy import SQLAlchemy # type: ignore
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from flask_login import LoginManager, UserMixin, login_user, logout_user
from flask_migrate import Migrate

import traceback
import random
import string
import datetime

# Initialising the flask app
app = Flask(__name__)

# Initialising the configuration of the database: SQLALCHEMY
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///:memory:'
app.config["SQLALCHEMY_BINDS"] = {
    'registration': 'sqlite:///valentina_new_student.db',
    'web_content':'sqlite:///web_contents.db',
    'SignUp' : 'sqlite:///SignUp.db'
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SECRET_KEY"] = "K0lade001."

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
    

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80),  unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    password_again = db.Column(db.String(80), nullable=False)
    is__admin = db.Column(db.String(3))


    def __repr__(self):
        return f"id:{self.id},  username:{self.username}, email: {self.email}, password: {self.password}, password_again: {self.password_again}, admin: {self.is__admin}"

# Creates a user loader callback that returns the user object given an id
@login_manager.user_loader
def loader_user(user_id):
    return SignUp.query.get(user_id)


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

@app.route('/sign_in', methods=["POST", "GET"])
def sign_in():
    username = request.form.get('username')
    password = request.form.get('password')
    # admin = SignUp.query.filter_by(is__admin)

    if request.method == "POST":
        message = 'Please, check your Username or Passworw again'
        message2 = "Sorry! You are not registered"
        user = SignUp.query.filter_by(username=username).first()
        print(user)
        if user in SignUp.query.all():
            if user.password == password:
                if user.is__admin == '1':
                    login_user(user)
                    return render_template('dashboard.html')
                login_user(user)
                return 'Signed In'
            return render_template("signin.html", message=message)
        return render_template("signin.html", message2=message2)

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
    return render_template('usersDB.html',  users=[users, greet])
    
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


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route('/signup_now', methods=["POST", "GET"])
def signup_now():
    if request.method == 'POST':
        new_signUp = SignUp(
            username = request.form.get('username'),
            email = request.form.get('email'),
            password = request.form.get('password'),
            password_again = request.form.get('password_again'),
            is__admin = request.form.get('admin'),
        )
        
        # print(SignUp.query.filter_by(username=request.form.get('username')).first())
        print(new_signUp)

        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        password_again = request.form.get('password_again')

        if SignUp.query.filter_by(username=username).scalar():
            Usermessages = 'Username already existed'
            return render_template('signup.html', Usermessages=Usermessages)
        elif SignUp.query.filter_by(email=email).scalar():
            Emailmessages = 'Email already existed'
            return render_template('signup.html', Emailmessages=Emailmessages)
        elif password != password_again:
            pass_error = 'Password is not matching'
            return render_template('signup.html', pass_error=pass_error)


        try:
            db.session.add(new_signUp)
            db.session.commit()
            return redirect('join')
           
        except Exception as e:
            db.session.rollback()  # Roll back the session to clean up the failed transaction
            print('Error details:', str(e))
            print(traceback.format_exc())  # Print the stack trace for more details
            errors = 'Issues creating registration'
            return render_template('signup.html', errors=errors)



if __name__ == '__main__':
    app.run(debug=True)