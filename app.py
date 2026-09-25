from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

IST_OFFSET = timedelta(hours=5, minutes=30)

def now_ist():
    return datetime.utcnow() + IST_OFFSET

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
loginManager = LoginManager()
loginManager.init_app(app)
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)

class User(db.Model,UserMixin):
    __tablename__ = "users"
    uID = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(80),unique=True,nullable=False)
    passw = db.Column(db.Text,nullable=False)
    comments = db.relationship('Comment',backref='author',lazy=True)
   
    def __repr__(self):
        return f'<User {self.username}>'
    def get_id(self):
        return str(self.uID)
    
class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key = True)
    content = db.Column(db.Text, nullable = False)
    date = db.Column(db.DateTime, default = now_ist, nullable=False)
    userID = db.Column(db.Integer, db.ForeignKey('users.uID') ,nullable=False)

    def __repr__(self):
        return f'<Comment {self.id}>'

with app.app_context():
    db.create_all()

@loginManager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/s',methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        passw = request.form.get('passw')
        hashedPassw = bcrypt.generate_password_hash(passw).decode('utf-8')

        if User.query.filter_by(username=username).first() is not None:
            flash("Username Taken! Try a New One")
            return render_template('form.html')
        else:
            db.session.add(User(username=username,passw=hashedPassw))
            db.session.commit()
            return redirect(url_for('login'))
        
    return render_template('form.html')

@app.route('/l',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        passw = request.form.get('passw')

        if User.query.filter_by(username=username).first() is None:
            flash("No User Found")
            return render_template('form.html')
        else:
            user = User.query.filter_by(username=username).first()
            isValid = bcrypt.check_password_hash(user.passw,passw)
            if isValid:
                login_user(user)
                return redirect(url_for('home'))
            else:
                flash("Wrong Password!")
                return render_template('form.html')

        
    return render_template('form.html')

@app.route("/comments",methods=['GET','POST'])
@login_required
def home():
    if request.method == 'POST':
        text = request.form.get('text')
        c = Comment(content=text,userID=current_user.uID)
        db.session.add(c)
        db.session.commit()
        return redirect(url_for('home'))

    display = Comment.query.order_by(Comment.id.desc()).all()
    return render_template('home.html', display=display)

@app.route('/lo')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run()