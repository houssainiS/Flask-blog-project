from flask_login import UserMixin
from datetime import datetime
from app import db  # Import db here after initialization

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<User {self.username}>"

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('blogs', lazy=True))
    likes = db.Column(db.Integer, default=0)  # New column to track likes

    def __repr__(self):
        return f"<Blog {self.title}>"

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    blog_id = db.Column(db.Integer, db.ForeignKey('blog.id'), nullable=False)

    user = db.relationship('User', backref=db.backref('comments', lazy=True))
    blog = db.relationship('Blog', backref=db.backref('comments', lazy=True))

    def __repr__(self):
        return f"<Comment {self.content[:20]}... by User {self.user_id}>"
