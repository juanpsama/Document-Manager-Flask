from functools import wraps

from flask import flash, redirect, url_for, render_template, Blueprint
from flask_login import login_user, LoginManager, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

from models import User, Role, db
from forms import RegisterForm, LoginForm

login_manager = LoginManager()
auth_blueprint = Blueprint('auth', __name__, template_folder = 'templates')

def redirect_unauthorized():
    flash('Registrate antes de acceder a la pagina !!')
    return redirect(url_for('auth.login'))

@login_manager.unauthorized_handler
def unauthorized():
    #return 'goog'
    return redirect_unauthorized()

# Create a user_loader callback
@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)

#TODO: this is not tested, should be tested 
def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get the user's role from the database
            role = Role.query.filter_by(id=current_user.role_id).first()

            # Check if the role has the required permission
            if not getattr(role, permission):
                flash('No tienes permisos para ver esta pagina.')
                return redirect(url_for('auth.login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

## User operations
@auth_blueprint.route('/register', methods = ['GET', 'POST'])
# @permission_required('can_create_users')
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data
        user = db.session.execute(db.select(User).where(User.email == email)).scalar()
        if user:
            flash('Ese email ya existe porfavor log in.')
            return redirect(url_for('auth.login'))

        user_role = db.session.execute(db.select(Role).where(Role.role_title == 'user')).scalar()
        # Use Werkzeug to hash the user's password when creating a new user.
        hash_password = generate_password_hash(password=password, method='pbkdf2:sha256', salt_length=8) 
        new_user = User(
            name = name,
            email = email,
            password = hash_password,
            role = user_role
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('bills.get_all'))
    return render_template("register.html", form = form)


@auth_blueprint.route('/login', methods = ['GET', 'POST'])
def login(): 
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        # requested_user = db.get_or_404(User, post_id)

        # Retrieve a user from the database based on their email. 
        user = db.session.execute(db.select(User).where(User.email == email)).scalar()
        if user:
            if check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('bills.get_all'))
            flash('Contraseña incorrecta, porfavor intenta de nuevo.')
        else:
            flash('Ese email no esta registrado, porfavor intenta de nuevo!!')
    return render_template("login.html", form = form)

@auth_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
