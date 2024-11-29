from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import User, Blog, Comment  # Import Comment model

main = Blueprint('main', __name__)

# Registration route
@main.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        user = User(username=username, password=hashed_password)
        db.session.add(user)
        db.session.commit()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('main.login'))

    return render_template('register.html')

# Login route
@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for('main.home'))
        else:
            flash("Invalid login credentials", "danger")

    return render_template('login.html')

# Home route
@main.route('/')
def home():
    blogs = Blog.query.all()
    return render_template('home.html', blogs=blogs)

# Create blog route
@main.route('/create_blog', methods=['GET', 'POST'])
@login_required
def create_blog():
    if request.method == "POST":
        title = request.form.get('title')
        content = request.form.get('content')
        new_blog = Blog(title=title, content=content, user_id=current_user.id)
        db.session.add(new_blog)
        db.session.commit()

        flash("Blog post created!", "success")
        return redirect(url_for('main.home'))

    return render_template('create_blog.html')

# View blog and handle comments
@main.route("/blog/<int:blog_id>", methods=['GET', 'POST'])
def view_blog(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    
    # Handle comment form submission
    if request.method == 'POST':
        if current_user.is_authenticated:
            comment_content = request.form.get('content')
            if comment_content:
                comment = Comment(content=comment_content, user_id=current_user.id, blog_id=blog.id)
                db.session.add(comment)
                db.session.commit()
                flash('Comment added!', 'success')
            else:
                flash('Comment cannot be empty.', 'warning')
        else:
            flash('You must be logged in to comment.', 'danger')
        return redirect(url_for('main.view_blog', blog_id=blog.id))
    
    return render_template('view_blog.html', blog=blog)

# Edit blog route
@main.route('/blog/edit/<int:blog_id>', methods=['GET', 'POST'])
@login_required
def edit_blog(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    
    if request.method == 'POST':
        if blog.user_id == current_user.id or current_user.is_admin:
            blog.title = request.form['title']
            blog.content = request.form['content']
            db.session.commit()
            flash('Blog Updated Successfully!', 'success')
            return redirect(url_for('main.home'))
        else:
            flash('You are not authorized to edit this blog.', 'danger')

    return render_template('edit_blog.html', blog=blog)

# Delete blog route
@main.route('/blog/delete/<int:blog_id>', methods=['POST'])
@login_required
def delete_blog(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    if blog.user_id == current_user.id or current_user.is_admin:
        db.session.delete(blog)
        db.session.commit()
        flash('Blog Deleted Successfully!', 'danger')
    else:
        flash('You are not authorized to delete this blog.', 'danger')
    return redirect(url_for('main.home'))

# Admin panel route
@main.route("/admin")
@login_required
def admin():
    if not current_user.is_admin:
        flash("You are not authorized to access the admin panel.", "danger")
        return redirect(url_for('main.home'))

    blogs = Blog.query.all()
    return render_template('admin.html', blogs=blogs)

# Delete blog from admin route
@main.route("/delete_blog/<int:blog_id>")
@login_required
def delete_blog_from_admin(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    if blog.user_id == current_user.id or current_user.is_admin:
        db.session.delete(blog)
        db.session.commit()
        flash("Blog deleted", "success")
    else:
        flash("You are not authorized to delete this blog.", "danger")
    return redirect(url_for('main.admin'))

# Logout route
@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('main.login'))

# Like a blog
@main.route('/like/<int:blog_id>', methods=['POST'])
@login_required
def like_blog(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    blog.likes += 1
    db.session.commit()
    flash('You liked this blog!', 'success')
    return redirect(url_for('main.view_blog', blog_id=blog.id))
