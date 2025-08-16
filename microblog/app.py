# microblog_app/app.py
import os
import tempfile
from flask import Flask
from models import db
from routes import main
from sqlalchemy import text

def create_database_views(app):
    """Create database views automatically during initialization"""
    with app.app_context():
        try:
            # Drop existing views
            drop_statements = [
                "DROP VIEW IF EXISTS v_user_stats",
                "DROP VIEW IF EXISTS v_post_summary", 
                "DROP VIEW IF EXISTS v_recent_posts",
                "DROP VIEW IF EXISTS v_top_contributors",
                "DROP VIEW IF EXISTS v_dashboard_summary"
            ]
            
            for stmt in drop_statements:
                db.session.execute(text(stmt))
            
            # Create views
            view_statements = [
                """CREATE VIEW v_user_stats AS
                   SELECT u.id, u.username, u.email, COUNT(p.id) as post_count,
                          MAX(p.date_posted) as last_post_date, MIN(p.date_posted) as first_post_date
                   FROM user u LEFT JOIN post p ON u.id = p.user_id
                   GROUP BY u.id, u.username, u.email""",
                
                """CREATE VIEW v_post_summary AS
                   SELECT p.id, p.title, p.content, p.date_posted, p.user_id,
                          u.username as author_username, u.email as author_email, LENGTH(p.content) as content_length
                   FROM post p JOIN user u ON p.user_id = u.id""",
                
                """CREATE VIEW v_recent_posts AS
                   SELECT p.id, p.title, SUBSTR(p.content, 1, 100) as content_preview,
                          p.date_posted, u.username as author, LENGTH(p.content) as content_length
                   FROM post p JOIN user u ON p.user_id = u.id
                   WHERE p.date_posted >= datetime('now', '-30 days')""",
                
                """CREATE VIEW v_top_contributors AS
                   SELECT u.id, u.username, u.email, COUNT(p.id) as total_posts,
                          AVG(LENGTH(p.content)) as avg_post_length, MAX(p.date_posted) as latest_post
                   FROM user u LEFT JOIN post p ON u.id = p.user_id
                   GROUP BY u.id, u.username, u.email
                   HAVING COUNT(p.id) > 0""",
                
                """CREATE VIEW v_dashboard_summary AS
                   SELECT (SELECT COUNT(*) FROM user) as total_users,
                          (SELECT COUNT(*) FROM post) as total_posts,
                          (SELECT COUNT(*) FROM post WHERE date_posted >= datetime('now', '-7 days')) as posts_this_week,
                          (SELECT COUNT(*) FROM post WHERE date_posted >= datetime('now', '-1 day')) as posts_today,
                          (SELECT username FROM user u JOIN post p ON u.id = p.user_id GROUP BY u.id ORDER BY COUNT(p.id) DESC LIMIT 1) as top_contributor"""
            ]
            
            for stmt in view_statements:
                db.session.execute(text(stmt))
            
            db.session.commit()
            print("Database views created successfully during initialization.")
            
        except Exception as e:
            db.session.rollback()
            print(f"Warning: Could not create database views during initialization: {e}")

def create_app():
    """Application factory function"""
    app = Flask(__name__)
    
    # Create a temporary database file
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(db_fd)  # Close the file descriptor
    
    # Configure the app
    app.config['SECRET_KEY'] = 'your-secret-key-here'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    print(f"Using temp instance path: {os.path.dirname(db_path)}")
    
    # Initialize database
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(main)
    
    # Create database tables and views
    with app.app_context():
        db.create_all()
        create_database_views(app)
    
    return app

# Create the app
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5001)