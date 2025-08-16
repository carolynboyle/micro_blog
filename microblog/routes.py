# microblog_app/routes.py
from flask import Blueprint, render_template, url_for, flash, redirect, request, make_response
from models import db, User, Post
from forms import RegistrationForm, PostForm
from sqlalchemy import text
from faker import Faker
import csv
import io
import pandas as pd
import json
from datetime import datetime, timedelta

main = Blueprint('main', __name__)

# --- MAIN DASHBOARD (Mixed - uses direct queries for user selection) ---

@main.route("/")
@main.route("/dashboard")
def dashboard():
    # Get selected user from URL parameter, or default to first user
    selected_user_id = request.args.get('user_id', type=int)
    
    if selected_user_id:
        user = User.query.get(selected_user_id)
    else:
        user = User.query.first()
    
    # Get all users for the dropdown
    all_users = User.query.all()
    
    # If no user exists, show the dashboard anyway with a message to register
    if not user:
        # Create a mock user object for template rendering
        class MockUser:
            username = "Guest"
            email = "guest@example.com"
            created_at = None
            is_admin = False
            id = 0
        
        user = MockUser()
        recent_posts = []
        user_posts_count = 0
        admin_stats = {
            'total_users': User.query.count(),
            'total_posts': Post.query.count()
        }
        flash('Welcome! Please register to start using the microblog.', 'info')
    else:
        # Get recent posts (limit to 5 for dashboard) - using direct query for user interaction
        recent_posts = Post.query.order_by(Post.date_posted.desc()).limit(5).all()
        
        # Count user's posts
        user_posts_count = Post.query.filter_by(user_id=user.id).count()
        
        # Admin stats (you can expand this later)
        admin_stats = {
            'total_users': User.query.count(),
            'total_posts': Post.query.count()
        }
    
    # Get all posts for display - using direct query for interactive dashboard
    posts = Post.query.order_by(Post.date_posted.desc()).all()
    
    return render_template('dashboard.html', 
                         posts=posts, 
                         title='Dashboard',
                         user=user,
                         all_users=all_users,
                         recent_posts=recent_posts,
                         user_posts_count=user_posts_count,
                         admin_stats=admin_stats)

# --- WRITE OPERATIONS ---

@main.route("/register", methods=['GET', 'POST'])
def register():
    """WRITE: Create new user"""
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}! You can now create posts.', 'success')
        return redirect(url_for('main.dashboard'))
    return render_template('register.html', title='Register', form=form)

@main.route("/post/new", methods=['GET', 'POST'])
def new_post():
    """WRITE: Create new post"""
    # Get the user_id from URL parameters (passed from dashboard)
    user_id = request.args.get('user_id', type=int)
    
    if user_id:
        current_user = User.query.get(user_id)
    else:
        current_user = User.query.first()
    
    form = PostForm()
    if form.validate_on_submit():
        if current_user:
            post = Post(title=form.title.data, content=form.content.data, author=current_user)
            db.session.add(post)
            db.session.commit()
            flash('Your post has been created!', 'success')
            # Redirect back to dashboard with the same user selected
            if user_id:
                return redirect(url_for('main.dashboard', user_id=user_id))
            else:
                return redirect(url_for('main.dashboard'))
        else:
            flash('No user found to associate with the post. Please register a user first.', 'danger')
    
    return render_template('create_post.html', title='New Post', form=form, user=current_user)

@main.route("/user/<username>")
def user_profile(username):
    """WRITE: View and edit user profile (allows user updates)"""
    user = User.query.filter_by(username=username).first_or_404()
    
    # Get all posts by this user using direct query (for profile management)
    user_posts = Post.query.filter_by(user_id=user.id).order_by(Post.date_posted.desc()).all()
    
    # Get user stats
    total_posts = len(user_posts)
    
    return render_template('user_profile.html', 
                         title=f'{user.username} - Profile',
                         user=user,
                         posts=user_posts,
                         total_posts=total_posts)

@main.route("/user/<username>/edit", methods=['GET', 'POST'])
def edit_user_profile(username):
    """WRITE: Edit user profile"""
    user = User.query.filter_by(username=username).first_or_404()
    
    # Here you would add a user edit form
    # For now, just redirect back to profile
    flash('User profile editing not yet implemented.', 'info')
    return redirect(url_for('main.user_profile', username=username))

# --- READ-ONLY VIEWS EXCLUSIVELY ---

@main.route("/views/users")
def readonly_users():
    """READ-ONLY: User list using user stats view"""
    try:
        users = db.session.execute(text("SELECT * FROM v_user_stats ORDER BY post_count DESC")).fetchall()
        
        return render_template('readonly_users.html',
                             title='Users (Read-Only)',
                             users=users)
    except Exception as e:
        flash(f'Database views not found. Please populate database first. Error: {e}', 'warning')
        return redirect(url_for('main.admin_dashboard'))

