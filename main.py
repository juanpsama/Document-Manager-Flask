from datetime import datetime
import os 

from flask import Flask, abort, render_template, redirect, url_for, flash, request, send_from_directory
from flask_bootstrap import Bootstrap5
from flask_login import login_user, LoginManager, current_user, logout_user, login_required
from flask_uploads import configure_uploads

from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

# Import your forms from the forms.py
from forms import CreateBillForm, RegisterForm, LoginForm, TagForm, CreateRoleForm, DocumentTypeForm, images
# Import db models from the models.py
from models import User, Bill, Tag, File, FileGroup, Role, DocumentType,  db

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY')
Bootstrap5(app)

# This is for config where the files should be stored
app.config['UPLOADS_DEFAULT_DEST'] =  'files/'
configure_uploads(app, (images, ))

# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URI", "sqlite:///posts.db")
# db = SQLAlchemy()
db.init_app(app)

with app.app_context():
    db.create_all()
    try: 
        # Create a new Role instance
        admin_role = Role(
            role_title='admin',
            role_description='Admin role with all permissions',
            can_view_users=True,
            can_edit_users=True,
            can_delete_users=True,
            can_create_users=True,
            can_view_bills=True,
            can_edit_bills=True,
            can_delete_bills=True,
            can_create_bills=True,
            can_view_tags=True,
            can_edit_tags=True,
            can_delete_tags=True,
            can_create_tags=True,
            can_view_roles=True,
            can_edit_roles=True,
            can_delete_roles=True,
            can_create_roles=True,
            can_manage_document_types = True
        )

        # Add the Role instance to the session
        db.session.add(admin_role)

        # Commit the session to save the changes
        db.session.commit()

        # Create a new User 
        hash_password = generate_password_hash(password='name', method='pbkdf2:sha256', salt_length=8)
        new_user = User(
            email = 'jp@mail.com',
            password = hash_password, 
            name='name', 
            role = admin_role   
        )
        
        db.session.add(new_user)
        db.session.commit()
    except:
        print('there is a admin already')
        pass

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app) 

def redirect_unauthorized():
    flash('Registrate antes de acceder a la pagina !!')
    return redirect(url_for('login'))
# TODO: Segment in different files all the different parts of the app
# Ex: Login, Bills, Roles, etc..
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
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

## Roles operations
@app.route('/roles', methods = ['GET', 'POST'])
@login_required
@permission_required('can_view_roles')
def roles_panel():
    result = db.session.execute(db.select(Role))
    roles = result.scalars().all()
    return render_template('roles.html', all_roles = roles)

@app.route('/roles/delete/<int:user_id>')
@login_required
@permission_required('can_delete_roles')
def delete_role(user_id):
    role_to_delete = db.get_or_404(Role, user_id)
    db.session.delete(role_to_delete)
    db.session.commit()
    # flash('User removed')
    return redirect(url_for('roles_panel'))

@app.route('/roles/create', methods = ['GET', 'POST'])
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
        
        return redirect(url_for('roles_panel'))
    return render_template("register-role.html", form = form)

@app.route('/roles/edit/<int:role_id>', methods = ['GET', 'POST'])
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
        role.can_create_roles = edit_role_form.can_create_roles.data,
        role.can_manage_document_types = edit_role_form.can_manage_document_types.data
        
        db.session.commit()
        return redirect(url_for("roles_panel"))
    return render_template("register-role.html", form = edit_role_form)

@app.route('/user/changue-role/<int:user_id>', methods = ['GET', 'POST'])
@login_required
@permission_required('can_edit_users')
def changue_role(user_id):

    # Get the user in order to edit its properties
    user = db.get_or_404(User, user_id)

    # Get all the roles available
    result = db.session.execute(db.select(Role))
    roles = result.scalars().all()
    if request.method == 'POST':
        # Role selected by the user
        role_selected = request.form.get('user_role')
        print(role_selected)        
        
        user.role = db.get_or_404(Role, role_selected)
        db.session.commit()
        return redirect(url_for('users_panel'))
    
    return render_template('edit-user-role.html', roles = roles, user=user)
    
 
## User operations
@app.route('/register', methods = ['GET', 'POST'])
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
            return redirect(url_for('login'))
        
        # Use Werkzeug to hash the user's password when creating a new user.
        hash_password = generate_password_hash(password=password, method='pbkdf2:sha256', salt_length=8) 
        new_user = User(
            name = name,
            email = email,
            password = hash_password
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('get_all_posts'))
    return render_template("register.html", form = form)


