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
    
    # Ensure uploads directory exists with correct path
    uploads_dir = os.path.join(app.static_folder, 'uploads')
    os.makedirs(uploads_dir, exist_ok=True)
    print(f"Upload directory created at: {uploads_dir}")
    
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
    app.register_blueprint(metrics_bp, url_prefix='/metrics')
    app.register_blueprint(forest_bp, url_prefix='/api/forest')
    app.register_blueprint(product_bp, url_prefix='/api/product')
    app.register_blueprint(profile_bp, url_prefix='/api/profile')
    app.register_blueprint(general_bp, url_prefix='/api/general')

    # Register like routes that need to be accessible from main views
    from .routes.forest_routes import register_like_routes
    register_like_routes(app)

    from .models import User, Note, CarbonData, Product, HarvestPeriod
    
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
            
            if 'contact_email' not in columns:
                conn.execute(db.text('ALTER TABLE user ADD COLUMN contact_email VARCHAR(150)'))
            
            if 'contact_phone' not in columns:
                conn.execute(db.text('ALTER TABLE user ADD COLUMN contact_phone VARCHAR(50)'))
            
            if 'contact_visible' not in columns:
                conn.execute(db.text('ALTER TABLE user ADD COLUMN contact_visible BOOLEAN DEFAULT 1'))

            # Add new location fields
            if 'business_address' not in columns:
                conn.execute(db.text('ALTER TABLE user ADD COLUMN business_address VARCHAR(255)'))
            if 'business_city' not in columns:
                conn.execute(db.text('ALTER TABLE user ADD COLUMN business_city VARCHAR(100)'))
            if 'business_postal_code' not in columns:
                conn.execute(db.text('ALTER TABLE user ADD COLUMN business_postal_code VARCHAR(20)'))
            if 'business_country' not in columns:
                conn.execute(db.text('ALTER TABLE user ADD COLUMN business_country VARCHAR(100)'))

            if 'forest_address' not in columns:
                conn.execute(db.text('ALTER TABLE user ADD COLUMN forest_address VARCHAR(255)'))
            if 'forest_city' not in columns:
                conn.execute(db.text('ALTER TABLE user ADD COLUMN forest_city VARCHAR(100)'))
            if 'forest_postal_code' not in columns:
                conn.execute(db.text('ALTER TABLE user ADD COLUMN forest_postal_code VARCHAR(20)'))
            if 'forest_country' not in columns:
                conn.execute(db.text('ALTER TABLE user ADD COLUMN forest_country VARCHAR(100)'))

            # Add coordinate fields
            if 'forest_latitude' not in columns:
                conn.execute(db.text('ALTER TABLE user ADD COLUMN forest_latitude FLOAT'))
            if 'forest_longitude' not in columns:
                conn.execute(db.text('ALTER TABLE user ADD COLUMN forest_longitude FLOAT'))
            if 'business_latitude' not in columns:
                conn.execute(db.text('ALTER TABLE user ADD COLUMN business_latitude FLOAT'))
            if 'business_longitude' not in columns:
                conn.execute(db.text('ALTER TABLE user ADD COLUMN business_longitude FLOAT'))

            if 'messages_enabled' not in columns:
                conn.execute(db.text('ALTER TABLE user ADD COLUMN messages_enabled BOOLEAN DEFAULT 1'))
            
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

    # Create ForestLike table if it doesn't exist
    if 'forest_like' not in inspector.get_table_names():
        from .models import ForestLike
        ForestLike.__table__.create(db.engine)
        print('Created ForestLike table!')

    # Create Message table if it doesn't exist  
    if 'message' not in inspector.get_table_names():
        from .models import Message
        Message.__table__.create(db.engine)
        print('Created Message table!')
    
    print('Database schema updated!')
