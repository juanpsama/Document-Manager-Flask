from datetime import datetime
import os 

from flask import Flask, abort, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap5
from flask_login import login_user, LoginManager, current_user, logout_user, login_required
from flask_uploads import configure_uploads

from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

# Import your forms from the forms.py
from forms import CreateBillForm, RegisterForm, LoginForm, TagForm, images
# Import db models from the models.py
from models import User, Bill, Tag,  db

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY')
Bootstrap5(app)

# This is for config where the files should be stored
app.config['UPLOADS_DEFAULT_DEST'] =  'static/files/'
configure_uploads(app, (images, ))

# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URI", "sqlite:///posts.db")
# db = SQLAlchemy()
db.init_app(app)

with app.app_context():
    db.create_all()
    try: 
        hash_password = generate_password_hash(password='name', method='pbkdf2:sha256', salt_length=8)
        new_user = User(
        email = 'jp@mail.com',
        password = hash_password, 
        name='name', 
        is_admin = True
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
    flash('You have to register or login !!')
    return redirect(url_for('login'))

@login_manager.unauthorized_handler
def unauthorized():
    #return 'goog'
    return redirect_unauthorized()

# Create a user_loader callback
@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)

#Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        #The first user register is set as the admin 
        if not current_user.is_admin:
            return abort(404)
        return f(*args, **kwargs)
    return decorated_function

## User operations
@app.route('/register', methods = ['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data
        user = db.session.execute(db.select(User).where(User.email == email)).scalar()
        if user:
            flash('That email alredy exist please log in.')
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
            flash('Password Incorrect, please try again.')
        else:
            flash('That email doesnt exist, please try again!!')
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
@admin_required
def users_panel():
    result = db.session.execute(db.select(User))
    users = result.scalars().all()
    return render_template('users.html', all_users = users)

@login_required
@admin_required
@app.route('/users/edit/<int:user_id>', methods = ['GET', 'POST'])
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

@login_required
@admin_required
@app.route('/users/delete/<int:user_id>')
def delete_user(user_id):
    user_to_delete = db.get_or_404(User, user_id)
    db.session.delete(user_to_delete)
    db.session.commit()
    # flash('User removed')
    return redirect(url_for('users_panel'))

@login_required
@admin_required
@app.route('/users/change_admin/<int:user_id>')
def change_admin(user_id):
    user = db.get_or_404(User, user_id)
    user.is_admin = not user.is_admin
    db.session.commit()
    
    return redirect(url_for('users_panel'))


## Operations for the bills
@app.route('/all_bills')
@login_required
def get_all_posts():
    result = db.session.execute(db.select(Bill))
    posts = result.scalars().all()
    return render_template("index.html", all_posts=posts)

@app.route("/bill/<int:post_id>", methods=["GET", "POST"])
@login_required
def show_post(post_id):
    requested_post = db.get_or_404(Bill, post_id)
    form = TagForm()
    if form.validate_on_submit():
        # Allow only logged-in users to comment on posts
        if not current_user.is_authenticated:
           redirect_unauthorized()
        
        # new_comment = Comment(
        #     text=form.body.data,
        #     author=current_user,
        #     parent_post=requested_post
        # )

        # db.session.add(new_comment)
        # db.session.commit()

    return render_template("post.html", post=requested_post, form = form)

@app.route("/new-bill", methods=["GET", "POST"])
@login_required
def add_new_post():
    form = CreateBillForm()
    if form.validate_on_submit():
        
        # the multiple file field returns a list of files 
        bill_file_pdf = form.bill_file_pdf.data
        # print(bill_file_pdf)  
        client_deposit_image = form.client_file_image.data
        deposit_image = form.deposit_file_image.data

        bill_file_pdf_path = os.path.join(app.config['UPLOADS_DEFAULT_DEST'], bill_file_pdf.filename)
        client_deposit_image_path = os.path.join(app.config['UPLOADS_DEFAULT_DEST'], client_deposit_image.filename)
        deposit_image_path = os.path.join(app.config['UPLOADS_DEFAULT_DEST'], deposit_image.filename)

        bill_file_pdf.save(bill_file_pdf_path)
        client_deposit_image.save(client_deposit_image_path)
        deposit_image.save(deposit_image_path)

        new_bill = Bill(
            author = current_user,
            folio = str(datetime.now()).replace(' ', '_'),
            document_type = form.document_type.data,
            payment_date = form.payment_date.data,
            bill_date = form.bill_date.data,
            bill_concept = form.bill_concept.data,
            description = form.description.data,
            bill_pdf = bill_file_pdf_path.replace('static/',''),
            client_deposit_image = client_deposit_image_path.replace('static/',''),
            deposit_image = deposit_image_path.replace('static/','') 
        )
        db.session.add(new_bill)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)

@app.route("/edit-bill/<int:post_id>", methods=["GET", "POST"])
@login_required
@admin_required # Only an admin user can edit a post
def edit_post(post_id):
    post = db.get_or_404(Bill, post_id)
    edit_form = CreateBillForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = current_user
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))
    return render_template("make-post.html", form=edit_form, is_edit=True)

@app.route("/delete/<int:post_id>")
@login_required
@admin_required # Only an admin user can delete a bill
def delete_post(post_id):
    post_to_delete = db.get_or_404(Bill, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))

@app.route("/delete-comment/<int:comment_id>")
@login_required
@admin_required # Only an admin user can delete a comment
def delete_comment(comment_id):
    # comment_to_delete = db.get_or_404(Comment, comment_id)
    # parent_id = comment_to_delete.post_id
    # db.session.delete(comment_to_delete)
    # db.session.commit()
    return redirect(url_for('show_post', post_id = 1))

if __name__ == "__main__":
    app.run(debug=True, port=5000)
