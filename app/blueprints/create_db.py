
from flask import Blueprint, redirect, render_template, url_for
from werkzeug.security import generate_password_hash, check_password_hash

import app
from ..forms.forms import FillDatabaseForm
from ..models.models import Role, User, test_db_integrity
from ..extensions import db


db_blueprint = Blueprint('db', __name__, template_folder = 'templates')

@db_blueprint.route('/create-db', methods = ['GET', 'POST'])
def create_db():
    form = FillDatabaseForm()
    if test_db_integrity():
        return redirect(url_for('auth.login'))
    
    if form.validate_on_submit():

        new_role = Role(
            role_title = 'admin',
            role_description = 'Administrator with full permissions',
            can_view_users = True,
            can_edit_users = True,
            can_delete_users = True,
            can_create_users = True,
            can_view_bills = True,
            can_edit_bills = True,
            can_delete_bills = True,
            can_create_bills = True,
            can_view_tags = True,
            can_edit_tags = True,
            can_delete_tags = True,
            can_create_tags = True,
            can_view_roles = True,
            can_edit_roles = True,
            can_delete_roles = True,
            can_create_roles = True,
            can_manage_document_types = True
        )
        db.session.add(new_role)
        db.session.flush()
        
        hash_password = generate_password_hash(password=form.password.data, method='pbkdf2:sha256', salt_length=8) 
        new_user = User(
            name = form.username.data,
            email = form.email.data,
            password = hash_password,
            role = new_role
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('auth.login'))

    return render_template("create-db.html", form = form)