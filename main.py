import os 

from flask import Flask, redirect, url_for
from flask_bootstrap import Bootstrap5
from flask_uploads import configure_uploads

# Import your forms from the forms.py
from forms import  images
# Import db models from the models.py
from models import db

#Blueprints
from roles import roles_blueprint
from auth import login_manager, auth_blueprint
from users import users_blueprint
from bills import bills_blueprint
from doc_types import doc_types_blueprint
from tags import tags_blueprint


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY')
Bootstrap5(app)

# This is for config where the files should be stored
app.config['UPLOADS_DEFAULT_DEST'] =  'files/'
configure_uploads(app, (images, ))

# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URI", "sqlite:///posts.db")

db.init_app(app)

with app.app_context():
    db.create_all()

login_manager.init_app(app) 

# TODO: Create a blueprint folder where all blueprints will live and add a __init__.py to make it a package
# Auth 
app.register_blueprint(auth_blueprint, url_prefix = '/')
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
    return redirect(url_for('auth.login'))

if __name__ == "__main__":
    app.run(debug=True, port=5000)