@main.route("/views/posts")
def readonly_posts():
    """READ-ONLY: Posts list using post summary view"""
    try:
        posts = db.session.execute(text("SELECT * FROM v_post_summary ORDER BY date_posted DESC LIMIT 50")).fetchall()
        
        return render_template('readonly_posts.html',
                             title='Posts (Read-Only)',
                             posts=posts)
    except Exception as e:
        flash(f'Database views not found. Please populate database first. Error: {e}', 'warning')
        return redirect(url_for('main.admin_dashboard'))

@main.route("/views/user/<username>")
def readonly_user_profile(username):
    """READ-ONLY: User profile using views (no editing)"""
    try:
        # Get user stats from view
        user_stats = db.session.execute(text("""
            SELECT * FROM v_user_stats 
            WHERE username = :username
        """), {'username': username}).fetchone()
        
        if not user_stats:
            flash(f'User {username} not found.', 'error')
            return redirect(url_for('main.readonly_users'))
        
        # Get user's posts from post summary view
        user_posts = db.session.execute(text("""
            SELECT * FROM v_post_summary 
            WHERE author_username = :username
            ORDER BY date_posted DESC
        """), {'username': username}).fetchall()
        
        return render_template('readonly_user_profile.html',
                             title=f'{username} - Profile (Read-Only)',
                             user_stats=user_stats,
                             posts=user_posts,
                             total_posts=len(user_posts))
        
    except Exception as e:
        flash(f'Error loading user profile: {e}', 'danger')
        return redirect(url_for('main.readonly_users'))

# --- PANDAS ANALYTICS (READ-ONLY) ---

@main.route("/analytics/dashboard")
def analytics_dashboard():
    """READ-ONLY: Advanced analytics dashboard using pandas"""
    try:
        # Use read-only views for analytics
        users_df = pd.read_sql("SELECT * FROM v_user_stats", db.engine)
        posts_df = pd.read_sql("SELECT * FROM v_post_summary ORDER BY date_posted DESC", db.engine)
        
        # Convert date columns to datetime
        if not posts_df.empty:
            posts_df['date_posted'] = pd.to_datetime(posts_df['date_posted'])
            posts_df['post_date'] = posts_df['date_posted'].dt.date
            posts_df['post_month'] = posts_df['date_posted'].dt.to_period('M')
        
        # Calculate analytics
        analytics = {}
        
        if not users_df.empty:
            analytics['user_stats'] = {
                'total_users': len(users_df),
                'avg_posts_per_user': round(users_df['post_count'].mean(), 2),
                'median_posts_per_user': users_df['post_count'].median(),
                'most_active_user': users_df.loc[users_df['post_count'].idxmax()]['username'] if users_df['post_count'].max() > 0 else 'None',
                'users_with_posts': len(users_df[users_df['post_count'] > 0]),
                'users_without_posts': len(users_df[users_df['post_count'] == 0])
            }
        
        if not posts_df.empty:
            analytics['post_stats'] = {
                'total_posts': len(posts_df),
                'avg_content_length': round(posts_df['content_length'].mean(), 2),
                'median_content_length': posts_df['content_length'].median(),
                'longest_post': posts_df['content_length'].max(),
                'shortest_post': posts_df['content_length'].min(),
                'posts_last_7_days': len(posts_df[posts_df['date_posted'] > datetime.now() - timedelta(days=7)]),
                'posts_last_30_days': len(posts_df[posts_df['date_posted'] > datetime.now() - timedelta(days=30)])
            }
            
            # Top authors
            top_authors = posts_df['author_username'].value_counts().head(5).to_dict()
            analytics['top_authors'] = top_authors
            
            # Posts by month
            if not posts_df.empty:
                posts_by_month = posts_df.groupby('post_month').size().to_dict()
                posts_by_month = {str(k): v for k, v in posts_by_month.items()}
                analytics['posts_by_month'] = posts_by_month
        
        return render_template('analytics_dashboard.html',
                             title='Analytics Dashboard',
                             analytics=analytics,
                             users_data=users_df.to_dict('records') if not users_df.empty else [],
                             posts_data=posts_df.head(20).to_dict('records') if not posts_df.empty else [])
    
    except Exception as e:
        flash(f'Error generating analytics: {e}', 'danger')
        return redirect(url_for('main.admin_dashboard'))

