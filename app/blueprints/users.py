from flask import Blueprint, render_template, url_for, redirect, request, flash
from jinja2 import TemplateNotFound
from werkzeug.security import generate_password_hash

from .auth import login_required, permission_required
from ..models.models import User, Role, db
from ..forms.forms import RegisterForm

users_blueprint = Blueprint('users', __name__, template_folder = 'templates')

@users_blueprint.route('/changue-role/<int:user_id>', methods = ['GET', 'POST'])
@login_required
@permission_required('can_edit_users')
def changue_role(user_id):

    # Get the user in order to edit its properties
    user = db.get_or_404(User, user_id)

    # Get all the roles available
    result = db.session.execute(db.select(Role).where(Role.is_active))
    roles = result.scalars().all()
    if request.method == 'POST':
        # Role selected by the user
        role_selected = request.form.get('user_role')
        
        user.role = db.get_or_404(Role, role_selected)
        db.session.commit()
        return redirect(url_for('users.users_panel'))
    
    return render_template('edit-user-role.html', roles = roles, user=user)
    
 
@users_blueprint.route('/')
@login_required
@permission_required('can_view_users')
def users_panel():
    result = db.session.execute(db.select(User))
    users = result.scalars().all()
    return render_template('users.html', all_users = users)

@users_blueprint.route('/edit/<int:user_id>', methods = ['GET', 'POST'])
@login_required
@permission_required('can_edit_users')
def edit_user(user_id):
    user = db.get_or_404(User, user_id)
    edit_form = RegisterForm(
        name = user.name,
        email = user.email
    )
    if edit_form.validate_on_submit():
        user.name = edit_form.name.data
        user.email = edit_form.email.data
        
        user.password = generate_password_hash(password=edit_form.password.data, method='pbkdf2:sha256', salt_length=8) 
        db.session.commit()
        return redirect(url_for("users.users_panel"))
    return render_template("register.html", form=edit_form)

@users_blueprint.route('/delete/<int:user_id>')
@login_required
@permission_required('can_delete_users')
def delete_user(user_id):
    user_to_delete = db.get_or_404(User, user_id)
    db.session.delete(user_to_delete)
    db.session.commit()
    flash('User removed')
    return redirect(url_for('users.users_panel'))