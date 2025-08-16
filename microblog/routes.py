# microblog_app/routes.py
from flask import Blueprint, render_template, url_for, flash, redirect, request
from . import db
from .models import User, Post
from .forms import RegistrationForm, PostForm
from sqlalchemy import text
from faker import Faker # Ensure Faker is imported here for populate_db route

main = Blueprint('main', __name__)

# The new initial dashboard page, also accessible via "/"
@main.route("/")
@main.route("/dashboard")
def dashboard():
    # Now, the dashboard will also display all posts
    posts = Post.query.order_by(Post.date_posted.desc()).all()
    return render_template('dashboard.html', posts=posts, title='Dashboard')

# --- Removed the old @main.route("/home") and def home(): function ---


@main.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}! You can now create posts.', 'success')
        return redirect(url_for('main.dashboard')) # Redirect to dashboard after registration
    return render_template('register.html', title='Register', form=form)

@main.route("/post/new", methods=['GET', 'POST'])
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        user = User.query.first() # Still assuming first user for simplicity.
        if user:
            post = Post(title=form.title.data, content=form.content.data, author=user)
            db.session.add(post)
            db.session.commit()
            flash('Your post has been created!', 'success')
            return redirect(url_for('main.dashboard')) # Redirect to dashboard after creating a post
        else:
            flash('No user found to associate with the post. Please register a user first.', 'danger')
    return render_template('create_post.html', title='New Post', form=form)

# New route for administrative dashboard
@main.route("/admin")
def admin_dashboard():
    return render_template('admin_dashboard.html', title='Admin Dashboard')

# --- Administrative Functions ---

@main.route("/admin/populate_db")
def populate_db():
    try:
        with db.session.no_autoflush:
            db.session.execute(text("DELETE FROM post;"))
            db.session.execute(text("DELETE FROM user;"))
        db.session.commit()

        fake = Faker()
        print("Re-populating user table with Faker data...")
        for _ in range(10):
            user = User(username=fake.user_name(), email=fake.email())
            db.session.add(user)
        db.session.commit()
        print("User table re-populated.")

        print("Re-populating post table with Faker data...")
        users = User.query.all()
        for user in users:
            for _ in range(fake.random_int(min=1, max=5)):
                post = Post(title=fake.sentence(), content=fake.paragraph(), author=user)
                db.session.add(post)
        db.session.commit()
        print("Post table re-populated.")

        flash('Database populated with new test data!', 'info')
    except Exception as e:
        db.session.rollback()
        flash(f'Error populating database: {e}', 'danger')
        print(f"Error populating database: {e}")

    return redirect(url_for('main.admin_dashboard'))