from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
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

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

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
    
    # Ensure uploads directory exists
    os.makedirs('website/static/uploads', exist_ok=True)
    
    print('Database schema updated!')