@app.route('/login', methods = ['GET', 'POST'])
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
                return redirect(url_for('get_all_posts'))
            # flash('Password Incorrect, please try again.')
            flash('Contraseña incorrecta, porfavor intenta de nuevo.')
        else:
            # flash('That email doesnt exist, please try again!!')
            flash('Ese email no esta registrado, porfavor intenta de nuevo!!')
    return render_template("login.html", form = form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))

@app.route('/')
def redirect_main():
    return redirect(url_for('login'))

# CRUD operations for users
@app.route('/users')
@login_required
@permission_required('can_view_users')
def users_panel():
    result = db.session.execute(db.select(User))
    users = result.scalars().all()
    return render_template('users.html', all_users = users)

@app.route('/users/edit/<int:user_id>', methods = ['GET', 'POST'])
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
        return redirect(url_for("users_panel"))
    return render_template("register.html", form=edit_form)

@app.route('/users/delete/<int:user_id>')
@login_required
@permission_required('can_delete_users')
def delete_user(user_id):
    user_to_delete = db.get_or_404(User, user_id)
    db.session.delete(user_to_delete)
    db.session.commit()
    # flash('User removed')
    return redirect(url_for('users_panel'))

## Operations for the bills
@app.route('/all_bills')
@login_required
@permission_required('can_view_bills')
def get_all_posts():

    page = request.args.get('page', 1, type=int)
    per_page = 10
    bills = Bill.query.order_by(Bill.folio.desc()).paginate(page=page, per_page=per_page, error_out=False)

    return render_template("index.html", all_posts=bills)

@app.route('/download/<int:file_id>')
@login_required
def downloadFile(file_id):
    filename = db.get_or_404(File, file_id)
    uploads = app.root_path
    
    return send_from_directory(uploads, filename.file_url)

@app.route("/bill/<int:bill_id>", methods=["GET", "POST"])
@login_required
@permission_required('can_view_bills')
def show_post(bill_id):
    requested_bill = db.get_or_404(Bill, bill_id)
    return render_template("post.html", post=requested_bill)

@app.route("/new-bill", methods=["GET", "POST"])
@login_required
@permission_required('can_create_bills')
def add_new_bill():
    form = CreateBillForm()
    
    document_types = db.session.execute(db.select(DocumentType)).scalars().all()
    tags = db.session.execute(db.select(Tag)).scalars().all()
    
    tag_choices = [(tag.id, tag.name) for tag in tags]  
    form.tags.choices = tag_choices

    type_choices = [(type.id, type.name) for type in document_types]  
    form.document_type.choices = type_choices

    # form.document_type.choices = [('Hola', 'hola2'), ('Hola1', 'hola1')]
    
    if form.validate_on_submit():
        # TODO: Encapsulate repetitive code into a function 
    
        # The multiple file field returns a list of files 
        # Assigning all the list to variables
        bill_files_pdf = form.bill_file_pdf.data
        client_deposit_images = form.client_file_image.data
        deposit_images = form.deposit_file_image.data

        # Getting a path to store every file on all the three lists
        bill_file_pdf_paths = [os.path.join(app.config['UPLOADS_DEFAULT_DEST'], 
                                            f'{str(datetime.now()).replace(" ", "_").replace(":",".")}{current_user.id}{os.path.splitext(file.filename)[1]}') 
                                            for file in bill_files_pdf]
        
        client_deposit_image_paths = [os.path.join(app.config['UPLOADS_DEFAULT_DEST'], 
                                            f'{str(datetime.now()).replace(" ", "_").replace(":",".")}{current_user.id}{os.path.splitext(file.filename)[1]}') 
                                            for file in client_deposit_images]
                                            
        deposit_image_paths = [os.path.join(app.config['UPLOADS_DEFAULT_DEST'], file.filename) for file in deposit_images]

        # Saving every one of the files in all three lists
        for i in range(len(bill_files_pdf)):
            bill_files_pdf[i].save(bill_file_pdf_paths[i])

        for i in range(len(client_deposit_images)):
            client_deposit_images[i].save(client_deposit_image_paths[i])

        for i in range(len(deposit_images)):
            deposit_images[i].save(deposit_image_paths[i])

        # Storing in the database as files to assign to a FileGroup
        bill_file_group = FileGroup()
        for path in bill_file_pdf_paths:
            new_file = File(
                file_url = path,
                file_group = bill_file_group  
            )
            db.session.add(new_file)
            db.session.commit()

        client_images_file_group = FileGroup()
        for path in client_deposit_image_paths:
            new_file = File(
                file_url = path,
                file_group = client_images_file_group 
            )
            db.session.add(new_file)
            db.session.commit()

        deposit_images_file_group = FileGroup()
        for path in deposit_image_paths:
            new_file = File(
                file_url = path,
                file_group = deposit_images_file_group  
            )
            db.session.add(new_file)
            db.session.commit()

        document_type_selected = db.get_or_404(DocumentType, form.document_type.data)
        new_bill = Bill(
            author = current_user,
            folio = str(datetime.now()).replace(' ', '_'),
            document_type = document_type_selected,
            
            payment_date = form.payment_date.data,
            bill_date = form.bill_date.data,
            bill_concept = form.bill_concept.data,
            description = form.description.data,
            # Assingning each group of files to the columns in bills
            bill_pdf = bill_file_group,
            client_deposit_image = client_images_file_group,
            deposit_image = deposit_images_file_group
        )
        db.session.add(new_bill)

        # 'form.tags.data' is a list of the tags selected
        for tag_id in form.tags.data:
            tag_selected = db.get_or_404(Tag, tag_id)
            new_bill.tags.append(tag_selected)

        db.session.commit()

        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)

