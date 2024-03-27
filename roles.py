from flask import Blueprint, render_template, abort, url_for, redirect, flash
from jinja2 import TemplateNotFound

from models import Role, db
from forms import CreateRoleForm
from auth import login_required, permission_required

roles_blueprint = Blueprint('roles', __name__, template_folder = 'templates')

## Roles operations
@roles_blueprint.route('/', methods = ['GET', 'POST'])
@login_required
@permission_required('can_view_roles')
def roles_panel():
    result = db.session.execute(db.select(Role))
    roles = result.scalars().all()
    return render_template('roles.html', all_roles = roles)

@roles_blueprint.route('/delete/<int:role_id>')
@login_required
@permission_required('can_delete_roles')
def delete_role(role_id):
    role_to_delete = db.get_or_404(Role, role_id)
    db.session.delete(role_to_delete)
    db.session.commit()
    return redirect(url_for('roles.roles_panel'))

@roles_blueprint.route('/create', methods = ['GET', 'POST'])
@permission_required('can_create_roles')
def create_role():
    form = CreateRoleForm()
    if form.validate_on_submit():
        role = db.session.execute(db.select(Role).where(Role.role_title == form.role_title.data)).scalar()
        if role:
            flash('Ese nombre de rol ya existe por favor ingresa otro.')
            return redirect(url_for('roles_panel'))
         
        new_role = Role(
            role_title = form.role_title.data,
            role_description = form.role_description.data,
            can_view_users = form.can_view_users.data,
            can_edit_users = form.can_edit_users.data,
            can_delete_users = form.can_delete_users.data,
            can_create_users = form.can_create_users.data,
            can_view_bills = form.can_view_bills.data,
            can_edit_bills = form.can_edit_bills.data,
            can_delete_bills = form.can_delete_bills.data,
            can_create_bills = form.can_create_bills.data,
            can_view_tags = form.can_view_tags.data,
            can_edit_tags = form.can_edit_tags.data,
            can_delete_tags = form.can_delete_tags.data,
            can_create_tags = form.can_create_tags.data,
            can_view_roles = form.can_view_roles.data,
            can_edit_roles = form.can_edit_roles.data,
            can_delete_roles = form.can_delete_roles.data,
            can_create_roles = form.can_create_roles.data,
            can_manage_document_types = form.can_manage_document_types.data
        )
        db.session.add(new_role)
        db.session.commit()
        
        return redirect(url_for('roles.roles_panel'))
    return render_template("register-role.html", form = form)

@roles_blueprint.route('/edit/<int:role_id>', methods = ['GET', 'POST'])
@login_required
@permission_required('can_edit_roles')
def edit_role(role_id):
    # Get the role from the database
    role = db.session.query(Role).filter_by(id=role_id).first()

    # Create a form with the data from the role
    edit_role_form = CreateRoleForm(
        role_title = role.role_title,
        role_description = role.role_description,
        can_view_users = role.can_view_users,
        can_edit_users = role.can_edit_users,
        can_delete_users = role.can_delete_users,
        can_create_users = role.can_create_users,
        can_view_bills = role.can_view_bills,
        can_edit_bills = role.can_edit_bills,
        can_delete_bills = role.can_delete_bills,
        can_create_bills = role.can_create_bills,
        can_view_tags = role.can_view_tags,
        can_edit_tags = role.can_edit_tags,
        can_delete_tags = role.can_delete_tags,
        can_create_tags = role.can_create_tags,
        can_view_roles = role.can_view_roles,
        can_edit_roles = role.can_edit_roles,
        can_delete_roles = role.can_delete_roles,
        can_create_roles = role.can_create_roles,
        can_manage_document_types = role.can_manage_document_types
    )

    if edit_role_form.validate_on_submit():
        role.role_title = edit_role_form.role_title.data
        role.role_description = edit_role_form.role_description.data

        role.can_view_users = edit_role_form.can_view_users.data
        role.can_edit_users = edit_role_form.can_edit_users.data
        role.can_delete_users = edit_role_form.can_delete_users.data
        role.can_create_users = edit_role_form.can_create_users.data

        role.can_view_bills = edit_role_form.can_view_bills.data
        role.can_edit_bills = edit_role_form.can_edit_bills.data
        role.can_delete_bills = edit_role_form.can_delete_bills.data
        role.can_create_bills = edit_role_form.can_create_bills.data

        role.can_view_tags = edit_role_form.can_view_tags.data
        role.can_edit_tags = edit_role_form.can_edit_tags.data
        role.can_delete_tags = edit_role_form.can_delete_tags.data
        role.can_create_tags = edit_role_form.can_create_tags.data

        role.can_view_roles = edit_role_form.can_view_roles.data
        role.can_edit_roles = edit_role_form.can_edit_roles.data
        role.can_delete_roles = edit_role_form.can_delete_roles.data
        role.can_create_roles = edit_role_form.can_create_roles.data
        role.can_manage_document_types = edit_role_form.can_manage_document_types.data
        
        db.session.commit()
        return redirect(url_for("roles.roles_panel"))
    return render_template("register-role.html", form = edit_role_form)