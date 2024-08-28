from flask import Flask, request, redirect, url_for, render_template, jsonify, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from uuid import uuid4
from config import ApplicationConfig
from flask_bcrypt import Bcrypt
from flask_cors import CORS


app = Flask(__name__, template_folder='templates')
db = SQLAlchemy()
bcyrpt = Bcrypt(app)
CORS(app)
CORS(app, resources={r"/login": {"origins": ["*"]}, r"/portal": {"origins": ["*"]}}, methods=["GET", "POST"], supports_credentials=True)
def get_uuid():
    return uuid4().hex


app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_COOKIE_SECURE"] = True
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "None"
Session(app)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, unique=True, primary_key=True, default=get_uuid)
    name = db.Column(db.String(25), unique=False, nullable=False)
    password = db.Column(db.Text, nullable=False)

app.config.from_object(ApplicationConfig)
db.init_app(app)

with app.app_context():
    db.create_all()
    user_1 = User(name='admin', password=bcyrpt.generate_password_hash('adminpassword@2004').decode('utf-8'))
    user_2 = User(name='niketa sengar', password=bcyrpt.generate_password_hash('niketapassword@2004').decode('utf-8'))

    db.session.add_all([user_1, user_2])
    db.session.commit()

def authenticated_user(name, password):
    user = User.query.filter_by(name=name).first()
    if user and bcyrpt.check_password_hash(user.password, password):
        session['user_name'] = user.name
        return user
    return None


@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        name = request.args.get('name')
        password = request.args.get('password')
        print(f'received login request with name:{name},password:{password}')
        authenticate_user = authenticated_user(name, password)
        print(f"Authenticated user: {authenticate_user}")
        if authenticate_user:
            return redirect(url_for('crm_portal'))
        else:
            return jsonify({'error': 'Authentication failed'}), 401

    elif request.method == 'POST':
        data = request.json
        name = data.get('name')
        password = data.get('password')
        print(f"Received login request with name: {name}, password: {password}")
        authenticate_user = authenticated_user(name, password)
        print(f"Authenticated user: {authenticate_user}")
         # Print the session data
        print("Session data:", session)
        if authenticate_user:
            return redirect(url_for('crm_portal'))
        else:
            return jsonify({'error': 'Authentication failed'}), 401

@app.route('/portal')
def crm_portal():
    user_name = session.get('user_name', None)
    if user_name:
        return render_template('index.html', user_name=user_name)
    else:
        return redirect(url_for('login'))

# redirect to login page after loging out
# @app.route("/logout")
# def logout():
#     session.pop('user_name', None)
#     return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5001)



































# from flask import Flask, request, redirect, url_for, render_template, jsonify, session, send_from_directory
# from flask_session import Session
# from flask_sqlalchemy import SQLAlchemy
# from uuid import uuid4
# from config import ApplicationConfig
# from flask_bcrypt import Bcrypt
# from flask_cors import CORS 
  

# app = Flask(__name__, template_folder='templates')
# db = SQLAlchemy()
# bcrypt = Bcrypt(app)
# CORS(app)
# CORS(app, resources={r"/login": {"origins": ["*"]}, r"/portal": {"origins": ["*"]}}, methods=["GET", "POST"], supports_credentials=True)

# def get_uuid():
#     return uuid4().hex

# app.config["SESSION_PERMANENT"] = False
# app.config["SESSION_TYPE"] = "filesystem"
# Session(app)

# # creating the table  
# class User(db.Model):
#     __tablename__ = 'users'
#     id = db.Column(db.Integer, unique=True, primary_key=True, default=get_uuid)
#     name = db.Column(db.String(25), unique=False, nullable=False)
#     password = db.Column(db.Text, nullable=False)

# app.config.from_object(ApplicationConfig)
# db.init_app(app)

# # username and password for authentication 
# with app.app_context():
#     db.create_all()
#     user_1 = User(name='admin', password=bcrypt.generate_password_hash('adminpassword@2004').decode('utf-8'))
#     user_2 = User(name='niketa sengar', password=bcrypt.generate_password_hash('niketapassword@2004').decode('utf-8'))

# # created the session for the user
#     db.session.add_all([user_1, user_2])
#     db.session.commit()


# # authentication logic for loging into the portal
# def authenticated_user(name, password):
#     print(f"Attempting to authenticate user with name: {name}")
#     user = User.query.filter_by(name=name).first()
#     print(f"User: {user}")
#     if user and bcrypt.check_password_hash(user.password, password):
#         # Store user name in session after successful authentication
#         session['user_name'] = user.name
#         return user
#     else:
#         print("authentication failed")
#     return None


# @app.route('/login', methods=['POST'])
# def login():
#      if request.method == 'POST':
#         # Handle POST request
#         data = request.json
#         name = data.get('name')
#         password = data.get('password')
#         print(f"Received login request with name: {name}, password: {password}")
#         authenticate_user = authenticated_user(name, password)
#         print(f"Authenticated user: {authenticate_user}")
#         if authenticate_user:
#             return redirect(url_for('crm_portal'))
#         else:
#          return jsonify({'error': 'Authentication failed'}), 401



# @app.route('/portal')
# def crm_portal():
#     # Retrieve user name from the session
#     user_name = session.get('user_name')
#     print(f"Session user_name:{user_name}")

#     if user_name:
#         # Pass user name to the template
#       return render_template('index.html', user_name=user_name)
#     else:
#         return redirect(url_for('login'))
    

# # redirect to login page after loging out
# @app.route("/logout")
# def logout():
#     session.pop('user_name', None)
#     return redirect("/login")


# if __name__ == "__main__":
#     app.run(debug=True,host='0.0.0.0',port=5001)
