from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path, makedirs
from flask_login import LoginManager
import os
import datetime

db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    # Ensure CSS directory exists
    css_dir = os.path.join('website', 'static', 'css')
    os.makedirs(css_dir, exist_ok=True)
    
    # Copy CSS files to the correct location
    from shutil import copyfile
    
    # Define CSS files to copy
    css_files = [
        ('website/static/css/base.css', 'base.css'),
        ('website/static/css/components.css', 'components.css'),
        ('website/static/css/home.css', 'home.css'),
        ('website/static/css/forest.css', 'forest.css'),
        ('website/static/css/auth.css', 'auth.css'),
        ('website/static/css/profile.css', 'profile.css')
    ]
    
    # Copy each CSS file
    for src, dest in css_files:
        dest_path = os.path.join(css_dir, dest)
        try:
            # Create the file if it doesn't exist
            if not os.path.exists(src):
                with open(src, 'w') as f:
                    f.write('/* CSS file created by app initialization */')
                print(f"Created empty CSS file: {src}")
            
            # Copy the file
            copyfile(src, dest_path)
            print(f"Copied {src} to {dest_path}")
        except Exception as e:
            print(f"Error copying CSS file {src}: {e}")
    
    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    # Register individual blueprints for direct access if needed
    from .routes.metrics_routes import metrics_bp
    from .routes.forest_routes import forest_bp
    from .routes.product_routes import product_bp
    from .routes.profile_routes import profile_bp
    from .routes.general_routes import general_bp

    # Register blueprints with correct URL prefixes
    app.register_blueprint(metrics_bp, url_prefix='/metrics')  # Changed from /api/metrics
    app.register_blueprint(forest_bp, url_prefix='/api/forest')
    app.register_blueprint(product_bp, url_prefix='/api/product')
    app.register_blueprint(profile_bp, url_prefix='/api/profile')
    app.register_blueprint(general_bp, url_prefix='/api/general')

    from .models import User, Note, CarbonData, Product, HarvestPeriod
    
    # Ensure uploads directory exists
    os.makedirs(os.path.join('website', 'static', 'uploads'), exist_ok=True)
    
    with app.app_context():
        db.create_all()
        update_database_schema(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app

def create_database(app):
    if not path.exists('website/' + DB_NAME):
        with app.app_context():
            db.create_all()
        print('Created Database!')

def update_database_schema(app):
    """Update database schema to include new columns if they don't exist yet."""
    from sqlalchemy import inspect
    from .models import User, CarbonData, Product, HarvestPeriod
    
    inspector = inspect(db.engine)
    
    # Check and update User table
    if 'user' in inspector.get_table_names():
        columns = [column['name'] for column in inspector.get_columns('user')]
        
        # Add missing columns to User table
        with db.engine.connect() as conn:
            if 'account_type' not in columns:
                conn.execute(db.text('ALTER TABLE user ADD COLUMN account_type VARCHAR(20) DEFAULT "business"'))
            
            if 'business_name' not in columns:
                conn.execute(db.text('ALTER TABLE user ADD COLUMN business_name VARCHAR(150)'))
            
            if 'business_location' not in columns:
                conn.execute(db.text('ALTER TABLE user ADD COLUMN business_location VARCHAR(150)'))
            
            if 'business_about' not in columns:
                conn.execute(db.text('ALTER TABLE user ADD COLUMN business_about TEXT'))
            
            if 'forest_name' not in columns:
                conn.execute(db.text('ALTER TABLE user ADD COLUMN forest_name VARCHAR(150)'))
            
            if 'forest_location' not in columns:
                conn.execute(db.text('ALTER TABLE user ADD COLUMN forest_location VARCHAR(150)'))
            
            if 'forest_image' not in columns:
                conn.execute(db.text('ALTER TABLE user ADD COLUMN forest_image VARCHAR(255)'))
            
            conn.commit()
    
    # Create CarbonData table if it doesn't exist
    if 'carbon_data' not in inspector.get_table_names():
        CarbonData.__table__.create(db.engine)
        print('Created CarbonData table!')
    else:
        # Check and update CarbonData table
        columns = [column['name'] for column in inspector.get_columns('carbon_data')]
        
        with db.engine.connect() as conn:
            if 'biodiversity_index' not in columns:
                conn.execute(db.text('ALTER TABLE carbon_data ADD COLUMN biodiversity_index FLOAT DEFAULT 0.75'))
            
            if 'date_added' not in columns:
                # Add column without default value (SQLite limitation)
                conn.execute(db.text('ALTER TABLE carbon_data ADD COLUMN date_added TIMESTAMP'))
                
                # Update existing rows with current timestamp
                current_time = datetime.datetime.now().isoformat()
                conn.execute(db.text(f"UPDATE carbon_data SET date_added = '{current_time}'"))
            
            conn.commit()
    
    # Create Product table if it doesn't exist
    if 'product' not in inspector.get_table_names():
        Product.__table__.create(db.engine)
        print('Created Product table!')
    
    # Create HarvestPeriod table if it doesn't exist
    if 'harvest_period' not in inspector.get_table_names():
        HarvestPeriod.__table__.create(db.engine)
        print('Created HarvestPeriod table!')
    
    # Create MetricsHistory table if it doesn't exist
    if 'metrics_history' not in inspector.get_table_names():
        from .models import MetricsHistory
        MetricsHistory.__table__.create(db.engine)
        print('Created MetricsHistory table!')

        
    # Ensure uploads directory exists
    os.makedirs('website/static/uploads', exist_ok=True)
    
    print('Database schema updated!')