@app.route("/edit-bill/<int:bill_id>", methods=["GET", "POST"])
@login_required
@permission_required('can_edit_bills')
def edit_post(bill_id):
    bill = db.get_or_404(Bill, bill_id)

    edit_form = CreateBillForm(
        document_type = bill.document_type,
        payment_date = bill.payment_date,
        bill_date = bill.bill_date,
        bill_concept = bill.bill_concept,
        description = bill.description
    )

    if edit_form.validate_on_submit():
        bill.document_type = edit_form.document_type.data
        bill.payment_date = edit_form.payment_date.data
        bill.bill_date = edit_form.bill_date.data
        bill.bill_concept = edit_form.bill_concept.data
        bill.description = edit_form.description.data
        db.session.commit()
        return redirect(url_for("show_post", bill_id=bill.id))
    return render_template("make-post.html", form=edit_form, is_edit=True)

@app.route("/delete/<int:post_id>")
@login_required
@permission_required('can_delete_bills')
def delete_bill(post_id):
    post_to_delete = db.get_or_404(Bill, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))



# Operations for tags and types
# TODO: make operations to edit, add and view tags

@app.route('/tag', methods = ['GET', 'POST'])
@login_required
@permission_required('can_view_tags')
@permission_required('can_create_tags')
def get_post_tag():
    form = TagForm()
    if request.method == 'POST':
        new_tag = Tag( name = form.name.data )
    
        db.session.add(new_tag)
        db.session.commit()

    result = db.session.execute(db.select(Tag))
    tags = result.scalars().all()
    return render_template('tag-manager.html', form = form, items = tags)

@app.route("/tag/<int:tag_id>", methods = ['GET'])
@login_required
@permission_required('can_delete_tags')
def delete_tag(tag_id):
    tag_to_delete = db.get_or_404(Tag, tag_id)
    db.session.delete(tag_to_delete)
    db.session.commit()
    return redirect(url_for('get_post_tag'))

# Operations for document_types
@app.route('/document-types', methods = ['GET', 'POST'])
@login_required
@permission_required('can_manage_document_types')
def get_document_types():
    form = DocumentTypeForm()
    if request.method == 'POST':
        new_tag = DocumentType( name = form.name.data )

        db.session.add(new_tag)
        db.session.commit()

    result = db.session.execute(db.select(DocumentType))
    document_type = result.scalars().all()

    # Se necesita otro template para cada vista tag y type
    return render_template('type-manager.html', form = form, items = document_type)

@app.route("/document-type/<int:type_id>", methods = ['GET'])
@login_required
@permission_required('can_manage_document_types')
def delete_document_type(type_id):
    tag_to_delete = db.get_or_404(DocumentType, type_id)
    db.session.delete(tag_to_delete)
    db.session.commit()
    return redirect(url_for('get_document_types'))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
