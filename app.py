from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

IST_OFFSET = timedelta(hours=5, minutes=30)

def now_ist():
    return datetime.utcnow() + IST_OFFSET

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')

db = SQLAlchemy(app)

class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key = True)
    content = db.Column(db.Text, nullable = False)
    date = db.Column(db.DateTime, default = now_ist, nullable=False)

    def __repr__(self):
        return f'<Comment {self.id}>'

with app.app_context():
    db.create_all()


@app.route("/",methods=['GET','POST'])
def home():
    if request.method == 'POST':
        text = request.form.get('text')
        c = Comment(content=text)
        db.session.add(c)
        db.session.commit()
        return redirect(url_for('home'))

    display = Comment.query.order_by(Comment.id.desc()).all()
    return render_template('home.html', display=display)

if __name__ == "__main__":
    app.run()