from flask import Flask, redirect, url_for
from flask_bootstrap import Bootstrap5
from flask_uploads import configure_uploads
from flask_migrate import Migrate

from app.models.models import test_db_integrity

# Import your forms from the forms.py
from .forms.forms import  images

# Import db models from the models.py
# from .models.models import db

from .extensions import db

from .config import SECRET_KEY, DB_URL, UPLOAD_DESTINATION

#Blueprints
from .blueprints.roles import roles_blueprint
from .blueprints.auth import login_manager, auth_blueprint
from .blueprints.users import users_blueprint
from .blueprints.bills import bills_blueprint
from .blueprints.doc_types import doc_types_blueprint
from .blueprints.tags import tags_blueprint
from .blueprints.create_db import db_blueprint

def create_app(test_config=None):
    # create and configure the app

    app = Flask(__name__)
    app.config['SECRET_KEY'] = SECRET_KEY
    Bootstrap5(app)

    # This is for config where the files should be stored
    app.config['UPLOADS_DEFAULT_DEST'] = UPLOAD_DESTINATION
    configure_uploads(app, (images, ))

    # CONNECT TO DB
    app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL

    db.init_app(app)
    Migrate(app, db)

    with app.app_context():
        db.create_all()

    login_manager.init_app(app) 
    # Auth 
    app.register_blueprint(auth_blueprint, url_prefix = '/auth')

    app.register_blueprint(db_blueprint, url_prefix = '/db')
    # Roles operations
    app.register_blueprint(roles_blueprint, url_prefix = '/roles')
    # User
    app.register_blueprint(users_blueprint, url_prefix = '/users')
    # Documents
    app.register_blueprint(bills_blueprint, url_prefix = '/documents')
    # Document types
    app.register_blueprint(doc_types_blueprint, url_prefix = '/document-types')
    # Tags
    app.register_blueprint(tags_blueprint, url_prefix = '/tags')

    @app.route('/')
    def redirect_main():
        if not test_db_integrity():
            return redirect(url_for('db.create_db'))
        return redirect(url_for('auth.login'))
    
    return app