@main.route("/analytics/export")
def export_analytics():
    """READ-ONLY: Export comprehensive analytics as CSV using pandas"""
    try:
        # Use read-only view for export
        df = pd.read_sql("SELECT * FROM v_user_stats ORDER BY post_count DESC", db.engine)
        
        if not df.empty:
            # Add activity categories
            df['activity_level'] = pd.cut(
                df['post_count'], 
                bins=[0, 1, 5, 10, float('inf')], 
                labels=['Inactive', 'Low', 'Medium', 'High']
            )
        
        # Export to CSV
        output = df.to_csv(index=False)
        response = make_response(output)
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = 'attachment; filename=microblog_analytics.csv'
        
        return response
    
    except Exception as e:
        flash(f'Error exporting analytics: {e}', 'danger')
        return redirect(url_for('main.analytics_dashboard'))

@main.route("/analytics/user_report")
def user_activity_report():
    """READ-ONLY: Detailed user activity report using pandas"""
    try:
        # Use read-only view for user activity analysis
        df = pd.read_sql("SELECT * FROM v_post_summary ORDER BY date_posted DESC", db.engine)
        
        if df.empty:
            flash('No post data available for analysis.', 'info')
            return redirect(url_for('main.analytics_dashboard'))
        
        # Convert to datetime
        df['date_posted'] = pd.to_datetime(df['date_posted'])
        df['post_date'] = df['date_posted'].dt.date
        df['post_month'] = df['date_posted'].dt.to_period('M')
        df['post_hour'] = df['date_posted'].dt.hour
        df['post_weekday'] = df['date_posted'].dt.day_name()
        
        # User activity summary
        user_summary = df.groupby('author_username').agg({
            'content_length': ['mean', 'sum', 'count'],
            'post_date': ['min', 'max']
        }).round(2)
        
        # Flatten column names
        user_summary.columns = ['avg_content_length', 'total_content_length', 'post_count', 'first_post', 'latest_post']
        user_summary = user_summary.reset_index()
        
        # Activity by time patterns
        activity_patterns = {
            'posts_by_weekday': df['post_weekday'].value_counts().to_dict(),
            'posts_by_hour': df['post_hour'].value_counts().sort_index().to_dict(),
            'posts_by_month': df['post_month'].value_counts().sort_index().to_dict()
        }
        
        return render_template('user_activity_report.html',
                             title='User Activity Report',
                             user_summary=user_summary.to_dict('records'),
                             activity_patterns=activity_patterns,
                             total_posts=len(df))
    
    except Exception as e:
        flash(f'Error generating user activity report: {e}', 'danger')
        return redirect(url_for('main.analytics_dashboard'))

# --- ADMIN FUNCTIONS (WRITE: Database Management) ---

@main.route("/admin")
def admin_dashboard():
    """Admin dashboard with stats from read-only view"""
    # Get current stats for display using read-only view
    try:
        summary = db.session.execute(text("SELECT * FROM v_dashboard_summary")).fetchone()
        total_users = summary.total_users if summary else 0
        total_posts = summary.total_posts if summary else 0
    except:
        total_users = User.query.count()
        total_posts = Post.query.count()
    
    return render_template('admin_dashboard.html', 
                         title='Admin Dashboard',
                         total_users=total_users,
                         total_posts=total_posts)

@main.route("/admin/create_empty_db")
def create_empty_db():
    """WRITE: Clear all database data"""
    try:
        # Delete all data
        with db.session.no_autoflush:
            db.session.execute(text("DELETE FROM post;"))
            db.session.execute(text("DELETE FROM user;"))
        db.session.commit()
        
        flash('Database cleared! All users and posts have been deleted.', 'warning')
        print("Database cleared successfully.")
    except Exception as e:
        db.session.rollback()
        flash(f'Error clearing database: {e}', 'danger')
        print(f"Error clearing database: {e}")
    
    return redirect(url_for('main.admin_dashboard'))

@main.route("/admin/populate_db")
def populate_db():
    """WRITE: Populate database with test data"""
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

@main.route("/admin/export_users")
def export_users():
    """READ-ONLY: Export users using read-only view"""
    try:
        # Use read-only view for export
        users = db.session.execute(text("SELECT * FROM v_user_stats ORDER BY post_count DESC")).fetchall()
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['ID', 'Username', 'Email', 'Post Count', 'First Post', 'Latest Post'])
        
        # Write user data
        for user in users:
            writer.writerow([user.id, user.username, user.email, user.post_count, 
                           user.first_post_date or 'N/A', user.last_post_date or 'N/A'])
        
        # Create response
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = 'attachment; filename=users_export.csv'
        
        return response
    
    except Exception as e:
        flash(f'Error exporting users: {e}', 'danger')
        return redirect(url_for('main.admin_dashboard'))